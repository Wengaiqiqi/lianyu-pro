<template>
  <div class="public-page" :class="{ 'dark-theme': theme === 'dark' }">
    <section class="public-hero">
      <div class="hero-glow hero-glow-left"></div>
      <div class="hero-glow hero-glow-right"></div>
      <div class="hero-shell">
        <div class="hero-copy">
          <span class="hero-eyebrow">{{ viewingUser ? '公开书签集' : '发现公开收藏' }}</span>
          <h1 class="hero-title">
            {{ viewingUser ? `${viewingUser.nickname || viewingUser.username} 的公开书签` : '链域广场' }}
          </h1>
          <p class="hero-subtitle">
            {{ viewingUser ? '按分类浏览对方公开分享的网站与工具。' : '链域，一个链接让我们进入相同的区域' }}
          </p>

          <div class="hero-search">
            <div class="search-input-wrapper">
              <el-icon class="search-icon" :size="18"><Search /></el-icon>
              <input
                v-model="searchKeyword"
                class="search-input"
                :placeholder="viewingUser ? '搜索当前用户的公开书签' : '搜索用户昵称或用户名'"
                @keyup.enter="handleSearch"
              />
              <button class="search-btn" @click="handleSearch">
                {{ viewingUser ? '筛选书签' : '查找用户' }}
              </button>
            </div>
          </div>

          <div class="hero-stats">
            <div class="stat-chip">
              <span class="stat-value">{{ viewingUser ? total : totalPublicBookmarks }}</span>
              <span class="stat-label">{{ viewingUser ? '当前书签' : '公开书签' }}</span>
            </div>
            <div class="stat-chip">
              <span class="stat-value">{{ viewingUser ? categoryCount : totalPublicUsers }}</span>
              <span class="stat-label">{{ viewingUser ? '分类数量' : '分享用户' }}</span>
            </div>
            <div class="stat-chip">
              <span class="stat-value">{{ viewingUser ? (viewingUser.like_count || 0) : userList.length }}</span>
              <span class="stat-label">{{ viewingUser ? '收到点赞' : '已加载用户' }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <div class="content-shell" v-loading="loading">
      <div class="content-layout">
        <aside class="public-sidebar">
          <div class="sidebar-inner">
            <section class="side-card ranking-card">
              <div class="side-header">
                <div>
                  <p class="side-eyebrow">公开网址榜</p>
                  <h3>按访问热度</h3>
                </div>
                <div class="side-tabs">
                  <button
                    v-for="item in bookmarkRankingTabs"
                    :key="item.value"
                    type="button"
                    class="side-tab"
                    :class="{ active: bookmarkRankingType === item.value }"
                    @click="switchBookmarkRanking(item.value)"
                  >
                    {{ item.label }}
                  </button>
                </div>
              </div>

              <div class="rank-list">
                <div
                  v-for="(item, idx) in bookmarkRankingList"
                  :key="item.url"
                  class="rank-row-wrap"
                  @mouseleave="clearDirectLinkState(getDirectLinkKey('rank', item.id))"
                >
                  <a
                    :href="createTransitPath(item.id)"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="rank-row"
                  >
                  <span class="rank-index">{{ idx + 1 }}</span>
                  <img v-if="item.favicon" :src="item.favicon" class="rank-icon" @error="handleImageError" />
                  <div v-else class="rank-icon rank-fallback">{{ (item.title || 'U').charAt(0).toUpperCase() }}</div>
                  <div class="rank-copy">
                    <h4>{{ item.title }}</h4>
                    <div class="rank-actions">
                      <button
                        type="button"
                        class="collect-action rank-collect"
                        :disabled="isCollecting(item)"
                        @click.stop.prevent="collectBookmark(item)"
                      >
                        {{ isCollecting(item) ? '加入中...' : '加入我的链域' }}
                      </button>
                    </div>
                  </div>
                  <span class="rank-score">{{ item.period_visits || 0 }}</span>
                  </a>
                  <button
                    type="button"
                    :class="['direct-link-chip', { 'is-hidden': hiddenDirectLinkKey === getDirectLinkKey('rank', item.id) }]"
                    @click.stop="openDirectUrl(getDirectLinkKey('rank', item.id), item.url)"
                  >
                    <span class="direct-link-arrow">&gt;</span>
                    <span>直达</span>
                  </button>
                </div>
                <el-empty v-if="!bookmarkRankingList.length" description="暂无榜单" :image-size="64" />
              </div>
            </section>

            <section class="side-card ranking-card">
              <div class="side-header">
                <div>
                  <p class="side-eyebrow">热门用户榜</p>
                  <h3>按用户热度</h3>
                </div>
                <div class="side-tabs vertical">
                  <button
                    v-for="item in userRankingTabs"
                    :key="item.value"
                    type="button"
                    class="side-tab"
                    :class="{ active: userRankingMetric === item.value }"
                    @click="switchUserRanking(item.value)"
                  >
                    {{ item.label }}
                  </button>
                </div>
              </div>

              <div class="rank-list">
                <button
                  v-for="(user, idx) in userRankingList"
                  :key="user.id"
                  type="button"
                  class="rank-row user-rank-row"
                  @click="viewUserPublic(user)"
                >
                  <span class="rank-index">{{ idx + 1 }}</span>
                  <el-avatar v-if="user.avatar" :src="user.avatar" :size="34" />
                  <el-avatar v-else :size="34" class="default-avatar mini-avatar">
                    {{ (user.nickname || user.username || 'U').charAt(0).toUpperCase() }}
                  </el-avatar>
                  <div class="rank-copy">
                    <h4>{{ user.nickname || user.username }}</h4>
                    <p>@{{ user.username }}</p>
                  </div>
                  <span class="rank-score">{{ getUserMetricValue(user) }}</span>
                </button>
                <el-empty v-if="!userRankingList.length" description="暂无榜单" :image-size="64" />
              </div>
            </section>
          </div>
        </aside>

        <main class="public-main">
          <section v-if="viewingUser" class="toolbar-card">
            <div class="toolbar-main">
              <el-button class="back-btn" @click="goBack">
                <el-icon><ArrowLeft /></el-icon>
                返回用户列表
              </el-button>

              <div class="viewing-user-info">
                <el-avatar v-if="viewingUser.avatar" :src="viewingUser.avatar" :size="46" />
                <el-avatar v-else :size="46" class="default-avatar">
                  {{ (viewingUser.nickname || viewingUser.username || 'U').charAt(0).toUpperCase() }}
                </el-avatar>
                <div class="viewing-user-copy">
                  <div class="viewing-user-name">{{ viewingUser.nickname || viewingUser.username }}</div>
                  <div class="viewing-user-meta">
                    <span>{{ viewingUser.public_count || total || 0 }} 个公开书签</span>
                    <span>{{ categoryCount }} 个分类</span>
                    <span>{{ viewingUser.follower_count || 0 }} 人关注</span>
                    <span>{{ viewingUser.like_count || 0 }} 次点赞</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="toolbar-side">
              <button
                v-if="!isSelf(viewingUser)"
                type="button"
                class="action-pill follow"
                :class="{ active: viewingUser.is_following }"
                @click="toggleFollow(viewingUser)"
              >
                {{ viewingUser.is_following ? '已关注' : '关注' }}
              </button>
              <button
                type="button"
                class="action-pill like"
                :class="{ active: viewingUser.is_liked }"
                @click="toggleLike(viewingUser)"
              >
                👍 {{ viewingUser.like_count || 0 }}
              </button>
              <span class="toolbar-badge">{{ activeSearchKeyword || '全部内容' }}</span>
            </div>
          </section>

          <section v-if="!viewingUser" class="section-block">
            <div class="section-header">
              <div>
                <p class="section-eyebrow">公开用户</p>
                <h2 class="section-title">选择一个分享者</h2>
              </div>
              <p class="section-summary">共 {{ sortedUsers.length }} 位用户可浏览</p>
            </div>

            <div class="user-toolbar">
              <div class="sort-switch">
                <button
                  class="sort-chip"
                  :class="{ active: sortMode === 'popular' }"
                  type="button"
                  @click="sortMode = 'popular'"
                >
                  推荐排序
                </button>
                <button
                  class="sort-chip"
                  :class="{ active: sortMode === 'name' }"
                  type="button"
                  @click="sortMode = 'name'"
                >
                  名称排序
                </button>
              </div>
              <p class="sort-hint">
                {{ sortMode === 'popular' ? '优先展示公开书签更多的用户；' : '按昵称/用户名做自然排序；' }}
              </p>
            </div>

            <el-empty v-if="!loading && sortedUsers.length === 0" description="暂无公开用户" />

            <div v-else class="user-grid">
              <div
                v-for="user in sortedUsers"
                :key="user.id"
                class="user-card"
              >
                <button class="user-card-main" type="button" @click="viewUserPublic(user)">
                  <div class="user-card-top">
                    <el-avatar v-if="user.avatar" :src="user.avatar" :size="58" />
                    <el-avatar v-else :size="58" class="default-avatar user-avatar">
                      {{ (user.nickname || user.username || 'U').charAt(0).toUpperCase() }}
                    </el-avatar>
                  </div>
                  <div class="user-card-body">
                    <h3 class="user-card-name">{{ user.nickname || user.username }}</h3>
                    <p class="user-card-handle">@{{ user.username }}</p>
                  </div>
                  <div class="user-card-action">进入公开页</div>
                </button>

                <div class="user-card-social">
                  <div class="user-card-actions">
                    <button
                      type="button"
                      class="action-pill like"
                      :class="{ active: user.is_liked }"
                      @click.stop="toggleLike(user)"
                    >
                      👍 {{ user.like_count || 0 }}
                    </button>
                    <button
                      v-if="!isSelf(user)"
                      type="button"
                      class="action-pill follow"
                      :class="{ active: user.is_following }"
                      @click.stop="toggleFollow(user)"
                    >
                      {{ user.is_following ? '已关注' : '关注' }}
                    </button>
                  </div>
                  <span class="social-stat">{{ user.follower_count || 0 }} 人关注</span>
                </div>
              </div>
            </div>
          </section>

          <section v-if="viewingUser" class="section-block">
            <el-empty v-if="!loading && bookmarks.length === 0" description="该用户暂无公开书签" />

            <div v-else class="blocks-container">
              <div
                v-for="(group, categoryName) in groupedBookmarks"
                :key="categoryName"
                class="category-section"
              >
                <div class="category-header">
                  <div class="category-title-wrap">
                    <span class="category-icon">
                      <el-icon :size="18"><Grid /></el-icon>
                    </span>
                    <div>
                      <h3 class="category-title">{{ categoryName }}</h3>
                      <p class="category-count">{{ group.length }} 个站点</p>
                    </div>
                  </div>
                </div>

                <div class="nav-grid">
                  <div
                    v-for="item in group"
                    :key="item.id"
                    class="nav-card-wrap"
                    @mouseleave="clearDirectLinkState(getDirectLinkKey('nav', item.id))"
                  >
                    <a
                      :href="createTransitPath(item.id)"
                      target="_blank"
                      rel="noopener noreferrer"
                      class="nav-card"
                    >
                    <div class="card-icon-wrapper">
                      <img v-if="item.favicon" :src="item.favicon" class="site-icon" @error="handleImageError" />
                      <div v-else class="site-fallback">
                        {{ (item.title || 'U').charAt(0).toUpperCase() }}
                      </div>
                    </div>
                    <div class="card-info">
                      <div class="card-heading">
                        <h4 class="site-title">{{ item.title }}</h4>
                      </div>
                      <p class="site-desc" :title="item.description || '暂无描述'">
                        {{ item.description || '暂无描述' }}
                      </p>
                      <p class="site-url" :title="item.url">{{ item.url }}</p>
                      <div class="card-actions">
                        <button
                          type="button"
                          class="collect-action"
                          :disabled="isCollecting(item)"
                          @click.stop.prevent="collectBookmark(item)"
                        >
                          {{ isCollecting(item) ? '加入中...' : '加入我的链域' }}
                        </button>
                      </div>
                    </div>
                    </a>
                    <button
                      type="button"
                      :class="['direct-link-chip', { 'is-hidden': hiddenDirectLinkKey === getDirectLinkKey('nav', item.id) }]"
                      @click.stop="openDirectUrl(getDirectLinkKey('nav', item.id), item.url)"
                    >
                      <span class="direct-link-arrow">&gt;</span>
                      <span>直达</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <div class="pagination" v-if="total > perPage">
              <el-pagination
                v-model:current-page="page"
                :page-size="perPage"
                :total="total"
                background
                layout="prev, pager, next"
                @current-change="loadUserBookmarks"
              />
            </div>
          </section>
        </main>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Grid, Search } from '@element-plus/icons-vue'

