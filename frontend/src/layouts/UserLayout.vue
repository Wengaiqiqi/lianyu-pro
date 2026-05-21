<template>
  <div class="user-layout">
    <header class="header">
      <div class="header-shell page-shell">
        <div class="brand" @click="router.push('/')">
          <div class="brand-mark">
            <el-icon :size="22"><Link /></el-icon>
          </div>
          <div class="brand-copy">
            <strong>{{ brandTitle }}</strong>
            <span>{{ brandSubtitle }}</span>
          </div>
        </div>

        <div class="header-main">
          <el-menu
            :default-active="$route.path"
            mode="horizontal"
            :ellipsis="false"
            router
            class="nav-menu"
          >
            <el-menu-item index="/">首页</el-menu-item>
            <template v-if="userStore.isLoggedIn()">
              <el-menu-item index="/dashboard">个人中心</el-menu-item>
              <el-menu-item index="/bookmarks">我的收藏</el-menu-item>
              <el-menu-item index="/rankings">热门榜单</el-menu-item>
              <el-menu-item index="/public">公开广场</el-menu-item>
              <el-menu-item index="/categories">分类管理</el-menu-item>
              <el-menu-item index="/search">全局搜索</el-menu-item>
              <el-menu-item index="/feedback">意见反馈</el-menu-item>
            </template>
          </el-menu>
        </div>

        <div class="header-actions">
          <el-button class="header-action" circle @click="toggleTheme">
            <el-icon><component :is="theme === 'dark' ? Sunny : Moon" /></el-icon>
          </el-button>

          <template v-if="userStore.isLoggedIn()">
            <el-badge :value="userStore.mailUnreadCount" :hidden="!userStore.mailUnreadCount" class="mail-badge">
              <el-button class="header-action" circle @click="router.push('/mailbox')">
                <el-icon><MessageBox /></el-icon>
              </el-button>
            </el-badge>

            <el-dropdown @command="handleCommand">
              <button type="button" class="profile-trigger">
                <el-avatar
                  v-if="userStore.user?.avatar"
                  :src="userStore.user.avatar"
                  :size="32"
                />
                <div v-else class="profile-fallback">
                  {{ (userStore.user?.nickname || userStore.user?.username || 'U').charAt(0).toUpperCase() }}
                </div>
                <div class="profile-copy">
                  <strong>{{ userStore.user?.nickname || userStore.user?.username }}</strong>
                  <span>{{ userStore.isAdmin() ? '管理员账户' : '个人空间' }}</span>
                </div>
                <el-icon class="trigger-arrow"><ArrowDown /></el-icon>
              </button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="mailbox">我的信箱</el-dropdown-item>
                  <el-dropdown-item command="feedback">提交反馈</el-dropdown-item>
                  <el-dropdown-item command="settings">个人设置</el-dropdown-item>
                  <el-dropdown-item v-if="userStore.isAdmin()" command="admin">进入后台</el-dropdown-item>
                  <el-dropdown-item divided command="logout">安全退出</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>

          <template v-else>
            <el-button class="ghost-button" @click="router.push('/register')">注册</el-button>
            <el-button type="primary" class="cta-button" @click="router.push('/login')">登录</el-button>
          </template>
        </div>
      </div>
    </header>

    <main class="layout-main" :class="{ 'home-main': $route.path === '/', 'transit-main': $route.path.startsWith('/go/'), 'auth-main': isAuthPage }">
      <div v-if="$route.path !== '/' && !$route.path.startsWith('/go/') && !isAuthPage" class="page-shell content-shell">
        <router-view />
      </div>
      <router-view v-else />
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowDown, Link, MessageBox, Moon, Sunny } from '@element-plus/icons-vue'
import { useTheme } from '@/composables/useTheme'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const router = useRouter()
const route = useRoute()
const { theme, toggleTheme } = useTheme()
const brandTitle = '\u94fe\u57df'
const brandSubtitle = '\u94fe\u63a5\u6211\u4eec\u7684\u76f8\u9047'
const isAuthPage = computed(() => route.path === '/login' || route.path === '/register')

function handleCommand(command) {
  if (command === 'mailbox') router.push('/mailbox')
  else if (command === 'feedback') router.push('/feedback')
  else if (command === 'settings') router.push('/settings')
  else if (command === 'admin') router.push('/admin')
  else if (command === 'logout') userStore.logout()
}

