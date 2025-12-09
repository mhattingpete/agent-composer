import { test, expect } from "@playwright/test";

test("capture: log the request being sent to agui", async ({ page }) => {
  // Intercept requests to /api/copilotkit
  const requests: any[] = [];

  page.on("request", async (request) => {
    if (request.url().includes("/api/copilotkit")) {
      const postData = request.postData();
      console.log("=== REQUEST TO COPILOTKIT ===");
      console.log("URL:", request.url());
      console.log("Method:", request.method());
      console.log("Headers:", JSON.stringify(request.headers(), null, 2));
      if (postData) {
        try {
          const parsed = JSON.parse(postData);
          console.log("Body:", JSON.stringify(parsed, null, 2));
        } catch {
          console.log("Body (raw):", postData);
        }
      }
      requests.push({ url: request.url(), body: postData });
    }
  });

  page.on("response", async (response) => {
    if (response.url().includes("/api/copilotkit")) {
      console.log("=== RESPONSE FROM COPILOTKIT ===");
      console.log("Status:", response.status());
      try {
        const body = await response.text();
        console.log("Response body:", body.substring(0, 500));
      } catch (e) {
        console.log("Could not read response body");
      }
    }
  });

  await page.goto("http://localhost:3000/default");
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(2000);

  // Find and fill the chat input
  const chatInput = page.locator("textarea").first();
  await expect(chatInput).toBeVisible({ timeout: 10000 });

  await chatInput.fill("Hello");
  await chatInput.press("Enter");

  // Wait for request to be made
  await page.waitForTimeout(5000);

  console.log("Total requests captured:", requests.length);
});