import {
  getPublicUserBookmarkRankings,
  getPublicUserBookmarks,
} from '@/api/bookmark'
import {
  followPublicUser,
  getPublicUserRankings,
  getPublicUsers,
  likePublicUser,
  unfollowPublicUser,
  unlikePublicUser,
} from '@/api/user'
import { useCollectBookmark } from '@/composables/useCollectBookmark'
import { useTheme } from '@/composables/useTheme'
import { getUser } from '@/utils/auth'
import { createTransitPath, normalizeExternalUrl } from '@/utils/transit'

const route = useRoute()
const router = useRouter()
const { theme } = useTheme()
const { collectBookmark, isCollecting } = useCollectBookmark()
const currentUser = getUser()

const userList = ref([])
const bookmarks = ref([])
const loading = ref(false)
const page = ref(1)
const perPage = 40
const total = ref(0)
const searchKeyword = ref('')
const activeSearchKeyword = ref('')
const viewingUser = ref(null)
const sortMode = ref('popular')

const bookmarkRankingType = ref('day')
const userRankingMetric = ref('followers')
const bookmarkRankingList = ref([])
const userRankingList = ref([])
const hiddenDirectLinkKey = ref(null)
const PUBLIC_RANKING_LIMIT = 5

const bookmarkRankingTabs = [
  { label: '日榜', value: 'day' },
  { label: '周榜', value: 'week' },
  { label: '月榜', value: 'month' },
]

