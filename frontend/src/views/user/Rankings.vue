<template>
  <div class="rankings-page" :class="{ 'dark-theme': theme === 'dark' }">
    <section class="page-hero compact-hero">
      <div>
        <h2>{{ heroTitle }}</h2>
        <p>{{ heroDescription }}</p>
      </div>
    </section>
    <el-card shadow="hover" class="rankings-card">
      <template #header>
        <div class="card-header">
          <div class="rankings-tabs">
            <span
              v-for="t in rankingTypes"
              :key="t.value"
              class="ranking-tab"
              :class="{ active: rankingType === t.value }"
              @click="switchRanking(t.value)"
            >
              <el-icon :size="16"><Top /></el-icon>
              {{ t.label }}
            </span>
          </div>
          <span class="rankings-tip">统计周期内访问量最高的 Top 50 网站</span>
        </div>
      </template>

      <div v-loading="loading" class="rankings-content">
        <el-empty v-if="!loading && rankingList.length === 0" description="暂无排行数据" />

        <div v-else class="rankings-list">
          <div
            v-for="(item, idx) in rankingList"
            :key="item.id"
            class="rank-item-wrap"
            @mouseleave="clearDirectLinkState(item.id)"
          >
            <a
              :href="createTransitPath(item.id)"
              target="_blank"
              rel="noopener noreferrer"
              class="rank-item"
            >
            <span class="rank-num" :class="{ gold: idx === 0, silver: idx === 1, bronze: idx === 2 }">
              {{ idx + 1 }}
            </span>
            <img v-if="item.favicon" :src="item.favicon" class="rank-icon" @error="handleImageError" />
            <el-avatar v-else :size="40" shape="square" class="rank-fallback">
              {{ (item.title || 'U').charAt(0) }}
            </el-avatar>
            <div class="rank-info">
              <span class="rank-title">{{ item.title }}</span>
              <span class="rank-url">{{ item.url }}</span>
              <span class="rank-category">
                <el-icon><Folder /></el-icon>
                {{ item.category_name || '未分类' }}
              </span>
            </div>
            <div class="rank-stats">
              <button
                type="button"
                class="collect-action"
                :disabled="isCollecting(item)"
                @click.stop.prevent="collectBookmark(item)"
              >
                {{ isCollecting(item) ? '加入中...' : '加入我的链域' }}
              </button>
              <span class="rank-visits">{{ item.visits || 0 }}</span>
              <span class="rank-label">次访问</span>
            </div>
            </a>
            <button
              type="button"
              :class="['direct-link-chip', { 'is-hidden': hiddenDirectLinkKey === item.id }]"
              @click.stop="openDirectUrl(item.id, item.url)"
            >
              <span class="direct-link-arrow">&gt;</span>
              <span>直达</span>
            </button>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getRankings } from '@/api/bookmark'
import { Top, Folder } from '@element-plus/icons-vue'
import { useCollectBookmark } from '@/composables/useCollectBookmark'
import { useTheme } from '@/composables/useTheme'
import { createTransitPath, normalizeExternalUrl } from '@/utils/transit'

const rankingType = ref('day')
const loading = ref(false)
const rankingList = ref([])
const hiddenDirectLinkKey = ref(null)
const { theme } = useTheme()
const { collectBookmark, isCollecting } = useCollectBookmark()
const heroTitle = '\u70ed\u95e8\u699c\u5355'
const heroDescription = '\u67e5\u770b\u8fd1\u671f\u8bbf\u95ee\u70ed\u5ea6\u66f4\u9ad8\u7684\u7ad9\u70b9\uff0c\u5feb\u901f\u53d1\u73b0\u5927\u5bb6\u5e38\u7528\u7684\u5185\u5bb9\u5165\u53e3\u3002'

const rankingTypes = [
  { label: '日榜', value: 'day' },
  { label: '周榜', value: 'week' },
  { label: '月榜', value: 'month' },
]

async function loadRankings() {
  loading.value = true
  try {
    const res = await getRankings(rankingType.value)
    rankingList.value = res.data || []
  } catch (error) {
    console.error('加载排行榜失败:', error)
    rankingList.value = []
  } finally {
    loading.value = false
  }
}

function switchRanking(type) {
  rankingType.value = type
  loadRankings()
}

function handleImageError(e) {
  e.target.style.display = 'none'
  const fallback = e.target.nextElementSibling
  if (fallback) fallback.style.display = 'flex'
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

onMounted(() => {
  loadRankings()
})
</script>

<style scoped>
.rankings-page {
  max-width: var(--app-content-wide);
  margin: 0 auto;
  padding: 12px 0 8px;
}

.page-header {
  text-align: left;
  margin-bottom: 24px;
  padding: 28px 30px;
  border: 1px solid var(--app-border);
  border-radius: 26px;
  background: linear-gradient(135deg, rgba(255, 118, 117, 0.08) 0%, rgba(255, 255, 255, 0.94) 56%, rgba(255, 255, 255, 0.98) 100%);
  box-shadow: var(--app-shadow-sm);
}

.page-header h1 {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 10px;
  font-size: 32px;
  color: #333;
  margin: 0 0 8px;
}

.page-header h1 .el-icon {
  color: #ff7675;
}

.page-header p {
  color: #909399;
  font-size: 14px;
  margin: 0;
}

.rankings-card :deep(.el-card__header) {
  padding: 16px 20px;
  border-bottom: 1px solid #f0f2f5;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
}

.rankings-tabs {
  display: flex;
  gap: 10px;
}

.ranking-tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 18px;
  border-radius: 20px;
  font-size: 14px;
  color: #666;
  cursor: pointer;
  transition: all 0.25s;
  background: #f5f7fa;
}

