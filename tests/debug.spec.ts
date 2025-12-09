import { test, expect } from "@playwright/test";

test("debug: check for errors and wait for response", async ({ page }) => {
  // Collect console errors
  const errors: string[] = [];
  page.on("console", (msg) => {
    if (msg.type() === "error") {
      errors.push(msg.text());
    }
  });

  page.on("pageerror", (err) => {
    errors.push(err.message);
  });

  await page.goto("http://localhost:3000/default");
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(3000);

  // Click on the "1 Issue" button if visible to see error details
  const issueButton = page.locator('text="1 Issue"');
  if (await issueButton.isVisible()) {
    await issueButton.click();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: "/tmp/claude/error-details.png" });
  }

  // Check backend health
  const backendHealth = await page.request.get("http://localhost:8000/health").catch(() => null);
  console.log("Backend health:", backendHealth?.status());

  // Check what endpoints exist
  const aguiResponse = await page.request.post("http://localhost:8000/agui", {
    data: { test: true }
  }).catch((e) => {
    console.log("AGUI error:", e.message);
    return null;
  });
  console.log("AGUI response:", aguiResponse?.status());

  // Print collected errors
  console.log("Collected errors:", errors);

  await page.screenshot({ path: "/tmp/claude/debug-final.png" });
});
