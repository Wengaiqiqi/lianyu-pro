<template>
  <div class="admin-statistics">
    <section class="page-hero compact-hero">
      <div>
        <h2>数据统计与分析</h2>
        <p>查看用户、收藏、访问趋势与热门内容分布，辅助后台运营决策。</p>
      </div>
      <div class="hero-summary">
        <span>总用户数</span>
        <strong>{{ stats.total_users || 0 }} 位用户</strong>
      </div>
    </section>
    <h2 class="page-title">数据统计与分析</h2>

    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card blue">
          <div class="stat-number">{{ stats.total_users || 0 }}</div>
          <div class="stat-label">注册用户</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card green">
          <div class="stat-number">{{ stats.active_users || 0 }}</div>
          <div class="stat-label">活跃用户</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card orange">
          <div class="stat-number">{{ stats.total_bookmarks || 0 }}</div>
          <div class="stat-label">总收藏数</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card purple">
          <div class="stat-number">{{ stats.total_visits || 0 }}</div>
          <div class="stat-label">总访问量</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>用户增长趋势（近7天）</template>
          <div ref="growthRef" style="height: 350px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>热门收藏分类</template>
          <div ref="categoryRef" style="height: 350px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>用户收藏排行 Top 10</template>
          <el-table :data="stats.top_users || []" stripe>
            <el-table-column type="index" label="排名" width="70" />
            <el-table-column prop="username" label="用户名" />
            <el-table-column prop="count" label="收藏数" width="120" />
            <el-table-column label="占比" width="120">
              <template #default="{ row }">
                <el-progress :percentage="stats.total_bookmarks ? Math.round(row.count / stats.total_bookmarks * 100) : 0" />
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>热门网址排行 Top 10</template>
          <el-table :data="stats.top_bookmarks || []" stripe>
            <el-table-column type="index" label="排名" width="70" />
            <el-table-column prop="title" label="网站名称" min-width="150" />
            <el-table-column prop="visits" label="访问次数" width="100">
              <template #default="{ row }">
                <span style="color: #ff7675; font-weight: 600;">{{ row.visits || 0 }}</span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watchEffect } from 'vue'
import { getStatistics } from '@/api/admin'
import * as echarts from 'echarts'

const stats = ref({})
const growthRef = ref()
const categoryRef = ref()
let growthChart = null
let categoryChart = null

function renderCharts() {
  if (growthRef.value && stats.value.user_growth?.length) {
    if (!growthChart) {
      growthChart = echarts.init(growthRef.value)
    }
    growthChart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: stats.value.user_growth.map(d => d.date.slice(5)), axisTick: { alignWithLabel: true } },
      yAxis: { type: 'value', minInterval: 1 },
      series: [{
        type: 'line',
        data: stats.value.user_growth.map(d => d.count),
        smooth: true,
        areaStyle: { color: 'rgba(64, 158, 255, 0.15)' },
        lineStyle: { color: '#409eff', width: 2 },
        itemStyle: { color: '#409eff' },
      }],
      grid: { left: 40, right: 20, top: 20, bottom: 30 },
    })
  }

  if (categoryRef.value && stats.value.category_distribution?.length) {
    if (!categoryChart) {
      categoryChart = echarts.init(categoryRef.value)
    }
    const data = stats.value.category_distribution
    categoryChart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      xAxis: { type: 'category', data: data.map(d => d.name), axisLabel: { rotate: 30 } },
      yAxis: { type: 'value', minInterval: 1 },
      series: [{
        type: 'bar',
        data: data.map(d => d.count),
        itemStyle: {
          borderRadius: [4, 4, 0, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#67c23a' },
            { offset: 1, color: '#b3e19d' },
          ]),
        },
      }],
      grid: { left: 40, right: 20, top: 20, bottom: 50 },
    })
  }
}

window.addEventListener('resize', () => {
  growthChart?.resize()
  categoryChart?.resize()
})

onMounted(async () => {
  const res = await getStatistics()
  stats.value = res.data
  await nextTick()
  renderCharts()
})

watchEffect(() => {
  if (stats.value.category_distribution?.length) {
    nextTick(renderCharts)
  }
})
</script>

<style scoped>
.compact-hero { margin-bottom: 20px; }
.hero-summary {
  min-width: 160px;
  padding: 14px 18px;
  border: 1px solid var(--app-border);
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.7);
}
.hero-summary span {
  display: block;
  font-size: 12px;
  color: var(--app-text-soft);
}
.hero-summary strong {
  display: block;
  margin-top: 8px;
  font-size: 18px;
  color: var(--app-text);
}
.page-title { display: none; }
.stats-row { margin-bottom: 20px; }
.stat-card { text-align: center; padding: 12px 0; }
.stat-number { font-size: 32px; font-weight: 700; }
.stat-label { color: #999; margin-top: 4px; font-size: 14px; }
.stat-card.blue .stat-number { color: #409eff; }
.stat-card.green .stat-number { color: #67c23a; }
.stat-card.orange .stat-number { color: #e6a23c; }
.stat-card.purple .stat-number { color: #9c27b0; }
.stat-card.red .stat-number { color: #f56c6c; }
</style>
