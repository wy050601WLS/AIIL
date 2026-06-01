<script setup>
import { reactive, ref } from 'vue'
import { useUserStore } from '../stores/user'
import { ElMessage } from 'element-plus'

const userStore = useUserStore()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({ username: '', password: '' })

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  await formRef.value.validate()
  loading.value = true
  try {
    await userStore.login(form)
  } catch {
    ElMessage.error('用户名或密码错误')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-card">
      <h1 class="auth-title">AI 智慧学习</h1>
      <p class="auth-subtitle">登录以开始对话</p>

      <el-form ref="formRef" :model="form" :rules="rules" @keyup.enter="handleLogin">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" size="large" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码" size="large" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" :loading="loading" @click="handleLogin" class="auth-btn">
            登录
          </el-button>
        </el-form-item>
      </el-form>

      <p class="auth-link">
        还没有账号？<router-link to="/register">立即注册</router-link>
      </p>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-primary);
}

.auth-card {
  width: 400px;
  padding: 48px 40px;
  background: var(--bg-secondary);
  border-radius: var(--radius-xl);
  border: 1px solid var(--border);
  box-shadow: var(--shadow);
}

.auth-title {
  font-size: 28px;
  font-weight: 700;
  text-align: center;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.auth-subtitle {
  text-align: center;
  color: var(--text-secondary);
  margin-bottom: 36px;
}

.auth-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
  border-radius: var(--radius-md);
}

.auth-link {
  text-align: center;
  color: var(--text-secondary);
  font-size: 14px;
}

.auth-link a {
  color: var(--accent);
  text-decoration: none;
}

.auth-link a:hover {
  color: var(--accent-hover);
}
</style>
