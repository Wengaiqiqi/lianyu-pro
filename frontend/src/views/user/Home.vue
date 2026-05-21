<template>
  <div class="home-page" :class="{ 'dark-theme': theme === 'dark' }">
    <div class="hero-banner">
      <div class="hero-overlay"></div>
      <div class="hero-content">
        <h1 class="hero-title">链域</h1>
        <p class="hero-subtitle">链域 - 链接我们的相遇</p>

        <div class="search-box">
          <div class="search-tabs">
            <span
              v-for="tab in searchTabList"
              :key="tab"
              class="search-tab"
              :class="{ active: activeTab === tab }"
              @click="switchTab(tab)"
            >{{ tab }}</span>
          </div>

          <div class="search-input-wrapper">
            <input
              v-model="searchKeyword"
              class="search-input"
              :placeholder="currentPlaceholder"
              @keyup.enter="handleSearch"
            />
            <button class="search-btn" @click="handleSearch">
              <el-icon :size="20"><Search /></el-icon>
            </button>
          </div>

          <div class="search-engines" v-if="currentEngines.length > 1">
            <span
              v-for="(engine, idx) in currentEngines"
              :key="engine.name"
              class="engine-item"
              :class="{ active: activeEngineIdx === idx }"
              @click="switchEngine(idx)"
            >{{ engine.name }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="nav-container">
      <aside class="nav-sidebar">
        <div class="sidebar-inner">
          <el-menu
            :default-active="selectedCategory ? String(selectedCategory) : '0'"
            class="category-menu"
            @select="handleSelectCategory"
          >
            <div class="sidebar-logo">
              <el-icon :size="20" color="#409eff"><Promotion /></el-icon>
              <span>链域导航</span>
            </div>
            <el-menu-item index="0">
              <el-icon><Menu /></el-icon>
              <span>全部收录</span>
            </el-menu-item>
            <el-menu-item
              v-for="cat in categories"
              :key="cat.id"
              :index="String(cat.id)"
            >
              <el-icon><Folder /></el-icon>
              <span>{{ cat.name }}</span>
            </el-menu-item>
          </el-menu>
        </div>
      </aside>

      <div class="content-layout">
        <section class="hot-strip side-card">
          <div class="hot-strip-header">
            <div class="hot-strip-title">
              <span class="hot-strip-mark"></span>
              <span>热门网址</span>
            </div>
            <div class="hot-strip-tabs">
              <button
                v-for="item in featuredTabs"
                :key="item.value"
                type="button"
                class="hot-strip-tab"
                :class="{ active: featuredTab === item.value }"
                @click="switchFeaturedTab(item.value)"
              >
                {{ item.label }}
              </button>
            </div>
          </div>

          <div class="hot-strip-body" v-loading="featuredLoading">
            <div v-if="visibleFeaturedItems.length" class="hot-strip-grid" :class="{ compact: featuredTab === 'visits' }">
              <div
                v-for="item in visibleFeaturedItems"
                :key="`${featuredTab}-${item.id}`"
                class="hot-strip-card-wrap"
                @mouseleave="clearDirectLinkState(getDirectLinkKey('featured', item.id))"
              >
                <a
                  :href="createTransitPath(item.id)"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="hot-strip-card"
                >
                  <div class="hot-strip-icon">
                    <img v-if="item.favicon" :src="item.favicon" class="hot-strip-site-icon" @error="handleImageError" />
                    <span v-else class="hot-strip-fallback">{{ (item.title || 'U').charAt(0).toUpperCase() }}</span>
                  </div>
                  <div class="hot-strip-copy">
                    <h3>{{ item.title }}</h3>
                    <p :title="item.description || item.url">{{ item.description || item.url }}</p>
                  </div>
                  <button
                    type="button"
                    class="collect-action hot-strip-collect"
                    :disabled="isCollecting(item)"
                    @click.stop.prevent="collectBookmark(item)"
                  >
                    {{ isCollecting(item) ? '加入中...' : '加入我的链域' }}
                  </button>
                </a>
                <button
                  type="button"
                  :class="['direct-link-chip', { 'is-hidden': hiddenDirectLinkKey === getDirectLinkKey('featured', item.id) }]"
                  @click.stop="openDirectUrl(getDirectLinkKey('featured', item.id), item.url)"
                >
                  <span class="direct-link-arrow">&gt;</span>
                  <span>直达</span>
                </button>
              </div>
            </div>

            <el-empty
              v-else-if="!featuredLoading"
              description="最近一周暂无数据"
              :image-size="72"
            />

            <button
              v-if="canLoadMoreFeatured"
              type="button"
              class="hot-strip-more"
              @click="loadMoreFeatured"
            >
              <span class="hot-strip-more-line"></span>
              <span>加载更多</span>
              <span class="hot-strip-more-line"></span>
            </button>

            <button
              v-if="canCollapseFeatured"
              type="button"
              class="hot-strip-more"
              @click="collapseFeatured"
            >
              <span class="hot-strip-more-line"></span>
              <span>收起</span>
              <span class="hot-strip-more-line"></span>
            </button>
          </div>
        </section>

        <main class="nav-content" v-loading="loading">
          <div v-if="activeSearchKeyword" class="search-result-hint">
            包含关键词 "<strong>{{ activeSearchKeyword }}</strong>" 的搜索结果
            <el-button link type="primary" @click="clearSearch" style="margin-left: 12px;">清除搜索</el-button>
          </div>

          <el-empty v-if="!loading && bookmarks.length === 0" description="暂无相关网站" />

          <div class="blocks-container" v-else>
            <div
              class="category-section"
              v-for="(group, categoryName) in groupedBookmarks"
              :key="categoryName"
            >
              <div class="section-title">
                <el-icon :size="20" color="#ff7675"><Grid /></el-icon>
                <h2>{{ categoryName }}</h2>
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
                      <el-avatar v-else :size="44" shape="square" class="fallback-icon">
                        {{ (item.title || 'U').charAt(0).toUpperCase() }}
                      </el-avatar>
                    </div>
                    <div class="card-info">
                      <h3 class="site-title">{{ item.title }}</h3>
                      <p class="site-desc" :title="item.description || '暂无描述'">
                        {{ item.description || '暂无描述' }}
                      </p>
                      <div class="site-meta">
                        <span class="user-info">
                          <el-icon><User /></el-icon> {{ item.nickname || item.username || '链域' }}
                        </span>
                      </div>
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
              @current-change="loadBookmarks"
            />
          </div>
        </main>

        <aside class="right-sidebar">
          <div class="right-sidebar-inner">
            <section class="side-card brand-card">
              <div class="brand-toolbar">
                <span class="brand-toolbar-more">收藏助手</span>
                <el-popover
                  placement="bottom-end"
                  :width="350"
                  trigger="hover"
                  popper-class="collect-guide-popper"
                >
                  <template #reference>
                    <button type="button" class="brand-toolbar-plus" aria-label="收藏帮助">
                      +
                    </button>
                  </template>

                  <div class="collect-guide">
                    <div class="collect-guide-item">
                      <h4>加入收藏夹</h4>
                      <p>按 <span>Ctrl+D</span> 可以收藏本网页，方便快速打开使用。</p>
                    </div>
                    <div class="collect-guide-item">
                      <h4>设为首页</h4>
                      <p>浏览器设置页 &gt; 启动时 选项中，打开特定网页或一组网页。</p>
                    </div>
                  </div>
                </el-popover>
              </div>

              <div class="brand-head">
                <div class="brand-badge">
                  <el-icon :size="22"><Promotion /></el-icon>
                </div>
                <div class="brand-copy">
                  <h3>链域</h3>
                  <p>链域，一个链接让我们进入相同的区域</p>
                </div>
              </div>

              <div class="brand-highlight">
                <div class="brand-highlight-value">{{ total }}</div>
                <div class="brand-highlight-label">当前页面收录</div>
              </div>

              <div class="brand-stats">
                <div class="brand-stat blue">
                  <strong>{{ categories.length }}</strong>
                  <span>分类数量</span>
                </div>
                <div class="brand-stat green">
                  <strong>{{ rankingVisits }}</strong>
                  <span>榜单热度</span>
                </div>
                <div class="brand-stat orange">
                  <strong>10</strong>
                  <span>榜单网址</span>
                </div>
              </div>
            </section>

            <section class="side-card ranking-card">
              <div class="ranking-header">
                <div class="ranking-title">
                  <el-icon :size="18"><StarFilled /></el-icon>
                  <span>热门网址</span>
                </div>
                <div class="ranking-tabs">
                  <button
                    v-for="item in rankingTabs"
                    :key="item.value"
                    type="button"
                    class="ranking-tab"
                    :class="{ active: rankingType === item.value }"
                    @click="switchRankingTab(item.value)"
                  >
                    {{ item.label }}
                  </button>
                </div>
              </div>

              <div class="ranking-list" v-loading="rankingLoading">
                <div
                  v-for="(item, idx) in top10RankingList"
                  :key="item.id"
                  class="ranking-item-wrap"
                  @mouseleave="clearDirectLinkState(getDirectLinkKey('sidebar-rank', item.id))"
                >
                  <a
                    :href="createTransitPath(item.id)"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="ranking-item"
                  >
                    <div class="ranking-index">{{ idx + 1 }}</div>
                    <div class="ranking-icon">
                      <img v-if="item.favicon" :src="item.favicon" class="ranking-site-icon" @error="handleImageError" />
                      <span v-else class="ranking-fallback">{{ (item.title || 'U').charAt(0).toUpperCase() }}</span>
                    </div>
                    <div class="ranking-info">
                      <h4>{{ item.title }}</h4>
                      <p :title="item.description || item.url">{{ item.description || item.url }}</p>
                      <div class="ranking-actions">
                        <button
                          type="button"
                          class="collect-action ranking-collect"
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
                    :class="['direct-link-chip', 'sidebar-ranking-direct-left', { 'is-hidden': hiddenDirectLinkKey === getDirectLinkKey('sidebar-rank', item.id) }]"
                    @click.stop="openDirectUrl(getDirectLinkKey('sidebar-rank', item.id), item.url)"
                  >
                    <span class="direct-link-arrow">&gt;</span>
                    <span>直达</span>
                  </button>
                </div>

                <el-empty
                  v-if="!rankingLoading && rankingList.length === 0"
                  description="暂无榜单数据"
                  :image-size="72"
                />

                <button type="button" class="ranking-more" @click="$router.push('/rankings')">
                  <span class="ranking-more-line"></span>
                  <span>查看全部榜单</span>
                  <span class="ranking-more-line"></span>
                </button>
              </div>
            </section>
          </div>
        </aside>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getPublicBookmarks, getRankings, getPublicUserBookmarkRankings } from '@/api/bookmark'
