import { HttpAgent, AbstractAgent, type RunAgentInput } from "@ag-ui/client";
import type { Observable } from "rxjs";
import {
  CopilotRuntime,
  ExperimentalEmptyAdapter,
  copilotRuntimeNodeHttpEndpoint,
} from "@copilotkit/runtime";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

/**
 * A wrapper agent that creates a fresh HttpAgent for each request.
 * This works around abort handling issues where the HttpAgent's internal
 * state can become corrupted after an abort, causing subsequent requests to fail.
 */
class FreshHttpAgent extends AbstractAgent {
  private url: string;
  private currentAgent: HttpAgent | null = null;

  constructor(config: { url: string }) {
    super();
    this.url = config.url;
  }

  run(input: RunAgentInput): Observable<any> {
    // Create a fresh HttpAgent for each request to ensure clean state
    this.currentAgent = new HttpAgent({ url: this.url });
    return this.currentAgent.run(input);
  }

  abortRun(): void {
    if (this.currentAgent) {
      this.currentAgent.abortRun();
      this.currentAgent = null;
    }
    super.abortRun();
  }
}

const runtime = new CopilotRuntime({
  agents: {
    agentic_chat: new FreshHttpAgent({ url: `${BACKEND_URL}/agui` }),
  },
});

const handler = copilotRuntimeNodeHttpEndpoint({
  runtime,
  serviceAdapter: new ExperimentalEmptyAdapter(),
  endpoint: "/api/copilotkit",
});

// GraphQL Yoga server works with Bun.serve
Bun.serve({
  port: 3002,
  fetch: handler.fetch,
});

console.log("CopilotKit server running on http://localhost:3002");
