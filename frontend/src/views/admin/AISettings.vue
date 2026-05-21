<template>
  <div class="ai-settings" v-loading="loading">
    <section class="page-hero compact-hero">
      <div>
        <h2>AI 配置</h2>
        <p>统一管理 AI 功能开关、接口地址、密钥与模型连接。</p>
      </div>
      <el-tag :type="form.enabled ? 'success' : 'info'" size="large">
        {{ form.enabled ? '已启用' : '未启用' }}
      </el-tag>
    </section>

    <el-card shadow="hover" class="page-card">
      <template #header>
        <div class="card-header">
          <span>AI 模型配置</span>
          <el-tag :type="form.enabled ? 'success' : 'info'" size="small">
            {{ form.enabled ? '已启用' : '未启用' }}
          </el-tag>
        </div>
      </template>

      <el-form ref="formRef" :model="form" label-width="120px" style="max-width: 600px">
        <el-form-item label="启用 AI 功能">
          <el-switch v-model="form.enabled" />
        </el-form-item>
        <el-form-item
          label="API 地址"
          :rules="[{ required: form.enabled, message: '请输入 API 地址' }]"
          prop="api_url"
        >
          <el-input v-model="form.api_url" placeholder="例如：https://api.openai.com/v1" />
          <div class="form-tip">兼容 OpenAI 接口格式的 API 地址，无需包含 /chat/completions</div>
        </el-form-item>
        <el-form-item
          label="API 密钥"
          :rules="[{ required: form.enabled, message: '请输入 API 密钥' }]"
          prop="api_key"
        >
          <el-input v-model="form.api_key" type="password" show-password placeholder="输入 API Key" />
        </el-form-item>
        <el-form-item
          label="模型名称"
          :rules="[{ required: form.enabled, message: '请输入模型名称' }]"
          prop="model_name"
        >
          <el-input v-model="form.model_name" placeholder="例如：gpt-4o-mini" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="saving" @click="handleSave">保存配置</el-button>
          <el-button :loading="testing" @click="handleTest">测试连接</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getAIConfig, updateAIConfig, testAIConfig } from '@/api/admin'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const saving = ref(false)
const testing = ref(false)
const formRef = ref()

const form = reactive({
  api_url: '',
  api_key: '',
  model_name: '',
  enabled: false,
})

async function loadConfig() {
  loading.value = true
  try {
    const res = await getAIConfig()
    Object.assign(form, res.data)
  } finally {
    loading.value = false
  }
}

async function handleSave() {
  if (form.enabled) {
    await formRef.value.validate()
  }
  saving.value = true
  try {
    await updateAIConfig(form)
    ElMessage.success('配置已保存')
    loadConfig()
  } finally {
    saving.value = false
  }
}

async function handleTest() {
  if (!form.api_url || !form.api_key || !form.model_name) {
    ElMessage.warning('请先填写完整的 API 配置')
    return
  }
  testing.value = true
  try {
    const res = await testAIConfig({
      api_url: form.api_url,
      api_key: form.api_key,
      model_name: form.model_name,
    })
    ElMessage.success(res.msg || '连接成功')
  } catch {
    // error handled by interceptor
  } finally {
    testing.value = false
  }
}

onMounted(loadConfig)
</script>

<style scoped>
.compact-hero {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.form-tip {
  margin-top: 4px;
  font-size: 12px;
  line-height: 1.4;
  color: #999;
}
</style>