import { Promotion, Search, Menu, Folder, Grid, User, StarFilled } from '@element-plus/icons-vue'
import { searchGroups, searchTabList } from './HomeSearch'
import { useCollectBookmark } from '@/composables/useCollectBookmark'
import { useTheme } from '@/composables/useTheme'
import { createTransitPath, normalizeExternalUrl } from '@/utils/transit'

const bookmarks = ref([])
const categories = ref([])
const loading = ref(false)
const rankingLoading = ref(false)
const featuredLoading = ref(false)
const page = ref(1)
const perPage = 40
const total = ref(0)
const selectedCategory = ref(null)
const searchKeyword = ref('')
const activeSearchKeyword = ref('')
const rankingType = ref('day')
const rankingList = ref([])
const featuredTab = ref('created')
const featuredExpanded = ref(false)
const featuredSourceItems = ref([])
const monthlyRecommendLoading = ref(false)
const hiddenDirectLinkKey = ref(null)
const { theme } = useTheme()
const { collectBookmark, isCollecting } = useCollectBookmark()
const FEATURED_WINDOW_DAYS = 7
const FEATURED_ROW_SIZE = 4
const FEATURED_DEFAULT_ROWS = 2
const FEATURED_DEFAULT_COUNT = FEATURED_ROW_SIZE * FEATURED_DEFAULT_ROWS

const activeTab = ref('站内')
const activeEngineIdx = ref(0)
const rankingTabs = [
  { label: '日榜', value: 'day' },
  { label: '周榜', value: 'week' },
  { label: '月榜', value: 'month' },
]

