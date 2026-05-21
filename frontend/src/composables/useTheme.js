import { ref } from 'vue'

const THEME_KEY = 'bookmark-theme'
const theme = ref('light')

function applyTheme(nextTheme) {
  theme.value = nextTheme
  document.documentElement.setAttribute('data-theme', nextTheme)
  localStorage.setItem(THEME_KEY, nextTheme)
}

export function initTheme() {
  const savedTheme = localStorage.getItem(THEME_KEY)
  if (savedTheme === 'dark' || savedTheme === 'light') {
    applyTheme(savedTheme)
    return
  }

  const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
  applyTheme(prefersDark ? 'dark' : 'light')
}

export function useTheme() {
  function toggleTheme() {
    applyTheme(theme.value === 'dark' ? 'light' : 'dark')
  }

  return {
    theme,
    toggleTheme,
  }
}
