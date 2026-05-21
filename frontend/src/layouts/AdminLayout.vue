<template>
  <div class="admin-layout">
    <aside class="aside">
      <div class="aside-shell">
        <div class="aside-logo">
          <div class="aside-logo-mark">
            <el-icon :size="20"><Setting /></el-icon>
          </div>
          <div class="aside-logo-copy">
            <strong>链域后台</strong>
            <span>内容、用户与系统管理</span>
          </div>
        </div>

        <el-menu
          :default-active="$route.path"
          router
          class="aside-menu"
          :background-color="'transparent'"
          :text-color="'var(--admin-aside-text)'"
          :active-text-color="'var(--admin-aside-active)'"
        >
          <el-menu-item index="/admin">
            <el-icon><DataAnalysis /></el-icon>
            <span>系统概览</span>
          </el-menu-item>
          <el-menu-item index="/admin/users">
            <el-icon><User /></el-icon>
            <span>用户管理</span>
          </el-menu-item>
          <el-menu-item index="/admin/bookmarks">
            <el-icon><Link /></el-icon>
            <span>内容管理</span>
          </el-menu-item>
          <el-menu-item index="/admin/categories">
            <el-icon><Folder /></el-icon>
            <span>分类维护</span>
          </el-menu-item>
          <el-menu-item index="/admin/statistics">
            <el-icon><TrendCharts /></el-icon>
            <span>数据统计</span>
          </el-menu-item>
          <el-menu-item index="/admin/logs">
            <el-icon><Document /></el-icon>
            <span>操作日志</span>
          </el-menu-item>
          <el-menu-item index="/admin/feedbacks">
            <el-icon><ChatDotRound /></el-icon>
            <span>反馈管理</span>
            <el-badge
              :value="userStore.adminUnreadFeedbackCount"
              :hidden="!userStore.adminUnreadFeedbackCount"
              :max="99"
              class="feedback-badge"
            >
              <span class="feedback-badge-anchor"></span>
            </el-badge>
          </el-menu-item>
          <el-menu-item index="/admin/ai-settings">
            <el-icon><MagicStick /></el-icon>
            <span>AI 设置</span>
          </el-menu-item>
          <el-menu-item index="/admin/pending">
            <el-icon><Bell /></el-icon>
            <span>待处理审核</span>
            <el-badge
              :value="userStore.adminPendingReviewCount"
              :hidden="!userStore.adminPendingReviewCount"
              :max="99"
              class="feedback-badge"
            >
              <span class="feedback-badge-anchor"></span>
            </el-badge>
          </el-menu-item>
          <el-menu-item index="/admin/settings">
            <el-icon><Setting /></el-icon>
            <span>个人设置</span>
          </el-menu-item>
        </el-menu>
      </div>
    </aside>

    <div class="admin-main">
      <header class="admin-header">
        <div v-if="false" class="header-left">
          <el-breadcrumb>
            <el-breadcrumb-item :to="{ path: '/admin' }">后台</el-breadcrumb-item>
            <el-breadcrumb-item v-if="$route.meta.title !== '管理后台'">{{ $route.meta.title }}</el-breadcrumb-item>
          </el-breadcrumb>
          <div class="header-caption">
            <strong>{{ $route.meta.title || '管理后台' }}</strong>
            <span>保持数据清晰、流程稳定与内容质量。</span>
          </div>
        </div>

        <div class="header-right">
          <el-button class="header-action" circle @click="toggleTheme">
            <el-icon><component :is="theme === 'dark' ? Sunny : Moon" /></el-icon>
          </el-button>

          <el-dropdown @command="handleCommand">
            <button type="button" class="admin-user">
              <el-avatar v-if="userStore.user?.avatar" :src="userStore.user.avatar" :size="32" />
              <div v-else class="admin-avatar">
                {{ (userStore.user?.nickname || userStore.user?.username || 'A').charAt(0).toUpperCase() }}
              </div>
              <div class="admin-user-copy">
                <strong>{{ userStore.user?.nickname || userStore.user?.username }}</strong>
                <span>管理员</span>
              </div>
              <el-icon><ArrowDown /></el-icon>
            </button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="home">返回前台</el-dropdown-item>
                <el-dropdown-item divided command="logout">安全退出</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <main class="admin-content">
        <div class="page-shell admin-content-shell">
          <router-view />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Moon, Sunny, ChatDotRound } from '@element-plus/icons-vue'
import { useTheme } from '@/composables/useTheme'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const router = useRouter()
const route = useRoute()
const { theme, toggleTheme } = useTheme()

function handleCommand(command) {
  if (command === 'home') router.push('/')
  else if (command === 'logout') userStore.logout()
}

async function refreshAdminUnreadCount() {
  if (userStore.isAdmin()) {
    await Promise.all([
      userStore.fetchAdminUnreadFeedbackCount(),
      userStore.fetchAdminPendingReviewCount(),
    ])
  }
}

onMounted(refreshAdminUnreadCount)

watch(
  () => [route.fullPath, userStore.token],
  () => {
    refreshAdminUnreadCount()
  },
  { immediate: true }
)
</script>

<style scoped>
.admin-layout {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 268px minmax(0, 1fr);
  background: var(--admin-main-bg);
  color: var(--app-text);
}

.aside {
  position: sticky;
  top: 0;
  height: 100vh;
  padding: 18px;
}

.aside-shell {
  height: 100%;
  padding: 18px 14px;
  border-radius: 30px;
  background:
    radial-gradient(circle at top, rgba(120, 181, 255, 0.12), transparent 28%),
    var(--admin-aside-bg);
  box-shadow: 0 24px 54px rgba(8, 15, 24, 0.28);
  overflow: auto;
}