const featuredTabs = [
  { label: '发布', value: 'created' },
  { label: '更新', value: 'updated' },
  { label: '浏览', value: 'visits' },
]
const currentEngines = computed(() => searchGroups[activeTab.value] || [])
const currentEngine = computed(() => currentEngines.value[activeEngineIdx.value] || currentEngines.value[0])
const currentPlaceholder = computed(() => currentEngine.value?.placeholder || '输入关键词搜索')
const rankingVisits = computed(() =>
  rankingList.value.reduce((sum, item) => sum + Number(item.visits || 0), 0)
)
const top10RankingList = computed(() => rankingList.value.slice(0, 10))
const recentWindowStart = computed(() => Date.now() - FEATURED_WINDOW_DAYS * 24 * 60 * 60 * 1000)
const recentPublishedList = computed(() =>
  featuredSourceItems.value
    .filter(item => isWithinRecentWindow(item.created_at))
    .sort((a, b) => getTimestamp(b.created_at) - getTimestamp(a.created_at))
)
const recentUpdatedList = computed(() =>
  featuredSourceItems.value
    .filter(item => isWithinRecentWindow(item.updated_at))
    .sort((a, b) => getTimestamp(b.updated_at) - getTimestamp(a.updated_at))
)
const featuredBrowseList = computed(() =>
  [...featuredSourceItems.value]
    .sort((a, b) => {
      const visitDiff = Number(b.visits || 0) - Number(a.visits || 0)
      if (visitDiff !== 0) return visitDiff
      return getTimestamp(b.updated_at || b.created_at) - getTimestamp(a.updated_at || a.created_at)
    })
    .slice(0, FEATURED_ROW_SIZE)
)
const activeFeaturedItems = computed(() => {
  if (featuredTab.value === 'updated') return recentUpdatedList.value
  if (featuredTab.value === 'visits') return featuredBrowseList.value
  return recentPublishedList.value
})
const visibleFeaturedItems = computed(() => {
  if (featuredTab.value === 'visits' || featuredExpanded.value) return activeFeaturedItems.value
  return activeFeaturedItems.value.slice(0, FEATURED_DEFAULT_COUNT)
})
const canLoadMoreFeatured = computed(() =>
  featuredTab.value !== 'visits' &&
  activeFeaturedItems.value.length > FEATURED_DEFAULT_COUNT &&
  !featuredExpanded.value
)
const canCollapseFeatured = computed(() =>
  featuredTab.value !== 'visits' &&
  activeFeaturedItems.value.length > FEATURED_DEFAULT_COUNT &&
  featuredExpanded.value
)

const groupedBookmarks = computed(() => {
  const groups = {}
  bookmarks.value.forEach(item => {
    const catName = item.category_name || '未分类'
    if (!groups[catName]) groups[catName] = []
    groups[catName].push(item)
  })
  return groups
})

function getTimestamp(value) {
  const timestamp = value ? new Date(value).getTime() : 0
  return Number.isNaN(timestamp) ? 0 : timestamp
}

function isWithinRecentWindow(value) {
  const timestamp = getTimestamp(value)
  return timestamp >= recentWindowStart.value
}

function switchTab(tab) {
  activeTab.value = tab
  activeEngineIdx.value = 0
}

function switchEngine(idx) {
  activeEngineIdx.value = idx
}

function handleSearch() {
  const keyword = searchKeyword.value.trim()
  if (!keyword) return

  const engine = currentEngine.value
  if (!engine) return

  if (engine.url === '__internal__') {
    activeSearchKeyword.value = keyword
    page.value = 1
    loadBookmarks()
  } else {
    const url = engine.url.replace('%s', encodeURIComponent(keyword))
    window.open(url, '_blank')
  }
}

function clearSearch() {
  searchKeyword.value = ''
  activeSearchKeyword.value = ''
  page.value = 1
  loadBookmarks()
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

async function loadBookmarks() {
  loading.value = true
  try {
    const params = { page: page.value, per_page: perPage }
    if (selectedCategory.value) params.category_id = selectedCategory.value
    if (activeSearchKeyword.value) params.keyword = activeSearchKeyword.value

    const res = await getPublicBookmarks(params)
    bookmarks.value = res.data.items || []
    total.value = res.data.total || 0
    if (res.data.categories) {
      categories.value = res.data.categories
    }
  } catch (error) {
    console.error('加载导航失败:', error)
  } finally {
    loading.value = false
  }
}

async function loadFeaturedBookmarks() {
  featuredLoading.value = true
  try {
    const firstRes = await getPublicBookmarks({ page: 1, per_page: 200 })
    const firstItems = firstRes.data?.items || []
    const totalItems = Number(firstRes.data?.total || firstItems.length)

    if (totalItems > firstItems.length) {
      const fullRes = await getPublicBookmarks({ page: 1, per_page: totalItems })
      featuredSourceItems.value = fullRes.data?.items || firstItems
    } else {
      featuredSourceItems.value = firstItems
    }
  } catch (error) {
    console.error('加载首页热门栏失败:', error)
    featuredSourceItems.value = []
  } finally {
    featuredLoading.value = false
  }
}

async function loadRankings() {
  rankingLoading.value = true
  try {
    const res = await getRankings(rankingType.value)
    rankingList.value = res.data || []
  } catch (error) {
    console.error('加载排行榜失败:', error)
  } finally {
    rankingLoading.value = false
  }
}

async function loadMonthlyRecommendations() {
  monthlyRecommendLoading.value = true
  try {
    const res = await getPublicUserBookmarkRankings('month', {
      period: 'previous_month',
      limit: 5,
    })
    const items = res.data?.items || []
    const homeCategoryNames = categories.value.map(c => c.name)

    for (const item of items) {
      const alreadyFeatured = featuredSourceItems.value.some(b => b.id === item.id)

      if (item.category_name && homeCategoryNames.includes(item.category_name)) {
        if (!alreadyFeatured) {
          featuredSourceItems.value.push(item)
        }
      }
    }
  } catch (error) {
    console.error('加载本月推荐失败:', error)
  } finally {
    monthlyRecommendLoading.value = false
  }
}

function switchFeaturedTab(type) {
  featuredTab.value = type
  featuredExpanded.value = false
}

function loadMoreFeatured() {
  featuredExpanded.value = true
}

function collapseFeatured() {
  featuredExpanded.value = false
}

function switchRankingTab(type) {
  rankingType.value = type
  loadRankings()
}

function handleSelectCategory(index) {
  selectedCategory.value = index === '0' ? null : parseInt(index, 10)
  page.value = 1
  searchKeyword.value = ''
  activeSearchKeyword.value = ''
  loadBookmarks()
}

function handleImageError(event) {
  event.target.style.display = 'none'
}

onMounted(async () => {
  await loadBookmarks()
  loadFeaturedBookmarks()
  loadRankings()
  loadMonthlyRecommendations()
})
</script>

<style scoped>
.home-page {
  background-color: #f5f7fa;
  min-height: calc(100vh - 60px);
}

.hero-banner {
  position: relative;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 40%, #0f3460 70%, #1a1a2e 100%);
  min-height: 320px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse at 20% 50%, rgba(64, 158, 255, 0.15) 0%, transparent 60%),
    radial-gradient(ellipse at 80% 50%, rgba(103, 58, 183, 0.12) 0%, transparent 60%);
  pointer-events: none;
}

