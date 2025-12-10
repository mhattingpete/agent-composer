import { CopilotKit } from "@copilotkit/react-core";
import Chat from "./components/Chat";
import "@copilotkit/react-ui/styles.css";
import "./copilotkit.css";

function App() {
  return (
    <CopilotKit
      runtimeUrl="/api/copilotkit"
      showDevConsole={false}
      agent="agentic_chat"
    >
      <Chat />
    </CopilotKit>
  );
}

export default App;
