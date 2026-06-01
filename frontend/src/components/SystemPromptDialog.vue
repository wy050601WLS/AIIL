<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  initialPrompt: { type: String, default: '' },
})
const emit = defineEmits(['update:visible', 'save'])

const promptText = ref('')

watch(() => props.visible, (val) => {
  if (val) promptText.value = props.initialPrompt || ''
})

function handleSave() {
  emit('save', promptText.value)
  emit('update:visible', false)
}

function handleClose() {
  emit('update:visible', false)
}
</script>

<template>
  <el-dialog
    :model-value="visible"
    title="系统提示词"
    width="500px"
    @update:model-value="handleClose"
  >
    <p class="hint">系统提示词会作为 AI 的上下文指令，影响其回答风格和行为。</p>
    <el-input
      v-model="promptText"
      type="textarea"
      :rows="6"
      placeholder="例如：你是一个友好的编程助手，请用中文回答问题，并给出代码示例。"
    />
    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" @click="handleSave">保存</el-button>
    </template>
  </el-dialog>
</template>

<style scoped>
.hint {
  font-size: 13px;
  color: var(--text-muted);
  margin-bottom: 12px;
}
</style>
