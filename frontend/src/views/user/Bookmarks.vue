<template>
  <div class="bookmarks-page" :class="{ 'dark-theme': theme === 'dark' }">
    <section class="page-hero compact-hero">
      <div>
        <h2>我的收藏</h2>
        <p>集中管理已保存的网站、分类归档和公开展示状态。</p>
      </div>
      <el-button type="primary" @click="openDialog()">
        <el-icon><Plus /></el-icon>
        添加链接
      </el-button>
    </section>

    <div class="filter-bar page-card">
      <el-tree-select
        v-model="filterCategory"
        :data="categories"
        :props="{ label: 'name', value: 'id', children: 'children' }"
        placeholder="按分类筛选"
        clearable
        check-strictly
        class="mobile-full-width"
        style="width: 220px"
        @change="loadBookmarks"
      />
    </div>

    <el-card shadow="never" class="page-card table-card" v-loading="loading">
      <el-empty v-if="!loading && bookmarks.length === 0" description="暂无收藏，点击上方按钮添加链接" />

      <template v-else>
        <el-table :data="bookmarks" stripe width="100%">
          <el-table-column label="网站" width="320">
            <template #default="{ row }">
              <div class="site-cell">
                <img v-if="row.favicon" :src="row.favicon" class="favicon" alt="" />
                <div class="site-text">
                  <a :href="row.url" target="_blank" rel="noopener noreferrer" class="site-title" @click="handleVisit(row.id)">
                    {{ row.title }}
                  </a>
                  <div class="site-url">{{ row.url }}</div>
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="描述" min-width="420" show-overflow-tooltip header-align="center" align="left" />
          <el-table-column label="分类" width="100" align="center">
            <template #default="{ row }">
              <el-tag v-if="row.category_name" size="small">{{ row.category_name }}</el-tag>
              <span v-else class="no-category">未分类</span>
            </template>
          </el-table-column>
          <el-table-column label="公开" width="84" align="center">
            <template #default="{ row }">
              <el-switch
                :model-value="row.is_public"
                :loading="togglingId === row.id"
                :disabled="togglingId === row.id"
                inline-prompt
                style="--el-switch-off-color: #dcdfe6; --el-switch-on-color: #67c23a;"
                @change="(val) => handlePublicToggle(val, row)"
              />
            </template>
          </el-table-column>
          <el-table-column label="访问" width="84" align="center">
            <template #default="{ row }">
              <span class="visit-count">{{ row.visits || 0 }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="128" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" size="small" @click="openDialog(row)">编辑</el-button>
              <el-popconfirm title="确定删除该收藏吗？" @confirm="handleDelete(row.id)">
                <template #reference>
                  <el-button link type="danger" size="small">删除</el-button>
                </template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination" v-if="total > perPage">
          <el-pagination
            v-model:current-page="page"
            :page-size="perPage"
            :total="total"
            layout="prev, pager, next, total"
            @current-change="loadBookmarks"
          />
        </div>
      </template>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑收藏' : '添加收藏'" width="560px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="网址" prop="url">
          <el-input v-model="form.url" placeholder="请输入网址">
            <template #append>
              <el-button :loading="fetching" @click="handleFetch">一键抓取</el-button>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="网页标题" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="网页描述" />
        </el-form-item>
        <el-form-item label="分类">
          <el-popover
            v-model:visible="categoryPickerVisible"
            placement="bottom-start"
            trigger="click"
            :width="480"
            popper-class="category-picker-popper"
            @show="syncExpandedParents"
          >
            <template #reference>
              <button type="button" class="category-trigger">
                <span :class="{ placeholder: !selectedCategoryName }">{{ selectedCategoryName || '选择分类' }}</span>
                <span class="trigger-arrow">⌄</span>
              </button>
            </template>

            <div class="category-picker">
              <button type="button" class="category-option root-option" @click="selectCategory(null)">
                <span>不选择分类</span>
              </button>

              <div v-for="parent in categories" :key="parent.id" class="category-group">
                <div class="category-option">
                  <button type="button" class="category-label tree-label" @click="selectCategory(parent.id)">
                    <span class="tree-prefix">
                      <span
                        v-if="parent.children?.length"
                        :class="['tree-arrow', { expanded: expandedParentIds.includes(parent.id) }]"
                        @click.stop="toggleParent(parent.id)"
                      >
                        <el-icon><CaretRight /></el-icon>
                      </span>
                      <span v-else class="tree-arrow placeholder"></span>
                      <el-icon class="tree-folder"><Folder /></el-icon>
                    </span>
                    <span>{{ parent.name }}</span>
                  </button>
                  <div class="category-actions">
                    <button
                      v-if="parent.children?.length"
                      type="button"
                      class="category-expand"
                      :aria-label="expandedParentIds.includes(parent.id) ? '收起子分类' : '展开子分类'"
                      @click.stop="toggleParent(parent.id)"
                    >
                      <span :class="['expand-arrow', { expanded: expandedParentIds.includes(parent.id) }]">⌄</span>
                    </button>
                    <button type="button" class="category-add" @click="openQuickCategoryDialog('child', parent.id)">+</button>
                  </div>
                </div>

                <div v-if="parent.children?.length && expandedParentIds.includes(parent.id)" class="category-children">
                  <div v-for="child in parent.children" :key="child.id" class="category-option child-option">
                    <button type="button" class="category-label tree-label child-tree-label" @click="selectCategory(child.id)">
                      <span class="tree-prefix">
                        <span class="tree-arrow placeholder"></span>
                        <el-icon class="tree-folder"><Folder /></el-icon>
                      </span>
                      <span>{{ child.name }}</span>
                    </button>
                  </div>
                </div>
              </div>

              <button type="button" class="category-create-root" @click="openQuickCategoryDialog('parent')">
                <span class="plus-mark">+</span>
                <span>新建大分类</span>
              </button>
            </div>
          </el-popover>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="quickCategoryDialogVisible"
      :title="quickCategoryMode === 'parent' ? '新建大分类' : '新建小分类'"
      width="420px"
      destroy-on-close
    >
      <el-form ref="quickCategoryFormRef" :model="quickCategoryForm" :rules="quickCategoryRules" label-width="90px">
        <el-form-item v-if="quickCategoryMode === 'child'" label="上级分类" prop="parent_id">
          <div class="quick-parent-name">{{ selectedParentName || '未选择父分类' }}</div>
        </el-form-item>
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="quickCategoryForm.name" placeholder="请输入分类名称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="quickCategoryDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="creatingCategory" @click="handleQuickCategorySubmit">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { CaretRight, Folder, Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  addBookmark,
  deleteBookmark,
  fetchUrlInfo,
  getBookmarks,
  incrementVisit,
  updateBookmark,
  setPendingReview,
} from '@/api/bookmark'
import { createCategory, getCategories } from '@/api/category'
import { evaluateUrlSafety } from '@/api/ai'
import { useTheme } from '@/composables/useTheme'

const bookmarks = ref([])
const categories = ref([])
const loading = ref(false)
const page = ref(1)
const perPage = 20
const total = ref(0)
const filterCategory = ref(null)
const { theme } = useTheme()

const dialogVisible = ref(false)
const editingId = ref(null)
const formRef = ref()
const submitting = ref(false)
const fetching = ref(false)

const quickCategoryDialogVisible = ref(false)
const quickCategoryMode = ref('parent')
const quickCategoryFormRef = ref()
const creatingCategory = ref(false)
const categoryPickerVisible = ref(false)
const expandedParentIds = ref([])
const evaluating = ref(false)
const togglingId = ref(null)

const form = reactive({
  url: '',
  title: '',
  description: '',
  favicon: '',
  category_id: null,
  is_public: false,
})

const quickCategoryForm = reactive({
  name: '',
  parent_id: null,
})

const rules = {
  url: [{ required: true, message: '请输入网址', trigger: 'blur' }],
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
}

const quickCategoryRules = {
  name: [{ required: true, message: '请输入分类名称', trigger: 'blur' }],
  parent_id: [{
    validator: (_, value, callback) => {
      if (quickCategoryMode.value === 'child' && !value) {
        callback(new Error('请选择上级分类'))
        return
      }
      callback()
    },
    trigger: 'change',
  }],
}

const selectedCategoryName = computed(() => findCategoryName(form.category_id))
const selectedParentName = computed(() => findCategoryName(quickCategoryForm.parent_id))

function findCategoryName(categoryId) {
  if (!categoryId) return ''
  const visit = (list) => {
    for (const item of list) {
      if (item.id === categoryId) return item.name
      if (item.children?.length) {
        const found = visit(item.children)
        if (found) return found
      }
    }
    return ''
  }
  return visit(categories.value)
}

function resetForm() {
  Object.assign(form, {
    url: '',
    title: '',
    description: '',
    favicon: '',
    category_id: null,
    is_public: false,
  })
  editingId.value = null
}

function openDialog(row) {
  resetForm()
  if (row) {
    editingId.value = row.id
    Object.assign(form, {
      url: row.url,
      title: row.title,
      description: row.description,
      favicon: row.favicon,
      category_id: row.category_id,
      is_public: row.is_public,
    })
  }
  dialogVisible.value = true
}

function openQuickCategoryDialog(mode, parentId = null) {
  quickCategoryMode.value = mode
  quickCategoryForm.name = ''
  quickCategoryForm.parent_id = mode === 'child' ? parentId : null
  categoryPickerVisible.value = false
  quickCategoryDialogVisible.value = true
}

function selectCategory(categoryId) {
  form.category_id = categoryId
  categoryPickerVisible.value = false
}

function toggleParent(parentId) {
  const index = expandedParentIds.value.indexOf(parentId)
  if (index >= 0) {
    expandedParentIds.value.splice(index, 1)
    return
  }
  expandedParentIds.value.push(parentId)
}

function findParentIdByCategoryId(categoryId) {
  if (!categoryId) return null
  for (const parent of categories.value) {
    if (parent.id === categoryId) return parent.id
    if (parent.children?.some(child => child.id === categoryId)) return parent.id
  }
  return null
}

function syncExpandedParents() {
  const parentId = findParentIdByCategoryId(form.category_id)
  expandedParentIds.value = parentId ? [parentId] : []
}

async function handleFetch() {
  if (!form.url) {
    ElMessage.warning('请输入网址')
    return
  }
  fetching.value = true
  try {
    const res = await fetchUrlInfo(form.url)
    if (res.data.title || res.data.description) {
      if (res.data.title) form.title = res.data.title
      if (res.data.description) form.description = res.data.description
      if (res.data.favicon) form.favicon = res.data.favicon
      ElMessage.success('抓取成功')
    } else {
      ElMessage.warning(res.data.error ? '抓取失败，请手动填写' : '网页未返回标题和描述，请手动补充')
    }
  } catch {
    ElMessage.warning('抓取失败，请手动填写')
  } finally {
    fetching.value = false
  }
}

async function handlePublicToggle(val, row) {
  togglingId.value = row.id

  if (!val) {
    try {
      await updateBookmark(row.id, { is_public: false })
      row.is_public = false
      ElMessage.success('已取消公开')
    } catch {
      row.is_public = true
      ElMessage.error('操作失败')
    } finally {
      togglingId.value = null
    }
    return
  }

  try {
    await ElMessageBox.confirm(
      '确定将该链接设置为公开吗？公开前会先进行 AI 安全评估。',
      '设置公开',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'info' }
    )
  } catch {
    row.is_public = false
    togglingId.value = null
    return
  }

  evaluating.value = true
  try {
    const res = await evaluateUrlSafety(row.url, row.title)
    evaluating.value = false

    if (res.data?.safe) {
      await updateBookmark(row.id, { is_public: true })
      row.is_public = true
      ElMessage.success('AI 评估通过，已设置为公开')
    } else {
      const reason = res.data?.reason || '内容可能存在风险'
      row.is_public = false
      try {
        await ElMessageBox.confirm(
          `AI 评估结果：${reason}\n\n是否提交管理员审核？`,
          '内容评估未通过',
          { confirmButtonText: '提交审核', cancelButtonText: '取消', type: 'warning' }
        )
        await updateBookmark(row.id, { is_public: false })
        await setPendingReview(row.id)
        ElMessage.info('已提交管理员审核')
        loadBookmarks()
      } catch {
        // user cancelled
      }
    }
  } catch (error) {
    evaluating.value = false
    row.is_public = false
    if (error !== 'cancel') {
      ElMessage.error('AI 评估失败，请稍后重试')
    }
  } finally {
    togglingId.value = null
  }
}

