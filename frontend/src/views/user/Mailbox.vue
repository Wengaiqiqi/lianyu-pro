<template>
  <div class="mailbox-page">
    <section class="page-hero compact-hero">
      <div>
        <h2>我的信箱</h2>
        <p>集中查看管理员回复、系统通知和反馈往来记录。</p>
      </div>
      <el-button @click="loadMailbox">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </section>

    <el-card shadow="never" class="page-card mailbox-card" v-loading="loading">
      <el-empty v-if="!loading && letters.length === 0" description="暂时还没有收到信件" />

      <template v-else>
        <el-collapse v-model="activeNames" class="letter-collapse" @change="handleCollapseChange">
          <el-collapse-item
            v-for="item in pagedLetters"
            :key="item.id"
            :name="String(item.id)"
            class="letter-panel"
          >
            <template #title>
              <div class="letter-summary">
                <div class="letter-summary-main">
                  <h3>{{ item.subject }}</h3>
                  <div class="letter-meta">
                    <span>更新时间：{{ formatTime(item.updated_at, true) }}</span>
                    <span>消息数：{{ item.messages?.length || 0 }}</span>
                  </div>
                </div>
                <el-tag :type="item.is_read_by_user ? 'info' : 'danger'">
                  {{ item.is_read_by_user ? '已读' : '未读' }}
                </el-tag>
              </div>
            </template>

            <div class="conversation-list">
              <article
                v-for="message in pagedMessages"
                :key="message.id"
                :class="['message-item', `message-${message.sender_type}`]"
              >
                <div class="message-head">
                  <span class="message-author">
                    {{ message.sender_type === 'admin' ? (message.sender_name || '管理员') : '我' }}
                  </span>
                  <span class="message-time">{{ formatTime(message.created_at, true) }}</span>
                </div>
                <p>{{ message.content }}</p>
              </article>
            </div>

            <div class="pagination-wrap" v-if="totalMessages > messagePageSize">
              <el-pagination
                v-model:current-page="messagePage"
                :page-size="messagePageSize"
                :total="totalMessages"
                layout="prev, pager, next"
                @current-change="() => {}"
              />
            </div>

            <div class="letter-actions">
              <el-button type="primary" plain @click="openReplyDialog(item)">回信</el-button>
              <el-button type="danger" plain @click="handleDelete(item)">删除</el-button>
            </div>
          </el-collapse-item>
        </el-collapse>

        <div class="pagination-wrap" v-if="letters.length > pageSize">
          <el-pagination
            v-model:current-page="page"
            :page-size="pageSize"
            :total="letters.length"
            layout="prev, pager, next"
            @current-change="handlePageChange"
          />
        </div>
      </template>
    </el-card>

    <el-dialog v-model="dialogVisible" width="680px" destroy-on-close title="回信">
      <div v-if="currentItem" class="dialog-context">
        <div class="dialog-subject">{{ currentItem.subject }}</div>
        <div class="dialog-hint">回信会追加到当前会话记录中，管理员可以继续查看和回复。</div>
      </div>
      <el-form label-position="top">
        <el-form-item label="回信内容">
          <el-input
            v-model="replyForm.reply"
            type="textarea"
            :rows="7"
            maxlength="5000"
            show-word-limit
            placeholder="请输入你想补充的内容"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="replyLoading" @click="handleReply">发送回信</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { deleteMyFeedback, getMailboxItems, markMailboxRead, replyMailboxItem } from '@/api/feedback'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const loading = ref(false)
const replyLoading = ref(false)
const letters = ref([])
const activeNames = ref([])
const page = ref(1)
const pageSize = 10
const messagePage = ref(1)
const messagePageSize = 5
const dialogVisible = ref(false)
const currentItem = ref(null)
const replyForm = ref({ reply: '' })

const pagedLetters = computed(() => {
  const start = (page.value - 1) * pageSize
  return letters.value.slice(start, start + pageSize)
})

const pagedMessages = computed(() => {
  if (!currentItem.value) return []
  const messages = currentItem.value.messages || []
  const start = (messagePage.value - 1) * messagePageSize
  return messages.slice(start, start + messagePageSize)
})

const totalMessages = computed(() => (currentItem.value?.messages || []).length)