.ranking-tab:hover {
  color: #409eff;
  background: #e6f1fc;
}

.ranking-tab.active {
  color: #fff;
  background: linear-gradient(135deg, #409eff, #66b1ff);
  font-weight: 600;
}

.rankings-tip {
  font-size: 13px;
  color: #c0c4cc;
}

.rankings-content {
  min-height: 300px;
}

.rankings-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.rank-item-wrap {
  position: relative;
}

.rank-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px 54px;
  background: #fafbfc;
  border: 1px solid #f0f2f5;
  border-radius: 18px;
  text-decoration: none;
  transition: all 0.25s;
}

.rank-item:hover {
  transform: translateX(4px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  border-color: #409eff;
  background: #fff;
}

.direct-link-chip {
  position: absolute;
  left: 50%;
  bottom: 10px;
  transform: translateX(-50%) translateY(10px);
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
  transform: translateX(-50%) translateY(10px) !important;
}

.rank-item-wrap:hover .direct-link-chip,
.rank-item-wrap:focus-within .direct-link-chip {
  opacity: 1;
  pointer-events: auto;
  transform: translateX(-50%) translateY(0);
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

.rank-num {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 700;
  color: #909399;
  background: #f0f2f5;
  flex-shrink: 0;
}

.rank-num.gold {
  background: linear-gradient(135deg, #ffd32a, #ff9f1a);
  color: #fff;
}

.rank-num.silver {
  background: linear-gradient(135deg, #ced6e0, #a4b0be);
  color: #fff;
}

.rank-num.bronze {
  background: linear-gradient(135deg, #f78fb3, #f8a5c2);
  color: #fff;
}

.rank-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  object-fit: cover;
  flex-shrink: 0;
}

.rank-fallback {
  width: 40px;
  height: 40px;
  background-color: #409eff;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  flex-shrink: 0;
}

.rank-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.rank-title {
  font-size: 16px;
  color: #333;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.rank-url {
  font-size: 12px;
  color: #409eff;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.rank-category {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #c0c4cc;
}

.rank-stats {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  text-align: center;
  padding: 0 16px;
  border-left: 1px solid #f0f2f5;
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

.rank-visits {
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: #ff7675;
}

.rank-label {
  font-size: 12px;
  color: #c0c4cc;
}

@media (max-width: 768px) {
  .rankings-page {
    padding: 12px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .page-header h1 {
    font-size: 20px;
  }

  .page-header p {
    font-size: 13px;
  }

  .card-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }

  .rankings-tip {
    font-size: 12px;
  }

  .rankings-tabs {
    width: 100%;
    justify-content: space-between;
    overflow-x: auto;
    scrollbar-width: none;
  }

  .ranking-tab {
    padding: 6px 10px;
    font-size: 12px;
    flex-shrink: 0;
  }

  .rank-item-wrap {
    position: relative;
  }

  .rank-item {
    padding: 12px;
    gap: 10px;
    min-height: 80px;
  }

  .direct-link-chip {
    opacity: 1;
    pointer-events: auto;
    transform: none;
    position: absolute;
    bottom: 8px;
    right: 12px;
    left: auto;
    top: auto;
  }

  .direct-link-arrow {
    display: none;
  }

  .direct-link-chip span:last-child {
    display: inline;
  }

  .rank-num {
    width: 24px;
    height: 24px;
    font-size: 12px;
    flex-shrink: 0;
  }

  .rank-icon,
  .rank-fallback {
    width: 28px;
    height: 28px;
    flex-shrink: 0;
  }

  .rank-info {
    flex: 1;
    min-width: 0;
  }

  .rank-title {
    font-size: 14px;
  }

  .rank-category {
    display: none;
  }

  .rank-stats {
    padding: 0;
    margin-top: auto;
  }

  .collect-action {
    display: none;
  }

  .rank-visits {
    font-size: 16px;
  }

  .rank-label {
    display: none;
  }
}

@media (min-width: 1280px) {
  .rankings-page {
    max-width: var(--app-content-wide);
  }

  .rankings-card {
    box-shadow: var(--app-shadow-sm);
  }

  .rank-item {
    padding: 20px 24px 56px;
  }

  .rank-title {
    font-size: 17px;
  }
}

.rankings-page.dark-theme .page-header h1,
.rankings-page.dark-theme .rank-title {
  color: var(--app-text);
}

.rankings-page.dark-theme .page-header p,
.rankings-page.dark-theme .rank-category,
.rankings-page.dark-theme .rank-label,
.rankings-page.dark-theme .rankings-tip {
  color: var(--app-text-soft);
}

.rankings-page.dark-theme .ranking-tab {
  background: #1a2837;
  color: var(--app-text-soft);
}

.rankings-page.dark-theme .ranking-tab:hover {
  background: rgba(108, 182, 255, 0.14);
  color: #7fc0ff;
}

.rankings-page.dark-theme .rank-item {
  background: var(--app-bg-elevated);
  border-color: var(--app-border);
}

.rankings-page.dark-theme .rank-item:hover {
  background: #182434;
  border-color: #6cb6ff;
}

.rankings-page.dark-theme .rank-num {
  background: #1a2837;
  color: #a8b8c8;
}

.rankings-page.dark-theme .rank-stats {
  border-left-color: var(--app-border);
}

.rankings-page.dark-theme .collect-action {
  background: rgba(108, 182, 255, 0.12);
  border-color: rgba(108, 182, 255, 0.2);
  color: #8cc5ff;
}

.rankings-page.dark-theme .collect-action:hover:not(:disabled) {
  background: rgba(108, 182, 255, 0.18);
  border-color: rgba(108, 182, 255, 0.3);
}

.rankings-page.dark-theme .direct-link-chip:hover {
  color: #8cc5ff;
}
</style>
