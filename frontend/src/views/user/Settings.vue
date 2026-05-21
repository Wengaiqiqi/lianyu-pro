<template>
  <div class="settings-page">
    <section class="page-hero compact-hero">
      <div>
        <h2>{{ heroTitle }}</h2>
        <p>{{ heroDescription }}</p>
      </div>
    </section>
    <el-row :gutter="24">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>修改个人信息</template>
          <el-form ref="profileFormRef" :model="profileForm" label-width="80px">
            <el-form-item label="昵称">
              <el-input v-model="profileForm.nickname" placeholder="请输入昵称" />
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
      </el-col>

      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>修改密码</template>
          <el-form ref="pwdFormRef" :model="pwdForm" :rules="pwdRules" label-width="80px">
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
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { updateUserProfile, changePassword } from '@/api/user'

const userStore = useUserStore()
const profileFormRef = ref()
const pwdFormRef = ref()
const profileLoading = ref(false)
const pwdLoading = ref(false)
const heroTitle = '\u4e2a\u4eba\u8bbe\u7f6e'
const heroDescription = '\u7ef4\u62a4\u4e2a\u4eba\u8d44\u6599\u4e0e\u8d26\u6237\u5b89\u5168\u4fe1\u606f\uff0c\u4fdd\u6301\u8d26\u6237\u72b6\u6001\u7a33\u5b9a\u53ef\u63a7\u3002'

const profileForm = reactive({ nickname: '', email: '', avatar: '' })
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
  profileForm.nickname = userStore.user?.nickname || ''
  profileForm.email = userStore.user?.email || ''
  profileForm.avatar = userStore.user?.avatar || ''
})
</script>

<style scoped>
.page-title { font-size: 20px; color: #333; margin-bottom: 24px; }
</style>
