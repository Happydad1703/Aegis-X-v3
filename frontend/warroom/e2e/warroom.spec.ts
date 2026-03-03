import { test, expect } from "@playwright/test";

/**
 * E2E: Warroom/CIC. DB-Only Read; no crash when API down; freshness/stale handling.
 */
test.describe("Warroom", () => {
  test("load / (Warroom Home)", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("h1")).toContainText("CIC Warroom");
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
    await expect(header.getByRole("link", { name: "Aegis-X V3 CIC" })).toBeVisible({ timeout: 10000 });
    await expect(header.getByText("Mode", { exact: true })).toBeVisible();
    await expect(header.getByText("Regime", { exact: true })).toBeVisible();
    await expect(header.getByText("E-Stop", { exact: true })).toBeVisible();
    await expect(header.getByText("Retract", { exact: true })).toBeVisible();
  });

  test("snapshot cards show audit metadata", async ({ page }) => {
    const greenPayload = {
      snapshot_key: "mock_key",
      data: { mode: "PAPER", regime_label: "Sideways" },
      source_name: "mock",
      generated_at: "2026-03-03T00:00:00Z",
      refresh_rate_sec: 10,
      freshness_status: "GREEN",
    };
    await page.route("**/api/snapshot/**", async (route) => {
      const url = route.request().url();
      const key = decodeURIComponent(url.split("/api/snapshot/")[1] || "mock_key");
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ ...greenPayload, snapshot_key: key }),
      });
    });
    await page.route("**/api/snapshot/latest?key=*", async (route) => {
      const reqUrl = new URL(route.request().url());
      const key = reqUrl.searchParams.get("key") || "mock_key";
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ ...greenPayload, snapshot_key: key }),
      });
    });
    await page.route("**/api/control/state", async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ emergency_stop: false, retract: false }) });
    });
    await page.route("**/api/health", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ meta: { source: "mock-health" } }),
      });
    });

    await page.goto("/");
    await expect(page.getByText("source_name").first()).toBeVisible({ timeout: 10000 });
    await expect(page.getByText("generated_at").first()).toBeVisible({ timeout: 5000 });
    await expect(page.getByText("freshness_status").first()).toBeVisible({ timeout: 5000 });
  });

  test("API down shows DISCONNECTED without crash", async ({ page }) => {
    await page.route("**/api/**", async (route) => {
      await route.abort("failed");
    });
    await page.goto("/");
    await expect(page.locator("header").getByText("DISCONNECTED")).toBeVisible({ timeout: 10000 });
    await expect(page.locator("h1")).toContainText("CIC Warroom");
  });

  test("stale snapshot locks cards and disables controls", async ({ page }) => {
    const stalePayload = {
      snapshot_key: "mock_key",
      data: { mode: "PAPER", regime_label: "Sideways" },
      source_name: "mock",
      generated_at: "2026-03-03T00:00:00Z",
      refresh_rate_sec: 10,
      freshness_status: "RED",
    };

    await page.route("**/api/control/state", async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ emergency_stop: false, retract: false }) });
    });
    await page.route("**/api/snapshot/**", async (route) => {
      const url = route.request().url();
      const key = decodeURIComponent(url.split("/api/snapshot/")[1] || "mock_key");
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ ...stalePayload, snapshot_key: key }),
      });
    });
    await page.route("**/api/snapshot/latest?key=*", async (route) => {
      const reqUrl = new URL(route.request().url());
      const key = reqUrl.searchParams.get("key") || "mock_key";
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ ...stalePayload, snapshot_key: key }),
      });
    });
    await page.route("**/api/health", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ meta: { source: "mock-health" } }),
      });
    });

    await page.goto("/");
    await expect(page.getByText("Read-only — 사령부 승인 필요").first()).toBeVisible({ timeout: 10000 });
    await expect(page.getByRole("button", { name: "E-Stop" })).toBeDisabled();
    await expect(page.getByRole("button", { name: "Retract" })).toBeDisabled();
  });
});
