<template>
  <div class="dashboard" v-loading="loading">
    <section class="page-hero dashboard-hero">
      <div>
        <h1>欢迎回来，{{ userStore.user?.nickname || userStore.user?.username }}</h1>
        <p>{{ greetingMessage }}</p>
      </div>
      <div class="hero-summary">
        <div class="summary-item">
          <strong>{{ stats.total_bookmarks }}</strong>
          <span>收藏总量</span>
        </div>
        <div class="summary-item">
          <strong>{{ stats.public_bookmarks }}</strong>
          <span>公开内容</span>
        </div>
      </div>
    </section>

    <section class="stats-grid">
      <article class="metric-card page-card">
        <span>收藏总量</span>
        <strong>{{ stats.total_bookmarks }}</strong>
        <p>沉淀你的常用网址资产</p>
      </article>
      <article class="metric-card page-card">
        <span>分类数量</span>
        <strong>{{ stats.total_categories }}</strong>
        <p>按主题整理导航内容</p>
      </article>
      <article class="metric-card page-card">
        <span>公开收藏</span>
        <strong>{{ stats.public_bookmarks }}</strong>
        <p>已对外展示的优质链接</p>
      </article>
      <article class="metric-card page-card">
        <span>关注人数</span>
        <strong>{{ stats.following_public_users }}</strong>
        <p>你正在关注的公开用户</p>
      </article>
    </section>

    <section class="content-grid">
      <el-card shadow="never" class="chart-card page-card">
        <template #header>
          <div class="section-head">
            <div>
              <strong>分类分布</strong>
              <span>查看当前收藏内容在不同分类中的占比。</span>
            </div>
          </div>
        </template>
        <div v-if="stats.total_bookmarks === 0" class="chart-empty">
          <el-empty description="暂无数据" />
        </div>
        <div v-else ref="chartRef" class="chart-panel"></div>
      </el-card>

      <el-card shadow="never" class="recent-card page-card">
        <template #header>
          <div class="section-head">
            <div>
              <strong>最近收藏</strong>
              <span>最近收录的网址会在这里持续更新。</span>
            </div>
          </div>
        </template>

        <div v-if="stats.recent_bookmarks?.length" class="recent-list">
          <div v-for="item in stats.recent_bookmarks" :key="item.id" class="recent-item">
            <div class="recent-title">
              <el-icon color="var(--app-primary)"><Link /></el-icon>
              <a :href="item.url" target="_blank" rel="noopener noreferrer">{{ item.title }}</a>
            </div>
            <span class="recent-time">{{ formatTime(item.created_at) }}</span>
          </div>
        </div>
        <el-empty v-else description="暂无收藏" :image-size="80" />
      </el-card>
    </section>

    <el-card shadow="never" class="follow-card page-card">
      <template #header>
        <div class="section-head">
          <div>
            <strong>已关注的公开用户</strong>
            <span>从你关注的公开空间里发现更多值得收藏的网站。</span>
          </div>
        </div>
      </template>

      <div v-if="followedUsers.length" class="follow-grid">
        <button
          v-for="user in followedUsers"
          :key="user.id"
          type="button"
          class="follow-user-card"
          @click="goToPublicUser(user)"
        >
          <div class="follow-user-top">
            <el-avatar v-if="user.avatar" :src="user.avatar" :size="46" />
            <el-avatar v-else :size="46" class="follow-avatar">
              {{ (user.nickname || user.username || 'U').charAt(0).toUpperCase() }}
            </el-avatar>
            <span class="follow-like">❤ {{ user.like_count || 0 }}</span>
          </div>
          <h3>{{ user.nickname || user.username }}</h3>
          <p>{{ user.nickname || user.username }}</p>
          <div class="follow-meta">
            <span>{{ user.public_count || 0 }} 个公开书签</span>
            <span>{{ user.follower_count || 0 }} 人关注</span>
          </div>
        </button>
      </div>
      <el-empty v-else description="你还没有关注公开用户" :image-size="80" />
    </el-card>

    <el-card shadow="never" class="ai-card page-card">
      <template #header>
        <div class="section-head">
          <div>
            <strong>AI 兴趣分析</strong>
            <span>根据你的收藏偏好，生成兴趣标签与站点推荐。</span>
          </div>
          <div class="section-actions">
            <span v-if="aiData.analyzed_at" class="analyzed-time">
              上次分析：{{ formatTime(aiData.analyzed_at) }}
            </span>
            <el-button size="small" :loading="aiLoading" @click="handleAnalyze">
              {{ aiData.analyzed_at ? '重新分析' : '开始分析' }}
            </el-button>
          </div>
        </div>
      </template>

      <div v-if="aiLoading" class="ai-loading">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>AI 正在分析你的收藏偏好并生成推荐内容...</span>
      </div>

      <template v-else-if="aiData.interests.length">
        <div class="interests-grid">
          <div v-for="item in aiData.interests" :key="item.tag" class="interest-item">
            <div class="interest-tag">{{ item.tag }}</div>
            <div class="interest-desc">{{ item.description }}</div>
            <div class="interest-count">相关收藏：{{ item.count }} 条</div>
          </div>
        </div>

        <div v-if="aiData.recommendations.length" class="recommendation-block">
          <div class="recommendation-head">
            <strong>AI 推荐网站</strong>
            <span>根据你的兴趣画像进行延展推荐。</span>
          </div>
          <div class="rec-grid">
            <div v-for="(item, idx) in aiData.recommendations" :key="idx" class="rec-item">
              <div class="rec-header">
                <a :href="item.url" target="_blank" rel="noopener noreferrer" class="rec-title">{{ item.title }}</a>
                <el-button link type="primary" size="small" @click="openUrl(item.url)">
                  <el-icon><TopRight /></el-icon>
                </el-button>
              </div>
              <div class="rec-url">{{ item.url }}</div>
              <div class="rec-desc">{{ item.description }}</div>
            </div>
          </div>
        </div>
      </template>

      <div v-else-if="aiError" class="ai-tip">
        <el-icon color="var(--app-warning)"><WarningFilled /></el-icon>
        <span>{{ aiError }}</span>
      </div>
      <div v-else class="ai-tip">
        <el-icon color="var(--app-text-soft)"><InfoFilled /></el-icon>
        <span>点击“开始分析”，让 AI 基于你的收藏习惯生成兴趣画像和网站推荐。</span>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { nextTick, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import {
  InfoFilled,
  Link,
  Loading,
  TopRight,
  WarningFilled,
} from '@element-plus/icons-vue'
import { analyzeInterests, getInterests } from '@/api/ai'
import { getFollowingPublicUsers, getUserStats } from '@/api/user'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const greetingMessage = '\u795d\u4f60\u6709\u6109\u5feb\u7684\u4e00\u5929\u3002'
const loading = ref(false)
const chartRef = ref()
const followedUsers = ref([])
const stats = ref({
  total_bookmarks: 0,
  total_categories: 0,
  public_bookmarks: 0,
  following_public_users: 0,
  category_stats: [],
  recent_bookmarks: [],
})

const aiLoading = ref(false)
const aiError = ref('')
const aiData = reactive({
  interests: [],
  recommendations: [],
  analyzed_at: null,
})

function formatTime(time) {
  if (!time) return ''
  const dateStr = time.endsWith('Z') ? time : `${time}Z`
  const date = new Date(dateStr)
  if (Number.isNaN(date.getTime())) return ''
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  })
}

