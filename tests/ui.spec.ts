import { test, expect } from "@playwright/test";

test.describe("Agent Composer UI", () => {
  test("should load the chat interface", async ({ page }) => {
    // Navigate to the default chat page
    await page.goto("http://localhost:3000/default");

    // Wait for the page to load
    await page.waitForLoadState("networkidle");

    // Take a screenshot for debugging
    await page.screenshot({ path: "/tmp/claude/ui-loaded.png" });

    // Check if the CopilotChat component is visible
    // Look for common CopilotKit elements
    const chatContainer = page.locator('[data-testid="background-container"]');
    await expect(chatContainer).toBeVisible({ timeout: 10000 });

    console.log("Chat container found!");
  });

  test("should display initial greeting", async ({ page }) => {
    await page.goto("http://localhost:3000/default");
    await page.waitForLoadState("networkidle");

    // Look for the initial greeting text
    const greeting = page.getByText("Hi, I'm an agent. Want to chat?");
    await expect(greeting).toBeVisible({ timeout: 15000 });

    await page.screenshot({ path: "/tmp/claude/greeting-visible.png" });
    console.log("Greeting message found!");
  });

  test("should show chat input", async ({ page }) => {
    await page.goto("http://localhost:3000/default");
    await page.waitForLoadState("networkidle");

    // Look for textarea or input for chat
    const chatInput = page.locator('textarea, input[type="text"]').first();
    await expect(chatInput).toBeVisible({ timeout: 10000 });

    await page.screenshot({ path: "/tmp/claude/chat-input.png" });
    console.log("Chat input found!");
  });

  test("should send a message and get a response", async ({ page }) => {
    await page.goto("http://localhost:3000/default");
    await page.waitForLoadState("networkidle");

    // Wait for chat to be ready
    await page.waitForTimeout(2000);

    // Find and fill the chat input
    const chatInput = page.locator('textarea').first();
    await expect(chatInput).toBeVisible({ timeout: 10000 });

    await chatInput.fill("Hello, can you hear me?");
    await page.screenshot({ path: "/tmp/claude/message-typed.png" });

    // Submit the message (press Enter or click send button)
    await chatInput.press("Enter");

    // Wait for response (look for any new message in the chat)
    await page.waitForTimeout(10000);
    await page.screenshot({ path: "/tmp/claude/after-send.png" });

    console.log("Message sent, check screenshots for response");
  });
});
