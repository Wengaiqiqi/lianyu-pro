import request from './request'

export function getBookmarks(params) {
  return request.get('/bookmarks', { params })
}

export function addBookmark(data) {
  return request.post('/bookmarks', data)
}

export function updateBookmark(id, data) {
  return request.put(`/bookmarks/${id}`, data)
}

export function deleteBookmark(id) {
  return request.delete(`/bookmarks/${id}`)
}

export function fetchUrlInfo(url) {
  return request.post('/bookmarks/fetch-info', { url })
}

export function searchBookmarks(params) {
  return request.get('/bookmarks/search', { params })
}

export function getPublicBookmarks(params) {
  return request.get('/bookmarks/public', { params })
}

export function getPublicBookmarkDetail(id) {
  return request.get(`/bookmarks/public/${id}`)
}

export function getPublicBookmarkVisitTrend(id, params) {
  return request.get(`/bookmarks/public/${id}/visit-trend`, { params })
}

export function getPublicUserBookmarks(params) {
  return request.get('/bookmarks/users/public', { params })
}

export function getPublicUserBookmarkRankings(type, extraParams = {}) {
  return request.get('/bookmarks/users/public/rankings', { params: { type, ...extraParams } })
}

export function getRankings(type) {
  return request.get('/bookmarks/rankings', { params: { type, limit: 50 } })
}

export function incrementVisit(id) {
  return request.post(`/bookmarks/${id}/visit`)
}

export function getPendingReview() {
  return request.get('/bookmarks/pending-review')
}

export function approveBookmark(id, categoryId = null) {
  const data = {}
  if (categoryId) {
    data.category_id = categoryId
  }
  return request.post(`/bookmarks/${id}/approve`, data)
}

export function rejectBookmark(id) {
  return request.post(`/bookmarks/${id}/reject`)
}

export function setPendingReview(id, data = {}) {
  return request.post(`/bookmarks/${id}/set-pending`, data)
}
