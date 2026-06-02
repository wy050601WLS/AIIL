<!--
  Settings 视图 — 用户设置页

  功能：个人信息（昵称/头像）、偏好设置（字体/密度/默认模型）、修改密码、对话模板管理
  页面加载时从后端获取最新资料填充表单
-->
<script setup>
import { reactive, ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { changePassword } from '../api/auth'
import { useUserStore } from '../stores/user'
import { useTemplatesStore } from '../stores/templates'
import { useRouter } from 'vue-router'

const userStore = useUserStore()
const templatesStore = useTemplatesStore()
const router = useRouter()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({ oldPassword: '', newPassword: '', confirmPassword: '' })

// 预设头像列表（emoji）
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

// 模板编辑状态
const editingTemplate = ref(null)   // 正在编辑的模板对象
const editTitle = ref('')
const editContent = ref('')
const editCategory = ref('')

/** 用户自建的模板列表（排除内置模板） */
const userTemplates = computed(() => templatesStore.templates.filter(t => !t.is_builtin))

// 页面加载时从后端获取最新资料并填充表单
onMounted(async () => {
  await userStore.loadProfile()
  profileForm.nickname = userStore.nickname || ''
  profileForm.avatar = userStore.avatar || presetAvatars[0]
  prefForm.fontSize = userStore.preferences?.fontSize || 15
  prefForm.messageDensity = userStore.preferences?.messageDensity || 'normal'
  prefForm.defaultModel = userStore.preferences?.defaultModel || ''
  templatesStore.loadTemplates()
})

// 修改密码表单验证规则
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

/** 提交修改密码：验证旧密码 → 更新 → 强制重新登录 */
async function handleSubmit() {
  try {
    await formRef.value.validate()
  } catch {
    return
  }
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

/** 保存个人信息（昵称和头像） */
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

/** 保存偏好设置（字体大小、消息密度、默认模型） */
async function savePreferences() {
  try {
    await userStore.saveProfile({ preferences: { ...prefForm } })
    ElMessage.success('偏好设置已保存')
  } catch {
    ElMessage.error('保存失败')
  }
}

/** 返回对话页 */
function goBack() {
  router.push('/')
}

// ===== 模板管理 =====

/** 进入编辑模式 */
function startEditTemplate(tpl) {
  editingTemplate.value = tpl.id
  editTitle.value = tpl.title
  editContent.value = tpl.content
  editCategory.value = tpl.category || ''
}

/** 取消编辑 */
function cancelEditTemplate() {
  editingTemplate.value = null
}

/** 保存模板编辑 */
async function saveEditTemplate(tpl) {
  if (!editTitle.value.trim() || !editContent.value.trim()) {
    ElMessage.warning('标题和内容不能为空')
    return
  }
  await templatesStore.editTemplate(tpl.id, {
    title: editTitle.value.trim(),
    content: editContent.value.trim(),
    category: editCategory.value.trim() || null,
  })
  editingTemplate.value = null
}

/** 删除模板（带确认） */
async function handleDeleteTemplate(tpl) {
  try {
    await templatesStore.removeTemplate(tpl.id)
  } catch {
    // 已在 store 中处理
  }
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

      <!-- 对话模板管理 -->
      <div class="settings-section">
        <h3>对话模板管理</h3>
        <div v-if="templatesStore.loading" class="template-loading">加载中...</div>
        <div v-else>
          <div v-if="userTemplates.length === 0" class="template-empty">暂无自定义模板</div>
          <div v-for="tpl in userTemplates" :key="tpl.id" class="template-manage-item">
            <template v-if="editingTemplate === tpl.id">
              <el-input v-model="editTitle" size="small" placeholder="标题" class="template-edit-field" />
              <el-input v-model="editCategory" size="small" placeholder="分类（可选）" class="template-edit-field" />
              <el-input v-model="editContent" type="textarea" :rows="2" placeholder="模板内容" class="template-edit-field" />
              <div class="template-edit-actions">
                <el-button type="primary" size="small" @click="saveEditTemplate(tpl)">保存</el-button>
                <el-button size="small" @click="cancelEditTemplate">取消</el-button>
              </div>
            </template>
            <template v-else>
              <div class="template-manage-info">
                <span class="template-manage-title">{{ tpl.title }}</span>
                <span v-if="tpl.category" class="template-manage-cat">{{ tpl.category }}</span>
                <span class="template-manage-preview">{{ tpl.content.slice(0, 50) }}...</span>
              </div>
              <div class="template-manage-actions">
                <el-button type="primary" text size="small" @click="startEditTemplate(tpl)">编辑</el-button>
                <el-button type="danger" text size="small" @click="handleDeleteTemplate(tpl)">删除</el-button>
              </div>
            </template>
          </div>
        </div>
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

/* ===== 模板管理 ===== */

.template-loading,
.template-empty {
  color: var(--text-muted);
  font-size: 13px;
  padding: 8px 0;
}

.template-manage-item {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid var(--border);
}

.template-manage-item:last-child {
  border-bottom: none;
}

.template-manage-info {
  flex: 1;
  min-width: 0;
}

.template-manage-title {
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 500;
}

.template-manage-cat {
  display: inline-block;
  font-size: 11px;
  color: var(--accent);
  background: var(--accent-bg);
  padding: 1px 6px;
  border-radius: 8px;
  margin-left: 8px;
}

.template-manage-preview {
  display: block;
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.template-manage-actions {
  flex-shrink: 0;
  display: flex;
  gap: 4px;
  margin-left: 8px;
}

.template-edit-field {
  margin-bottom: 8px;
}

.template-edit-actions {
  display: flex;
  gap: 8px;
}
</style>
