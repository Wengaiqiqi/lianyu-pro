<template>
  <div class="go-page" :class="{ 'dark-theme': theme === 'dark' }">
    <div class="go-frame">
      <section class="go-hero">
      <div class="hero-orb orb-left"></div>
      <div class="hero-orb orb-right"></div>
      <div class="hero-shell">
        <div class="hero-copy">
          <span class="hero-tag">链域安全中转</span>
          <h1>{{ bookmark?.title || '正在加载站点信息' }}</h1>
        </div>
      </div>
      </section>

      <div class="go-shell" v-loading="loading">
      <el-empty v-if="!loading && !bookmark" description="未找到该站点或该内容暂不可访问" />

      <div v-else-if="bookmark" class="go-layout">
        <main class="primary-panel">
          <section class="site-card">
            <div class="site-head">
              <div class="site-brand">
                <div class="site-icon-wrap">
                  <img v-if="bookmark.favicon" :src="bookmark.favicon" :alt="bookmark.title" class="site-icon" @error="handleImageError" />
                  <span v-else class="site-fallback">{{ fallbackLetter }}</span>
                </div>
                <div class="site-copy">
                  <p class="site-kicker">{{ bookmark.category_name || '外部站点' }}</p>
                  <h2>{{ bookmark.title }}</h2>
                  <p class="site-desc">{{ bookmark.description || '该站点暂未填写简介，点击继续访问后会前往原始地址。' }}</p>
                </div>
              </div>
            </div>

            <div class="meta-grid">
              <div class="meta-item">
                <span>目标域名</span>
                <strong>{{ domain }}</strong>
              </div>
              <div class="meta-item">
                <span>收录分类</span>
                <strong>{{ bookmark.category_name || '未分类' }}</strong>
              </div>
              <div class="meta-item">
                <span>累计访问</span>
                <strong>{{ bookmark.visits || 0 }}</strong>
              </div>
              <div class="meta-item">
                <span>最近更新</span>
                <strong>{{ formatDateTime(bookmark.updated_at) }}</strong>
              </div>
            </div>

            <div class="address-box">
              <span class="address-label">外部地址</span>
              <p :title="safeUrl">{{ safeUrl }}</p>
            </div>

            <div class="action-row">
              <button type="button" class="primary-btn" :disabled="jumping" @click="openTarget">
                {{ jumping ? '正在跳转...' : '继续访问目标站点' }}
              </button>
              <button type="button" class="secondary-btn" @click="closeTransitTab">返回上一页</button>
            </div>
          </section>

          <section class="trend-card">
            <div class="trend-head">
              <div>
                <h3>近期日访问趋势</h3>
                <p>最近 7 天访问次数</p>
              </div>
              <div class="trend-total">{{ recentVisitTotal }}</div>
            </div>
            <StatsChart :option="trendOption" :height="240" />
          </section>

          <section class="notice-card">
            <div class="notice-head">
              <h3>访问提示</h3>
            </div>
            <ul class="notice-list">
              <li>目标页面属于第三方站点，页面内容与后续行为不受链域直接控制。</li>
              <li>如果目标页失效、跳转异常或内容变更，可返回后重新选择其他站点。</li>
              <li>建议先核对域名、简介和分类，再决定是否继续访问。</li>
            </ul>
          </section>
        </main>

        <aside class="secondary-panel">
          <section class="side-card">
            <div class="side-head center">
              <h3>站点摘要</h3>
            </div>
            <div class="summary-list">
              <div class="summary-item">
                <span>站点名称</span>
                <strong>{{ bookmark.title }}</strong>
              </div>
              <div class="summary-item">
                <span>发布来源</span>
                <strong>{{ bookmark.nickname || bookmark.username || '链域公共库' }}</strong>
              </div>
              <div class="summary-item">
                <span>首次收录</span>
                <strong>{{ formatDateTime(bookmark.created_at) }}</strong>
              </div>
            </div>
          </section>

          <section class="side-card" v-if="relatedItems.length">
            <div class="side-head center">
              <h3>同类站点</h3>
            </div>
            <a
              v-for="item in relatedItems"
              :key="item.id"
              :href="createTransitPath(item.id)"
              class="related-item"
            >
              <div class="related-icon">
                <img v-if="item.favicon" :src="item.favicon" :alt="item.title" @error="handleImageError" />
                <span v-else>{{ (item.title || 'U').charAt(0).toUpperCase() }}</span>
              </div>
              <div class="related-copy">
                <strong>{{ item.title }}</strong>
                <p>{{ item.description || item.url }}</p>
              </div>
            </a>
          </section>
        </aside>
      </div>
    </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { getPublicBookmarkDetail, getPublicBookmarks, getPublicBookmarkVisitTrend, incrementVisit } from '@/api/bookmark'
