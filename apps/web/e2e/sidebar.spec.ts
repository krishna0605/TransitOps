import { expect, test } from "@playwright/test";

test("desktop sidebar reserves page content space", async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 800 });
  await page.goto("/dashboard");
  await expect(page.locator("[data-sidebar=trigger]")).toBeVisible();
  const dimensions = await page.locator("main").evaluate((element) => {
    const rect = element.getBoundingClientRect();
    return { left: rect.left, width: rect.width, viewport: window.innerWidth };
  });
  expect(dimensions.left).toBeGreaterThanOrEqual(48);
  expect(dimensions.left + dimensions.width).toBeLessThanOrEqual(
    dimensions.viewport + 1,
  );
});

test("mobile navigation opens as a sheet", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/dashboard");
  await page.locator("[data-sidebar=trigger]").click();
  await expect(page.getByRole("dialog", { name: "Sidebar" })).toBeVisible();
});
