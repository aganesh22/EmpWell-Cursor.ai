import React, { createContext, useEffect, useState, useContext } from 'react';

// Types for theme
export type ThemeMode = 'light' | 'dark';

interface ThemeContextValue {
  theme: ThemeMode;
  toggleTheme: () => void;
  setTheme: (theme: ThemeMode) => void;
}

// Create context with default values
const ThemeContext = createContext<ThemeContextValue>({
  theme: 'light',
  // eslint-disable-next-line @typescript-eslint/no-empty-function
  toggleTheme: () => {},
  // eslint-disable-next-line @typescript-eslint/no-empty-function
  setTheme: () => {},
});

// Provider component
export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // Initialize theme from localStorage or default to light theme
  const [theme, setThemeState] = useState<ThemeMode>(() => {
    if (typeof window === 'undefined') return 'light';

    const stored = localStorage.getItem('theme-mode') as ThemeMode | null;
    if (stored === 'light' || stored === 'dark') return stored;

    // Default to light theme for better initial user experience
    // Users can still switch to dark if they prefer
    return 'light';
  });

  // Persist theme preference and update <html> class list with smooth transitions
  useEffect(() => {
    if (typeof window === 'undefined') return;

    localStorage.setItem('theme-mode', theme);
    const root = document.documentElement;
    
    // Add transition class for smooth theme switching
    root.style.transition = 'background-color 0.3s ease, color 0.3s ease';
    
    if (theme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }

    // Also update meta theme-color for mobile browsers
    const metaThemeColor = document.querySelector('meta[name="theme-color"]');
    if (metaThemeColor) {
      metaThemeColor.setAttribute('content', theme === 'dark' ? '#0a0a0a' : '#ffffff');
    } else {
      const meta = document.createElement('meta');
      meta.name = 'theme-color';
      meta.content = theme === 'dark' ? '#0a0a0a' : '#ffffff';
      document.head.appendChild(meta);
    }
  }, [theme]);

  const toggleTheme = () => setThemeState((prev) => (prev === 'dark' ? 'light' : 'dark'));
  
  const setTheme = (newTheme: ThemeMode) => setThemeState(newTheme);

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

// Convenience hook
export const useTheme = () => useContext(ThemeContext);