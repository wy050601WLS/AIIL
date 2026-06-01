<script setup>
import { reactive, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { changePassword } from '../api/auth'
import { useUserStore } from '../stores/user'
import { useRouter } from 'vue-router'

const userStore = useUserStore()
const router = useRouter()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({ oldPassword: '', newPassword: '', confirmPassword: '' })

const presetAvatars = [
  '🧑‍💻', '👨‍🎓', '👩‍🎓', '🧑‍🔬', '👨‍💼', '👩‍💼', '🦊', '🐱',
  '🐼', '🦉', '🌟', '🎯', '🚀', '💡', '📚', '🎨',
]

const profileForm = reactive({
  nickname: '',
  avatar: presetAvatars[0],
})

const prefForm = reactive({
  fontSize: 15,
  messageDensity: 'normal',
  defaultModel: '',
})

onMounted(async () => {
  await userStore.loadProfile()
  profileForm.nickname = userStore.nickname || ''
  profileForm.avatar = userStore.avatar || presetAvatars[0]
  prefForm.fontSize = userStore.preferences?.fontSize || 15
  prefForm.messageDensity = userStore.preferences?.messageDensity || 'normal'
  prefForm.defaultModel = userStore.preferences?.defaultModel || ''
})

const rules = {
  oldPassword: [{ required: true, message: '请输入旧密码', trigger: 'blur' }],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 100, message: '密码长度 6-100 个字符', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== form.newPassword) callback(new Error('两次密码不一致'))
        else callback()
      },
      trigger: 'blur',
    },
  ],
}

async function handleSubmit() {
  await formRef.value.validate()
  loading.value = true
  try {
    await changePassword(form.oldPassword, form.newPassword)
    ElMessage.success('密码修改成功，请重新登录')
    userStore.logout()
  } catch {
    ElMessage.error('旧密码错误')
  } finally {
    loading.value = false
  }
}

async function saveProfile() {
  try {
    await userStore.saveProfile({
      nickname: profileForm.nickname,
      avatar: profileForm.avatar,
    })
    ElMessage.success('个人信息已保存')
  } catch {
    ElMessage.error('保存失败')
  }
}

async function savePreferences() {
  try {
    await userStore.saveProfile({ preferences: { ...prefForm } })
    ElMessage.success('偏好设置已保存')
  } catch {
    ElMessage.error('保存失败')
  }
}

function goBack() {
  router.push('/')
}
</script>

<template>
  <div class="settings-page">
    <div class="settings-card">
      <div class="settings-header">
        <el-button text @click="goBack" class="back-btn">&larr; 返回</el-button>
        <h2>用户设置</h2>
      </div>

      <!-- 个人信息 -->
      <div class="settings-section">
        <h3>个人信息</h3>
        <div class="avatar-picker">
          <div
            v-for="a in presetAvatars"
            :key="a"
            class="avatar-option"
            :class="{ selected: profileForm.avatar === a }"
            @click="profileForm.avatar = a"
          >{{ a }}</div>
        </div>
        <el-input v-model="profileForm.nickname" placeholder="昵称（留空则显示用户名）" maxlength="50" />
        <el-button type="primary" class="save-btn" @click="saveProfile">保存个人信息</el-button>
      </div>

      <!-- 偏好设置 -->
      <div class="settings-section">
        <h3>偏好设置</h3>
        <div class="pref-item">
          <label>消息字体大小</label>
          <el-slider v-model="prefForm.fontSize" :min="12" :max="20" :step="1" show-input />
        </div>
        <div class="pref-item">
          <label>消息密度</label>
          <el-radio-group v-model="prefForm.messageDensity">
            <el-radio value="compact">紧凑</el-radio>
            <el-radio value="normal">正常</el-radio>
            <el-radio value="relaxed">宽松</el-radio>
          </el-radio-group>
        </div>
        <el-button type="primary" class="save-btn" @click="savePreferences">保存偏好</el-button>
      </div>

      <!-- 修改密码 -->
      <div class="settings-section">
        <h3>修改密码</h3>
        <el-form ref="formRef" :model="form" :rules="rules">
          <el-form-item prop="oldPassword">
            <el-input v-model="form.oldPassword" type="password" placeholder="旧密码" show-password />
          </el-form-item>
          <el-form-item prop="newPassword">
            <el-input v-model="form.newPassword" type="password" placeholder="新密码（至少 6 位）" show-password />
          </el-form-item>
          <el-form-item prop="confirmPassword">
            <el-input v-model="form.confirmPassword" type="password" placeholder="确认新密码" show-password />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="loading" @click="handleSubmit">保存</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 账号信息 -->
      <div class="settings-section">
        <h3>账号信息</h3>
        <p class="info-row">用户名：{{ userStore.username }}</p>
        <p v-if="userStore.nickname" class="info-row">昵称：{{ userStore.nickname }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.settings-page {
  min-height: 100vh;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 60px 20px;
  background: var(--bg-primary);
}

.settings-card {
  width: 480px;
  background: var(--bg-secondary);
  border-radius: var(--radius-xl);
  border: 1px solid var(--border);
  padding: 32px;
}

.settings-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 32px;
}

.settings-header h2 {
  font-size: 20px;
  color: var(--text-primary);
  margin: 0;
}

.back-btn {
  color: var(--text-secondary);
}

.settings-section {
  margin-bottom: 32px;
}

.settings-section h3 {
  font-size: 16px;
  color: var(--text-primary);
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border);
}

.info-row {
  color: var(--text-secondary);
  font-size: 14px;
  margin-bottom: 4px;
}

.avatar-picker {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 8px;
  margin-bottom: 16px;
}

.avatar-option {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  border-radius: var(--radius-sm);
  border: 2px solid transparent;
  cursor: pointer;
  transition: border-color 0.15s;
  background: var(--bg-tertiary);
}

.avatar-option:hover {
  border-color: var(--accent-hover);
}

.avatar-option.selected {
  border-color: var(--accent);
  background: var(--accent-bg);
}

.save-btn {
  margin-top: 12px;
}

.pref-item {
  margin-bottom: 20px;
}

.pref-item label {
  display: block;
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}
</style>
