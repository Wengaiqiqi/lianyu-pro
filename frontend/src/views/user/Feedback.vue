<template>
  <div class="feedback-page">
    <section class="page-hero compact-hero">
      <div>
        <h2>反馈中心</h2>
        <p>提交建议、问题和体验反馈，并持续查看自己的反馈记录。</p>
      </div>
    </section>

    <div class="feedback-layout">
      <el-card shadow="never" class="page-card compose-card">
        <template #header>
          <div class="card-title">
            <strong>提交反馈</strong>
            <span>建议尽量描述使用场景、问题现象和预期效果。</span>
          </div>
        </template>

        <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
          <el-form-item label="反馈标题" prop="subject">
            <el-input v-model="form.subject" maxlength="200" show-word-limit placeholder="例如：桌面端导航层级还可以更清晰" />
          </el-form-item>
          <el-form-item label="联系方式">
            <el-input
              v-model="form.contact"
              maxlength="120"
              show-word-limit
              placeholder="可选，填写邮箱 / 微信 / 其他方便联系的信息"
            />
          </el-form-item>
          <el-form-item label="反馈内容" prop="content">
            <el-input
              v-model="form.content"
              type="textarea"
              :rows="10"
              maxlength="5000"
              show-word-limit
              placeholder="请尽量写清场景、问题和预期效果"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="submitting" @click="handleSubmit">发送给管理员</el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <el-card shadow="never" v-loading="loading" class="page-card history-card">
        <template #header>
          <div class="history-header">
            <div class="card-title">
              <strong>我的反馈记录</strong>
              <span>你可以回看自己提交过的所有内容。</span>
            </div>
            <el-button link type="primary" @click="loadFeedbacks">刷新</el-button>
          </div>
        </template>

        <el-empty v-if="!loading && feedbacks.length === 0" description="你还没有提交过反馈" />

        <div v-else class="history-body">
          <div class="history-scroll">
            <div class="feedback-list">
              <article v-for="item in feedbacks" :key="item.id" class="feedback-item">
                <div class="feedback-top">
                  <div>
                    <h3>{{ item.subject }}</h3>
                    <div class="feedback-meta">
                      <span>{{ formatTime(item.created_at) }}</span>
                      <span v-if="item.contact">联系方式：{{ item.contact }}</span>
                    </div>
                  </div>
                  <div class="feedback-actions">
                    <el-button link type="danger" @click="handleDelete(item)">删除</el-button>
                  </div>
                </div>

                <div class="feedback-block">
                  <div class="block-label">我的反馈</div>
                  <p>{{ item.content }}</p>
                </div>
              </article>
            </div>
          </div>

          <div class="pagination-wrap" v-if="total > pageSize">
            <el-pagination
              v-model:current-page="page"
              :page-size="pageSize"
              :total="total"
              layout="prev, pager, next"
              @current-change="loadFeedbacks"
            />
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { createFeedback, deleteMyFeedback, getMyFeedbacks } from '@/api/feedback'

const formRef = ref()
const loading = ref(false)
const submitting = ref(false)
const feedbacks = ref([])
const page = ref(1)
const pageSize = 3
const total = ref(0)

const form = reactive({
  subject: '',
  contact: '',
  content: '',
})

const rules = {
  subject: [{ required: true, message: '请输入反馈标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入反馈内容', trigger: 'blur' }],
}

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

async function loadFeedbacks() {
  loading.value = true
  try {
    const res = await getMyFeedbacks({ page: page.value, per_page: pageSize })
    feedbacks.value = res.data?.items || []
    total.value = Number(res.data?.total || 0)
    const maxPage = Math.max(Math.ceil(total.value / pageSize), 1)
    if (page.value > maxPage) page.value = maxPage
  } finally {
    loading.value = false
  }
}

async function handleSubmit() {
  await formRef.value.validate()
  submitting.value = true
  try {
    await createFeedback(form)
    ElMessage.success('反馈已发送，请留意信箱回复')
    page.value = 1
    form.subject = ''
    form.contact = ''
    form.content = ''
    await loadFeedbacks()
  } finally {
    submitting.value = false
  }
}

async function handleDelete(item) {
  await ElMessageBox.confirm(`确定删除“${item.subject}”吗？删除后不可恢复。`, '删除反馈', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消',
  })

  await deleteMyFeedback(item.id)
  ElMessage.success('反馈已删除')
  await loadFeedbacks()
}

onMounted(loadFeedbacks)
</script>

<style scoped>
.feedback-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.compact-hero {
  margin-bottom: 0;
  padding-block: 24px;
}

.feedback-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(380px, 0.95fr);
  gap: 20px;
}

.compose-card,
.history-card {
  min-height: 680px;
}

.compose-card :deep(.el-card__body),
.history-card :deep(.el-card__body) {
  height: 100%;
}

.history-card :deep(.el-card__body) {
  display: flex;
  flex-direction: column;
}

.card-title strong {
  display: block;
  font-size: 18px;
  color: var(--app-text);
}

.card-title span {
  display: block;
  margin-top: 6px;
  font-size: 13px;
  color: var(--app-text-soft);
}

.history-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.history-body {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.history-scroll {
  flex: 1;
  overflow-y: auto;
  min-height: 0;
}

.feedback-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.feedback-item {
  padding: 18px;
  border: 1px solid var(--app-border);
  border-radius: 18px;
  background: linear-gradient(180deg, var(--app-bg-soft) 0%, var(--app-bg-elevated) 100%);
}

.feedback-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}

.feedback-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.feedback-top h3 {
  margin: 0;
  font-size: 18px;
  color: var(--app-text);
}

.feedback-meta {
  margin-top: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  color: var(--app-text-soft);
  font-size: 13px;
}

.feedback-block {
  padding: 14px;
  border-radius: 14px;
  background: rgba(64, 158, 255, 0.06);
  border: 1px solid rgba(64, 158, 255, 0.1);
}

.block-label {
  margin-bottom: 10px;
  font-size: 13px;
  font-weight: 600;
  color: #409eff;
}

.feedback-block p {
  margin: 0;
  color: var(--app-text);
  line-height: 1.75;
  white-space: pre-wrap;
  word-break: break-word;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 4;
  overflow: hidden;
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  padding-top: 18px;
  margin-top: auto;
}

@media (max-width: 980px) {
  .feedback-layout {
    grid-template-columns: 1fr;
  }

  .compose-card,
  .history-card {
    min-height: auto;
  }

  .history-scroll {
    flex: unset;
    overflow: visible;
    min-height: unset;
  }
}

@media (max-width: 768px) {
  .feedback-top {
    flex-direction: column;
    align-items: flex-start;
  }

  .feedback-actions {
    width: 100%;
    justify-content: space-between;
  }
}
</style>
