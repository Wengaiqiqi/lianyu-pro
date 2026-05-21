<template>
  <div class="admin-users">
    <section class="page-hero compact-hero">
      <div>
        <h2>用户管理</h2>
        <p>查看用户状态、角色权限和收藏规模，快速处理异常账号。</p>
      </div>
      <el-input
        v-model="keyword"
        placeholder="搜索用户名"
        class="search-input"
        clearable
        @keyup.enter="loadUsers"
        @clear="loadUsers"
      >
        <template #append>
          <el-button @click="loadUsers"><el-icon><Search /></el-icon></el-button>
        </template>
      </el-input>
    </section>

    <el-card shadow="never" class="page-card table-card">
      <el-table :data="users" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="username" label="用户名" min-width="140" />
        <el-table-column prop="email" label="邮箱" min-width="200" />
        <el-table-column prop="role" label="角色" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'info'">
              {{ row.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="bookmark_count" label="收藏数量" width="110" align="center" />
        <el-table-column label="注册时间" width="130" align="center">
          <template #default="{ row }">
            {{ new Date(row.created_at).toLocaleDateString('zh-CN') }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <template v-if="row.role !== 'admin'">
              <el-popconfirm
                :title="`确定${row.is_active ? '禁用' : '启用'}该用户吗？`"
                @confirm="handleToggle(row.id)"
              >
                <template #reference>
                  <el-button link :type="row.is_active ? 'warning' : 'success'">
                    {{ row.is_active ? '禁用' : '启用' }}
                  </el-button>
                </template>
              </el-popconfirm>
              <el-popconfirm
                title="将永久删除该用户及其关联收藏数据，确定继续吗？"
                @confirm="handleDelete(row.id)"
              >
                <template #reference>
                  <el-button link type="danger">删除</el-button>
                </template>
              </el-popconfirm>
            </template>
            <span v-else class="admin-label">不可操作</span>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination" v-if="total > perPage">
        <el-pagination
          v-model:current-page="page"
          :page-size="perPage"
          :total="total"
          layout="prev, pager, next, total"
          @current-change="loadUsers"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getUsers, toggleUserStatus, deleteUser } from '@/api/admin'

const users = ref([])
const loading = ref(false)
const keyword = ref('')
const page = ref(1)
const perPage = 20
const total = ref(0)

async function loadUsers() {
  loading.value = true
  try {
    const res = await getUsers({ page: page.value, per_page: perPage, keyword: keyword.value })
    users.value = res.data.items
    total.value = res.data.total
  } finally {
    loading.value = false
  }
}

async function handleToggle(id) {
  await toggleUserStatus(id)
  ElMessage.success('操作成功')
  loadUsers()
}

async function handleDelete(id) {
  try {
    await deleteUser(id)
    ElMessage.success('用户已删除')
    page.value = 1
    loadUsers()
  } catch {
    // handled by interceptor
  }
}

onMounted(loadUsers)
</script>

<style scoped>
.admin-users {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.compact-hero {
  margin-bottom: 0;
  padding-block: 24px;
}

.search-input {
  width: min(280px, 100%);
}

.table-card {
  overflow: hidden;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.admin-label {
  color: var(--app-text-muted);
  font-size: 12px;
}

@media (max-width: 768px) {
  .search-input {
    width: 100%;
  }
}
</style>
