<template>
  <div class="auth-page auth-page-register">
    <AuthStreamScene
      class="auth-scene"
      :title="sceneTitle"
      :description-lines="sceneDescriptionLines"
      :keywords="sceneKeywords"
    />

    <section class="auth-panel">
      <el-card class="auth-card" shadow="never">
        <div class="card-head">
          <span class="card-kicker">CREATE ACCOUNT</span>
          <h2>{{ cardTitle }}</h2>
          <p>{{ cardDescription }}</p>
        </div>

        <el-form ref="formRef" :model="form" :rules="rules" label-width="0" size="large">
          <el-form-item prop="username">
            <el-input v-model="form.username" :placeholder="usernamePlaceholder" prefix-icon="User" />
          </el-form-item>
          <el-form-item prop="email">
            <el-input v-model="form.email" :placeholder="emailPlaceholder" prefix-icon="Message" />
          </el-form-item>
          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              type="password"
              :placeholder="passwordPlaceholder"
              prefix-icon="Lock"
              show-password
            />
          </el-form-item>
          <el-form-item prop="confirmPassword">
            <el-input
              v-model="form.confirmPassword"
              type="password"
              :placeholder="confirmPasswordPlaceholder"
              prefix-icon="Lock"
              show-password
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="loading" class="submit-button" @click="handleRegister">
              {{ submitLabel }}
            </el-button>
          </el-form-item>
        </el-form>

        <div class="auth-footer">
          {{ footerPrefix }}
          <router-link to="/login">{{ footerLinkLabel }}</router-link>
        </div>
      </el-card>
    </section>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AuthStreamScene from '@/components/AuthStreamScene.vue'
import { register } from '@/api/auth'

const router = useRouter()
const formRef = ref()
const loading = ref(false)

const form = reactive({ username: '', email: '', password: '', confirmPassword: '' })

const cardTitle = '\u521b\u5efa\u8d26\u53f7'
const cardDescription = '\u586b\u5199\u57fa\u7840\u4fe1\u606f\u540e\u5373\u53ef\u5f00\u59cb\u6574\u7406\u6536\u85cf\u3001\u5efa\u7acb\u5206\u7c7b\u5e76\u63a2\u7d22\u516c\u5f00\u5bfc\u822a\u3002'
const usernamePlaceholder = '\u8bf7\u8f93\u5165\u7528\u6237\u540d\uff083-20 \u4e2a\u5b57\u7b26\uff09'
const emailPlaceholder = '\u8bf7\u8f93\u5165\u90ae\u7bb1\uff08\u9009\u586b\uff09'
const passwordPlaceholder = '\u8bf7\u8f93\u5165\u5bc6\u7801\uff08\u81f3\u5c11 6 \u4f4d\uff09'
const confirmPasswordPlaceholder = '\u8bf7\u518d\u6b21\u786e\u8ba4\u5bc6\u7801'
const submitLabel = '\u6ce8\u518c'
const footerPrefix = '\u5df2\u6709\u8d26\u53f7\uff1f'
const footerLinkLabel = '\u7acb\u5373\u767b\u5f55'
const registerSuccessMessage = '\u6ce8\u518c\u6210\u529f\uff0c\u8bf7\u767b\u5f55'
const usernameRequiredMessage = '\u8bf7\u8f93\u5165\u7528\u6237\u540d'
const usernameLengthMessage = '\u7528\u6237\u540d\u957f\u5ea6\u4e3a 3-20 \u4e2a\u5b57\u7b26'
const passwordRequiredMessage = '\u8bf7\u8f93\u5165\u5bc6\u7801'
const passwordLengthMessage = '\u5bc6\u7801\u957f\u5ea6\u81f3\u5c11 6 \u4f4d'
const confirmPasswordRequiredMessage = '\u8bf7\u518d\u6b21\u786e\u8ba4\u5bc6\u7801'
const confirmMismatchMessage = '\u4e24\u6b21\u8f93\u5165\u7684\u5bc6\u7801\u4e0d\u4e00\u81f4'

const sceneTitle = '\u5f00\u59cb\u4f7f\u7528\u94fe\u57df'
const sceneDescriptionLines = [
  '\u521b\u5efa\u8d26\u53f7\u540e\u5373\u53ef\u6574\u7406\u5e38\u7528\u7ad9\u70b9\u3001\u5efa\u7acb\u5206\u7c7b\u5e76\u6c89\u6dc0\u4e2a\u4eba\u5bfc\u822a\u3002',
  '\u4ece\u6536\u85cf\u3001\u53d1\u73b0\u5230\u516c\u5f00\u5206\u4eab\uff0c\u90fd\u5728\u4e00\u4e2a\u7edf\u4e00\u7a7a\u95f4\u5185\u5b8c\u6210\u3002',
]
const sceneKeywords = [
  '\u521b\u5efa\u8d26\u53f7',
  '\u5206\u7c7b\u7ba1\u7406',
  '\u516c\u5f00\u5206\u4eab',
  '\u5185\u5bb9\u53d1\u73b0',
]