.hero-content {
  position: relative;
  z-index: 1;
  text-align: center;
  width: 100%;
  max-width: 680px;
  padding: 40px 20px;
}

.hero-title {
  font-size: 32px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 8px;
  letter-spacing: 2px;
}

.hero-subtitle {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0 0 28px;
}

.search-box {
  width: 100%;
}

.search-tabs {
  display: flex;
  justify-content: center;
  gap: 4px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.search-tabs .hot-strip-more {
  display: none;
}

.search-tab {
  padding: 6px 18px;
  border-radius: 20px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  transition: all 0.25s;
  user-select: none;
}

.search-tab:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.1);
}

.search-tab.active {
  color: #fff;
  background: rgba(64, 158, 255, 0.6);
  font-weight: 600;
}

.search-input-wrapper {
  display: flex;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.search-input {
  flex: 1;
  border: none;
  outline: none;
  padding: 14px 20px;
  font-size: 15px;
  color: #333;
  background: transparent;
}

.search-input::placeholder {
  color: #bbb;
}

.search-btn {
  width: 56px;
  border: none;
  background: #409eff;
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.search-btn:hover {
  background: #337ecc;
}

.search-engines {
  display: flex;
  justify-content: center;
  gap: 6px;
  margin-top: 14px;
  flex-wrap: wrap;
}

.engine-item {
  padding: 4px 14px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.55);
  cursor: pointer;
  border-radius: 14px;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.engine-item:hover {
  color: rgba(255, 255, 255, 0.9);
  border-color: rgba(255, 255, 255, 0.2);
}

.engine-item.active {
  color: #fff;
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
}

.nav-container {
  display: flex;
  max-width: 100%;
  margin: 0 auto;
  padding: 24px;
  gap: 24px;
  flex: 1;
  width: 100%;
  box-sizing: border-box;
}

.nav-sidebar {
  width: 240px;
  flex-shrink: 0;
}

.sidebar-inner {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  position: sticky;
  top: 80px;
  max-height: calc(100vh - 100px);
  overflow-y: auto;
}

.sidebar-inner::-webkit-scrollbar {
  width: 4px;
}

.sidebar-inner::-webkit-scrollbar-thumb {
  background: #dcdfe6;
  border-radius: 2px;
}

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 20px;
  font-size: 18px;
  font-weight: 700;
  color: #2c3e50;
  border-bottom: 1px solid #ebeef5;
  margin-bottom: 8px;
}

.category-menu {
  border-right: none;
}

.category-menu .el-menu-item {
  height: 50px;
  line-height: 50px;
  font-size: 15px;
}

.category-menu .el-menu-item.is-active {
  background-color: #e6f1fc;
  color: #409eff;
  font-weight: bold;
  border-right: 3px solid #409eff;
}

.content-layout {
  flex: 1;
  min-width: 0;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 300px;
  gap: 24px;
}

.hot-strip.side-card {
  grid-column: 1 / -1;
  padding: 18px 18px 12px;
  background: linear-gradient(180deg, var(--app-bg-soft) 0%, #f3f7fb 100%);
  border-color: var(--app-border);
  box-shadow: var(--app-shadow);
  color: var(--app-text);
}

.hot-strip-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.hot-strip-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  font-weight: 700;
  color: var(--app-text);
}

.hot-strip-mark {
  width: 10px;
  height: 10px;
  border-radius: 3px;
  transform: rotate(45deg);
  background: linear-gradient(135deg, #2da9ff 0%, #5fd0ff 100%);
  box-shadow: 0 0 0 4px rgba(45, 169, 255, 0.12);
}

.hot-strip-tabs {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.hot-strip-tab {
  border: none;
  padding: 0;
  background: transparent;
  color: var(--app-text-soft);
  font-size: 14px;
  cursor: pointer;
  transition: color 0.2s ease;
}

.hot-strip-tab::after {
  content: '*';
  margin-left: 10px;
  color: #565b63;
}

.hot-strip-tab:last-child::after {
  display: none;
}

.hot-strip-tab:hover,
.hot-strip-tab.active {
  color: #38abff;
}

.hot-strip-body {
  min-height: 132px;
}

.hot-strip-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.hot-strip-card-wrap,
.nav-card-wrap {
  position: relative;
}

.hot-strip-card {
  display: flex;
  align-items: center;
  gap: 14px;
  min-width: 0;
  padding: 14px 12px;
  border-radius: 14px;
  background: var(--app-bg-elevated);
  border: 1px solid var(--app-border);
  box-shadow: 0 8px 22px rgba(16, 24, 40, 0.06);
  text-decoration: none;
  transition: transform 0.2s ease, background 0.2s ease, border-color 0.2s ease;
}

.hot-strip-card:hover {
  transform: translateY(-1px);
  background: #ffffff;
  border-color: #cfe0f2;
}

.hot-strip-icon {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  overflow: hidden;
  background: #eef3f8;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hot-strip-site-icon {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hot-strip-fallback {
  color: var(--app-text);
  font-size: 16px;
  font-weight: 700;
}

.hot-strip-copy {
  min-width: 0;
  flex: 1;
}

.hot-strip-copy h3 {
  margin: 0 0 5px;
  font-size: 15px;
  font-weight: 700;
  color: var(--app-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.hot-strip-copy p {
  margin: 0;
  font-size: 13px;
  line-height: 1.45;
  color: var(--app-text-soft);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.hot-strip-more {
  width: 100%;
  margin-top: 14px;
  border: none;
  background: transparent;
  color: #9098a1;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
}

.hot-strip-more:hover {
  color: #d4d9df;
}

.hot-strip-more-line {
  width: 120px;
  max-width: 18%;
  height: 1px;
  background: linear-gradient(90deg, transparent 0%, #42464c 50%, transparent 100%);
}

.hot-strip-tab::after {
  content: '*';
  color: rgba(107, 122, 140, 0.65);
}


.hot-strip-more {
  color: var(--app-text-soft);
}

.hot-strip-more:hover {
  color: var(--app-text);
}

.hot-strip-more-line {
  background: linear-gradient(90deg, transparent 0%, rgba(107, 122, 140, 0.32) 50%, transparent 100%);
}

.hot-strip-tab::after {
  content: '*';
}

.nav-content {
  min-width: 0;
}

.search-result-hint {
  background: #fff;
  padding: 15px 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  color: #555;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
}

.blocks-container {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.category-section {
  margin-bottom: 24px;
  padding-bottom: 10px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  padding-bottom: 8px;
}

.section-title h2 {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.nav-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
}

.nav-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px;
  background: #fdfdfd;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  text-decoration: none;
  box-shadow: 0 14px 28px rgba(15, 23, 42, 0.06);
  transition: all 0.2s ease;
}

.nav-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 18px 36px rgba(15, 23, 42, 0.12);
  border-color: #c6e2ff;
  background: #fff;
}

.direct-link-chip {
  position: absolute;
  top: 50%;
  right: 10px;
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

.hot-strip-card-wrap:hover .direct-link-chip,
.hot-strip-card-wrap:focus-within .direct-link-chip,
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

.card-icon-wrapper {
  width: 44px;
  height: 44px;
  flex-shrink: 0;
  border-radius: 10px;
  overflow: hidden;
  background: #f0f2f5;
  display: flex;
  align-items: center;
  justify-content: center;
}

.site-icon {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.fallback-icon {
  background-color: #409eff;
  color: #fff;
  font-size: 20px;
  font-weight: bold;
}

.card-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.site-title {
  font-size: 15px;
  color: #2c3e50;
  font-weight: 600;
  margin: 0 0 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.site-desc {
  font-size: 12px;
  color: #7f8c8d;
  margin: 0 0 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.4;
  height: 33px;
}

.site-meta {
  font-size: 12px;
  color: #999;
  display: flex;
  align-items: center;
  gap: 6px;
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
  display: inline-flex;
  align-items: center;
  justify-content: center;
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

.hot-strip-collect {
  align-self: flex-start;
}

.hot-strip-card-wrap .direct-link-chip {
  top: auto;
  right: auto;
  bottom: 12px;
  left: 50%;
  transform: translateX(-50%) translateY(10px);
}

.hot-strip-card-wrap:hover .direct-link-chip,
.hot-strip-card-wrap:focus-within .direct-link-chip {
  transform: translateX(-50%) translateY(0);
}

.hot-strip-card-wrap .direct-link-chip.is-hidden {
  transform: translateX(-50%) translateY(10px) !important;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 3px;
  background: #f4f4f5;
  padding: 2px 6px;
  border-radius: 3px;
}

.pagination {
  margin-top: 30px;
  display: flex;
  justify-content: center;
}

.right-sidebar {
  min-width: 0;
}

.right-sidebar-inner {
  position: sticky;
  top: 80px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.side-card {
  border-radius: 18px;
  background: linear-gradient(180deg, #ffffff 0%, #f7faff 100%);
  border: 1px solid #e4ebf3;
  box-shadow: 0 10px 24px rgba(27, 55, 90, 0.08);
  color: #24384f;
  overflow: hidden;
}

.brand-card {
  padding: 18px;
}

.brand-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.brand-toolbar-more {
  font-size: 12px;
  color: #7f90a3;
}

.brand-toolbar-plus {
  width: 22px;
  height: 22px;
  border: none;
  border-radius: 50%;
  background: #ffffff;
  color: #4a5e74;
  box-shadow: 0 4px 12px rgba(23, 43, 77, 0.14);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  line-height: 1;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.brand-toolbar-plus:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(23, 43, 77, 0.18);
}

.brand-head {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 18px;
}

.brand-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: linear-gradient(135deg, #4da0ff 0%, #66b8ff 100%);
  color: #fff;
  flex-shrink: 0;
}

.brand-copy h3 {
  margin: 0;
  font-size: 22px;
  color: #1f3348;
  line-height: 1.2;
}

.brand-copy p {
  margin: 0;
  font-size: 13px;
  line-height: 1.4;
  color: #6d8095;
}

.brand-highlight {
  padding: 16px;
  border-radius: 16px;
  background: linear-gradient(135deg, #edf5ff 0%, #f6f9ff 100%);
  border: 1px solid #d9e8fb;
  text-align: center;
}

.brand-highlight-value {
  font-size: 36px;
  line-height: 1;
  font-weight: 700;
  color: #7dc1ff;
}

.brand-highlight-label {
  margin-top: 8px;
  font-size: 12px;
  letter-spacing: 0.08em;
  color: #7b8ea2;
}

.brand-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  margin-top: 12px;
}

.brand-stat {
  padding: 12px 8px;
  border-radius: 14px;
  text-align: center;
  background: #f7fafc;
  border: 1px solid #e6edf5;
}

.brand-stat strong {
  display: block;
  font-size: 20px;
  line-height: 1.1;
}

.brand-stat span {
  display: block;
  margin-top: 6px;
  font-size: 12px;
  color: #7a8b9c;
}

.brand-stat.blue strong {
  color: #6fb4ff;
}

.brand-stat.green strong {
  color: #65dd8c;
}

.brand-stat.orange strong {
  color: #ffb264;
}

.ranking-card {
  padding: 16px;
}

.ranking-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}

.ranking-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 700;
  color: #23384e;
}

.ranking-tabs {
  display: flex;
  gap: 6px;
}

.ranking-tab {
  border: none;
  background: transparent;
  color: #7a8c9f;
  font-size: 12px;
  cursor: pointer;
  padding: 4px 2px;
  border-bottom: 2px solid transparent;
}

.ranking-tab.active {
  color: #65b4ff;
  border-bottom-color: #65b4ff;
}

.ranking-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 180px;
  max-height: 680px;
  overflow-y: auto;
}

.ranking-item-wrap {
  position: relative;
}

.ranking-item {
  display: grid;
  grid-template-columns: 24px 40px minmax(0, 1fr);
  align-items: center;
  gap: 8px;
  padding: 10px;
  border-radius: 12px;
  background: #f7fafc;
  border: 1px solid #e8eef5;
  text-decoration: none;
  transition: background 0.2s ease, transform 0.2s ease;
}

.ranking-more {
  width: 100%;
  margin-top: 10px;
  border: none;
  background: transparent;
  color: var(--app-text-soft);
  font-size: 13px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 8px 0;
}

.ranking-more:hover {
  color: #409eff;
}

.ranking-more-line {
  width: 60px;
  max-width: 25%;
  height: 1px;
  background: linear-gradient(90deg, transparent 0%, rgba(107, 122, 140, 0.32) 50%, transparent 100%);
}

.ranking-item:hover {
  background: #ffffff;
  transform: translateY(-1px);
}

.ranking-index {
  font-size: 13px;
  font-weight: 700;
  color: #6a8cb1;
  text-align: center;
}

.ranking-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: #edf3f8;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ranking-site-icon {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.ranking-fallback {
  color: #fff;
  font-size: 16px;
  font-weight: 700;
}

.ranking-info {
  min-width: 0;
  flex: 1;
}

.ranking-info h4 {
  margin: 0 0 4px;
  font-size: 14px;
  color: #24384d;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.ranking-info p {
  margin: 0;
  font-size: 12px;
  line-height: 1.5;
  color: #7b8d9f;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.ranking-actions {
  display: flex;
  justify-content: flex-start;
  margin-top: 10px;
}

.ranking-collect {
  align-self: center;
}

.sidebar-ranking-direct-left {
  top: 50%;
  left: 8px;
  right: auto;
  bottom: auto;
  transform: translateY(-50%) translateX(-10px);
}

.ranking-item-wrap:hover .sidebar-ranking-direct-left,
.ranking-item-wrap:focus-within .sidebar-ranking-direct-left {
  opacity: 1;
  pointer-events: auto;
  transform: translateY(-50%) translateX(0);
}

.ranking-item-wrap .sidebar-ranking-direct-left.is-hidden {
  transform: translateY(-50%) translateX(-10px) !important;
}

:deep(.collect-guide-popper.el-popper) {
  border: none;
  border-radius: 16px;
  padding: 0;
  overflow: hidden;
  background: linear-gradient(180deg, #f7fbff 0%, #eef5fb 100%);
  box-shadow: 0 18px 40px rgba(8, 15, 23, 0.18);
}

:deep(.collect-guide-popper.el-popper .el-popper__arrow::before) {
  background: #f4f9fe;
  border: none;
}

.collect-guide {
  padding: 18px 20px;
  color: #284057;
}

.collect-guide-item + .collect-guide-item {
  margin-top: 16px;
}

.collect-guide-item h4 {
  margin: 0 0 8px;
  font-size: 15px;
  color: #4da0ff;
}

.collect-guide-item p {
  margin: 0;
  font-size: 13px;
  line-height: 1.7;
  color: #5f7388;
}

.collect-guide-item span {
  color: #3b90f2;
  font-weight: 700;
}

@media (max-width: 1200px) {
  .content-layout {
    grid-template-columns: minmax(0, 1fr);
  }

  .hot-strip-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .right-sidebar-inner {
    position: static;
  }
}

@media (max-width: 768px) {
  .hero-banner {
    min-height: 260px;
  }

  .hero-title {
    font-size: 24px;
  }

  .hero-stats {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 10px;
    width: 100%;
  }

  .hero-content {
    max-width: 100%;
    padding: 28px 16px 32px;
  }

  .search-box {
    width: 100%;
  }

  .search-tabs,
  .search-engines,
  .hot-strip-tabs,
  .ranking-tabs {
    justify-content: flex-start;
    flex-wrap: nowrap;
    overflow-x: auto;
    scrollbar-width: none;
    -ms-overflow-style: none;
  }

  .search-tabs::-webkit-scrollbar,
  .search-engines::-webkit-scrollbar,
  .hot-strip-tabs::-webkit-scrollbar,
  .ranking-tabs::-webkit-scrollbar {
    display: none;
  }

  .search-tab,
  .engine-item,
  .hot-strip-tab,
  .ranking-tab {
    flex: 0 0 auto;
  }

  .search-tab {
    padding: 5px 12px;
    font-size: 13px;
  }

  .search-input-wrapper {
    border-radius: 14px;
  }

  .search-input {
    min-width: 0;
    padding: 12px 14px;
    font-size: 14px;
  }

  .nav-container {
    flex-direction: column;
    gap: 16px;
    padding: 0 12px 24px;
    margin-top: 18px;
  }

  .content-layout {
    gap: 18px;
  }

  .hot-strip {
    padding: 16px 14px 12px;
  }

  .hot-strip-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .hot-strip-tabs,
  .ranking-tabs {
    width: 100%;
    padding-bottom: 4px;
  }

  .hot-strip-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
  }

  .hot-strip-card {
    padding: 12px;
  }

  .nav-card {
    align-items: flex-start;
  }

  .card-actions,
  .ranking-actions {
    width: 100%;
  }

  .collect-action {
    width: 100%;
    justify-content: center;
  }

  .direct-link-chip {
    position: static;
    opacity: 1;
    pointer-events: auto;
    align-self: flex-end;
    transform: none !important;
    min-width: 68px;
    height: 30px;
    padding: 0 10px 0 8px;
    margin-top: 8px;
  }

  .hot-strip-card-wrap,
  .nav-card-wrap,
  .ranking-item-wrap {
    display: flex;
    flex-direction: column;
  }

  .hot-strip-card-wrap .direct-link-chip,
  .hot-strip-card-wrap .direct-link-chip.is-hidden,
  .sidebar-ranking-direct-left,
  .ranking-item-wrap .sidebar-ranking-direct-left.is-hidden {
    transform: none !important;
    left: auto;
    right: auto;
    top: auto;
    bottom: auto;
  }

  .collect-action {
    padding: 5px 8px;
    font-size: 11px;
  }

  .sidebar-ranking-direct-left {
    left: 6px;
    min-width: 64px;
    height: 28px;
    padding: 0 8px 0 6px;
  }

  .hot-strip-copy h3 {
    font-size: 14px;
  }

  .hot-strip-copy p {
    font-size: 12px;
  }

  .nav-sidebar {
    width: 100%;
  }

  .sidebar-inner {
    position: static;
  }

  .sidebar-logo {
    display: none;
  }

  .category-menu {
    display: flex;
    overflow-x: auto;
    -ms-overflow-style: none;
    scrollbar-width: none;
  }

  .category-menu::-webkit-scrollbar {
    display: none;
  }

  :deep(.category-menu.el-menu) {
    width: max-content;
    min-width: 100%;
    border-right: none;
  }

  :deep(.category-menu .el-menu-item) {
    flex: 0 0 auto;
  }

  .nav-grid {
    grid-template-columns: repeat(auto-fill, minmax(100%, 1fr));
  }

  .brand-stats {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 576px) {
  .hero-stats {
    grid-template-columns: 1fr;
  }

  .hero-content {
    padding-inline: 12px;
  }

  .nav-container {
    padding: 0 10px 20px;
  }

  .hot-strip,
  .ranking-card,
  .brand-card,
  .search-result-hint {
    border-radius: 14px;
  }

  .hot-strip-grid {
    grid-template-columns: 1fr;
  }

  .hot-strip-card,
  .nav-card,
  .ranking-item {
    padding: 12px;
  }

  .nav-card {
    gap: 12px;
  }

  .section-title {
    margin-bottom: 12px;
  }

  .section-title h2 {
    font-size: 16px;
  }

  .search-result-hint {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .brand-highlight-value {
    font-size: 30px;
  }
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  align-self: flex-start;
  padding: 8px 14px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.14);
  border: 1px solid rgba(255, 255, 255, 0.18);
  color: rgba(255, 255, 255, 0.92);
  font-size: 12px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  margin-bottom: 14px;
}

.hero-stats {
  display: grid;
  grid-template-columns: repeat(2, minmax(220px, 280px));
  justify-content: center;
  gap: 16px;
  width: min(720px, 100%);
  margin: 22px auto 0;
}

.hero-stat {
  padding: 16px 18px;
  border-radius: 18px;
  background: rgba(10, 24, 42, 0.26);
  border: 1px solid rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(10px);
}

.hero-stat strong {
  display: block;
  font-size: 30px;
  line-height: 1;
  color: #fff;
}

.hero-stat span {
  display: block;
  margin-top: 8px;
  font-size: 12px;
  letter-spacing: 0.08em;
  color: rgba(255, 255, 255, 0.72);
}

.hero-banner {
  position: relative;
  overflow: hidden;
}

.hero-banner::before {
  content: '';
  position: absolute;
  inset: auto -8% -36% auto;
  width: 420px;
  height: 420px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.22) 0%, transparent 68%);
  pointer-events: none;
}

.hero-content {
  max-width: var(--app-content-width);
  margin: 0 auto;
  padding-inline: 28px;
}

.nav-container {
  max-width: var(--app-content-width);
  margin: 20px auto 0;
  padding: 0 20px 34px;
}

.sidebar-inner,
.category-section,
.search-result-hint {
  border-radius: 22px;
  border: 1px solid var(--app-border);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98) 0%, var(--app-bg-elevated) 100%);
  box-shadow: var(--app-shadow-sm);
}

.category-section {
  padding: 22px;
}

.section-title h2 {
  font-size: 21px;
  color: var(--app-text);
}

.brand-toolbar-more {
  font-size: 12px;
  color: var(--app-text-soft);
  font-weight: 600;
  letter-spacing: 0.08em;
}

.brand-highlight-value {
  color: var(--app-primary);
}

.category-menu {
  padding: 14px 10px;
}

:deep(.category-menu.el-menu) {
  border-right: none;
}

:deep(.category-menu .el-menu-item) {
  height: 42px;
  border-radius: 12px;
  margin-bottom: 6px;
}

:deep(.category-menu .el-menu-item.is-active) {
  background: var(--app-primary-soft);
  color: var(--app-primary);
}

.nav-card,
.ranking-item,
.hot-strip-card {
  border-radius: 18px;
}

.nav-card:hover,
.ranking-item:hover,
.hot-strip-card:hover {
  box-shadow: var(--app-shadow-sm);
}

@media (min-width: 1280px) {
  .hero-content {
    padding-inline: 24px;
  }

  .nav-container {
    margin-top: 24px;
    padding: 0 18px 40px;
  }

  .content-layout {
    grid-template-columns: minmax(0, 1fr) 340px;
    gap: 24px;
  }

  .nav-grid {
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 18px;
  }

  .hot-strip-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

.home-page.dark-theme {
  background-color: var(--app-bg);
}

.home-page.dark-theme .hero-banner {
  background: linear-gradient(135deg, #08111c 0%, #0d1a2a 40%, #10243d 72%, #0b1522 100%);
}

.home-page.dark-theme .sidebar-inner,
.home-page.dark-theme .search-result-hint,
.home-page.dark-theme .side-card,
.home-page.dark-theme .category-section,
.home-page.dark-theme .nav-card,
.home-page.dark-theme .ranking-item {
  background: var(--app-bg-elevated);
  border-color: var(--app-border);
  box-shadow: var(--app-shadow);
}

.home-page.dark-theme .hot-strip.side-card {
  background: linear-gradient(180deg, #171b20 0%, #111418 100%);
  border-color: #252b33;
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.32);
}

.home-page.dark-theme .hot-strip-title,
.home-page.dark-theme .hot-strip-copy h3 {
  color: #eef3f8;
}

.home-page.dark-theme .hot-strip-tab {
  color: #7d8793;
}

.home-page.dark-theme .hot-strip-tab::after {
  color: #4b5560;
}

.home-page.dark-theme .hot-strip-tab:hover,
.home-page.dark-theme .hot-strip-tab.active {
  color: #64bbff;
}

.home-page.dark-theme .hot-strip-card {
  background: linear-gradient(180deg, #303236 0%, #2a2c30 100%);
  border-color: #2a323b;
  box-shadow: 0 12px 26px rgba(0, 0, 0, 0.22);
}

.home-page.dark-theme .hot-strip-card:hover {
  background: linear-gradient(180deg, #37393d 0%, #313338 100%);
  border-color: #385065;
}

.home-page.dark-theme .hot-strip-icon {
  background: #1d1f23;
}

.home-page.dark-theme .hot-strip-copy p,
.home-page.dark-theme .hot-strip-more {
  color: #93a0ad;
}

.home-page.dark-theme .collect-action {
  background: rgba(108, 182, 255, 0.12);
  border-color: rgba(108, 182, 255, 0.2);
  color: #8cc5ff;
}

.home-page.dark-theme .direct-link-chip:hover {
  color: #8cc5ff;
}

.home-page.dark-theme .collect-action:hover:not(:disabled) {
  background: rgba(108, 182, 255, 0.18);
  border-color: rgba(108, 182, 255, 0.3);
}

.home-page.dark-theme .sidebar-logo,
.home-page.dark-theme .section-title h2,
.home-page.dark-theme .site-title,
.home-page.dark-theme .brand-copy h3,
.home-page.dark-theme .ranking-title,
.home-page.dark-theme .ranking-info h4 {
  color: var(--app-text);
}

.home-page.dark-theme .brand-copy p,
.home-page.dark-theme .site-desc,
.home-page.dark-theme .ranking-info p,
.home-page.dark-theme .search-result-hint,
.home-page.dark-theme .brand-highlight-label,
.home-page.dark-theme .brand-stat span,
.home-page.dark-theme .ranking-tab,
.home-page.dark-theme .site-meta {
  color: var(--app-text-soft);
}

.home-page.dark-theme .search-input-wrapper {
  background: rgba(17, 27, 39, 0.92);
  border-color: rgba(108, 182, 255, 0.14);
}

.home-page.dark-theme .search-input {
  color: var(--app-text);
}

.home-page.dark-theme .search-input::placeholder {
  color: var(--app-text-soft);
}

.home-page.dark-theme .search-tab:hover,
.home-page.dark-theme .engine-item.active,
.home-page.dark-theme .engine-item:hover {
  background: rgba(255, 255, 255, 0.08);
}

.home-page.dark-theme .category-menu .el-menu-item.is-active {
  background-color: rgba(108, 182, 255, 0.14);
  color: #7fc0ff;
  border-right-color: #7fc0ff;
}

.home-page.dark-theme .card-icon-wrapper,
.home-page.dark-theme .ranking-icon,
.home-page.dark-theme .brand-stat,
.home-page.dark-theme .user-info {
  background: #1a2837;
  border-color: var(--app-border);
}

.home-page.dark-theme .ranking-item:hover,
.home-page.dark-theme .nav-card:hover {
  background: #1a2837;
}

.home-page.dark-theme .brand-toolbar-more {
  color: var(--app-text-soft);
}

.home-page.dark-theme .brand-toolbar-plus {
  background: #162230;
  color: #dbe7f4;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.28);
}

.home-page.dark-theme :deep(.collect-guide-popper.el-popper) {
  background: linear-gradient(180deg, rgba(31, 46, 61, 0.98) 0%, rgba(22, 31, 43, 0.98) 100%);
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.42);
}

.home-page.dark-theme :deep(.collect-guide-popper.el-popper .el-popper__arrow::before) {
  background: rgba(29, 42, 56, 0.98);
}

.home-page.dark-theme .collect-guide {
  color: #e5edf7;
}

.home-page.dark-theme .collect-guide-item h4 {
  color: #8ec9ff;
}

.home-page.dark-theme .collect-guide-item p {
  color: rgba(229, 237, 247, 0.82);
}

.home-page.dark-theme .collect-guide-item span {
  color: #66b8ff;
}

.home-page.dark-theme .nav-card {
  box-shadow: 0 16px 30px rgba(0, 0, 0, 0.24);
}

.home-page.dark-theme .nav-card:hover {
  box-shadow: 0 20px 38px rgba(0, 0, 0, 0.32);
}

.home-page.dark-theme .brand-highlight {
  background: linear-gradient(135deg, rgba(39, 97, 172, 0.26) 0%, rgba(26, 53, 87, 0.42) 100%);
  border-color: rgba(108, 182, 255, 0.18);
}

.home-page.dark-theme .nav-container,
.home-page.dark-theme .content-layout {
  background: transparent;
}

.home-page.dark-theme .search-tab,
.home-page.dark-theme .engine-item {
  color: rgba(231, 238, 247, 0.72);
}

.home-page.dark-theme .hero-stat {
  background: rgba(8, 17, 28, 0.34);
  border-color: rgba(255, 255, 255, 0.12);
}

.home-page.dark-theme .sidebar-inner,
.home-page.dark-theme .category-section,
.home-page.dark-theme .search-result-hint {
  background: linear-gradient(180deg, rgba(17, 30, 47, 0.98) 0%, rgba(13, 23, 38, 0.98) 100%);
}

.home-page.dark-theme .ranking-tab.active,
.home-page.dark-theme .brand-highlight-value,
.home-page.dark-theme .ranking-index {
  color: #7fc0ff;
}

.home-page {
  --home-shell-width: 1840px;
  --home-sidebar-width: 244px;
  --home-right-width: 276px;
}

.hero-banner {
  min-height: 288px;
}

.hero-content {
  max-width: var(--home-shell-width);
  padding: 34px 18px 28px;
}

.hero-title {
  font-size: 36px;
  margin-bottom: 10px;
}

.hero-subtitle {
  max-width: 760px;
  margin: 0 auto 24px;
  font-size: 15px;
}

.hero-stats {
  width: min(620px, 100%);
  margin-top: 20px;
}

.search-box {
  width: min(1240px, 100%);
  margin: 0 auto;
}

.search-input-wrapper {
  min-height: 58px;
  border-radius: 16px;
}

.search-input {
  padding-inline: 24px;
  font-size: 16px;
}

.search-btn {
  width: 64px;
}

.nav-container {
  max-width: var(--home-shell-width);
  padding: 0 6px 42px;
  gap: 20px;
}

.nav-sidebar {
  width: var(--home-sidebar-width);
}

.content-layout {
  grid-template-columns: minmax(0, 1fr) var(--home-right-width);
  gap: 18px;
}

.nav-content {
  min-width: 0;
}

.hot-strip.side-card {
  padding: 16px 18px 10px;
}

.hot-strip-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.hot-strip-card {
  min-height: 110px;
}

.nav-grid {
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 18px;
}

@media (min-width: 1440px) {
  .content-layout {
    grid-template-columns: minmax(0, 1fr) 288px;
  }

  .hot-strip-grid {
    grid-template-columns: repeat(5, minmax(0, 1fr));
  }

  .nav-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

@media (max-width: 1360px) {
  .home-page {
    --home-right-width: 268px;
  }

  .hero-content {
    padding-inline: 16px;
  }

  .nav-container {
    padding-inline: 10px;
    gap: 18px;
  }

  .nav-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  }
}

@media (max-width: 1200px) {
  .home-page {
    --home-sidebar-width: 244px;
  }

  .nav-container {
    gap: 18px;
  }

  .hot-strip-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 960px) {
  .hero-banner {
    min-height: 264px;
  }

  .hero-content {
    padding: 28px 18px 30px;
  }

  .hero-title {
    font-size: 28px;
  }

  .hero-subtitle {
    margin-bottom: 20px;
  }

  .search-box,
  .hero-stats {
    width: 100%;
  }

  .nav-container {
    flex-direction: column;
  }

  .nav-sidebar {
    width: 100%;
  }

  .content-layout {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>