import StatsChart from '@/components/StatsChart.vue'
import { useTheme } from '@/composables/useTheme'
import { createTransitPath, normalizeExternalUrl } from '@/utils/transit'

const route = useRoute()
const router = useRouter()
const { theme } = useTheme()

const bookmark = ref(null)
const relatedItems = ref([])
const visitTrend = ref([])
const loading = ref(false)
const jumping = ref(false)

const safeUrl = computed(() => normalizeExternalUrl(bookmark.value?.url || ''))
const fallbackLetter = computed(() => (bookmark.value?.title || 'U').charAt(0).toUpperCase())
const recentVisitTotal = computed(() =>
  visitTrend.value.reduce((sum, item) => sum + Number(item.visits || 0), 0)
)
const domain = computed(() => {
  try {
    return new URL(safeUrl.value).host
  } catch {
    return '未知域名'
  }
})
const trendOption = computed(() => ({
  grid: { left: 16, right: 16, top: 28, bottom: 18, containLabel: true },
  tooltip: {
    trigger: 'axis',
    backgroundColor: theme.value === 'dark' ? '#162231' : '#ffffff',
    borderColor: theme.value === 'dark' ? '#223245' : '#dfe8f2',
    textStyle: { color: theme.value === 'dark' ? '#e7eef7' : '#1b2c40' },
  },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: visitTrend.value.map(item => item.date.slice(5)),
    axisLine: { lineStyle: { color: theme.value === 'dark' ? '#2b3a4d' : '#d7e3ef' } },
    axisLabel: { color: theme.value === 'dark' ? '#95a8bc' : '#6f8195' },
    axisTick: { show: false },
  },
  yAxis: {
    type: 'value',
    minInterval: 1,
    splitLine: { lineStyle: { color: theme.value === 'dark' ? '#223245' : '#edf2f7' } },
    axisLabel: { color: theme.value === 'dark' ? '#95a8bc' : '#6f8195' },
  },
  series: [
    {
      data: visitTrend.value.map(item => item.visits),
      type: 'line',
      smooth: true,
      symbolSize: 8,
      lineStyle: { width: 3, color: '#f08b44' },
      itemStyle: { color: '#f08b44' },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(240, 139, 68, 0.32)' },
            { offset: 1, color: 'rgba(240, 139, 68, 0.04)' },
          ],
        },
      },
    },
  ],
}))

