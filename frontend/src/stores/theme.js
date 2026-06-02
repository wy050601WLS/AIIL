/**
 * 主题状态管理 Store
 *
 * 管理深色/浅色主题切换，持久化到 localStorage。
 * 通过在 document.documentElement 上切换 'light' class 实现主题变化。
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const theme = ref(localStorage.getItem('theme') || 'dark')

  /** 将当前主题应用到 DOM：浅色模式添加 light class，深色模式移除 */
  function applyTheme() {
    if (theme.value === 'light') {
      document.documentElement.classList.add('light')
    } else {
      document.documentElement.classList.remove('light')
    }
  }

  /** 切换深色/浅色主题并持久化 */
  function toggle() {
    theme.value = theme.value === 'dark' ? 'light' : 'dark'
    localStorage.setItem('theme', theme.value)
    applyTheme()
  }

  // 初始化时立即应用主题
  applyTheme()

  return { theme, toggle }
})
