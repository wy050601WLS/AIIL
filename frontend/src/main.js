/**
 * 应用入口模块
 *
 * 创建 Vue 应用实例并注册插件：
 * - Pinia：状态管理
 * - Vue Router：路由
 * - Element Plus：UI 组件库（含深色主题 CSS 变量）
 * - highlight.js：代码块语法高亮样式
 */

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import 'highlight.js/styles/github-dark.css'

import App from './App.vue'
import router from './router'
import './style.css'

const app = createApp(App)
app.use(createPinia())   // 注册 Pinia 状态管理
app.use(router)          // 注册路由
app.use(ElementPlus)     // 注册 Element Plus 组件库
app.mount('#app')
