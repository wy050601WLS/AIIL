/**
 * 应用入口模块
 *
 * 创建 Vue 应用实例并注册插件：
 * - Pinia：状态管理
 * - Vue Router：路由
 * - Element Plus：按需导入（由 unplugin-vue-components 自动处理）
 * - highlight.js：代码块语法高亮样式
 */

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import 'highlight.js/styles/github-dark.css'

import App from './App.vue'
import router from './router'
import './style.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
