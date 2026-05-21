import { defineStore } from 'pinia'
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getToken, setToken, removeToken, getUser, setUser } from '@/utils/auth'
import { login as loginApi, logout as logoutApi, getProfile } from '@/api/auth'
import { getUnreadMailboxCount, getAdminUnreadFeedbackCount } from '@/api/feedback'
import { getPendingReview } from '@/api/bookmark'
import router from '@/router'

export const useUserStore = defineStore('user', () => {
  const token = ref(getToken() || '')
  const user = ref(getUser() || null)
  const profileLoaded = ref(false)
  const mailUnreadCount = ref(0)
  const adminUnreadFeedbackCount = ref(0)
  const adminPendingReviewCount = ref(0)

  function applyUserProfile(profile) {
    user.value = profile
    setUser(profile)
  }

  async function login(form) {
    const res = await loginApi(form)
    token.value = res.data.token
    setToken(res.data.token)
    applyUserProfile(res.data.user)
    profileLoaded.value = true
    await fetchUnreadMailboxCount()
    return res.data.user
  }

  async function fetchProfile() {
    const res = await getProfile()
    applyUserProfile(res.data)
    profileLoaded.value = true
    return res.data
  }

  async function hydrateProfile(force = false) {
    if (!token.value) {
      profileLoaded.value = false
      mailUnreadCount.value = 0
      adminUnreadFeedbackCount.value = 0
      adminPendingReviewCount.value = 0
      return null
    }
    if (!force && profileLoaded.value && user.value) {
      return user.value
    }
    try {
      const profile = await fetchProfile()
      await fetchUnreadMailboxCount()
      return profile
    } catch {
      return user.value
    }
  }

  async function fetchUnreadMailboxCount() {
    if (!token.value) {
      mailUnreadCount.value = 0
      return 0
    }
    try {
      const res = await getUnreadMailboxCount()
      mailUnreadCount.value = Number(res.data?.unread_count || 0)
      return mailUnreadCount.value
    } catch {
      return mailUnreadCount.value
    }
  }

  async function fetchAdminUnreadFeedbackCount() {
    if (!user.value || user.value?.role !== 'admin') {
      adminUnreadFeedbackCount.value = 0
      return 0
    }
    try {
      const res = await getAdminUnreadFeedbackCount()
      adminUnreadFeedbackCount.value = Number(res.data?.unread_count || 0)
      return adminUnreadFeedbackCount.value
    } catch {
      return adminUnreadFeedbackCount.value
    }
  }

  async function fetchAdminPendingReviewCount() {
    if (!user.value || user.value?.role !== 'admin') {
      adminPendingReviewCount.value = 0
      return 0
    }
    try {
      const res = await getPendingReview()
      adminPendingReviewCount.value = Array.isArray(res.data) ? res.data.length : 0
      return adminPendingReviewCount.value
    } catch {
      return adminPendingReviewCount.value
    }
  }

  function setMailUnreadCount(count) {
    mailUnreadCount.value = Math.max(Number(count) || 0, 0)
  }

  function setAdminUnreadFeedbackCount(count) {
    adminUnreadFeedbackCount.value = Math.max(Number(count) || 0, 0)
  }

  function setAdminPendingReviewCount(count) {
    adminPendingReviewCount.value = Math.max(Number(count) || 0, 0)
  }

  async function logout() {
    try {
      await logoutApi()
    } catch {}
    token.value = ''
    user.value = null
    profileLoaded.value = false
    mailUnreadCount.value = 0
    adminUnreadFeedbackCount.value = 0
    adminPendingReviewCount.value = 0
    removeToken()
    router.push('/login')
    ElMessage.success('已安全退出')
  }

  function isLoggedIn() {
    return !!token.value
  }

  function isAdmin() {
    return user.value?.role === 'admin'
  }

  return {
    token,
    user,
    profileLoaded,
    mailUnreadCount,
    adminUnreadFeedbackCount,
    adminPendingReviewCount,
    login,
    fetchProfile,
    hydrateProfile,
    fetchUnreadMailboxCount,
    fetchAdminUnreadFeedbackCount,
    fetchAdminPendingReviewCount,
    setMailUnreadCount,
    setAdminUnreadFeedbackCount,
    setAdminPendingReviewCount,
    applyUserProfile,
    logout,
    isLoggedIn,
    isAdmin,
  }
})
