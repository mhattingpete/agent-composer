import { test, expect } from "@playwright/test";

test.describe("Chat UI", () => {
  test("should display chat interface and receive response", async ({ page }) => {
    // Go to chat page
    await page.goto("/default");

    // Wait for the chat interface to load
    await expect(page.getByText("Hi, I'm an agent. Want to chat?")).toBeVisible({ timeout: 10000 });

    // Find the input textarea
    const input = page.locator('textarea[placeholder*="Type a message"]');
    await expect(input).toBeVisible();

    // Type a simple message - just "hi" to get a quick response
    await input.fill("hi");

    // Press Enter to send
    await input.press("Enter");

    // Wait for the user message to appear (use exact match)
    await expect(page.getByText("hi", { exact: true })).toBeVisible({ timeout: 5000 });

    // Wait for an assistant response - look for a second copilotKitAssistantMessage
    // The first one is the initial greeting, the second one is the AI response
    await expect(async () => {
      const assistantMessages = page.locator('.copilotKitAssistantMessage');
      const count = await assistantMessages.count();
      expect(count).toBeGreaterThanOrEqual(2);
    }).toPass({ timeout: 60000 }); // 60s for LLM to respond

    // Verify the second message has content
    const secondMessage = page.locator('.copilotKitAssistantMessage').nth(1);
    const text = await secondMessage.textContent();
    expect(text).toBeTruthy();
    expect(text!.length).toBeGreaterThan(5);

    // Take a screenshot to verify
    await page.screenshot({ path: '/tmp/claude/chat-response.png' });

    console.log("Chat test passed - received response from agent!");
  });

  test("should show suggestions", async ({ page }) => {
    await page.goto("/default");

    // Check that suggestions are visible
    await expect(page.getByText("Change background")).toBeVisible({ timeout: 10000 });
    await expect(page.getByText("Generate sonnet")).toBeVisible();
  });
});