.aside-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding: 8px 10px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.aside-logo-mark {
  width: 42px;
  height: 42px;
  border-radius: 14px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1f6ad0 0%, #78b5ff 100%);
  color: #fff;
}

.aside-logo-copy {
  display: flex;
  flex-direction: column;
}

.aside-logo-copy strong {
  color: #f5f8fc;
  font-size: 16px;
}

.aside-logo-copy span {
  color: rgba(231, 238, 247, 0.62);
  font-size: 12px;
}

.aside-menu {
  border-right: none;
}

.admin-main {
  min-width: 0;
  display: flex;
  flex-direction: column;
  padding-right: 18px;
}

.admin-header {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 18px;
  padding: 22px 0 12px;
}

.header-left {
  min-width: 0;
}

.header-caption {
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.header-caption strong {
  font-size: 24px;
  line-height: 1.1;
  color: var(--app-text);
}

.header-caption span {
  font-size: 13px;
  color: var(--app-text-soft);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-action {
  background: var(--app-bg-elevated);
  border-color: var(--app-border);
  color: var(--app-text);
}

.admin-user {
  border: 1px solid var(--app-border);
  background: var(--app-bg-elevated);
  border-radius: 999px;
  padding: 6px 12px 6px 6px;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  color: var(--header-text);
  box-shadow: var(--app-shadow-sm);
}

.admin-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f39c5d 0%, #de6b49 100%);
  color: #fff;
  font-weight: 700;
}

.admin-user-copy {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.admin-user-copy strong {
  font-size: 13px;
}

.admin-user-copy span {
  font-size: 11px;
  color: var(--app-text-soft);
}

.admin-content {
  flex: 1;
  padding: 0 0 30px;
}

.admin-content-shell {
  min-height: 100%;
  width: 100%;
  max-width: none;
  margin: 0;
}

.feedback-badge {
  margin-left: auto;
}

.feedback-badge-anchor {
  display: block;
  width: 8px;
  height: 8px;
}

.feedback-badge :deep(.el-badge__content) {
  border: none;
}

:deep(.aside-menu .el-menu-item) {
  margin: 6px 0;
  height: 46px;
  border-radius: 14px;
  padding-inline: 16px;
  gap: 10px;
}

:deep(.aside-menu .el-menu-item > span) {
  min-width: 0;
  line-height: 1;
}

.admin-content-shell :deep(.page-hero) {
  align-items: center;
  gap: 20px;
  padding: 24px 28px;
  margin-bottom: 20px;
}

.admin-content-shell :deep(.page-hero > div:first-child) {
  min-width: 0;
}

.admin-content-shell :deep(.page-hero h1),
.admin-content-shell :deep(.page-hero h2) {
  margin: 0;
}

.admin-content-shell :deep(.page-hero p) {
  max-width: 760px;
}

.admin-content-shell :deep(.page-card) {
  border-radius: 24px;
}

.admin-content-shell :deep(.page-card .el-card__header) {
  padding: 22px 24px 0;
}

.admin-content-shell :deep(.page-card .el-card__body) {
  padding: 22px 24px 24px;
}

.admin-content-shell :deep(.table-card .el-card__body) {
  padding: 6px 0 24px;
}

.admin-content-shell :deep(.filter-panel) {
  padding: 18px 20px;
}

.admin-content-shell :deep(.pagination) {
  margin-top: 24px;
}

:deep(.aside-menu .el-menu-item.is-active) {
  background: var(--admin-aside-surface);
}

:deep(.el-breadcrumb__inner),
:deep(.el-breadcrumb__inner a) {
  color: var(--app-text-soft);
}

@media (max-width: 960px) {
  .admin-layout {
    grid-template-columns: 1fr;
  }

  .aside {
    position: relative;
    height: auto;
    padding: 12px 12px 0;
  }

  .aside-shell {
    height: auto;
    border-radius: 24px;
  }

  .aside-menu {
    display: flex;
    overflow-x: auto;
    scrollbar-width: none;
    -ms-overflow-style: none;
  }

  .aside-menu::-webkit-scrollbar {
    display: none;
  }

  :deep(.aside-menu .el-menu-item) {
    flex-shrink: 0;
    margin-right: 8px;
  }

  .admin-main {
    padding-right: 0;
  }

  .admin-header,
  .admin-content {
    padding-inline: 12px;
  }
}

@media (max-width: 768px) {
  .admin-header {
    flex-direction: column;
    align-items: flex-start;
    padding-top: 18px;
  }

  .header-right {
    width: 100%;
    justify-content: space-between;
  }

  .admin-content-shell :deep(.page-hero) {
    padding: 20px 18px;
    gap: 16px;
  }

  .admin-content-shell :deep(.page-card .el-card__header) {
    padding: 18px 18px 0;
  }

  .admin-content-shell :deep(.page-card .el-card__body) {
    padding: 18px;
  }

  .admin-content-shell :deep(.table-card .el-card__body) {
    padding: 0 0 18px;
  }

  .admin-user-copy span {
    display: none;
  }
}

@media (min-width: 1280px) {
  .admin-layout {
    grid-template-columns: 292px minmax(0, 1fr);
  }

  .admin-main {
    padding-right: 22px;
  }

  .admin-header {
    padding: 26px 0 14px;
  }

  .admin-content {
    padding: 0 0 36px;
  }

  .admin-content-shell :deep(.page-hero) {
    padding: 28px 32px;
    margin-bottom: 22px;
  }
}
</style>
