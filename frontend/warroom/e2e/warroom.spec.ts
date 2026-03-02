import { test, expect } from "@playwright/test";

/**
 * E2E: Warroom/CIC. DB-Only Read; no crash when API down; freshness/stale handling.
 */
test.describe("Warroom", () => {
  test("load / (Warroom Home)", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("h1")).toContainText("Sensor Fusion");
  });

  test("load / and show 6 core snapshot areas", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByText("regime_current").first()).toBeVisible({ timeout: 15000 });
    await expect(page.getByText("allocation_matrix").first()).toBeVisible({ timeout: 5000 });
    await expect(page.getByText("risk_guard").first()).toBeVisible({ timeout: 5000 });
    await expect(page.getByText("operation_mode").first()).toBeVisible({ timeout: 5000 });
    await expect(page.getByText("engine_heartbeat").first()).toBeVisible({ timeout: 5000 });
    await expect(page.getByText("fleet_budget_snapshot").first()).toBeVisible({ timeout: 5000 });
  });

  test("load /regime", async ({ page }) => {
    await page.goto("/regime");
    await expect(page.locator("h1")).toContainText("Regime");
  });

  test("header shows connection or degrade state", async ({ page }) => {
    await page.goto("/");
    const header = page.locator("header");
    await expect(header).toBeVisible();
    await expect(header.getByText(/Aegis-X|Mode|Regime|E-Stop|Retract|DISCONNECTED|DEGRADED|OK/)).toBeVisible({ timeout: 10000 });
  });

  test("snapshot cards show audit metadata", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByText("source_name").first()).toBeVisible({ timeout: 10000 });
    await expect(page.getByText("generated_at").first()).toBeVisible({ timeout: 5000 });
    await expect(page.getByText("freshness_status").first()).toBeVisible({ timeout: 5000 });
  });
});
