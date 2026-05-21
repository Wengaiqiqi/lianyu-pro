<template>
  <div class="admin-bookmarks">
    <section class="page-hero compact-hero">
      <div>
        <h2>内容管理</h2>
        <p>筛选、审核和维护全站公开收藏内容，快速处理异常链接。</p>
      </div>
      <div class="hero-summary">
        <span>{{ total }}</span>
        <small>当前记录</small>
      </div>
    </section>

    <section class="filter-panel page-card">
      <el-select v-model="statusFilter" placeholder="状态筛选" clearable style="width: 160px" @change="loadBookmarks">
        <el-option label="全部" value="" />
        <el-option label="正常" value="normal" />
        <el-option label="已屏蔽" value="blocked" />
      </el-select>
      <el-input v-model="keyword" placeholder="搜索标题或 URL" style="width: 320px" clearable @keyup.enter="loadBookmarks" @clear="loadBookmarks">
        <template #append>
          <el-button @click="loadBookmarks"><el-icon><Search /></el-icon></el-button>
        </template>
      </el-input>
    </section>

    <el-card shadow="never" class="page-card table-card">
      <el-table :data="bookmarks" stripe v-loading="loading">
        <el-table-column label="网站" min-width="300">
          <template #default="{ row }">
            <a :href="row.url" target="_blank" rel="noopener noreferrer" class="site-link">{{ row.title }}</a>
            <div class="site-url">{{ row.url }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="username" label="用户" width="120" />
        <el-table-column prop="category_name" label="分类" width="110" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.category_name" size="small">{{ row.category_name }}</el-tag>
            <span class="muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_blocked ? 'danger' : 'success'" size="small">
              {{ row.is_blocked ? '已屏蔽' : '正常' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="visits" label="访问" width="90" align="center">
          <template #default="{ row }">
            <span class="visit-count">{{ row.visits || 0 }}</span>
          </template>
        </el-table-column>
        <el-table-column label="时间" width="120" align="center">
          <template #default="{ row }">
            {{ new Date(row.created_at).toLocaleDateString('zh-CN') }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button link :type="row.is_blocked ? 'success' : 'warning'" @click="handleToggleBlock(row.id)">
              {{ row.is_blocked ? '取消屏蔽' : '屏蔽' }}
            </el-button>
            <el-popconfirm title="确定删除该网站吗？" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button link type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination" v-if="total > perPage">
        <el-pagination v-model:current-page="page" :page-size="perPage" :total="total" layout="prev, pager, next, total" @current-change="loadBookmarks" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getAllBookmarks, toggleBlockBookmark, adminDeleteBookmark } from '@/api/admin'

const bookmarks = ref([])
const loading = ref(false)
const keyword = ref('')
const statusFilter = ref('')
const page = ref(1)
const perPage = 20
const total = ref(0)

async function loadBookmarks() {
  loading.value = true
  try {
    const res = await getAllBookmarks({ page: page.value, per_page: perPage, keyword: keyword.value, status: statusFilter.value })
    bookmarks.value = res.data.items
    total.value = res.data.total
  } finally {
    loading.value = false
  }
}

async function handleToggleBlock(id) {
  await toggleBlockBookmark(id)
  ElMessage.success('操作成功')
  loadBookmarks()
}

async function handleDelete(id) {
  await adminDeleteBookmark(id)
  ElMessage.success('删除成功')
  loadBookmarks()
}

onMounted(loadBookmarks)
</script>

<style scoped>
.admin-bookmarks {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.compact-hero {
  margin-bottom: 0;
  padding-block: 24px;
}

.hero-summary {
  min-width: 120px;
  padding: 18px 20px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.74);
  border: 1px solid rgba(220, 229, 240, 0.92);
  text-align: center;
}

.hero-summary span {
  display: block;
  font-size: 30px;
  font-weight: 700;
  color: var(--app-text);
}

.hero-summary small {
  display: block;
  margin-top: 8px;
  color: var(--app-text-soft);
  font-size: 12px;
}

.filter-panel {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px;
  flex-wrap: wrap;
}

.table-card {
  overflow: hidden;
}

.site-link {
  color: var(--app-text);
  text-decoration: none;
  font-weight: 600;
}

.site-link:hover {
  color: var(--app-primary);
}

.site-url {
  margin-top: 6px;
  font-size: 12px;
  color: var(--app-text-soft);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 360px;
}

.muted {
  color: var(--app-text-muted);
}

.visit-count {
  color: #de6b49;
  font-weight: 700;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 22px;
}

@media (max-width: 768px) {
  .filter-panel {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