const validateConfirm = (rule, value, callback) => {
  if (value !== form.password) callback(new Error(confirmMismatchMessage))
  else callback()
}

const rules = {
  username: [
    { required: true, message: usernameRequiredMessage, trigger: 'blur' },
    { min: 3, max: 20, message: usernameLengthMessage, trigger: 'blur' },
  ],
  password: [
    { required: true, message: passwordRequiredMessage, trigger: 'blur' },
    { min: 6, message: passwordLengthMessage, trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: confirmPasswordRequiredMessage, trigger: 'blur' },
    { validator: validateConfirm, trigger: 'blur' },
  ],
}

async function handleRegister() {
  await formRef.value.validate()
  loading.value = true
  try {
    await register({ username: form.username, password: form.password, email: form.email })
    ElMessage.success(registerSuccessMessage)
    router.push('/login')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  position: relative;
  min-height: calc(100vh - var(--app-header-height));
  overflow: hidden;
  isolation: isolate;
  --auth-safe-lane-width: 620px;
  --auth-scene-side-padding: clamp(28px, 4vw, 72px);
  --auth-scene-top-space: 0px;
}

.auth-scene {
  position: absolute;
  inset: 0;
}

.auth-panel {
  position: relative;
  z-index: 2;
  min-height: inherit;
  width: 100%;
  padding: clamp(28px, 4vw, 56px);
  display: flex;
  justify-content: center;
  align-items: center;
}

.auth-card {
  width: min(100%, 560px);
  max-width: 560px;
  padding: 14px;
  border: 1px solid rgba(211, 223, 240, 0.92);
  border-radius: 32px;
  background: rgba(255, 255, 255, 0.84);
  backdrop-filter: blur(24px);
  box-shadow: 0 24px 72px rgba(20, 32, 51, 0.14);
}

.card-head {
  margin-bottom: 24px;
}

.card-kicker {
  display: inline-flex;
  align-items: center;
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(47, 128, 237, 0.1);
  color: var(--app-primary);
  font-size: 12px;
  letter-spacing: 0.12em;
}

.card-head h2 {
  margin-top: 18px;
  font-size: 34px;
  line-height: 1.05;
  color: var(--app-text);
}

.card-head p {
  margin-top: 10px;
  font-size: 14px;
  line-height: 1.75;
  color: var(--app-text-soft);
}

.submit-button {
  width: 100%;
  height: 50px;
  border-radius: 16px;
  font-size: 15px;
  font-weight: 600;
}

.auth-footer {
  margin-top: 16px;
  text-align: center;
  font-size: 14px;
  color: var(--app-text-soft);
}

.auth-footer a {
  color: var(--app-primary);
  text-decoration: none;
  font-weight: 600;
}

:deep(.auth-card .el-card__body) {
  padding: 28px;
}

:deep(.el-input__wrapper) {
  min-height: 52px;
  border-radius: 16px;
}

@media (max-width: 1260px) {
  .auth-page {
    --auth-scene-top-space: 170px;
  }

  .auth-panel {
    padding-top: calc(28px + var(--auth-scene-top-space));
    align-items: flex-start;
  }
}

@media (max-width: 920px) {
  .auth-page {
    min-height: calc(100vh - var(--app-header-height));
    --auth-scene-top-space: 140px;
  }

  .auth-panel {
    padding: calc(14px + var(--auth-scene-top-space)) 16px 22px;
    align-items: flex-start;
    justify-content: center;
  }

  .auth-card {
    width: 100%;
    max-width: 520px;
  }
}

@media (max-width: 768px) {
  .auth-card {
    border-radius: 22px;
  }

  .card-head h2 {
    font-size: 28px;
  }

  :deep(.auth-card .el-card__body) {
    padding: 18px;
  }

  :deep(.el-input__wrapper) {
    min-height: 50px;
  }
}

@media (max-width: 640px) {
  .auth-page {
    --auth-scene-top-space: 126px;
  }

  .auth-panel {
    padding: calc(10px + var(--auth-scene-top-space)) 12px 18px;
  }

  .auth-card {
    border-radius: 20px;
  }

  .card-head h2 {
    font-size: 26px;
  }

  .card-head p {
    line-height: 1.65;
  }
}

@media (max-width: 480px) {
  .auth-page {
    --auth-scene-top-space: 112px;
  }

  .auth-panel {
    padding: calc(10px + var(--auth-scene-top-space)) 10px 16px;
  }

  .card-kicker {
    padding: 6px 10px;
    font-size: 11px;
  }

  .card-head {
    margin-bottom: 18px;
  }

  .card-head h2 {
    margin-top: 14px;
    font-size: 24px;
  }

  .card-head p,
  .auth-footer {
    font-size: 13px;
  }

  .submit-button {
    height: 48px;
  }

  :deep(.auth-card .el-card__body) {
    padding: 16px;
  }
}

:global(:root[data-theme='dark'] .auth-card) {
  border-color: rgba(44, 64, 89, 0.9);
  background: rgba(12, 23, 38, 0.78);
  box-shadow: 0 28px 72px rgba(0, 0, 0, 0.32);
}
</style>