function formatDateTime(value) {
  if (!value) return '暂无记录'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '暂无记录'
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function handleImageError(event) {
  event.target.style.display = 'none'
}

async function loadRelatedItems() {
  if (!bookmark.value?.category_id) {
    relatedItems.value = []
    return
  }

  try {
    const res = await getPublicBookmarks({
      page: 1,
      per_page: 8,
      category_id: bookmark.value.category_id,
    })
    relatedItems.value = (res.data?.items || [])
      .filter(item => item.id !== bookmark.value.id)
      .slice(0, 4)
  } catch {
    relatedItems.value = []
  }
}

async function loadVisitTrend() {
  if (!bookmark.value?.id) {
    visitTrend.value = []
    return
  }

  try {
    const res = await getPublicBookmarkVisitTrend(bookmark.value.id, { days: 7 })
    visitTrend.value = res.data?.items || []
  } catch {
    visitTrend.value = []
  }
}

async function loadBookmark() {
  loading.value = true
  bookmark.value = null
  relatedItems.value = []
  visitTrend.value = []
  jumping.value = false

  try {
    const res = await getPublicBookmarkDetail(route.params.id)
    bookmark.value = res.data || null
    await Promise.all([loadRelatedItems(), loadVisitTrend()])
  } catch (error) {
    console.error('加载中转页失败:', error)
    bookmark.value = null
  } finally {
    loading.value = false
  }
}

async function openTarget() {
  if (!bookmark.value || !safeUrl.value || jumping.value) return

  jumping.value = true

  try {
    await incrementVisit(bookmark.value.id)
    bookmark.value.visits = Number(bookmark.value.visits || 0) + 1
  } catch (error) {
    console.error('记录访问失败:', error)
  } finally {
    window.location.href = safeUrl.value
  }
}

function closeTransitTab() {
  window.close()

  window.setTimeout(() => {
    if (!window.closed) {
      router.back()
    }
  }, 120)
}

onMounted(loadBookmark)

watch(() => route.params.id, () => {
  loadBookmark()
})
</script>

<style scoped>
.go-page {
  min-height: calc(100vh - 60px);
  padding-top: 6px;
  background:
    radial-gradient(circle at top left, rgba(240, 139, 68, 0.1), transparent 34%),
    linear-gradient(180deg, #f5f9fd 0%, #eef4fa 34%, #f9fbfd 100%);
}

.go-frame {
  width: min(1320px, calc(100% - 24px));
  margin: 0 auto;
  overflow: hidden;
  border: 1px solid rgba(219, 229, 240, 0.95);
  border-radius: 34px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.94) 0%, rgba(243, 248, 253, 0.96) 100%);
  box-shadow: 0 24px 60px rgba(20, 45, 78, 0.08);
}

.go-hero {
  position: relative;
  overflow: hidden;
  padding: 42px 0 30px;
  background: linear-gradient(135deg, rgba(15, 35, 64, 0.98) 0%, rgba(21, 58, 98, 0.96) 52%, rgba(20, 89, 92, 0.92) 100%);
}

.hero-shell,
.go-shell {
  width: min(1120px, calc(100% - 40px));
  margin: 0 auto;
}

.hero-copy {
  position: relative;
  z-index: 1;
  max-width: 760px;
}

.hero-tag {
  display: inline-flex;
  align-items: center;
  min-height: 32px;
  padding: 0 14px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.12);
  color: rgba(255, 244, 227, 0.9);
  font-size: 12px;
  letter-spacing: 0.14em;
}

.hero-copy h1 {
  margin: 18px 0 0;
  font-size: clamp(32px, 4vw, 52px);
  line-height: 1.06;
  color: #fff8ef;
}

.hero-orb {
  position: absolute;
  border-radius: 999px;
  filter: blur(10px);
}

.orb-left {
  top: -100px;
  left: -80px;
  width: 280px;
  height: 280px;
  background: rgba(240, 139, 68, 0.16);
}

.orb-right {
  right: -100px;
  bottom: -120px;
  width: 360px;
  height: 360px;
  background: rgba(93, 197, 255, 0.14);
}

.go-shell {
  padding: 28px 0 44px;
}

.go-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.08fr) 340px;
  gap: 28px;
}

.primary-panel,
.secondary-panel {
  min-width: 0;
}

.site-card,
.trend-card,
.notice-card,
.side-card {
  border: 1px solid #e1eaf3;
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 18px 40px rgba(20, 45, 78, 0.08);
}

@media (min-width: 1280px) {
  .go-frame {
    width: min(1340px, calc(100% - 28px));
    border-radius: 38px;
  }

  .hero-shell {
    width: min(1140px, calc(100% - 56px));
  }

  .go-shell {
    width: min(1140px, calc(100% - 56px));
    padding-top: 34px;
  }

  .go-layout {
    grid-template-columns: minmax(0, 1.14fr) 360px;
    gap: 32px;
  }

  .site-card,
  .trend-card,
  .notice-card,
  .side-card {
    border-radius: 30px;
  }

  .site-copy h2 {
    font-size: 34px;
  }
}

