import { useEffect, useState } from 'react'

import { ThemeContext } from './themeContext'


export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(() => localStorage.getItem('debugmentor-theme') || 'dark')

  useEffect(() => {
    document.documentElement.dataset.theme = theme
    localStorage.setItem('debugmentor-theme', theme)
  }, [theme])

  return (
    <ThemeContext.Provider value={{
      theme,
      toggleTheme: () => setTheme((current) => (current === 'dark' ? 'light' : 'dark')),
    }}>
      {children}
    </ThemeContext.Provider>
  )
}
