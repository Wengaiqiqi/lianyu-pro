import { createRouter, createWebHashHistory } from 'vue-router'
import { getToken, getUser } from '@/utils/auth'

const routes = [
  {
    path: '/',
    component: () => import('@/layouts/UserLayout.vue'),
    children: [
      { path: '', name: 'Home', component: () => import('@/views/user/Home.vue'), meta: { title: '首页' } },
      { path: 'go/:id', name: 'Go', component: () => import('@/views/user/Go.vue'), meta: { title: '跳转页' } },
      { path: 'login', name: 'Login', component: () => import('@/views/user/Login.vue'), meta: { title: '登录', guest: true } },
      { path: 'register', name: 'Register', component: () => import('@/views/user/Register.vue'), meta: { title: '注册', guest: true } },
      { path: 'dashboard', name: 'Dashboard', component: () => import('@/views/user/Dashboard.vue'), meta: { title: '个人中心', auth: true } },
      { path: 'bookmarks', name: 'Bookmarks', component: () => import('@/views/user/Bookmarks.vue'), meta: { title: '我的收藏', auth: true } },
      { path: 'categories', name: 'Categories', component: () => import('@/views/user/Categories.vue'), meta: { title: '分类管理', auth: true } },
      { path: 'rankings', name: 'Rankings', component: () => import('@/views/user/Rankings.vue'), meta: { title: '热门榜单', auth: true } },
      { path: 'public', name: 'Public', component: () => import('@/views/user/Public.vue'), meta: { title: '公开广场', auth: true } },
      { path: 'search', name: 'Search', component: () => import('@/views/user/Search.vue'), meta: { title: '全局搜索', auth: true } },
      { path: 'feedback', name: 'Feedback', component: () => import('@/views/user/Feedback.vue'), meta: { title: '意见反馈', auth: true } },
      { path: 'mailbox', name: 'Mailbox', component: () => import('@/views/user/Mailbox.vue'), meta: { title: '站内信', auth: true } },
      { path: 'settings', name: 'Settings', component: () => import('@/views/user/Settings.vue'), meta: { title: '个人设置', auth: true } },
    ],
  },
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: { auth: true, admin: true },
    children: [
      { path: '', name: 'AdminDashboard', component: () => import('@/views/admin/Dashboard.vue'), meta: { title: '管理后台' } },
      { path: 'users', name: 'AdminUsers', component: () => import('@/views/admin/Users.vue'), meta: { title: '用户管理' } },
      { path: 'bookmarks', name: 'AdminBookmarks', component: () => import('@/views/admin/Bookmarks.vue'), meta: { title: '内容管理' } },
      { path: 'categories', name: 'AdminCategories', component: () => import('@/views/admin/Categories.vue'), meta: { title: '分类维护' } },
      { path: 'statistics', name: 'AdminStatistics', component: () => import('@/views/admin/Statistics.vue'), meta: { title: '数据统计' } },
      { path: 'logs', name: 'AdminLogs', component: () => import('@/views/admin/Logs.vue'), meta: { title: '操作日志' } },
      { path: 'feedbacks', name: 'AdminFeedbacks', component: () => import('@/views/admin/Feedback.vue'), meta: { title: '反馈管理' } },
      { path: 'ai-settings', name: 'AdminAISettings', component: () => import('@/views/admin/AISettings.vue'), meta: { title: 'AI 设置' } },
      { path: 'pending', name: 'AdminPending', component: () => import('@/views/admin/PendingReview.vue'), meta: { title: '待处理审核' } },
      { path: 'settings', name: 'AdminSettings', component: () => import('@/views/admin/Settings.vue'), meta: { title: '个人设置' } },
    ],
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title || '链域'} - 链域`
  const token = getToken()
  const user = getUser()

  if (to.meta.auth && !token) {
    next('/login')
    return
  }

  if (to.meta.admin && (!user || user.role !== 'admin')) {
    next('/')
    return
  }

  if (to.meta.guest && token) {
    next('/dashboard')
    return
  }

  next()
})

export default router