function formatTime(value, withTime = false) {
  if (!value) return ''
  const dateStr = value.endsWith('Z') ? value : `${value}Z`
  const date = new Date(dateStr)
  if (Number.isNaN(date.getTime())) return ''
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

function handlePageChange() {
  activeNames.value = []
}

function openReplyDialog(item) {
  currentItem.value = item
  replyForm.value.reply = ''
  dialogVisible.value = true
}

function syncCurrentItem() {
  if (!currentItem.value) return
  const latest = letters.value.find(item => item.id === currentItem.value.id)
  if (latest) currentItem.value = latest
}

async function handleReply() {
  if (!currentItem.value) return
  if (!replyForm.value.reply.trim()) {
    ElMessage.warning('请输入回信内容')
    return
  }
  replyLoading.value = true
  try {
    await replyMailboxItem(currentItem.value.id, { reply: replyForm.value.reply })
    ElMessage.success('回信已发送')
    await loadMailbox()
    syncCurrentItem()
    replyForm.value.reply = ''
  } finally {
    replyLoading.value = false
  }
}

async function handleCollapseChange(names) {
  const normalizedNames = Array.isArray(names) ? names : [names]
  activeNames.value = normalizedNames.filter(Boolean)

  if (normalizedNames.length > 0 && normalizedNames[0]) {
    const item = pagedLetters.value.find(letter => String(letter.id) === String(normalizedNames[0]))
    if (item) {
      currentItem.value = item
      messagePage.value = 1
    }
  }

  for (const name of activeNames.value) {
    const item = pagedLetters.value.find(letter => String(letter.id) === String(name))
    if (!item || item.is_read_by_user) continue
    const res = await markMailboxRead(item.id)
    item.is_read_by_user = true
    userStore.setMailUnreadCount(Number(res.data?.unread_count || 0))
  }
}

async function loadMailbox() {
  loading.value = true
  try {
    const res = await getMailboxItems()
    letters.value = res.data?.items || []
    const maxPage = Math.max(Math.ceil(letters.value.length / pageSize), 1)
    if (page.value > maxPage) page.value = maxPage
    activeNames.value = []
    userStore.setMailUnreadCount(Number(res.data?.unread_count || 0))
  } finally {
    loading.value = false
  }
}

async function handleDelete(item) {
  await ElMessageBox.confirm('确定删除吗？', '删除信件', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消',
  })

  await deleteMyFeedback(item.id)
  if (currentItem.value?.id === item.id) {
    dialogVisible.value = false
    currentItem.value = null
  }
  ElMessage.success('信件已删除')
  await loadMailbox()
}

onMounted(loadMailbox)
</script>

<style scoped>
.mailbox-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.compact-hero {
  margin-bottom: 0;
  padding-block: 24px;
}

.mailbox-card {
  overflow: hidden;
}

.letter-collapse {
  border-top: none;
  border-bottom: none;
}

.letter-panel :deep(.el-collapse-item__header) {
  height: auto;
  line-height: normal;
  padding: 18px 0;
  align-items: flex-start;
}

.letter-panel :deep(.el-collapse-item__wrap) {
  border-bottom: none;
}

.letter-summary {
  width: calc(100% - 24px);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.letter-summary-main {
  min-width: 0;
}

.letter-summary h3 {
  margin: 0;
  font-size: 18px;
  color: var(--app-text);
}

.letter-meta {
  margin-top: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  color: var(--app-text-soft);
  font-size: 13px;
}

.conversation-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.message-item {
  padding: 16px;
  border-radius: 14px;
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
  color: var(--app-text);
  line-height: 1.75;
  white-space: pre-wrap;
  word-break: break-word;
}

.letter-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 14px;
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  padding-top: 20px;
}

.dialog-subject {
  font-size: 16px;
  font-weight: 600;
  color: var(--app-text);
}

.dialog-hint {
  margin-top: 8px;
  margin-bottom: 16px;
  color: var(--app-text-soft);
  font-size: 13px;
}

@media (max-width: 768px) {
  .letter-summary,
  .message-head {
    flex-direction: column;
    width: 100%;
  }

  .letter-actions {
    width: 100%;
    flex-direction: column;
  }

  .letter-actions .el-button {
    width: 100%;
    margin-left: 0;
  }
}
</style>