const userRankingTabs = [
  { label: '被关注', value: 'followers' },
  { label: '点赞量', value: 'likes' },
  { label: '公开量', value: 'public' },
]

const nameCollator = new Intl.Collator('zh-Hans-CN-u-co-pinyin', {
  numeric: true,
  sensitivity: 'base',
})

const filteredUsers = computed(() => {
  const keyword = (activeSearchKeyword.value || searchKeyword.value || '').trim().toLowerCase()
  if (!keyword) return userList.value
  return userList.value.filter(user => {
    const nickname = (user.nickname || '').toLowerCase()
    const username = (user.username || '').toLowerCase()
    return nickname.includes(keyword) || username.includes(keyword)
  })
})

const sortedUsers = computed(() => {
  const users = [...filteredUsers.value]
  users.sort((a, b) => {
    const nameA = a.nickname || a.username || ''
    const nameB = b.nickname || b.username || ''

    if (sortMode.value === 'name') {
      return nameCollator.compare(nameA, nameB)
    }

    const countDiff = Number(b.public_count || 0) - Number(a.public_count || 0)
    if (countDiff !== 0) return countDiff
    return nameCollator.compare(nameA, nameB)
  })
  return users
})

const groupedBookmarks = computed(() => {
  const groups = {}
  bookmarks.value.forEach(item => {
    const categoryName = item.category_name || '未分类'
    if (!groups[categoryName]) groups[categoryName] = []
    groups[categoryName].push(item)
  })
  return groups
})

const categoryCount = computed(() => Object.keys(groupedBookmarks.value).length)
const totalPublicUsers = computed(() => userList.value.length)
const totalPublicBookmarks = computed(() =>
  userList.value.reduce((sum, user) => sum + Number(user.public_count || 0), 0)
)

