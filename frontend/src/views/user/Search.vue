<template>
  <div class="search-page" :class="{ 'dark-theme': theme === 'dark' }">
    <section class="page-hero compact-hero">
      <div>
        <h2>{{ heroTitle }}</h2>
        <p>{{ heroDescription }}</p>
      </div>
    </section>
    <div class="search-bar">
      <el-input
        v-model="keyword"
        placeholder="输入关键词搜索标题、描述或URL..."
        size="large"
        clearable
        @keyup.enter="handleSearch"
        @clear="results = []; total = 0"
      >
        <template #append>
          <el-button :loading="loading" @click="handleSearch">
            <el-icon><Search /></el-icon> 搜索
          </el-button>
        </template>
      </el-input>
    </div>

    <div class="search-results" v-if="searched">
      <p class="result-count" v-if="total > 0">共找到 {{ total }} 条结果</p>
      <el-empty v-if="!loading && results.length === 0 && searched" description="未找到相关收藏" />

      <div class="result-list">
        <el-card v-for="item in results" :key="item.id" shadow="hover" class="result-card">
          <div class="result-header">
            <img v-if="item.favicon" :src="item.favicon" class="favicon" alt="" />
            <el-icon v-else color="#409eff"><Link /></el-icon>
            <a :href="item.url" target="_blank" class="result-title">{{ item.title }}</a>
            <el-tag v-if="item.category_name" size="small">{{ item.category_name }}</el-tag>
          </div>
          <p class="result-url">{{ item.url }}</p>
          <p class="result-desc" v-if="item.description">{{ item.description }}</p>
          <div class="result-footer">
            <button
              type="button"
              class="collect-action"
              :disabled="isCollecting(item)"
              @click="collectBookmark(item)"
            >
              {{ isCollecting(item) ? '加入中...' : '加入我的链域' }}
            </button>
            <span>收藏于 {{ new Date(item.created_at).toLocaleDateString('zh-CN') }}</span>
          </div>
        </el-card>
      </div>

      <div class="pagination" v-if="total > perPage">
        <el-pagination v-model:current-page="page" :page-size="perPage" :total="total" layout="prev, pager, next" @current-change="handleSearch" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { searchBookmarks } from '@/api/bookmark'
import { ElMessage } from 'element-plus'
import { useCollectBookmark } from '@/composables/useCollectBookmark'
import { useTheme } from '@/composables/useTheme'

const keyword = ref('')
const results = ref([])
const loading = ref(false)
const searched = ref(false)
const page = ref(1)
const perPage = 20
const total = ref(0)
const { theme } = useTheme()
const { collectBookmark, isCollecting } = useCollectBookmark()
const heroTitle = '\u5168\u5c40\u641c\u7d22'
const heroDescription = '\u6309\u6807\u9898\u3001\u63cf\u8ff0\u6216\u94fe\u63a5\u5730\u5740\u5feb\u901f\u68c0\u7d22\u6536\u85cf\u5185\u5bb9\uff0c\u7f29\u77ed\u67e5\u627e\u8def\u5f84\u3002'

