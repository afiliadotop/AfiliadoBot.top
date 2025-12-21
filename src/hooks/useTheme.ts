import { useState, useEffect } from 'react';

type Theme = 'light' | 'dark' | 'system';

export const useTheme = () => {
    const [theme, setTheme] = useState<Theme>(() => {
        // Get from localStorage or default to system
        const stored = localStorage.getItem('theme') as Theme;
        return stored || 'system';
    });

    const [resolvedTheme, setResolvedTheme] = useState<'light' | 'dark'>('dark');

    useEffect(() => {
        const root = window.document.documentElement;

        // Determine actual theme to apply
        let actualTheme: 'light' | 'dark';

        if (theme === 'system') {
            actualTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        } else {
            actualTheme = theme;
        }

        setResolvedTheme(actualTheme);

        // Remove both classes first
        root.classList.remove('light', 'dark');

        // Add the resolved theme class
        root.classList.add(actualTheme);

        // Store preference
        localStorage.setItem('theme', theme);
    }, [theme]);

    // Listen to system theme changes when in system mode
    useEffect(() => {
        if (theme !== 'system') return;

        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

        const handleChange = () => {
            const actualTheme = mediaQuery.matches ? 'dark' : 'light';
            setResolvedTheme(actualTheme);

            const root = window.document.documentElement;
            root.classList.remove('light', 'dark');
            root.classList.add(actualTheme);
        };

        mediaQuery.addEventListener('change', handleChange);
        return () => mediaQuery.removeEventListener('change', handleChange);
    }, [theme]);

    return { theme, setTheme, resolvedTheme };
};
