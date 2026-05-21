<template>
  <div class="settings-page">
    <section class="page-hero compact-hero">
      <div>
        <h2>个人设置</h2>
        <p>维护管理员资料与账号安全信息。</p>
      </div>
    </section>

    <div class="settings-grid">
      <el-card shadow="never" class="page-card">
        <template #header>
          <div class="card-title">
            <strong>修改个人信息</strong>
            <span>更新展示名称、邮箱和头像地址。</span>
          </div>
        </template>
        <el-form ref="profileFormRef" :model="profileForm" label-width="88px">
          <el-form-item label="用户名">
            <el-input v-model="profileForm.username" placeholder="请输入用户名" />
          </el-form-item>
          <el-form-item label="邮箱">
            <el-input v-model="profileForm.email" placeholder="请输入邮箱" />
          </el-form-item>
          <el-form-item label="头像 URL">
            <el-input v-model="profileForm.avatar" placeholder="请输入头像图片地址" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="profileLoading" @click="handleUpdateProfile">保存修改</el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <el-card shadow="never" class="page-card">
        <template #header>
          <div class="card-title">
            <strong>修改密码</strong>
            <span>建议定期更新密码以保持账号安全。</span>
          </div>
        </template>
        <el-form ref="pwdFormRef" :model="pwdForm" :rules="pwdRules" label-width="88px">
          <el-form-item label="原密码" prop="old_password">
            <el-input v-model="pwdForm.old_password" type="password" show-password placeholder="请输入原密码" />
          </el-form-item>
          <el-form-item label="新密码" prop="new_password">
            <el-input v-model="pwdForm.new_password" type="password" show-password placeholder="请输入新密码（至少 6 位）" />
          </el-form-item>
          <el-form-item label="确认密码" prop="confirm_password">
            <el-input v-model="pwdForm.confirm_password" type="password" show-password placeholder="请再次输入新密码" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="pwdLoading" @click="handleChangePassword">修改密码</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { updateUserProfile, changePassword } from '@/api/user'

const userStore = useUserStore()
const profileFormRef = ref()
const pwdFormRef = ref()
const profileLoading = ref(false)
const pwdLoading = ref(false)

const profileForm = reactive({ username: '', email: '', avatar: '' })
const pwdForm = reactive({ old_password: '', new_password: '', confirm_password: '' })

const validateConfirm = (rule, value, callback) => {
  if (value !== pwdForm.new_password) callback(new Error('两次输入的密码不一致'))
  else callback()
}

const pwdRules = {
  old_password: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少 6 位', trigger: 'blur' },
  ],
  confirm_password: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    { validator: validateConfirm, trigger: 'blur' },
  ],
}

async function handleUpdateProfile() {
  profileLoading.value = true
  try {
    const res = await updateUserProfile(profileForm)
    userStore.applyUserProfile(res.data)
    ElMessage.success('个人信息已更新')
  } finally {
    profileLoading.value = false
  }
}

async function handleChangePassword() {
  await pwdFormRef.value.validate()
  pwdLoading.value = true
  try {
    await changePassword({ old_password: pwdForm.old_password, new_password: pwdForm.new_password })
    ElMessage.success('密码修改成功')
    Object.assign(pwdForm, { old_password: '', new_password: '', confirm_password: '' })
  } finally {
    pwdLoading.value = false
  }
}

onMounted(() => {
  profileForm.username = userStore.user?.username || ''
  profileForm.email = userStore.user?.email || ''
  profileForm.avatar = userStore.user?.avatar || ''
})
</script>

<style scoped>
.settings-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.compact-hero {
  margin-bottom: 0;
  padding-block: 24px;
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.card-title strong {
  display: block;
  font-size: 18px;
  color: var(--app-text);
}

.card-title span {
  display: block;
  margin-top: 6px;
  font-size: 13px;
  color: var(--app-text-soft);
}

@media (max-width: 900px) {
  .settings-grid {
    grid-template-columns: 1fr;
  }
}
</style>
