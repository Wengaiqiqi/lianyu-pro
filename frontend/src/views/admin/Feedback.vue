<template>
  <div class="admin-feedback">
    <section class="page-hero compact-hero">
      <div>
        <h2>反馈管理</h2>
        <p>集中查看用户反馈、回复进度与处理状态，统一跟进问题闭环。</p>
      </div>
      <div class="filters">
        <el-select v-model="status" placeholder="状态筛选" clearable style="width: 160px" @change="handleFilterChange">
          <el-option label="待处理" value="pending" />
          <el-option label="已回复" value="replied" />
        </el-select>
        <el-input
          v-model="keyword"
          placeholder="搜索用户、标题或内容"
          clearable
          style="width: 260px"
          @keyup.enter="loadFeedbacks"
          @clear="handleFilterChange"
        >
          <template #append>
            <el-button @click="loadFeedbacks"><el-icon><Search /></el-icon></el-button>
          </template>
        </el-input>
      </div>
    </section>

    <el-table :data="feedbacks" stripe v-loading="loading">
      <el-table-column label="用户" min-width="140">
        <template #default="{ row }">
          <div class="user-cell">
            <el-avatar v-if="row.avatar" :src="row.avatar" :size="30" />
            <el-avatar v-else :size="30">{{ (row.nickname || row.username || 'U').charAt(0).toUpperCase() }}</el-avatar>
            <div>
              <div class="user-name">{{ row.nickname || row.username }}</div>
              <div class="user-sub">{{ row.username }}</div>
            </div>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="subject" label="反馈标题" min-width="180" />
      <el-table-column prop="contact" label="联系方式" min-width="140" />
      <el-table-column label="状态" width="120">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row)">{{ getStatusText(row) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="用户查收" width="100">
        <template #default="{ row }">
          <el-tag v-if="row.has_reply" :type="row.is_read_by_user ? 'info' : 'danger'">
            {{ row.is_read_by_user ? '已读' : '未读' }}
          </el-tag>
          <span v-else class="muted">-</span>
        </template>
      </el-table-column>
      <el-table-column label="更新时间" width="170">
        <template #default="{ row }">
          {{ formatTime(row.updated_at, true) }}
        </template>
      </el-table-column>
      <el-table-column label="消息数" width="90" align="center">
        <template #default="{ row }">
          {{ row.messages?.length || 0 }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="170" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openReplyDialog(row)">
            {{ row.has_reply ? '查看/回复' : '回复' }}
          </el-button>
          <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination" v-if="total > perPage">
      <el-pagination
        v-model:current-page="page"
        :page-size="perPage"
        :total="total"
        layout="prev, pager, next, total"
        @current-change="loadFeedbacks"
      />
    </div>

    <el-dialog v-model="dialogVisible" width="760px" destroy-on-close :title="currentItem?.subject || '反馈详情'">
      <template v-if="currentItem">
        <div class="dialog-meta">
          <span>用户：{{ currentItem.nickname || currentItem.username }}</span>
          <span v-if="currentItem.contact">联系方式：{{ currentItem.contact }}</span>
          <span>创建时间：{{ formatTime(currentItem.created_at, true) }}</span>
        </div>

        <div class="conversation-list">
          <article
            v-for="message in pagedAdminMessages"
            :key="message.id"
            :class="['message-item', `message-${message.sender_type}`]"
          >
            <div class="message-head">
              <span class="message-author">
                {{ message.sender_type === 'admin' ? (message.sender_name || '管理员') : (currentItem.nickname || currentItem.username || '用户') }}
              </span>
              <span class="message-time">{{ formatTime(message.created_at, true) }}</span>
            </div>
            <p>{{ message.content }}</p>
          </article>
        </div>

        <div class="pagination-wrap" v-if="totalAdminMessages > adminMessagePageSize">
          <el-pagination
            v-model:current-page="adminMessagePage"
            :page-size="adminMessagePageSize"
            :total="totalAdminMessages"
            layout="prev, pager, next"
            @current-change="() => {}"
          />
        </div>

        <el-form label-position="top" class="reply-form">
          <el-form-item label="回复内容">
            <el-input
              v-model="replyForm.reply"
              type="textarea"
              :rows="7"
              maxlength="5000"
              show-word-limit
              placeholder="输入回复内容，保存后会追加到会话记录"
            />
          </el-form-item>
        </el-form>
      </template>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="replyLoading" @click="handleReply">发送回复</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { deleteAdminFeedback, getAdminFeedbacks, replyAdminFeedback } from '@/api/feedback'

const loading = ref(false)
const replyLoading = ref(false)
const feedbacks = ref([])
const keyword = ref('')
const status = ref('')
const page = ref(1)
const perPage = 10
const total = ref(0)

const dialogVisible = ref(false)
const currentItem = ref(null)
const replyForm = reactive({
  reply: '',
})
const adminMessagePage = ref(1)
const adminMessagePageSize = 5

const pagedAdminMessages = computed(() => {
  if (!currentItem.value) return []
  const messages = currentItem.value.messages || []
  const start = (adminMessagePage.value - 1) * adminMessagePageSize
  return messages.slice(start, start + adminMessagePageSize)
})

const totalAdminMessages = computed(() => {
  return (currentItem.value?.messages || []).length
})

function formatTime(value, withTime = false) {
  if (!value) return ''
  const dateStr = value.endsWith('Z') ? value : value + 'Z'
  const date = new Date(dateStr)
  if (isNaN(date.getTime())) return ''
  return date.toLocaleString('zh-CN', withTime ? {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  } : {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  })
}

function getStatusText(row) {
  if (!row.has_reply) return '待首次回复'
  if (row.status === 'pending' && row.has_user_reply) return '用户已回信'
  return '已回复'
}

function getStatusType(row) {
  if (!row.has_reply) return 'warning'
  if (row.status === 'pending' && row.has_user_reply) return 'danger'
  return 'success'
}

async function loadFeedbacks() {
  loading.value = true
  try {
    const res = await getAdminFeedbacks({
      page: page.value,
      per_page: perPage,
      keyword: keyword.value,
      status: status.value,
    })
    feedbacks.value = res.data?.items || []
    total.value = Number(res.data?.total || 0)
  } finally {
    loading.value = false
  }
}

function handleFilterChange() {
  page.value = 1
  loadFeedbacks()
}

function openReplyDialog(row) {
  currentItem.value = row
  replyForm.reply = ''
  dialogVisible.value = true
}

function syncCurrentItem() {
  if (!currentItem.value) return
  const latest = feedbacks.value.find(item => item.id === currentItem.value.id)
  if (latest) {
    currentItem.value = latest
  }
}

async function handleReply() {
  if (!currentItem.value) return
  if (!replyForm.reply.trim()) {
    ElMessage.warning('请输入回复内容')
    return
  }
  replyLoading.value = true
  try {
    await replyAdminFeedback(currentItem.value.id, { reply: replyForm.reply })
    ElMessage.success('回复已发送')
    await loadFeedbacks()
    syncCurrentItem()
    replyForm.reply = ''
  } finally {
    replyLoading.value = false
  }
}

async function handleDelete(row) {
  await ElMessageBox.confirm('确定删除吗？', '删除反馈', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消',
  })

  await deleteAdminFeedback(row.id)
  if (currentItem.value?.id === row.id) {
    dialogVisible.value = false
    currentItem.value = null
  }
  ElMessage.success('反馈已删除')
  await loadFeedbacks()
}

