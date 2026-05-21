<template>
  <div class="pending-review-page">
    <section class="page-hero compact-hero">
      <div>
        <h2>待处理审核</h2>
        <p>集中处理公开申请与首页推荐审核，保持内容上线流程稳定可控。</p>
      </div>
      <el-button @click="loadData">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </section>

    <el-card v-loading="loading">
      <el-empty v-if="!loading && pendingList.length === 0" description="暂无待审核内容" />

      <div v-else class="pending-list">
        <div v-for="item in pendingList" :key="item.id" class="pending-item">
          <div class="pending-info">
            <div class="pending-title">
              <el-icon color="#409eff"><Link /></el-icon>
              <a :href="item.url" target="_blank" rel="noopener noreferrer">{{ item.title }}</a>
            </div>

            <div class="pending-meta">
              <span class="pending-url">{{ item.url }}</span>
              <span class="pending-type">
                <el-tag size="small" :type="item.pending_type === 'homepage' ? 'success' : 'info'">
                  {{ item.pending_type === 'homepage' ? '首页推荐审核' : '公开申请审核' }}
                </el-tag>
              </span>
              <span v-if="item.pending_type === 'homepage'" class="pending-category">
                <el-tag size="small" type="warning">{{ item.pending_category || '未分类' }}</el-tag>
              </span>
            </div>
          </div>

          <div class="pending-actions">
            <el-select
              v-if="item.pending_type === 'homepage'"
              v-model="selectedCategory[item.id]"
              placeholder="选择分类"
              size="default"
              style="width: 160px;"
            >
              <el-option
                v-for="cat in homeCategories"
                :key="cat.id"
                :label="cat.name"
                :value="cat.id"
              />
            </el-select>

            <el-button type="primary" size="small" @click="handleApprove(item)">
              {{ item.pending_type === 'homepage' ? '同意并分配分类' : '同意' }}
            </el-button>

            <el-popconfirm title="确定拒绝该请求？" @confirm="handleReject(item)">
              <template #reference>
                <el-button size="small" type="danger" plain>不同意</el-button>
              </template>
            </el-popconfirm>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getPendingReview, approveBookmark, rejectBookmark } from '@/api/bookmark'
import { getAdminCategories } from '@/api/category'

const loading = ref(false)
const pendingList = ref([])
const homeCategories = ref([])
const selectedCategory = ref({})

async function loadData() {
  loading.value = true
  try {
    const [pendingRes, catRes] = await Promise.all([
      getPendingReview(),
      getAdminCategories(),
    ])
    pendingList.value = pendingRes.data || []
    homeCategories.value = catRes.data || []
  } catch (error) {
    console.error('加载待审核列表失败', error)
  } finally {
    loading.value = false
  }
}

async function handleApprove(item) {
  const isHomepageReview = item.pending_type === 'homepage'
  const categoryId = selectedCategory.value[item.id]

  if (isHomepageReview && !categoryId) {
    ElMessage.warning('请先选择分类')
    return
  }

  try {
    await approveBookmark(item.id, isHomepageReview ? categoryId : null)
    ElMessage.success(isHomepageReview ? '审核通过，已分配分类' : '审核通过')
    delete selectedCategory.value[item.id]
    await loadData()
  } catch (error) {
    ElMessage.error(error.message || '操作失败')
  }
}

async function handleReject(item) {
  try {
    await rejectBookmark(item.id)
    ElMessage.success('已拒绝')
    delete selectedCategory.value[item.id]
    await loadData()
  } catch (error) {
    ElMessage.error(error.message || '操作失败')
  }
}

onMounted(loadData)
</script>

<style scoped>
.pending-review-page {
  padding: 20px;
}

.compact-hero { margin-bottom: 20px; }

.pending-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.pending-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #fafbfc;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  transition: all 0.2s;
}

.pending-item:hover {
  background: #fff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
  border-color: #cfe2f7;
}

.pending-info {
  flex: 1;
  min-width: 0;
}

.pending-title {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
}

.pending-title a {
  color: #333;
  text-decoration: none;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.pending-title a:hover {
  color: #409eff;
}

.pending-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: #999;
}

.pending-url {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 400px;
}

.pending-type,
.pending-category {
  flex-shrink: 0;
}

.pending-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

@media (max-width: 768px) {
  .pending-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .pending-meta,
  .pending-actions {
    width: 100%;
    flex-wrap: wrap;
  }

  .pending-url {
    max-width: 100%;
  }
}
</style>