async function refreshMailboxCount() {
  if (!userStore.isLoggedIn()) return
  await userStore.fetchUnreadMailboxCount()
}

onMounted(refreshMailboxCount)

watch(
  () => [route.fullPath, userStore.token],
  () => {
    refreshMailboxCount()
  },
  { immediate: true }
)
</script>

<style scoped>
.user-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  color: var(--app-text);
}

.header {
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: var(--app-header-blur);
  background: var(--header-bg);
  border-bottom: 1px solid var(--header-border);
}

.header-shell {
  min-height: var(--app-header-height);
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 24px;
  padding: 14px 28px;
}

.brand {
  display: inline-flex;
  align-items: center;
  gap: 14px;
  cursor: pointer;
}

.brand-mark {
  width: 46px;
  height: 46px;
  border-radius: 16px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  background: linear-gradient(135deg, var(--app-primary) 0%, #67b4ff 100%);
  box-shadow: 0 16px 28px rgba(47, 128, 237, 0.24);
}

.brand-copy {
  display: flex;
  flex-direction: column;
}

.brand-copy strong {
  font-size: 17px;
  line-height: 1;
  color: var(--header-text);
}

.brand-copy span {
  font-size: 12px;
  line-height: 1;
  color: var(--app-text-soft);
}

.header-main {
  min-width: 0;
}

.nav-menu {
  border-bottom: none !important;
  background: transparent;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-action,
.ghost-button {
  background: var(--app-bg-elevated);
  border-color: var(--app-border);
  color: var(--app-text);
}

.cta-button {
  padding-inline: 18px;
}

.profile-trigger {
  min-width: 0;
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

.profile-fallback {
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

.profile-copy {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  text-align: left;
  min-width: 0;
}

.profile-copy strong {
  max-width: 120px;
  font-size: 13px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.profile-copy span {
  font-size: 11px;
  color: var(--app-text-soft);
}

.trigger-arrow {
  color: var(--app-text-soft);
}

.layout-main {
  flex: 1;
}

.content-shell {
  padding: 28px 18px 36px;
}

.home-main {
  padding: 0;
}

.transit-main {
  padding: 0 0 36px;
}

.auth-main {
  padding: 0;
}

.mail-badge :deep(.el-badge__content) {
  border: none;
}

:deep(.el-menu--horizontal > .el-menu-item) {
  height: 48px;
  margin: 0 4px;
  border-radius: 999px;
  color: var(--header-text);
}

:deep(.el-menu--horizontal > .el-menu-item.is-active) {
  border-bottom: none;
  background: var(--app-primary-soft);
  color: var(--app-primary);
}

:deep(.el-menu--horizontal > .el-menu-item:hover) {
  color: var(--app-primary);
}

@media (max-width: 1080px) {
  .header-shell {
    grid-template-columns: 1fr;
    gap: 14px;
    padding: 16px 18px;
  }

  .header-actions {
    justify-content: space-between;
  }

  .profile-copy strong {
    max-width: 180px;
  }
}

@media (min-width: 1280px) {
  .header-shell {
    padding-inline: 16px;
  }

  .content-shell {
    padding-inline: 12px;
  }
}

@media (max-width: 768px) {
  .brand-copy span,
  .profile-copy span {
    display: none;
  }

  .profile-trigger {
    padding-right: 10px;
  }

  .nav-menu {
    overflow-x: auto;
    scrollbar-width: none;
    -ms-overflow-style: none;
  }

  .nav-menu::-webkit-scrollbar {
    display: none;
  }

  :deep(.el-menu--horizontal) {
    width: max-content;
    min-width: 100%;
  }

  :deep(.el-menu--horizontal > .el-menu-item) {
    padding: 0 14px;
    font-size: 13px;
  }

  .content-shell {
    padding: 20px 12px 24px;
  }

  .transit-main {
    padding-bottom: 24px;
  }
}

@media (min-width: 1280px) {
  .header-shell {
    padding-inline: 14px;
    gap: 32px;
  }

  .content-shell {
    padding: 34px 10px 42px;
  }

  .transit-main {
    padding-bottom: 42px;
  }

  .brand-copy strong {
    font-size: 18px;
  }

  :deep(.el-menu--horizontal > .el-menu-item) {
    padding-inline: 18px;
    font-size: 14px;
  }
}
</style>