function openUrl(url) {
  window.open(url, '_blank')
}

function goToPublicUser(user) {
  router.push({
    name: 'Public',
    query: { userId: String(user.id) },
  })
}

function renderChart() {
  if (!chartRef.value || !stats.value.category_stats?.length || stats.value.total_bookmarks === 0) return
  const chartData = stats.value.category_stats
    .filter(item => item.count > 0)
    .map(item => ({ name: item.name, value: item.count }))
  if (!chartData.length) return

  const isDark = document.documentElement.getAttribute('data-theme') === 'dark'
  const chart = echarts.init(chartRef.value)
  chart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    color: ['#2f80ed', '#45b36b', '#f0a64b', '#7c8cff', '#de6b49', '#65b7ff'],
    textStyle: {
      color: isDark ? '#ecf3fb' : '#142033',
    },
    series: [{
      type: 'pie',
      radius: ['44%', '72%'],
      itemStyle: {
        borderRadius: 10,
        borderColor: isDark ? '#111e2f' : '#fff',
        borderWidth: 3,
      },
      label: { show: true, formatter: '{b}\n{c} ({d}%)' },
      data: chartData,
    }],
  })
  window.addEventListener('resize', () => chart.resize())
}

async function loadSavedInterests() {
  try {
    const res = await getInterests()
    if (res.data) {
      aiData.interests = res.data.interests || []
      aiData.recommendations = res.data.recommendations || []
      aiData.analyzed_at = res.data.analyzed_at
    }
  } catch {
    // silent
  }
}

async function loadFollowedUsers() {
  try {
    const res = await getFollowingPublicUsers()
    followedUsers.value = res.data || []
  } catch {
    followedUsers.value = []
  }
}

async function handleAnalyze() {
  aiLoading.value = true
  aiError.value = ''
  try {
    const res = await analyzeInterests()
    if (res.data) {
      aiData.interests = res.data.interests || []
      aiData.recommendations = res.data.recommendations || []
      aiData.analyzed_at = res.data.analyzed_at
    }
    if (res.msg && !res.data?.interests?.length) {
      aiError.value = res.msg
    }
  } catch (error) {
    aiError.value = error.message || 'AI 分析失败'
  } finally {
    aiLoading.value = false
  }
}

onMounted(async () => {
  loading.value = true
  try {
    const res = await getUserStats()
    stats.value = res.data
    await nextTick()
    renderChart()
  } finally {
    loading.value = false
  }

  loadFollowedUsers()
  loadSavedInterests()
})
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.dashboard-hero {
  margin-bottom: 0;
}