async function handleSearch() {
  if (!keyword.value.trim()) {
    ElMessage.warning('请输入搜索关键词')
    return
  }
  loading.value = true
  searched.value = true
  try {
    const res = await searchBookmarks({ q: keyword.value.trim(), page: page.value, per_page: perPage })
    results.value = res.data.items
    total.value = res.data.total
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.search-page {
  max-width: var(--app-content-narrow);
  margin: 0 auto;
  padding: 6px 0 8px;
}

.page-header {
  margin-bottom: 22px;
  text-align: left;
  padding: 24px 28px;
  border: 1px solid var(--app-border);
  border-radius: 24px;
  background: linear-gradient(135deg, rgba(47, 128, 237, 0.1) 0%, rgba(255, 255, 255, 0.95) 58%, rgba(255, 255, 255, 0.98) 100%);
  box-shadow: var(--app-shadow-sm);
}

.page-header h2 { font-size: 30px; color: #333; }
.search-bar { margin: 0 0 24px; max-width: 860px; display: flex; justify-content: flex-start; }
.result-count { color: #666; margin-bottom: 18px; text-align: left; font-size: 14px; }
.result-list { display: grid; gap: 14px; }
.result-card { margin-bottom: 0; border-radius: 20px; }
.result-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}
.favicon { width: 18px; height: 18px; border-radius: 3px; }
.result-title {
  font-size: 15px;
  font-weight: 500;
  color: #333;
  text-decoration: none;
}
.result-title:hover { color: #409eff; }
.result-url { font-size: 12px; color: #67c23a; margin-bottom: 4px; }
.result-desc { font-size: 13px; color: #666; line-height: 1.5; }
.result-footer { font-size: 12px; color: #999; margin-top: 8px; display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.collect-action { border: 1px solid rgba(64, 158, 255, 0.24); background: rgba(64, 158, 255, 0.08); color: #409eff; border-radius: 999px; padding: 6px 10px; font-size: 12px; line-height: 1; cursor: pointer; transition: all 0.2s ease; }
.collect-action:hover:not(:disabled) { background: rgba(64, 158, 255, 0.14); border-color: rgba(64, 158, 255, 0.36); }
.collect-action:disabled { opacity: 0.65; cursor: wait; }
.pagination { text-align: center; margin-top: 26px; }

.search-page.dark-theme .page-header h2,
.search-page.dark-theme .result-title {
  color: var(--app-text);
}

.search-page.dark-theme .page-header {
  background: linear-gradient(135deg, rgba(114, 182, 255, 0.12) 0%, rgba(17, 30, 47, 0.96) 56%, rgba(13, 23, 38, 0.98) 100%);
}

.search-page.dark-theme .result-count,
.search-page.dark-theme .result-desc,
.search-page.dark-theme .result-footer {
  color: var(--app-text-soft);
}

.search-page.dark-theme .result-url {
  color: #7fc0ff;
}

.search-page.dark-theme .collect-action { background: rgba(108, 182, 255, 0.12); border-color: rgba(108, 182, 255, 0.2); color: #8cc5ff; }
.search-page.dark-theme .collect-action:hover:not(:disabled) { background: rgba(108, 182, 255, 0.18); border-color: rgba(108, 182, 255, 0.3); }

.search-page.dark-theme .result-card {
  background: var(--app-bg-elevated);
  border-color: var(--app-border);
}

.search-page.dark-theme :deep(.el-card__body) {
  background: var(--app-bg-elevated);
  color: var(--app-text);
}

.search-page.dark-theme :deep(.el-input-group__append) {
  background: transparent;
  border-color: var(--app-border);
  box-shadow: none;
  padding: 0;
  overflow: hidden;
}

.search-page.dark-theme :deep(.el-input__wrapper) {
  background: #162231;
  border-color: var(--app-border);
  box-shadow: none;
}

.search-page.dark-theme :deep(.el-input-group--append > .el-input__wrapper) {
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
}

.search-page.dark-theme :deep(.el-input-group__append .el-button) {
  margin: 0;
  border: none;
  border-radius: 0 8px 8px 0;
  background: linear-gradient(135deg, #2b78d0 0%, #3b90f2 100%);
  color: #fff;
  min-height: 40px;
  padding: 0 18px;
  box-shadow: none;
}

.search-page.dark-theme :deep(.el-input-group__append .el-button:hover),
.search-page.dark-theme :deep(.el-input-group__append .el-button:focus),
.search-page.dark-theme :deep(.el-input-group__append .el-button:active) {
  background: linear-gradient(135deg, #2b78d0 0%, #3b90f2 100%);
  color: #fff;
  box-shadow: none;
}

.search-page.dark-theme :deep(.el-input-group__append .el-button.is-disabled),
.search-page.dark-theme :deep(.el-input-group__append .el-button.is-loading) {
  background: linear-gradient(135deg, #2b78d0 0%, #3b90f2 100%);
  color: rgba(255, 255, 255, 0.92);
  opacity: 0.92;
}

@media (min-width: 1280px) {
  .search-page {
    max-width: 1360px;
  }

  .page-header {
    padding: 28px 32px;
  }

  .search-bar {
    max-width: 980px;
  }

  .result-card {
    box-shadow: var(--app-shadow-sm);
  }
}
</style>
