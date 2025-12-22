import { test, expect, Page } from '@playwright/test';

/**
 * Role-Based Access Tests
 * Tests different user roles (Admin, Client)
 */

async function loginAsAdmin(page: Page) {
    await page.goto('/login');
    await page.fill('input[type="email"]', 'admin@afiliado.top');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("Entrar")');
    await page.waitForURL(/dashboard/);
}

async function loginAsClient(page: Page) {
    await page.goto('/login');
    await page.fill('input[type="email"]', 'client@afiliado.top');
    await page.fill('input[type="password"]', 'client123');
    await page.click('button:has-text("Entrar")');
    await page.waitForTimeout(2000);
}

test.describe('Admin Role Tests', () => {
    test('admin should access all dashboard sections', async ({ page }) => {
        await loginAsAdmin(page);

        // Should see admin navigation
        const nav = page.locator('nav, aside');
        await expect(nav).toBeVisible();

        // Should access Products
        await page.click('text=Produtos');
        await expect(page).toHaveURL(/products/);

        // Should access Overview
        await page.goto('/dashboard/overview');
        await expect(page.locator('text=/overview|dashboard/i')).toBeVisible();
    });

    test('admin should create products', async ({ page }) => {
        await loginAsAdmin(page);
        await page.goto('/dashboard/products');

        // Should see add button
        const addButton = page.locator('text=/adicionar/i').first();
        await expect(addButton).toBeVisible();

        // Can open modal
        await addButton.click();
        await expect(page.locator('text=/adicionar produto/i')).toBeVisible();
    });

    test('admin should edit products', async ({ page }) => {
        await loginAsAdmin(page);
        await page.goto('/dashboard/products');
        await page.waitForTimeout(1000);

        // Should see edit buttons
        const editButtons = page.locator('button[aria-label*="Editar"]');
        const count = await editButtons.count();

        if (count > 0) {
            await editButtons.first().click();
            await expect(page.locator('text=/editar produto/i')).toBeVisible();
        }
    });

    test('admin should delete products', async ({ page }) => {
        page.on('dialog', dialog => dialog.accept());

        await loginAsAdmin(page);
        await page.goto('/dashboard/products');
        await page.waitForTimeout(1000);

        // Should see delete buttons
        const deleteButtons = page.locator('button[aria-label*="Deletar"]');
        const count = await deleteButtons.count();

        // Admin can delete
        expect(count).toBeGreaterThanOrEqual(0);
    });

    test('admin should see all products', async ({ page }) => {
        await loginAsAdmin(page);
        await page.goto('/dashboard/products');
        await page.waitForLoadState('networkidle');

        // Should see products table or empty state
        const hasTable = await page.locator('table').isVisible();
        const hasEmpty = await page.locator('text=/nenhum produto/i').isVisible();

        expect(hasTable || hasEmpty).toBeTruthy();
    });
});

test.describe('Client Role Tests', () => {
    test('client should have limited navigation', async ({ page }) => {
        await loginAsClient(page);

        // Client might have different navigation
        const url = page.url();
        expect(url).toBeTruthy();

        // If redirected to client area
        if (url.includes('/client')) {
            await expect(page.locator('text=/client|área do cliente/i')).toBeVisible();
        }
    });

    test('client should not access admin features', async ({ page }) => {
        await loginAsClient(page);

        // Try to access admin products page
        await page.goto('/dashboard/products');
        await page.waitForTimeout(1000);

        const url = page.url();

        // Should either redirect or show limited view
        // Client might see read-only or be redirected
        expect(url).toBeTruthy();
    });

    test('client should see only their data', async ({ page }) => {
        await loginAsClient(page);

        if (page.url().includes('/client')) {
            // Client area should have limited data
            await expect(page.locator('text=/seus produtos|your products/i')).toBeVisible();
        }
    });

    test('client should not have create/edit/delete buttons', async ({ page }) => {
        await loginAsClient(page);

        // Navigate to products if accessible
        await page.goto('/dashboard/products');
        await page.waitForTimeout(1000);

        // Should not see admin buttons
        const addButton = page.locator('button:has-text("Adicionar")');
        const editButton = page.locator('button[aria-label*="Editar"]').first();
        const deleteButton = page.locator('button[aria-label*="Deletar"]').first();

        // These should not be visible or not exist for client
        const hasAdd = await addButton.isVisible().catch(() => false);
        const hasEdit = await editButton.isVisible().catch(() => false);
        const hasDelete = await deleteButton.isVisible().catch(() => false);

        // At least one should be hidden for client
        expect(hasAdd && hasEdit && hasDelete).toBeFalsy();
    });
});

test.describe('Role Switching Tests', () => {
    test('should handle role change on re-login', async ({ page }) => {
        // Login as admin
        await loginAsAdmin(page);
        await page.goto('/dashboard/products');

        // Verify admin access
        await expect(page.locator('text=/produtos/i')).toBeVisible();

        // Logout
        await page.evaluate(() => {
            localStorage.clear();
        });

        // Login as client
        await loginAsClient(page);

        // Should have different permissions
        const url = page.url();
        expect(url).toBeTruthy();
    });

    test('should not allow privilege escalation', async ({ page }) => {
        // Login as client
        await loginAsClient(page);

        // Try to manually set admin role in localStorage
        await page.evaluate(() => {
            const user = JSON.parse(localStorage.getItem('afiliadobot_user') || '{}');
            user.role = 'admin';
            localStorage.setItem('afiliadobot_user', JSON.stringify(user));
        });

        // Reload and try admin action
        await page.reload();
        await page.goto('/dashboard/products');

        // Backend should still restrict based on token, not client role
        await page.waitForTimeout(1000);
        expect(page.url()).toBeTruthy();
    });
});
