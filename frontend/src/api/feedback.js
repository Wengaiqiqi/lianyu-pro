import request from './request'

export function createFeedback(data) {
  return request.post('/user/feedbacks', data)
}

export function getMyFeedbacks(params) {
  return request.get('/user/feedbacks', { params })
}

export function deleteMyFeedback(id) {
  return request.delete(`/user/feedbacks/${id}`)
}

export function getMailboxItems() {
  return request.get('/user/mailbox')
}

export function markMailboxRead(id) {
  return request.put(`/user/mailbox/${id}/read`)
}

export function replyMailboxItem(id, data) {
  return request.put(`/user/mailbox/${id}/reply`, data)
}

export function getUnreadMailboxCount() {
  return request.get('/user/mailbox/unread-count')
}

export function getAdminUnreadFeedbackCount() {
  return request.get('/admin/feedbacks/unread-count')
}

export function getAdminFeedbacks(params) {
  return request.get('/admin/feedbacks', { params })
}

export function replyAdminFeedback(id, data) {
  return request.put(`/admin/feedbacks/${id}/reply`, data)
}

export function deleteAdminFeedback(id) {
  return request.delete(`/admin/feedbacks/${id}`)
}