function getUserMetricValue(user) {
  if (userRankingMetric.value === 'likes') return user.like_count || 0
  if (userRankingMetric.value === 'public') return user.public_count || 0
  return user.follower_count || 0
}

function isSelf(user) {
  return !!(user && currentUser && Number(user.id) === Number(currentUser.id))
}

function syncUserState(targetUserId, patch) {
  userList.value = userList.value.map(user => (
    user.id === targetUserId ? { ...user, ...patch } : user
  ))

  userRankingList.value = userRankingList.value.map(user => (
    user.id === targetUserId ? { ...user, ...patch } : user
  ))

  if (viewingUser.value?.id === targetUserId) {
    viewingUser.value = { ...viewingUser.value, ...patch }
  }
}

async function loadUsers() {
  loading.value = true
  try {
    const res = await getPublicUsers()
    userList.value = res.data || []
  } catch (error) {
    console.error('加载公开用户失败:', error)
  } finally {
    loading.value = false
  }
}

async function loadBookmarkRankings() {
  const res = await getPublicUserBookmarkRankings(bookmarkRankingType.value)
  bookmarkRankingList.value = (res.data?.items || []).slice(0, PUBLIC_RANKING_LIMIT)
}

async function loadUserRankings() {
  const res = await getPublicUserRankings(userRankingMetric.value)
  userRankingList.value = (res.data?.items || []).slice(0, PUBLIC_RANKING_LIMIT)
}

async function loadUserBookmarks() {
  if (!viewingUser.value) return
  loading.value = true
  try {
    const params = {
      page: page.value,
      per_page: perPage,
      user_id: viewingUser.value.id,
    }
    if (activeSearchKeyword.value) params.keyword = activeSearchKeyword.value

    const res = await getPublicUserBookmarks(params)
    bookmarks.value = res.data.items || []
    total.value = res.data.total || 0
  } catch (error) {
    console.error('加载公开书签失败:', error)
  } finally {
    loading.value = false
  }
}

function viewUserPublic(user) {
  viewingUser.value = { ...user }
  page.value = 1
  activeSearchKeyword.value = ''
  searchKeyword.value = ''
  router.replace({
    name: 'Public',
    query: {
      userId: String(user.id),
    },
  })
  loadUserBookmarks()
}

function goBack() {
  viewingUser.value = null
  bookmarks.value = []
  total.value = 0
  page.value = 1
  activeSearchKeyword.value = ''
  searchKeyword.value = ''
  router.replace({ name: 'Public' })
}

function handleSearch() {
  const keyword = searchKeyword.value.trim()
  activeSearchKeyword.value = keyword

  if (viewingUser.value) {
    page.value = 1
    loadUserBookmarks()
  }
}

function handleImageError(event) {
  event.target.style.display = 'none'
}

function getDirectLinkKey(scope, id) {
  return `${scope}-${id}`
}

function clearDirectLinkState(key) {
  if (hiddenDirectLinkKey.value === key) {
    hiddenDirectLinkKey.value = null
  }
}

function openDirectUrl(key, url) {
  const target = normalizeExternalUrl(url)
  if (!target) return
  hiddenDirectLinkKey.value = key
  document.activeElement?.blur?.()
  window.open(target, '_blank', 'noopener,noreferrer')
}

async function handleVisit(id) {
  try {
    await incrementVisit(id)
    loadBookmarkRankings()
  } catch (error) {
    console.error('增加访问次数失败:', error)
  }
}

async function toggleFollow(user) {
  if (user.is_following) {
    const res = await unfollowPublicUser(user.id)
    syncUserState(user.id, {
      is_following: false,
      follower_count: res.data?.follower_count ?? Math.max(0, Number(user.follower_count || 0) - 1),
    })
  } else {
    const res = await followPublicUser(user.id)
    syncUserState(user.id, {
      is_following: true,
      follower_count: res.data?.follower_count ?? Number(user.follower_count || 0) + 1,
    })
  }
  loadUserRankings()
}

async function toggleLike(user) {
  if (user.is_liked) {
    const res = await unlikePublicUser(user.id)
    syncUserState(user.id, {
      is_liked: false,
      like_count: res.data?.like_count ?? Math.max(0, Number(user.like_count || 0) - 1),
    })
  } else {
    const res = await likePublicUser(user.id)
    syncUserState(user.id, {
      is_liked: true,
      like_count: res.data?.like_count ?? Number(user.like_count || 0) + 1,
    })
  }
  loadUserRankings()
}

function syncViewingUserFromRoute() {
  const userId = Number(route.query.userId || 0)
  if (!userId) return
  const matchedUser = userList.value.find(user => user.id === userId)
  if (matchedUser) {
    viewingUser.value = { ...matchedUser }
    loadUserBookmarks()
  }
}

function switchBookmarkRanking(type) {
  bookmarkRankingType.value = type
  loadBookmarkRankings()
}

function switchUserRanking(metric) {
  userRankingMetric.value = metric
  loadUserRankings()
}

onMounted(async () => {
  await Promise.all([
    loadUsers(),
    loadBookmarkRankings(),
    loadUserRankings(),
  ])
  syncViewingUserFromRoute()
})

watch(() => route.query.userId, () => {
  if (!userList.value.length) return
  if (!route.query.userId) {
    viewingUser.value = null
    return
  }
  syncViewingUserFromRoute()
})
</script>

