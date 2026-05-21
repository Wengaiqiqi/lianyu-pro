<template>
  <div class="categories-page">
    <section class="page-hero compact-hero">
      <div class="hero-copy">
        <h2>{{ heroTitle }}</h2>
        <p>{{ heroDescription }}</p>
      </div>
      <el-button type="primary" @click="openDialog()">
        <el-icon><Plus /></el-icon> {{ createLabel }}
      </el-button>
    </section>
    <el-card v-loading="loading">
      <el-empty v-if="!loading && categories.length === 0" description="暂无分类" />
      <el-tree
        v-else
        :data="categories"
        :props="{ label: 'name', children: 'children' }"
        node-key="id"
        default-expand-all
        :expand-on-click-node="false"
      >
        <template #default="{ node, data }">
          <div class="tree-node">
            <span class="node-label">
              <el-icon><Folder /></el-icon>
              {{ data.name }}
              <el-tag size="small" type="info" class="count-tag">{{ getTotalCount(data) }}</el-tag>
            </span>
            <span class="node-actions">
              <el-button link type="primary" size="small" @click.stop="openDialog(null, data.id)">添加子分类</el-button>
              <el-button link type="primary" size="small" @click.stop="openDialog(data)">编辑</el-button>
              <el-popconfirm title="确定删除该分类？" @confirm="handleDelete(data.id)">
                <template #reference>
                  <el-button link type="danger" size="small" @click.stop>删除</el-button>
                </template>
              </el-popconfirm>
            </span>
          </div>
        </template>
      </el-tree>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑分类' : '新建分类'" width="440px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="分类名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="分类描述（选填）" />
        </el-form-item>
        <el-form-item label="父分类">
          <el-tree-select
            v-model="form.parent_id"
            :data="categories"
            :props="{ label: 'name', value: 'id', children: 'children' }"
            placeholder="无（顶级分类）"
            clearable
            check-strictly
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort_order" :min="0" :max="999" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getCategories, getCategoriesFlat, createCategory, updateCategory, deleteCategory } from '@/api/category'
import { ElMessage } from 'element-plus'

const categories = ref([])
const flatCategories = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const editingId = ref(null)
const formRef = ref()
const submitting = ref(false)
const heroTitle = '\u5206\u7c7b\u7ba1\u7406'
const heroDescription = '\u6574\u7406\u4e2a\u4eba\u6536\u85cf\u5206\u7c7b\u7ed3\u6784\uff0c\u4fdd\u6301\u5f52\u6863\u6e05\u6670\u3001\u67e5\u627e\u987a\u624b\u3002'
const createLabel = '\u65b0\u5efa\u5206\u7c7b'

const form = reactive({ name: '', description: '', parent_id: null, sort_order: 0 })
const rules = { name: [{ required: true, message: '请输入分类名称', trigger: 'blur' }] }

function resetForm() {
  Object.assign(form, { name: '', description: '', parent_id: null, sort_order: 0 })
  editingId.value = null
}

function getTotalCount(data) {
  let count = data.bookmark_count || 0
  if (data.children && data.children.length > 0) {
    for (const child of data.children) {
      count += getTotalCount(child)
    }
  }
  return count
}

function openDialog(row, parentId) {
  resetForm()
  if (row) {
    editingId.value = row.id
    Object.assign(form, { name: row.name, description: row.description, parent_id: row.parent_id, sort_order: row.sort_order })
  } else if (parentId) {
    form.parent_id = parentId
  }
  dialogVisible.value = true
}

async function handleSubmit() {
  await formRef.value.validate()
  submitting.value = true
  try {
    if (editingId.value) {
      await updateCategory(editingId.value, form)
      ElMessage.success('更新成功')
    } else {
      await createCategory(form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadData()
  } finally {
    submitting.value = false
  }
}

async function handleDelete(id) {
  try {
    await deleteCategory(id)
    ElMessage.success('删除成功')
    loadData()
  } catch {}
}

async function loadData() {
  loading.value = true
  try {
    const [treeRes, flatRes] = await Promise.all([getCategories(), getCategoriesFlat()])
    categories.value = treeRes.data
    flatCategories.value = flatRes.data
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
.page-hero {
  margin-bottom: 20px;
}

.hero-copy {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.page-hero h2 {
  margin: 0;
  font-size: 36px;
  line-height: 1.15;
}

.page-hero p {
  margin: 0;
  font-size: 15px;
  line-height: 1.7;
  color: rgba(67, 98, 145, 0.9);
  max-width: 760px;
}
.tree-node {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex: 1;
  padding-right: 8px;
}
.node-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 19px;
}
.count-tag { margin-left: 4px; }
.node-actions {
  display: flex;
  gap: 12px;
}
.node-actions :deep(.el-button) {
  font-size: 16px;
}

@media (max-width: 768px) {
  .page-hero { margin-bottom: 12px; }
  .page-hero h2 { font-size: 28px; }
  .node-label { font-size: 15px; }
  .node-actions { gap: 6px; }
  .node-actions .el-button { margin-left: 0; padding: 2px 4px; }
  .el-card__body { padding: 10px; }
  :deep(.el-tree-node__content) { height: 36px; }
}
</style>