onMounted(loadFeedbacks)
</script>

<style scoped>
.compact-hero {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-name {
  color: var(--app-text);
  font-weight: 600;
}

.user-sub,
.muted {
  color: var(--app-text-soft);
  font-size: 12px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.dialog-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
  color: var(--app-text-soft);
  font-size: 13px;
}

.conversation-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}

.message-item {
  padding: 14px;
  border-radius: 12px;
  border: 1px solid var(--app-border);
}

.message-user {
  background: rgba(64, 158, 255, 0.06);
  border-color: rgba(64, 158, 255, 0.12);
}

.message-admin {
  background: rgba(103, 194, 58, 0.08);
  border-color: rgba(103, 194, 58, 0.14);
}

.message-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
}

.message-author {
  font-size: 13px;
  font-weight: 600;
  color: var(--app-text);
}

.message-time {
  font-size: 12px;
  color: var(--app-text-soft);
}

.message-item p {
  margin: 0;
  line-height: 1.7;
  color: var(--app-text);
  white-space: pre-wrap;
  word-break: break-word;
}

@media (max-width: 768px) {
  .compact-hero {
    flex-direction: column;
    align-items: stretch;
  }

  .filters {
    width: 100%;
  }

  .message-head {
    flex-direction: column;
  }
}
</style>
