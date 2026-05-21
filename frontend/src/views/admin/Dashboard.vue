<template>
  <div class="admin-dashboard">
    <section class="page-hero admin-hero">
      <div>
        <h1>系统概览</h1>
        <p>集中查看平台用户、收藏内容、分类结构和近况变化。</p>
      </div>
      <div class="hero-pulse">
        <span>运营中</span>
        <strong>{{ stats.total_users || 0 }} 位用户</strong>
      </div>
    </section>

    <section class="metric-grid">
      <article class="metric-card page-card">
        <span>用户总数</span>
        <strong>{{ stats.total_users || 0 }}</strong>
        <p>平台当前累计注册用户</p>
      </article>
      <article class="metric-card page-card">
        <span>收藏总量</span>
        <strong>{{ stats.total_bookmarks || 0 }}</strong>
        <p>全部用户收录的网站数量</p>
      </article>
      <article class="metric-card page-card">
        <span>分类总数</span>
        <strong>{{ stats.total_categories || 0 }}</strong>
        <p>目前可用的导航分类规模</p>
      </article>
      <article class="metric-card page-card warning-card">
        <span>已屏蔽内容</span>
        <strong>{{ stats.blocked_bookmarks || 0 }}</strong>
        <p>被拦截或下线的内容数量</p>
      </article>
    </section>

    <section class="chart-grid">
      <el-card shadow="never" class="page-card">
        <template #header>
          <div class="section-head">
            <div>
              <strong>近 7 日用户增长</strong>
              <span>快速观察近期注册走势。</span>
            </div>
          </div>
        </template>
        <div ref="growthChartRef" class="chart-panel"></div>
      </el-card>

      <el-card shadow="never" class="page-card">
        <template #header>
          <div class="section-head">
            <div>
              <strong>收藏分类分布</strong>
              <span>掌握平台内容主要集中在哪些分类。</span>
            </div>
          </div>
        </template>
        <div ref="categoryChartRef" class="chart-panel"></div>
      </el-card>
    </section>

    <el-card shadow="never" class="page-card ranking-table">
      <template #header>
        <div class="section-head">
          <div>
            <strong>收藏排行 Top 10</strong>
            <span>展示当前收藏数量领先的用户。</span>
          </div>
        </div>
      </template>
      <el-table :data="stats.top_users || []" stripe>
        <el-table-column type="index" label="排名" width="70" />
        <el-table-column prop="username" label="用户名" min-width="160" />
        <el-table-column prop="count" label="收藏数量" width="140" align="center" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { nextTick, onMounted, ref } from 'vue'
import * as echarts from 'echarts'
import { getStatistics } from '@/api/admin'

const stats = ref({})
const growthChartRef = ref()
const categoryChartRef = ref()

function renderCharts() {
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark'
  const axisColor = isDark ? '#97abc1' : '#61748a'
  const splitColor = isDark ? 'rgba(151, 171, 193, 0.16)' : 'rgba(97, 116, 138, 0.14)'
  const textColor = isDark ? '#ecf3fb' : '#142033'

  if (growthChartRef.value && stats.value.user_growth?.length) {
    const growthChart = echarts.init(growthChartRef.value)
    growthChart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: 34, right: 20, top: 20, bottom: 30 },
      xAxis: {
        type: 'category',
        data: stats.value.user_growth.map(item => item.date.slice(5)),
        axisLine: { lineStyle: { color: splitColor } },
        axisLabel: { color: axisColor },
      },
      yAxis: {
        type: 'value',
        minInterval: 1,
        axisLine: { show: false },
        splitLine: { lineStyle: { color: splitColor } },
        axisLabel: { color: axisColor },
      },
      series: [{
        type: 'bar',
        data: stats.value.user_growth.map(item => item.count),
        itemStyle: {
          color: '#2f80ed',
          borderRadius: [10, 10, 0, 0],
        },
      }],
      textStyle: { color: textColor },
    })
    window.addEventListener('resize', () => growthChart.resize())
  }

  if (categoryChartRef.value && stats.value.category_distribution?.length) {
    const validData = stats.value.category_distribution
      .filter(item => item.count > 0)
      .map(item => ({ name: item.name, value: item.count }))

    const categoryChart = echarts.init(categoryChartRef.value)
    categoryChart.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
      color: ['#2f80ed', '#45b36b', '#f0a64b', '#7c8cff', '#de6b49', '#65b7ff'],
      textStyle: { color: textColor },
      series: [{
        type: 'pie',
        radius: ['38%', '68%'],
        itemStyle: {
          borderRadius: 10,
          borderColor: isDark ? '#111e2f' : '#fff',
          borderWidth: 3,
        },
        label: { formatter: '{b}\n{c} 项 ({d}%)' },
        data: validData,
      }],
    })
    window.addEventListener('resize', () => categoryChart.resize())
  }
}

onMounted(async () => {
  const res = await getStatistics()
  stats.value = res.data
  await nextTick()
  renderCharts()
})
</script>

<style scoped>
.admin-dashboard {
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.admin-hero {
  margin-bottom: 0;
}

.hero-pulse {
  padding: 18px 20px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.76);
  border: 1px solid rgba(220, 229, 240, 0.92);
}

.hero-pulse span {
  display: block;
  font-size: 12px;
  color: var(--app-text-soft);
}

.hero-pulse strong {
  display: block;
  margin-top: 8px;
  font-size: 26px;
  color: var(--app-text);
}

.metric-grid {
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
  font-size: 34px;
  line-height: 1;
  color: var(--app-text);
}

.metric-card p {
  margin-top: 12px;
  font-size: 13px;
  line-height: 1.7;
  color: var(--app-text-soft);
}

.warning-card strong {
  color: var(--app-danger);
}

.chart-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
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

.chart-panel {
  height: 320px;
}

.ranking-table {
  overflow: hidden;
}

@media (max-width: 1080px) {
  .metric-grid,
  .chart-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .metric-grid,
  .chart-grid {
    grid-template-columns: 1fr;
  }
}

:global(:root[data-theme='dark'] .admin-dashboard .hero-pulse) {
  background: rgba(17, 30, 47, 0.82);
  border-color: rgba(35, 52, 71, 0.9);
}
</style>
