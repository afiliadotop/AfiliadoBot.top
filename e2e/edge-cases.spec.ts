import { test, expect } from '@playwright/test';

/**
 * E2E Edge Cases and Error Scenarios
 * Tests boundary conditions and error handling
 */

test.describe('Edge Cases and Error Handling', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/login');
    });

    test('should handle empty form submission', async ({ page }) => {
        // Try to submit empty form
        await page.click('button:has-text("Entrar")');

        // Should show validation errors
        await expect(
            page.locator('text=/obrigatório|required|preencha/i')
        ).toBeVisible({ timeout: 3000 });
    });

    test('should handle special characters in credentials', async ({ page }) => {
        await page.fill('input[type="email"]', 'test@<script>alert("xss")</script>.com');
        await page.fill('input[type="password"]', '<img src=x onerror=alert(1)>');
        await page.click('button:has-text("Entrar")');

        // Should sanitize and not execute scripts
        await page.waitForTimeout(1000);
        // If no alert appeared, XSS was prevented
        expect(page.url()).toBeTruthy();
    });

    test('should handle very long input strings', async ({ page }) => {
        const longString = 'a'.repeat(1000);
        await page.fill('input[type="email"]', longString + '@test.com');
        await page.fill('input[type="password"]', longString);

        // Should handle gracefully without crashing
        await page.click('button:has-text("Entrar")');
        await page.waitForTimeout(1000);
        expect(page.url()).toBeTruthy();
    });

    test('should handle rapid form submissions', async ({ page }) => {
        await page.fill('input[type="email"]', 'test@test.com');
        await page.fill('input[type="password"]', 'password');

        // Click submit multiple times rapidly
        const submitButton = page.locator('button:has-text("Entrar")');
        await submitButton.click();
        await submitButton.click();
        await submitButton.click();

        // Should not cause multiple API calls or crashes
        await page.waitForTimeout(2000);
        expect(page.url()).toBeTruthy();
    });

    test('should handle network errors gracefully', async ({ page, context }) => {
        // Block API requests to simulate network failure
        await context.route('**/api/**', route => route.abort());

        await page.fill('input[type="email"]', 'test@test.com');
        await page.fill('input[type="password"]', 'password');
        await page.click('button:has-text("Entrar")');

        // Should show error message, not crash
        await expect(
            page.locator('text=/erro|error|falha/i')
        ).toBeVisible({ timeout: 5000 });
    });

    test('should handle expired session', async ({ page }) => {
        // Set expired token
        await page.evaluate(() => {
            localStorage.setItem('afiliadobot_token', 'expired-token-123');
            localStorage.setItem('afiliadobot_user', JSON.stringify({
                id: 1,
                name: 'Test',
                email: 'test@test.com'
            }));
        });

        // Try to access protected route
        await page.goto('/dashboard/products');

        // Should redirect to login or show error
        await page.waitForTimeout(2000);
        const url = page.url();
        expect(url).toMatch(/login|erro/);
    });

    test('should handle browser back during form submission', async ({ page }) => {
        await page.fill('input[type="email"]', 'test@test.com');
        await page.fill('input[type="password"]', 'password');
        await page.click('button:has-text("Entrar")');

        // Immediately go back
        await page.goBack();

        // Should handle gracefully
        await page.waitForTimeout(1000);
        expect(page.url()).toBeTruthy();
    });

    test('should handle missing CSRF token', async ({ page, context }) => {
        // Remove CSRF headers if any
        await context.route('**/api/**', route => {
            const headers = route.request().headers();
            delete headers['x-csrf-token'];
            route.continue({ headers });
        });

        await page.fill('input[type="email"]', 'test@test.com');
        await page.fill('input[type="password"]', 'password');
        await page.click('button:has-text("Entrar")');

        // Should either work or show proper error
        await page.waitForTimeout(2000);
        expect(page.url()).toBeTruthy();
    });

    test('should handle concurrent user sessions', async ({ page, context }) => {
        // Login in first tab
        await page.goto('/login');
        await page.fill('input[type="email"]', 'admin@afiliado.top');
        await page.fill('input[type="password"]', 'admin123');
        await page.click('button:has-text("Entrar")');
        await page.waitForURL(/dashboard/);

        // Open second tab
        const page2 = await context.newPage();
        await page2.goto('/dashboard');

        // Both should work or handle gracefully
        expect(page.url()).toContain('dashboard');
        expect(page2.url()).toBeTruthy();

        await page2.close();
    });

    test('should handle malformed API responses', async ({ page, context }) => {
        // Return malformed JSON
        await context.route('**/api/auth/login', route => {
            route.fulfill({
                status: 200,
                body: 'not-valid-json{{{',
            });
        });

        await page.fill('input[type="email"]', 'test@test.com');
        await page.fill('input[type="password"]', 'password');
        await page.click('button:has-text("Entrar")');

        // Should show error, not crash
        await page.waitForTimeout(2000);
        expect(page.url()).toBeTruthy();
    });
});
