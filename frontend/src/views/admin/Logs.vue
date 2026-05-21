<template>
  <div class="admin-logs">
    <section class="page-hero compact-hero">
      <div>
        <h2>操作日志审计</h2>
        <p>按操作类型、用户和时间范围查看系统行为轨迹，并支持批量清理普通日志。</p>
      </div>
      <div class="hero-summary">
        <span>{{ total }}</span>
        <small>日志总数</small>
      </div>
    </section>

    <section class="filter-panel page-card">
      <el-input v-model="filterAction" placeholder="操作类型" clearable @keyup.enter="handleSearch" @clear="handleSearch" />
      <el-input v-model="filterUsername" placeholder="用户名" clearable @keyup.enter="handleSearch" @clear="handleSearch">
        <template #append>
          <el-button @click="handleSearch">
            <el-icon><Search /></el-icon>
          </el-button>
        </template>
      </el-input>
      <el-button type="danger" @click="openRangeDeleteDialog">
        <el-icon><Delete /></el-icon>
        按时间删除
      </el-button>
    </section>

    <el-card shadow="never" class="page-card table-card">
      <div class="table-wrap">
        <el-table :data="logs" stripe v-loading="loading" @selection-change="handleSelectionChange">
          <el-table-column type="selection" width="50" :selectable="row => !row.is_admin_log" />
          <el-table-column prop="id" label="ID" width="78" />
          <el-table-column prop="username" label="用户" width="120" />
          <el-table-column prop="action" label="操作" min-width="150">
            <template #default="{ row }">
              <el-tag size="small" :type="getActionType(row.action)">{{ row.action }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="target_type" label="目标类型" width="120" />
          <el-table-column prop="detail" label="详情" min-width="320" show-overflow-tooltip />
          <el-table-column prop="ip_address" label="IP 地址" width="150" />
          <el-table-column label="时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="90" fixed="right">
            <template #default="{ row }">
              <el-button
                v-if="!row.is_admin_log && row.target_type !== 'system'"
                link
                type="danger"
                size="small"
                @click="handleDelete(row)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div class="table-footer">
        <div class="selection-info">
          <span v-if="selectedLogs.length > 0">已选择 {{ selectedLogs.length }} 条</span>
          <el-button v-if="selectedLogs.length > 0" type="danger" size="small" @click="handleBatchDelete">
            批量删除
          </el-button>
        </div>
        <div v-if="total > perPage" class="pagination">
          <el-pagination
            v-model:current-page="page"
            :page-size="perPage"
            :total="total"
            layout="prev, pager, next, total"
            @current-change="loadLogs"
          />
        </div>
      </div>
    </el-card>

    <el-dialog v-model="rangeDeleteDialogVisible" title="按时间范围删除日志" width="460px">
      <el-form label-position="top">
        <el-form-item label="选择时间范围">
          <el-date-picker
            v-model="deleteDateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            :shortcuts="dateRangeShortcuts"
            style="width: 100%"
          />
        </el-form-item>
        <el-alert type="warning" :closable="false">
          将删除时间范围内所有普通用户日志，管理员日志会始终保留，此操作不可恢复。
        </el-alert>
      </el-form>
      <template #footer>
        <el-button @click="rangeDeleteDialogVisible = false">取消</el-button>
        <el-button type="danger" :loading="rangeDeleteLoading" @click="handleRangeDelete">确认删除</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { Search, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getLogs, deleteLog, deleteLogsByDateRange } from '@/api/admin'

const logs = ref([])
const loading = ref(false)
const filterAction = ref('')
const filterUsername = ref('')
const page = ref(1)
const perPage = 20
const total = ref(0)
const selectedLogs = ref([])

const rangeDeleteDialogVisible = ref(false)
const deleteDateRange = ref(null)
const rangeDeleteLoading = ref(false)

const dateRangeShortcuts = [
  {
    text: '最近 7 天',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 7 * 24 * 60 * 60 * 1000)
      return [start, end]
    },
  },
  {
    text: '最近 30 天',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 30 * 24 * 60 * 60 * 1000)
      return [start, end]
    },
  },
  {
    text: '最近 90 天',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 90 * 24 * 60 * 60 * 1000)
      return [start, end]
    },
  },
]

function getActionType(action) {
  if (!action) return ''
  if (action.includes('删除') || action.includes('屏蔽') || action.includes('禁用') || action.includes('拒绝')) return 'danger'
  if (action.includes('登录') || action.includes('注册') || action.includes('启用') || action.includes('通过审核')) return 'success'
  if (action.includes('更新') || action.includes('编辑') || action.includes('修改') || action.includes('回复')) return 'warning'
  return 'info'
}

function formatDate(value) {
  if (!value) return '-'
  const dateStr = value.endsWith('Z') ? value : `${value}Z`
  const date = new Date(dateStr)
  if (Number.isNaN(date.getTime())) return '-'
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  })
}

function handleSearch() {
  page.value = 1
  loadLogs()
}

function handleSelectionChange(selection) {
  selectedLogs.value = selection
}

async function handleDelete(row) {
  await ElMessageBox.confirm('确定删除该日志吗？', '删除日志', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消',
  })
  await deleteLog(row.id)
  ElMessage.success('日志已删除')
  await loadLogs()
}

async function handleBatchDelete() {
  const ids = selectedLogs.value.map(item => item.id)
  await ElMessageBox.confirm(`确定批量删除选中的 ${ids.length} 条日志吗？`, '批量删除', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消',
  })
  await Promise.all(ids.map(id => deleteLog(id)))
  ElMessage.success('批量删除完成')
  selectedLogs.value = []
  await loadLogs()
}

function openRangeDeleteDialog() {
  deleteDateRange.value = null
  rangeDeleteDialogVisible.value = true
}

async function handleRangeDelete() {
  if (!deleteDateRange.value || deleteDateRange.value.length !== 2) {
    ElMessage.warning('请选择时间范围')
    return
  }
  const [startDate, endDate] = deleteDateRange.value
  await ElMessageBox.confirm(`确定删除 ${startDate} 至 ${endDate} 范围内的日志吗？`, '按时间范围删除', {
    type: 'warning',
    confirmButtonText: '确认删除',
    cancelButtonText: '取消',
  })
  rangeDeleteLoading.value = true
  try {
    const res = await deleteLogsByDateRange({
      start_date: startDate,
      end_date: endDate,
    })
    ElMessage.success(`已删除 ${res.data.deleted_count || 0} 条日志`)
    rangeDeleteDialogVisible.value = false
    await loadLogs()
  } finally {
    rangeDeleteLoading.value = false
  }
}

async function loadLogs() {
  loading.value = true
  try {
    const res = await getLogs({
      page: page.value,
      per_page: perPage,
      action: filterAction.value,
      username: filterUsername.value,
    })
    logs.value = res.data.items || []
    total.value = res.data.total || 0
  } finally {
    loading.value = false
  }
}

onMounted(loadLogs)
</script>

<style scoped>
.admin-logs {
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

.filter-panel :deep(.el-input) {
  width: 200px;
}

.table-card {
  overflow: hidden;
}

.table-wrap {
  overflow-x: auto;
}

.table-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 18px;
  gap: 16px;
  flex-wrap: wrap;
}

.selection-info {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--app-text-soft);
  font-size: 14px;
}

.pagination {
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 768px) {
  .filter-panel {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-panel :deep(.el-input) {
    width: 100%;
  }

  .table-footer {
    flex-direction: column;
    align-items: stretch;
  }

  .pagination {
    justify-content: center;
  }
}
</style>