<style scoped>
.public-page {
  min-height: calc(100vh - 60px);
  background: #fff;
  color: #192534;
}

.public-hero {
  position: relative;
  overflow: hidden;
  width: min(var(--app-content-wide), calc(100% - 20px));
  margin: 0 auto;
  padding: 40px 0 28px;
  border-radius: 32px 32px 0 0;
  background: linear-gradient(135deg, rgba(16, 32, 58, 0.96) 0%, rgba(24, 58, 92, 0.94) 52%, rgba(40, 87, 98, 0.92) 100%);
}

.hero-glow {
  position: absolute;
  width: 420px;
  height: 420px;
  border-radius: 999px;
  filter: blur(12px);
  opacity: 0.55;
  pointer-events: none;
}

.hero-glow-left {
  top: -150px;
  left: -120px;
  background: rgba(239, 179, 94, 0.22);
}

.hero-glow-right {
  right: -140px;
  bottom: -180px;
  background: rgba(87, 182, 255, 0.18);
}

.hero-shell {
  position: relative;
  z-index: 1;
  width: min(var(--app-content-wide), calc(100% - 20px));
  margin: 0 auto;
}

.hero-copy {
  max-width: 860px;
  margin: 0 auto;
  padding: 18px 0;
  text-align: center;
}

.hero-eyebrow {
  display: inline-flex;
  align-items: center;
  height: 32px;
  padding: 0 14px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 244, 227, 0.9);
  font-size: 12px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.hero-title {
  margin: 18px 0 12px;
  font-size: clamp(34px, 4vw, 54px);
  line-height: 1.06;
  font-weight: 700;
  color: #fff8ef;
}

.hero-subtitle {
  max-width: 620px;
  margin: 0 auto 28px;
  font-size: 16px;
  line-height: 1.75;
  color: rgba(235, 240, 248, 0.76);
}

.hero-search {
  max-width: 720px;
  margin: 0 auto;
}

.search-input-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 66px;
  padding: 8px 8px 8px 18px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 20px 60px rgba(8, 18, 36, 0.22);
}

.search-icon {
  color: #6d7d8f;
  flex-shrink: 0;
}

.search-input {
  flex: 1;
  min-width: 0;
  border: none;
  outline: none;
  background: transparent;
  color: #1f2d3d;
  font-size: 15px;
}

.search-input::placeholder {
  color: #8d9aac;
}

.search-btn {
  height: 50px;
  padding: 0 22px;
  border: none;
  border-radius: 18px;
  background: linear-gradient(135deg, #f08b44 0%, #e86b3d 100%);
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}

.hero-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  margin-top: 22px;
  max-width: 760px;
  margin-left: auto;
  margin-right: auto;
}

.stat-chip {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 18px 20px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(12px);
}

.stat-value {
  font-size: 24px;
  line-height: 1;
  font-weight: 700;
  color: #fff;
}

.stat-label {
  font-size: 12px;
  letter-spacing: 0.06em;
  color: rgba(232, 239, 247, 0.7);
}

.content-shell {
  position: relative;
  width: min(var(--app-content-wide), calc(100% - 20px));
  margin: 0 auto 20px;
  min-height: calc(100vh - 60px - 280px);
  padding: 28px 10px 48px;
  box-sizing: border-box;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98) 0%, #f9fbfe 100%);
  border-radius: 0 0 30px 30px;
}

.content-shell::before {
  content: '';
  position: absolute;
  top: 0;
  left: 24px;
  right: 24px;
  height: 1px;
  background: linear-gradient(90deg, rgba(226, 233, 241, 0), rgba(226, 233, 241, 0.95) 12%, rgba(226, 233, 241, 0.95) 88%, rgba(226, 233, 241, 0));
}

.content-shell::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 28px;
  background: linear-gradient(180deg, rgba(237, 242, 248, 0.72) 0%, rgba(255, 255, 255, 0) 100%);
  pointer-events: none;
}

.content-layout {
  max-width: var(--app-content-wide);
  margin: 0 auto;
  display: grid;
  grid-template-columns: 320px minmax(0, 1fr);
  gap: 28px;
  align-items: start;
}

.public-sidebar {
  min-width: 0;
}

