<!--
  Register 视图 — 注册页

  功能：用户注册，含用户名/密码/确认密码表单验证
  注册成功后自动登录并跳转首页
-->
<script setup>
import { reactive, ref } from 'vue'
import { useUserStore } from '../stores/user'
import { ElMessage } from 'element-plus'

const userStore = useUserStore()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({ username: '', password: '', confirmPassword: '' })

// 表单验证规则：用户名 2-50 字符，密码 6-100 字符，两次密码一致
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 50, message: '用户名长度 2-50 个字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 100, message: '密码长度 6-100 个字符', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== form.password) callback(new Error('两次密码不一致'))
        else callback()
      },
      trigger: 'blur',
    },
  ],
}

/** 提交注册表单：验证 → 调用 store 注册（自动登录） → 失败提示 */
async function handleRegister() {
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  loading.value = true
  try {
    await userStore.register(form)
    ElMessage.success('注册成功')
  } catch {
    ElMessage.error('注册失败，用户名可能已存在')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-card">
      <h1 class="auth-title">创建账号</h1>
      <p class="auth-subtitle">注册后即可开始 AI 学习之旅</p>

      <el-form ref="formRef" :model="form" :rules="rules" @keyup.enter="handleRegister">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" size="large" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码（至少 6 位）" size="large" show-password />
        </el-form-item>
        <el-form-item prop="confirmPassword">
          <el-input v-model="form.confirmPassword" type="password" placeholder="确认密码" size="large" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" :loading="loading" @click="handleRegister" class="auth-btn">
            注册
          </el-button>
        </el-form-item>
      </el-form>

      <p class="auth-link">
        已有账号？<router-link to="/login">立即登录</router-link>
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
  width: var(--auth-card-width);
  padding: var(--space-xl) 40px;
  background: var(--bg-secondary);
  border-radius: var(--radius-xl);
  border: 1px solid var(--border);
  box-shadow: var(--shadow);
}

.auth-title {
  font-size: var(--text-2xl);
  font-weight: 700;
  text-align: center;
  color: var(--text-primary);
  margin-bottom: var(--space-sm);
}

.auth-subtitle {
  text-align: center;
  color: var(--text-secondary);
  margin-bottom: 36px;
}

.auth-btn {
  width: 100%;
  height: 44px;
  font-size: var(--text-lg);
  border-radius: var(--radius-md);
}

.auth-link {
  text-align: center;
  color: var(--text-secondary);
  font-size: var(--text-base);
}

.auth-link a {
  color: var(--accent);
  text-decoration: none;
}

.auth-link a:hover {
  color: var(--accent-hover);
}

@media (max-width: 480px) {
  .auth-card {
    width: 100%;
    padding: var(--space-xl) var(--space-lg);
  }
}
</style>
