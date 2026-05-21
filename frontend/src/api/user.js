import request from './request'

export function getUserProfile() {
  return request.get('/user/profile')
}

export function updateUserProfile(data) {
  return request.put('/user/profile', data)
}

export function changePassword(data) {
  return request.put('/user/password', data)
}

export function getUserStats() {
  return request.get('/user/stats')
}

export function getPublicUsers() {
  return request.get('/user/public-users')
}

export function getFollowingPublicUsers() {
  return request.get('/user/following/public-users')
}

export function followPublicUser(userId) {
  return request.post(`/user/public-users/${userId}/follow`)
}

export function unfollowPublicUser(userId) {
  return request.delete(`/user/public-users/${userId}/follow`)
}

export function likePublicUser(userId) {
  return request.post(`/user/public-users/${userId}/like`)
}

export function unlikePublicUser(userId) {
  return request.delete(`/user/public-users/${userId}/like`)
}

export function getPublicUserRankings(metric) {
  return request.get('/user/public-users/rankings', { params: { metric } })
}

export function getUsers(params) {
  return request.get('/admin/users', { params })
}