.site-card,
.trend-card,
.notice-card {
  padding: 26px;
}

.site-head {
  display: flex;
  align-items: flex-start;
  gap: 18px;
}

.site-brand {
  display: flex;
  gap: 18px;
  min-width: 0;
}

.site-icon-wrap {
  width: 78px;
  height: 78px;
  border-radius: 22px;
  overflow: hidden;
  background: linear-gradient(135deg, #edf4fb 0%, #dbe8f6 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.site-icon {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.site-fallback {
  color: #26598f;
  font-size: 28px;
  font-weight: 700;
}

.site-copy {
  min-width: 0;
}

.site-kicker {
  margin: 0 0 8px;
  color: #d46d41;
  font-size: 12px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.site-copy h2 {
  margin: 0;
  font-size: 30px;
  line-height: 1.15;
  color: #18293c;
}

.site-desc {
  margin: 12px 0 0;
  color: #617284;
  font-size: 14px;
  line-height: 1.8;
}

.meta-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
  margin-top: 24px;
}

.meta-item {
  padding: 16px 18px;
  border-radius: 20px;
  background: linear-gradient(180deg, #f9fbfd 0%, #f1f6fb 100%);
  border: 1px solid #e6eef6;
}

.meta-item span,
.address-label,
.side-head span,
.summary-item span {
  display: block;
  color: #7d8e9f;
  font-size: 12px;
}

.meta-item strong,
.summary-item strong {
  display: block;
  margin-top: 8px;
  color: #18293c;
  font-size: 16px;
}

.address-box {
  margin-top: 18px;
  padding: 18px 20px;
  border-radius: 22px;
  border: 1px dashed #d7e3ef;
  background: #fbfdff;
}

.address-box p {
  margin: 8px 0 0;
  color: #36526e;
  font-size: 14px;
  line-height: 1.7;
  word-break: break-all;
}

.action-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-top: 22px;
}

.primary-btn,
.secondary-btn {
  min-height: 46px;
  padding: 0 18px;
  border-radius: 16px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.primary-btn {
  border: none;
  background: linear-gradient(135deg, #f08b44 0%, #d96a3f 100%);
  color: #fff;
  box-shadow: 0 14px 28px rgba(217, 106, 63, 0.24);
}

.secondary-btn {
  border: 1px solid #d6e1ec;
  background: #fff;
  color: #27435f;
}

.primary-btn:disabled {
  opacity: 0.72;
  cursor: wait;
}

.trend-card,
.notice-card {
  margin-top: 22px;
}

.trend-head,
.notice-head,
.side-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
}

.trend-head h3,
.notice-head h3,
.side-head h3 {
  margin: 0;
  color: #1a2a3d;
  font-size: 18px;
}

.trend-head p {
  margin: 6px 0 0;
  color: #7c8b99;
  font-size: 13px;
}

.trend-total {
  min-width: 56px;
  height: 56px;
  border-radius: 18px;
  background: linear-gradient(135deg, #fff2e8 0%, #fff8f2 100%);
  color: #d46d41;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 700;
}

.notice-list {
  margin: 14px 0 0;
  padding-left: 18px;
  color: #5f7286;
  line-height: 1.8;
}

.secondary-panel {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.side-card {
  padding: 20px;
}

.side-head.center {
  justify-content: center;
  text-align: center;
}

.summary-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 16px;
}

.summary-item {
  padding: 14px 16px;
  border-radius: 18px;
  background: #f7fbff;
  border: 1px solid #e6eef6;
}

.related-item {
  display: flex;
  gap: 12px;
  margin-top: 14px;
  padding: 14px;
  border-radius: 18px;
  background: #f8fbff;
  border: 1px solid #e4edf6;
  text-decoration: none;
  transition: transform 0.2s ease, border-color 0.2s ease;
}

.related-item:hover {
  transform: translateY(-2px);
  border-color: rgba(240, 139, 68, 0.4);
}

.related-icon {
  width: 42px;
  height: 42px;
  border-radius: 14px;
  background: linear-gradient(135deg, #2d7dd2 0%, #58a6ff 100%);
  color: #fff;
  font-size: 16px;
  font-weight: 700;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.related-icon img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.related-copy {
  min-width: 0;
}

.related-copy strong {
  display: block;
  color: #1b2c40;
  font-size: 14px;
}

.related-copy p {
  margin: 6px 0 0;
  color: #6c7d8e;
  font-size: 12px;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

@media (max-width: 1080px) {
  .go-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .go-frame {
    width: min(100%, calc(100% - 12px));
    border-radius: 26px;
  }

  .hero-shell,
  .go-shell {
    width: min(100%, calc(100% - 24px));
  }

  .go-hero {
    padding-top: 28px;
  }

  .site-card,
  .trend-card,
  .notice-card,
  .side-card {
    border-radius: 24px;
  }

  .site-card,
  .trend-card,
  .notice-card {
    padding: 18px;
  }

  .site-head,
  .site-brand,
  .trend-head {
    flex-direction: column;
  }

  .status-card {
    width: 100%;
    text-align: left;
  }

  .meta-grid {
    grid-template-columns: 1fr;
  }

  .action-row {
    flex-direction: column;
    align-items: stretch;
  }

  .primary-btn,
  .secondary-btn {
    width: 100%;
  }
}

.go-page.dark-theme {
  background:
    radial-gradient(circle at top left, rgba(240, 139, 68, 0.08), transparent 30%),
    linear-gradient(180deg, #0f1722 0%, #111b27 38%, #0f1722 100%);
  color: var(--app-text);
}

.go-page.dark-theme .go-frame {
  border-color: rgba(35, 52, 71, 0.9);
  background: linear-gradient(180deg, rgba(12, 21, 33, 0.94) 0%, rgba(10, 18, 29, 0.98) 100%);
  box-shadow: 0 28px 70px rgba(0, 0, 0, 0.28);
}

.go-page.dark-theme .go-hero {
  background: linear-gradient(135deg, #08111c 0%, #0d1a2a 44%, #12304b 74%, #0b1522 100%);
}

.go-page.dark-theme .site-card,
.go-page.dark-theme .trend-card,
.go-page.dark-theme .notice-card,
.go-page.dark-theme .side-card,
.go-page.dark-theme .meta-item,
.go-page.dark-theme .summary-item,
.go-page.dark-theme .related-item,
.go-page.dark-theme .address-box,
.go-page.dark-theme .secondary-btn {
  background: var(--app-bg-elevated);
  border-color: var(--app-border);
  color: var(--app-text);
  box-shadow: var(--app-shadow);
}

.go-page.dark-theme .site-copy h2,
.go-page.dark-theme .trend-head h3,
.go-page.dark-theme .notice-head h3,
.go-page.dark-theme .side-head h3,
.go-page.dark-theme .meta-item strong,
.go-page.dark-theme .summary-item strong,
.go-page.dark-theme .related-copy strong {
  color: var(--app-text);
}

.go-page.dark-theme .site-desc,
.go-page.dark-theme .trend-head p,
.go-page.dark-theme .notice-list,
.go-page.dark-theme .address-box p,
.go-page.dark-theme .related-copy p,
.go-page.dark-theme .meta-item span,
.go-page.dark-theme .summary-item span,
.go-page.dark-theme .side-head span,
.go-page.dark-theme .address-label {
  color: var(--app-text-soft);
}

.go-page.dark-theme .site-icon-wrap {
  background: #1a2837;
}

.go-page.dark-theme .site-fallback {
  color: #8cc5ff;
}

.go-page.dark-theme .primary-btn {
  box-shadow: 0 16px 30px rgba(0, 0, 0, 0.24);
}

.go-page.dark-theme .trend-total {
  background: rgba(240, 139, 68, 0.14);
  color: #ffb27a;
}

.go-page.dark-theme .related-item:hover {
  background: #1a2837;
}
</style>
