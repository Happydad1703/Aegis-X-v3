import { test, expect } from "@playwright/test";

/**
 * Warroom/Cockpit E2E — SE compliance:
 * - Load homepage
 * - Verify 6 core snapshot panels render
 * - Verify freshness metadata present
 * - Trigger command → verify snapshot change (or command accepted)
 */
test.describe("Cockpit", () => {
  test("load homepage", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("h1")).toContainText("Aegis-X");
  });

  test("verify 6 core snapshot panels render on Global Overview", async ({ page }) => {
    await page.goto("/");
    await page.click("a:has-text('Global Overview')");
    const coreKeys = [
      "engine_heartbeat",
      "comm_health",
      "llm_status",
      "operation_mode",
      "regime_current",
      "risk_guard",
    ];
    for (const key of coreKeys) {
      await expect(page.locator(`.card h3:has-text("${key}")`)).toBeVisible({ timeout: 15000 });
    }
  });

  test("verify freshness metadata present on snapshot cards", async ({ page }) => {
    await page.goto("/");
    await page.click("a:has-text('Global Overview')");
    await expect(page.locator("text=refresh_rate_sec")).toBeVisible({ timeout: 10000 });
    await expect(page.locator("text=freshness_status")).toBeVisible({ timeout: 5000 });
    await expect(page.locator("text=source_name")).toBeVisible({ timeout: 5000 });
    await expect(page.locator("text=generated_at")).toBeVisible({ timeout: 5000 });
  });

  test("trigger Run Cycle command and verify no error", async ({ page }) => {
    await page.goto("/");
    await page.click("button:has-text('Run Cycle')");
    await page.waitForTimeout(2000);
    const err = page.locator("text=Contract Break");
    await expect(err).toHaveCount(0);
  });
});