.hero-summary {
  display: grid;
  grid-template-columns: repeat(2, minmax(120px, 1fr));
  gap: 12px;
}

.summary-item {
  padding: 16px 18px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.76);
  border: 1px solid rgba(220, 229, 240, 0.92);
}

.summary-item strong {
  display: block;
  font-size: 28px;
  color: var(--app-text);
}

.summary-item span {
  display: block;
  margin-top: 6px;
  font-size: 12px;
  color: var(--app-text-soft);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.metric-card {
  padding: 24px;
}

.metric-card span {
  font-size: 13px;
  color: var(--app-text-soft);
}

.metric-card strong {
  display: block;
  margin-top: 16px;
  font-size: 36px;
  line-height: 1;
  color: var(--app-text);
}

.metric-card p {
  margin-top: 12px;
  font-size: 13px;
  line-height: 1.7;
  color: var(--app-text-soft);
}

.content-grid {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 20px;
}

.section-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.section-head strong {
  display: block;
  font-size: 18px;
  color: var(--app-text);
}

.section-head span {
  display: block;
  margin-top: 6px;
  font-size: 13px;
  color: var(--app-text-soft);
}

.chart-panel,
.chart-empty {
  height: 320px;
}

.chart-empty {
  display: flex;
  align-items: center;
  justify-content: center;
}

.recent-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 320px;
}

.recent-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 0;
  border-bottom: 1px solid var(--app-border);
}

.recent-item:last-child {
  border-bottom: none;
}

.recent-title {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.recent-title a {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  text-decoration: none;
  color: var(--app-text);
}

.recent-title a:hover {
  color: var(--app-primary);
}

.recent-time {
  font-size: 12px;
  color: var(--app-text-soft);
}

.follow-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
}

.follow-user-card {
  border: 1px solid var(--app-border);
  background: linear-gradient(180deg, var(--app-bg-soft) 0%, var(--app-bg-elevated) 100%);
  border-radius: 18px;
  padding: 18px;
  text-align: left;
  cursor: pointer;
}

.follow-user-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--app-shadow-sm);
  border-color: rgba(47, 128, 237, 0.3);
}

.follow-user-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.follow-avatar {
  background: linear-gradient(135deg, #f08b44 0%, #cf5f37 100%);
  color: #fff;
  font-weight: 700;
}

.follow-like {
  font-size: 12px;
  color: #d95c5c;
  background: rgba(217, 92, 92, 0.12);
  border-radius: 999px;
  padding: 4px 10px;
}

.follow-user-card h3 {
  font-size: 17px;
  color: var(--app-text);
}

.follow-user-card p {
  margin-top: 6px;
  font-size: 13px;
  color: var(--app-text-soft);
}

.follow-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 14px;
}

.follow-meta span {
  font-size: 12px;
  color: var(--app-text-soft);
  background: var(--app-primary-soft);
  border-radius: 999px;
  padding: 6px 10px;
}

.section-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.analyzed-time {
  font-size: 12px;
  color: var(--app-text-soft);
}

.ai-loading,
.ai-tip {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 180px;
  color: var(--app-text-soft);
}

.ai-loading {
  color: var(--app-primary);
}

.interests-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.interest-item,
.rec-item {
  padding: 18px;
  border-radius: 18px;
  background: var(--app-bg-elevated);
  border: 1px solid var(--app-border);
}

.interest-tag {
  font-size: 16px;
  font-weight: 700;
  color: var(--app-primary);
}

.interest-desc,
.interest-count {
  margin-top: 8px;
  color: var(--app-text-soft);
  line-height: 1.7;
  font-size: 13px;
}

.recommendation-block {
  margin-top: 24px;
}

.recommendation-head strong {
  font-size: 18px;
  color: var(--app-text);
}

.recommendation-head span {
  display: block;
  margin-top: 6px;
  font-size: 13px;
  color: var(--app-text-soft);
}

.rec-grid {
  margin-top: 16px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.rec-item:hover,
.interest-item:hover {
  transform: translateY(-2px);
  box-shadow: var(--app-shadow-sm);
}

.rec-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.rec-title {
  min-width: 0;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  text-decoration: none;
  color: var(--app-text);
  font-weight: 600;
}

.rec-title:hover {
  color: var(--app-primary);
}

.rec-url,
.rec-desc {
  margin-top: 8px;
  font-size: 13px;
  color: var(--app-text-soft);
  line-height: 1.7;
}

@media (max-width: 1080px) {
  .stats-grid,
  .content-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .hero-summary,
  .stats-grid,
  .content-grid {
    grid-template-columns: 1fr;
  }

  .section-head,
  .section-actions {
    flex-direction: column;
    align-items: flex-start;
  }
}

:global(:root[data-theme='dark'] .dashboard .summary-item) {
  background: rgba(17, 30, 47, 0.82);
  border-color: rgba(35, 52, 71, 0.9);
}
</style>
