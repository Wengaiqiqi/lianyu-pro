import request from './request'

export function getUsers(params) {
  return request.get('/admin/users', { params })
}

export function toggleUserStatus(id) {
  return request.put(`/admin/users/${id}/status`)
}

export function deleteUser(id) {
  return request.delete(`/admin/users/${id}`)
}

export function getAllBookmarks(params) {
  return request.get('/admin/bookmarks', { params })
}

export function toggleBlockBookmark(id) {
  return request.put(`/admin/bookmarks/${id}/block`)
}

export function adminDeleteBookmark(id) {
  return request.delete(`/admin/bookmarks/${id}`)
}

export function getGlobalCategories() {
  return request.get('/admin/categories')
}

export function createGlobalCategory(data) {
  return request.post('/admin/categories', data)
}

export function updateGlobalCategory(id, data) {
  return request.put(`/admin/categories/${id}`, data)
}

export function deleteGlobalCategory(id) {
  return request.delete(`/admin/categories/${id}`)
}

export function getStatistics() {
  return request.get('/admin/statistics')
}

export function getLogs(params) {
  return request.get('/admin/logs', { params })
}

export function deleteLog(id) {
  return request.delete(`/admin/logs/${id}`)
}

export function deleteLogsByDateRange(params) {
  return request.delete('/admin/logs/date-range', { data: params })
}

export function getAIConfig() {
  return request.get('/admin/ai-config')
}

export function updateAIConfig(data) {
  return request.put('/admin/ai-config', data)
}

export function testAIConfig(data) {
  return request.post('/admin/ai-config/test', data)
}

export function createGlobalBookmark(data) {
  return request.post('/admin/global-bookmarks', data)
}

export function fetchBookmarkInfo(url) {
  return request.post('/bookmarks/fetch-info', { url })
}