.sidebar-inner {
  position: sticky;
  top: 84px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.side-card {
  border: 1px solid #e5edf5;
  border-radius: 24px;
  background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
  padding: 18px;
  box-shadow: 0 10px 28px rgba(33, 57, 91, 0.08);
}

@media (min-width: 1280px) {
  .hero-shell {
    max-width: var(--app-content-wide);
    margin: 0 auto;
  }

  .hero-copy {
    max-width: 940px;
  }

  .content-shell {
    padding: 32px 10px 52px;
  }

  .content-layout {
    grid-template-columns: 340px minmax(0, 1fr);
    gap: 32px;
  }

  .side-card {
    border-radius: 24px;
  }
}

.side-header {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-bottom: 16px;
}

.side-eyebrow {
  margin: 0 0 6px;
  color: #d57245;
  font-size: 12px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.side-header h3 {
  margin: 0;
  font-size: 20px;
  color: #1c2c3e;
}

.side-tabs {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.side-tabs.vertical {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.side-tab {
  min-height: 34px;
  padding: 0 12px;
  border: 1px solid #d9e3ee;
  border-radius: 999px;
  background: #fff;
  color: #55687d;
  font-size: 12px;
  cursor: pointer;
}

.side-tab.active {
  border-color: #f08b44;
  background: #fff3eb;
  color: #c95f37;
}

.rank-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.rank-row-wrap,
.nav-card-wrap {
  position: relative;
}

.rank-row {
  display: grid;
  grid-template-columns: 24px 34px minmax(0, 1fr) auto;
  align-items: center;
  gap: 10px;
  padding: 12px;
  border: 1px solid #e8eef5;
  border-radius: 16px;
  background: #fff;
  color: inherit;
  text-decoration: none;
}

.direct-link-chip {
  position: absolute;
  top: 50%;
  right: 12px;
  transform: translateY(-50%) translateX(10px);
  min-width: 74px;
  height: 32px;
  border: 1px solid color-mix(in srgb, var(--app-border) 72%, #6cb6ff 28%);
  border-radius: 999px;
  padding: 0 12px 0 10px;
  background: color-mix(in srgb, var(--app-bg-elevated) 88%, #6cb6ff 12%);
  color: var(--app-text);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  cursor: pointer;
  box-shadow: var(--app-shadow);
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s ease, transform 0.2s ease, background 0.2s ease, border-color 0.2s ease, color 0.2s ease;
  z-index: 2;
}

.direct-link-chip.is-hidden {
  opacity: 0 !important;
  pointer-events: none !important;
  transform: translateY(-50%) translateX(10px) !important;
}

.rank-row-wrap:hover .direct-link-chip,
.rank-row-wrap:focus-within .direct-link-chip,
.nav-card-wrap:hover .direct-link-chip,
.nav-card-wrap:focus-within .direct-link-chip {
  opacity: 1;
  pointer-events: auto;
  transform: translateY(-50%) translateX(0);
}

.direct-link-chip:hover {
  background: color-mix(in srgb, var(--app-bg-elevated) 78%, #6cb6ff 22%);
  border-color: color-mix(in srgb, var(--app-border) 48%, #6cb6ff 52%);
  color: #2f8fe8;
}

.direct-link-arrow {
  color: #409eff;
  font-size: 15px;
  line-height: 1;
}

.rank-actions {
  margin-top: 8px;
}

.user-rank-row {
  width: 100%;
  border: 1px solid #e8eef5;
  cursor: pointer;
  text-align: left;
}

.rank-index {
  font-size: 12px;
  font-weight: 700;
  color: #7c8ea1;
  text-align: center;
}

.rank-icon {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  object-fit: cover;
}

.rank-fallback {
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #2d7dd2 0%, #58a6ff 100%);
  color: #fff;
  font-size: 14px;
  font-weight: 700;
}

.mini-avatar {
  flex-shrink: 0;
}

.rank-copy {
  min-width: 0;
  flex: 1;
}

.rank-copy h4 {
  margin: 0 0 4px;
  font-size: 14px;
  color: #203144;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.rank-copy p {
  margin: 0;
  font-size: 12px;
  color: #7d8e9f;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.rank-score {
  font-size: 14px;
  font-weight: 700;
  color: #d46d41;
}

.card-actions {
  margin-top: 10px;
}

.collect-action {
  border: 1px solid rgba(64, 158, 255, 0.24);
  background: rgba(64, 158, 255, 0.08);
  color: #409eff;
  border-radius: 999px;
  padding: 6px 10px;
  font-size: 12px;
  line-height: 1;
  cursor: pointer;
  transition: all 0.2s ease;
}

.collect-action:hover:not(:disabled) {
  background: rgba(64, 158, 255, 0.14);
  border-color: rgba(64, 158, 255, 0.36);
}

.collect-action:disabled {
  opacity: 0.65;
  cursor: wait;
}

.rank-collect {
  align-self: center;
}

.public-main {
  min-width: 0;
}

.toolbar-card,
.section-block {
  border-radius: 28px;
}

.toolbar-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 22px;
  padding: 20px 22px;
  border: 1px solid #e3ebf4;
  background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
  box-shadow: 0 10px 28px rgba(33, 57, 91, 0.06);
}

.toolbar-main {
  display: flex;
  align-items: center;
  gap: 18px;
  min-width: 0;
}

.back-btn {
  border-radius: 14px;
}

.viewing-user-info {
  display: flex;
  align-items: center;
  gap: 14px;
  min-width: 0;
}

.default-avatar {
  background: linear-gradient(135deg, #f08b44 0%, #cf5f37 100%);
  color: #fff;
  font-weight: 700;
}

.viewing-user-copy {
  min-width: 0;
}

.viewing-user-name {
  font-size: 18px;
  font-weight: 700;
  color: #162538;
}

.viewing-user-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 6px;
  font-size: 13px;
  color: #68788a;
}

.toolbar-side {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.toolbar-badge {
  display: inline-flex;
  align-items: center;
  min-height: 38px;
  padding: 0 14px;
  border-radius: 999px;
  background: #eef4fb;
  color: #35506b;
  font-size: 13px;
}

.action-pill {
  min-height: 38px;
  padding: 0 14px;
  border: 1px solid #d9e3ee;
  border-radius: 999px;
  background: #fff;
  color: #55687d;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-pill.follow:hover,
.action-pill.follow.active {
  border-color: #4b90ff;
  background: #edf5ff;
  color: #2c6edc;
}

.action-pill.like:hover,
.action-pill.like.active {
  border-color: #f08b44;
  background: #fff3eb;
  color: #cf643a;
}

.section-block {
  width: 100%;
  padding: 22px;
  box-sizing: border-box;
  border: 1px solid #e3ebf4;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98) 0%, #f9fbfe 100%);
  box-shadow: 0 10px 28px rgba(33, 57, 91, 0.06);
}

.section-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 24px;
}

.section-eyebrow {
  margin: 0 0 8px;
  font-size: 12px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #d57245;
}

.section-title {
  margin: 0;
  font-size: 28px;
  line-height: 1.15;
  color: #17283b;
}

.section-summary {
  margin: 0;
  color: #6c7d8f;
  font-size: 14px;
}

.user-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 24px;
}

.sort-switch {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.sort-chip {
  min-height: 38px;
  padding: 0 16px;
  border: 1px solid #d9e3ee;
  border-radius: 999px;
  background: #fff;
  color: #55687d;
  font-size: 13px;
  cursor: pointer;
}

.sort-chip.active {
  border-color: #f08b44;
  background: #fff3eb;
  color: #c95f37;
}

.sort-hint {
  margin: 0;
  color: #7c8b99;
  font-size: 13px;
  line-height: 1.6;
  text-align: right;
}

.user-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 18px;
}

.user-card {
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 22px;
  border: 1px solid #e0e8f1;
  border-radius: 24px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.94) 0%, rgba(247, 250, 253, 0.96) 100%);
  transition: transform 0.24s ease, box-shadow 0.24s ease, border-color 0.24s ease;
}

.user-card:hover {
  transform: translateY(-4px);
  border-color: rgba(227, 118, 69, 0.38);
  box-shadow: 0 18px 36px rgba(42, 65, 96, 0.12);
}

.user-card-main {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0;
  border: none;
  background: transparent;
  text-align: center;
  cursor: pointer;
}

.user-card-top {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: row;
  gap: 14px;
  width: 100%;
}

.user-card-body {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-top: 18px;
  align-items: center;
}

.user-card-name {
  margin: 0;
  font-size: 20px;
  color: #18293d;
}

.user-card-handle {
  margin: 0;
  color: #7c8b99;
  font-size: 13px;
}

.user-card-desc {
  margin: 4px 0 0;
  color: #5a6b7c;
  font-size: 14px;
  line-height: 1.7;
}

.user-card-action {
  display: inline-flex;
  align-items: center;
  color: #d2693e;
  font-size: 14px;
  font-weight: 600;
  margin-top: 16px;
}

.user-card-social {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 2px;
}

.user-card-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  flex-wrap: nowrap;
}

.social-stat {
  font-size: 12px;
  color: #6f8195;
}

.blocks-container {
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.category-section {
  padding: 22px;
  border: 1px solid #e3ebf4;
  border-radius: 24px;
  background: linear-gradient(180deg, #ffffff 0%, #f9fbfd 100%);
}

.category-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.category-title-wrap {
  display: flex;
  align-items: center;
  gap: 14px;
}

.category-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 42px;
  border-radius: 14px;
  background: linear-gradient(135deg, #f08b44 0%, #d96a3f 100%);
  color: #fff;
}

.category-title {
  margin: 0;
  font-size: 20px;
  color: #1b2b3d;
}

.category-count {
  margin: 4px 0 0;
  color: #78889b;
  font-size: 13px;
}

.nav-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(270px, 1fr));
  gap: 16px;
}

.nav-card {
  display: flex;
  gap: 14px;
  padding: 16px;
  border: 1px solid #e5edf5;
  border-radius: 20px;
  background: #fff;
  text-decoration: none;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.nav-card:hover {
  transform: translateY(-3px);
  border-color: rgba(240, 139, 68, 0.4);
  box-shadow: 0 16px 32px rgba(33, 57, 91, 0.1);
}

.card-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  flex-shrink: 0;
  border-radius: 16px;
  background: #f2f6fb;
  overflow: hidden;
}

.site-icon {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.site-fallback {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #2d7dd2 0%, #58a6ff 100%);
  color: #fff;
  font-size: 20px;
  font-weight: 700;
}

.card-info {
  min-width: 0;
  flex: 1;
}

.card-heading {
  display: flex;
  align-items: center;
  gap: 10px;
}

.site-title {
  margin: 0;
  font-size: 16px;
  line-height: 1.45;
  font-weight: 700;
  color: #18293c;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.visit-tag {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  height: 24px;
  padding: 0 8px;
  border-radius: 999px;
  background: #fff2e8;
  color: #d46d41;
  font-size: 11px;
}

.site-desc {
  margin: 8px 0 10px;
  color: #617284;
  font-size: 13px;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
  min-height: 42px;
}

.site-url {
  margin: 0;
  color: #8a98a8;
  font-size: 12px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 28px;
}

@media (max-width: 1100px) {
  .content-layout {
    grid-template-columns: 1fr;
  }

  .sidebar-inner {
    position: static;
  }

  .public-sidebar {
    order: 2;
  }
}

@media (max-width: 768px) {
  .public-hero,
  .hero-shell,
  .content-shell {
    width: min(100%, calc(100% - 24px));
  }

  .content-shell::before {
    left: 0;
    right: 0;
  }

  .public-hero {
    padding-top: 24px;
  }

  .hero-title {
    font-size: 34px;
  }

  .hero-subtitle {
    font-size: 14px;
  }

  .search-input-wrapper {
    min-height: 58px;
    padding: 6px 6px 6px 14px;
    border-radius: 20px;
  }

  .search-btn {
    height: 44px;
    padding: 0 16px;
    border-radius: 14px;
    font-size: 13px;
  }

  .hero-stats {
    grid-template-columns: 1fr;
  }

  .toolbar-card,
  .section-header,
  .toolbar-main,
  .user-toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .toolbar-card,
  .section-block {
    padding: 18px;
  }

  .toolbar-side {
    justify-content: flex-start;
  }

  .section-title {
    font-size: 24px;
  }

  .sort-hint {
    text-align: left;
  }

  .user-grid,
  .nav-grid {
    grid-template-columns: 1fr;
  }

  .category-section {
    padding: 18px;
  }

  .side-tabs.vertical {
    grid-template-columns: 1fr;
  }

  .direct-link-chip {
    opacity: 1;
    pointer-events: auto;
    transform: translateY(-50%);
  }
}

.public-page.dark-theme {
  background: var(--app-bg);
  color: var(--app-text);
}

.public-page.dark-theme .public-hero {
  background: linear-gradient(135deg, #08111c 0%, #0d1a2a 42%, #12304b 72%, #0b1522 100%);
}

.public-page.dark-theme .search-input-wrapper {
  background: rgba(17, 27, 39, 0.92);
  border-color: rgba(108, 182, 255, 0.14);
}

.public-page.dark-theme .search-input {
  color: var(--app-text);
}

.public-page.dark-theme .search-input::placeholder {
  color: var(--app-text-soft);
}

.public-page.dark-theme .content-shell {
  background: linear-gradient(180deg, rgba(17, 30, 47, 0.98) 0%, rgba(13, 23, 38, 0.98) 100%);
  border: 1px solid var(--app-border);
}

.public-page.dark-theme .content-shell::before {
  background: linear-gradient(90deg, rgba(34, 50, 69, 0), rgba(34, 50, 69, 1) 12%, rgba(34, 50, 69, 1) 88%, rgba(34, 50, 69, 0));
}

.public-page.dark-theme .content-shell::after {
  background: linear-gradient(180deg, rgba(15, 23, 34, 0.72) 0%, rgba(15, 23, 34, 0) 100%);
}

.public-page.dark-theme .side-card,
.public-page.dark-theme .toolbar-card,
.public-page.dark-theme .section-block,
.public-page.dark-theme .toolbar-badge,
.public-page.dark-theme .sort-chip,
.public-page.dark-theme .user-card,
.public-page.dark-theme .category-section,
.public-page.dark-theme .nav-card,
.public-page.dark-theme .action-pill,
.public-page.dark-theme .rank-row,
.public-page.dark-theme .user-rank-row,
.public-page.dark-theme .side-tab {
  background: var(--app-bg-elevated);
  border-color: var(--app-border);
  color: var(--app-text);
}

.public-page.dark-theme .viewing-user-name,
.public-page.dark-theme .section-title,
.public-page.dark-theme .user-card-name,
.public-page.dark-theme .category-title,
.public-page.dark-theme .site-title,
.public-page.dark-theme .side-header h3,
.public-page.dark-theme .rank-copy h4 {
  color: var(--app-text);
}

.public-page.dark-theme .viewing-user-meta,
.public-page.dark-theme .section-summary,
.public-page.dark-theme .sort-hint,
.public-page.dark-theme .user-card-handle,
.public-page.dark-theme .user-card-desc,
.public-page.dark-theme .category-count,
.public-page.dark-theme .site-desc,
.public-page.dark-theme .site-url,
.public-page.dark-theme .social-stat,
.public-page.dark-theme .rank-copy p {
  color: var(--app-text-soft);
}

.public-page.dark-theme .sort-chip.active,
.public-page.dark-theme .visit-tag,
.public-page.dark-theme .action-pill.like.active,
.public-page.dark-theme .action-pill.like:hover,
.public-page.dark-theme .side-tab.active {
  background: rgba(240, 139, 68, 0.14);
  border-color: rgba(240, 139, 68, 0.22);
}

.public-page.dark-theme .action-pill.follow.active,
.public-page.dark-theme .action-pill.follow:hover {
  background: rgba(75, 144, 255, 0.14);
  border-color: rgba(75, 144, 255, 0.22);
}

.public-page.dark-theme .card-icon-wrapper {
  background: #1a2837;
}

.public-page.dark-theme .collect-action {
  background: rgba(108, 182, 255, 0.12);
  border-color: rgba(108, 182, 255, 0.2);
  color: #8cc5ff;
}

.public-page.dark-theme .collect-action:hover:not(:disabled) {
  background: rgba(108, 182, 255, 0.18);
  border-color: rgba(108, 182, 255, 0.3);
}

.public-page.dark-theme .direct-link-chip:hover {
  color: #8cc5ff;
}

.public-page.dark-theme .user-card:hover,
.public-page.dark-theme .nav-card:hover,
.public-page.dark-theme .rank-row:hover,
.public-page.dark-theme .user-rank-row:hover {
  background: #1a2837;
}

.public-page.dark-theme .toolbar-badge,
.public-page.dark-theme .rank-index {
  color: #8cb6df;
}
</style>
