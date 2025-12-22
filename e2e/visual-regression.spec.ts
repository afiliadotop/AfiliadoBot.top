import { test, expect } from '@playwright/test';

/**
 * Visual Regression Tests
 * Captures screenshots and compares with baseline
 */

test.describe('Visual Regression', () => {
    test('landing page visual regression', async ({ page }) => {
        await page.goto('/');
        await page.waitForLoadState('networkidle');

        // Full page screenshot
        await expect(page).toHaveScreenshot('landing-page.png', {
            fullPage: true,
            maxDiffPixels: 100, // Allow small differences
        });
    });

    test('login page visual regression', async ({ page }) => {
        await page.goto('/login');
        await page.waitForLoadState('networkidle');

        await expect(page).toHaveScreenshot('login-page.png', {
            fullPage: true,
        });
    });

    test('dashboard visual regression', async ({ page }) => {
        // Login first
        await page.goto('/login');
        await page.fill('input[type="email"]', 'admin@afiliado.top');
        await page.fill('input[type="password"]', 'admin123');
        await page.click('button:has-text("Entrar")');
        await page.waitForURL(/dashboard/);
        await page.waitForLoadState('networkidle');

        await expect(page).toHaveScreenshot('dashboard.png', {
            fullPage: true,
            maxDiffPixels: 200,
        });
    });

    test('products page visual regression', async ({ page }) => {
        // Login
        await page.goto('/login');
        await page.fill('input[type="email"]', 'admin@afiliado.top');
        await page.fill('input[type="password"]', 'admin123');
        await page.click('button:has-text("Entrar")');

        // Navigate to products
        await page.goto('/dashboard/products');
        await page.waitForLoadState('networkidle');

        await expect(page).toHaveScreenshot('products-page.png', {
            fullPage: true,
            maxDiffPixels: 200,
        });
    });

    test('dark mode visual regression', async ({ page }) => {
        await page.goto('/');

        // Toggle to dark mode
        const themeToggle = page.locator('button[aria-label*="tema"]').first();
        if (await themeToggle.isVisible()) {
            await themeToggle.click();
            await page.waitForTimeout(500);

            await expect(page).toHaveScreenshot('landing-dark-mode.png', {
                fullPage: true,
            });
        }
    });

    test('mobile viewport visual regression', async ({ page }) => {
        // Set mobile viewport
        await page.setViewportSize({ width: 375, height: 667 });
        await page.goto('/');
        await page.waitForLoadState('networkidle');

        await expect(page).toHaveScreenshot('mobile-landing.png', {
            fullPage: true,
        });
    });

    test('tablet viewport visual regression', async ({ page }) => {
        await page.setViewportSize({ width: 768, height: 1024 });
        await page.goto('/');
        await page.waitForLoadState('networkidle');

        await expect(page).toHaveScreenshot('tablet-landing.png', {
            fullPage: true,
        });
    });

    test('product modal visual regression', async ({ page }) => {
        // Login and navigate
        await page.goto('/login');
        await page.fill('input[type="email"]', 'admin@afiliado.top');
        await page.fill('input[type="password"]', 'admin123');
        await page.click('button:has-text("Entrar")');
        await page.goto('/dashboard/products');

        // Open modal
        await page.click('text=/adicionar|novo/i');
        await page.waitForTimeout(500);

        // Screenshot just the modal
        const modal = page.locator('[role="dialog"], .modal').first();
        if (await modal.isVisible()) {
            await expect(modal).toHaveScreenshot('product-modal.png');
        }
    });

    test('error state visual regression', async ({ page }) => {
        await page.goto('/login');

        // Trigger error
        await page.fill('input[type="email"]', 'wrong@test.com');
        await page.fill('input[type="password"]', 'wrong');
        await page.click('button:has-text("Entrar")');

        // Wait for error
        await page.waitForTimeout(2000);

        await expect(page).toHaveScreenshot('login-error-state.png');
    });
});
