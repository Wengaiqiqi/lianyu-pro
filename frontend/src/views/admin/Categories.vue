<template>
  <div class="admin-categories">
    <section class="page-hero compact-hero">
      <div>
        <h2>全局分类维护</h2>
        <p>统一维护公共分类结构与分类归属，保证内容组织清晰一致。</p>
      </div>
      <div class="header-actions">
        <el-button @click="openBookmarkDialog()">
          <el-icon><Link /></el-icon> 添加网页
        </el-button>
        <el-button type="primary" @click="openDialog()">
          <el-icon><Plus /></el-icon> 新建全局分类
        </el-button>
      </div>
    </section>

    <el-card v-loading="loading">
      <el-empty v-if="!loading && categories.length === 0" description="暂无全局分类" />
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
              <el-tag size="small" type="info">{{ data.bookmark_count || 0 }} 条收藏</el-tag>
            </span>
            <span class="node-actions">
              <el-button link type="primary" size="small" @click.stop="openDialog(null, data.id)">添加子分类</el-button>
              <el-button link type="primary" size="small" @click.stop="openBookmarkDialog(data.id)">添加网页</el-button>
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

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑分类' : '新建全局分类'" width="440px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="分类名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="分类描述" />
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

    <el-dialog v-model="bookmarkDialogVisible" title="添加网页" width="520px" destroy-on-close>
      <el-form ref="bookmarkFormRef" :model="bookmarkForm" :rules="bookmarkRules" label-width="80px">
        <el-form-item label="网址" prop="url">
          <el-input v-model="bookmarkForm.url" placeholder="https://example.com" @blur="handleFetchInfo">
            <template #append>
              <el-button :loading="fetching" @click="handleFetchInfo">抓取</el-button>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="标题" prop="title">
          <el-input v-model="bookmarkForm.title" placeholder="网页标题" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="bookmarkForm.description" type="textarea" :rows="2" placeholder="网页描述" />
        </el-form-item>
        <el-form-item label="分类">
          <el-tree-select
            v-model="bookmarkForm.category_id"
            :data="categorySelectData"
            :props="{ label: 'name', children: 'children', value: 'id' }"
            placeholder="选择分类（可选）"
            clearable
            check-strictly
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="bookmarkDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="bookmarkSubmitting" @click="handleBookmarkSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { getGlobalCategories, createGlobalCategory, updateGlobalCategory, deleteGlobalCategory, createGlobalBookmark, fetchBookmarkInfo } from '@/api/admin'
import { ElMessage } from 'element-plus'

const categories = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const editingId = ref(null)
const formRef = ref()
const submitting = ref(false)

const bookmarkDialogVisible = ref(false)
const bookmarkFormRef = ref()
const bookmarkSubmitting = ref(false)
const fetching = ref(false)

const form = reactive({ name: '', description: '', parent_id: null, sort_order: 0 })
const rules = { name: [{ required: true, message: '请输入分类名称', trigger: 'blur' }] }

const bookmarkForm = reactive({ url: '', title: '', description: '', category_id: null })
const bookmarkRules = { url: [{ required: true, message: '请输入网址', trigger: 'blur' }] }

const categorySelectData = computed(() => {
  return categories.value.map(c => ({
    id: c.id,
    name: c.name,
    children: (c.children || []).map(child => ({ id: child.id, name: child.name }))
  }))
})

function resetForm() {
  Object.assign(form, { name: '', description: '', parent_id: null, sort_order: 0 })
  editingId.value = null
}

function openDialog(row, parentId) {
  resetForm()
  if (row) {
    editingId.value = row.id
    Object.assign(form, { name: row.name, description: row.description, sort_order: row.sort_order })
  } else if (parentId) {
    form.parent_id = parentId
  }
  dialogVisible.value = true
}

function resetBookmarkForm() {
  Object.assign(bookmarkForm, { url: '', title: '', description: '', category_id: null })
}

function openBookmarkDialog(categoryId = null) {
  resetBookmarkForm()
  if (categoryId) {
    bookmarkForm.category_id = categoryId
  }
  bookmarkDialogVisible.value = true
}

async function handleFetchInfo() {
  const url = bookmarkForm.url.trim()
  if (!url) return
  fetching.value = true
  try {
    const res = await fetchBookmarkInfo(url)
    if (res.data.title) {
      bookmarkForm.title = res.data.title
      bookmarkForm.description = res.data.description || ''
    }
  } catch {} finally {
    fetching.value = false
  }
}

async function handleBookmarkSubmit() {
  await bookmarkFormRef.value.validate()
  bookmarkSubmitting.value = true
  try {
    await createGlobalBookmark(bookmarkForm)
    ElMessage.success('添加成功')
    bookmarkDialogVisible.value = false
  } catch {} finally {
    bookmarkSubmitting.value = false
  }
}

async function handleSubmit() {
  await formRef.value.validate()
  submitting.value = true
  try {
    if (editingId.value) {
      await updateGlobalCategory(editingId.value, form)
      ElMessage.success('更新成功')
    } else {
      await createGlobalCategory(form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadCategories()
  } finally {
    submitting.value = false
  }
}

async function handleDelete(id) {
  try {
    await deleteGlobalCategory(id)
    ElMessage.success('删除成功')
    loadCategories()
  } catch {}
}

async function loadCategories() {
  loading.value = true
  try {
    const res = await getGlobalCategories()
    categories.value = res.data
  } finally {
    loading.value = false
  }
}

onMounted(loadCategories)
</script>

<style scoped>
.compact-hero { margin-bottom: 20px; }
.header-actions { display: flex; gap: 8px; }
.tree-node { display: flex; justify-content: space-between; align-items: center; flex: 1; padding-right: 8px; }
.node-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 17px;
  line-height: 1.4;
  font-weight: 500;
}
.node-label :deep(.el-icon) {
  font-size: 17px;
}
.node-label :deep(.el-tag) {
  padding: 4px 10px;
  font-size: 13px;
  line-height: 1.2;
}
.node-actions { display: flex; gap: 4px; }
</style>
