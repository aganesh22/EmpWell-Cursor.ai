import React from 'react';
import { useTheme } from '../lib/theme';

/**
 * A simple floating button rendered on every page that toggles
 * between light and dark themes. It purposefully avoids relying on any
 * existing design system classes so that it works regardless of the page
 * specific CSS. Styling is kept inline for maximum encapsulation.
 */
export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      style={{
        position: 'fixed',
        bottom: 24,
        right: 24,
        width: 48,
        height: 48,
        borderRadius: '50%',
        background: 'var(--color-primary)',
        color: '#fff',
        border: 'none',
        fontSize: 20,
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        boxShadow: '0 4px 12px rgba(0,0,0,0.25)',
        zIndex: 10000,
      }}
      aria-label="Toggle dark mode"
      title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
    >
      {theme === 'dark' ? '🌞' : '🌙'}
    </button>
  );
}