async function handleSubmit() {
  await formRef.value.validate()
  submitting.value = true
  try {
    if (editingId.value) {
      await updateBookmark(editingId.value, form)
      ElMessage.success('更新成功')
    } else {
      await addBookmark(form)
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    loadBookmarks()
  } finally {
    submitting.value = false
  }
}

async function handleQuickCategorySubmit() {
  await quickCategoryFormRef.value.validate()
  creatingCategory.value = true
  try {
    const res = await createCategory({
      name: quickCategoryForm.name.trim(),
      parent_id: quickCategoryMode.value === 'child' ? quickCategoryForm.parent_id : null,
      description: '',
      sort_order: 0,
    })
    await loadCategories()
    form.category_id = res.data.id
    quickCategoryDialogVisible.value = false
    ElMessage.success('分类创建成功')
  } finally {
    creatingCategory.value = false
  }
}

async function handleDelete(id) {
  try {
    await deleteBookmark(id)
    ElMessage.success('删除成功')
    loadBookmarks()
  } catch {
    // handled by interceptor
  }
}

async function loadBookmarks() {
  loading.value = true
  try {
    const params = { page: page.value, per_page: perPage }
    if (filterCategory.value) params.category_id = filterCategory.value
    const res = await getBookmarks(params)
    bookmarks.value = res.data.items
    total.value = res.data.total
  } finally {
    loading.value = false
  }
}

async function loadCategories() {
  const res = await getCategories()
  categories.value = res.data
}

async function handleVisit(id) {
  try {
    await incrementVisit(id)
  } catch {
    // silent
  }
}

onMounted(() => {
  loadBookmarks()
  loadCategories()
})
</script>

<style scoped>
.bookmarks-page {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.compact-hero {
  margin-bottom: 0;
  padding-block: 24px;
}

.filter-bar,
.table-card {
  padding: 16px 18px;
}

.table-card {
  overflow: hidden;
}

.site-cell {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  min-width: 0;
}

.favicon {
  width: 22px;
  height: 22px;
  border-radius: 6px;
  flex-shrink: 0;
}

.site-text {
  flex: 1;
  overflow: hidden;
  min-width: 0;
}

.site-title {
  color: var(--app-text);
  text-decoration: none;
  font-weight: 600;
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.site-title:hover {
  color: var(--app-primary);
}

.site-url,
.no-category {
  font-size: 12px;
  color: var(--app-text-soft);
}

.site-url {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.visit-count {
  color: #de6b49;
  font-weight: 700;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.category-trigger {
  width: 100%;
  min-height: 40px;
  padding: 0 14px;
  border: 1px solid var(--el-border-color);
  border-radius: 10px;
  background: var(--app-bg-elevated);
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  color: var(--app-text);
}

.category-trigger .placeholder {
  color: var(--app-text-muted);
}

.trigger-arrow {
  color: var(--app-text-soft);
  font-size: 16px;
}

.category-picker {
  max-height: 320px;
  overflow: auto;
}

.category-group + .category-group {
  margin-top: 4px;
}

.category-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  min-height: 38px;
  border-radius: 8px;
}

.category-label,
.category-create-root,
.root-option {
  border: none;
  background: transparent;
  cursor: pointer;
}

.category-label {
  flex: 1;
  text-align: left;
  padding: 8px 10px;
  color: var(--app-text);
  border-radius: 8px;
}

.tree-label {
  display: flex;
  align-items: center;
  gap: 6px;
}

.tree-prefix {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

.tree-arrow {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 14px;
  color: var(--app-text-soft);
  transition: transform 0.2s ease;
}

.tree-arrow.expanded {
  transform: rotate(90deg);
}

.tree-arrow.placeholder {
  visibility: hidden;
}

.tree-folder {
  color: var(--app-text);
  font-size: 16px;
}

.category-label:hover,
.root-option:hover {
  background: var(--app-bg-muted);
}

.category-actions {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

.category-expand,
.category-add {
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 999px;
  cursor: pointer;
  flex-shrink: 0;
}

.category-expand {
  display: none;
}

.category-expand:hover {
  background: var(--app-bg-muted);
}

.expand-arrow {
  display: inline-block;
  font-size: 14px;
  line-height: 1;
  transition: transform 0.2s ease;
}

.expand-arrow.expanded {
  transform: rotate(180deg);
}

.category-add {
  background: var(--app-primary-soft);
  color: var(--app-primary);
}

.category-add:hover {
  background: rgba(47, 128, 237, 0.18);
}

.category-children {
  margin-left: 20px;
}

.child-option .category-label {
  color: var(--app-text-soft);
}

.child-tree-label {
  padding-left: 30px;
}

.root-option {
  width: 100%;
  text-align: left;
  padding: 8px 10px;
  color: var(--app-text-soft);
  border-radius: 8px;
}

.category-create-root {
  width: 100%;
  margin-top: 8px;
  padding: 10px 12px;
  border-top: 1px solid var(--app-border);
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--app-primary);
  text-align: left;
}

.plus-mark {
  font-size: 18px;
  line-height: 1;
}

.quick-parent-name {
  width: 100%;
  min-height: 40px;
  padding: 0 12px;
  border: 1px solid var(--app-border);
  border-radius: 10px;
  background: var(--app-bg-soft);
  display: flex;
  align-items: center;
  color: var(--app-text-soft);
}

@media (max-width: 768px) {
  .filter-bar {
    display: flex;
    width: 100%;
  }

  .mobile-full-width {
    width: 100% !important;
  }

  .table-card {
    padding-inline: 12px;
  }

  .el-table {
    font-size: 13px;
  }

  :deep(.el-table__cell) {
    padding: 8px 0;
  }

  .site-url {
    max-width: 150px;
  }
}
</style>
