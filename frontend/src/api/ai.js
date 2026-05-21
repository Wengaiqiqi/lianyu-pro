import request from './request'

export function getInterests() {
  return request.get('/ai/interests')
}

export function analyzeInterests() {
  return request.post('/ai/interests/analyze', null, { timeout: 600000 })
}

export function evaluateUrlSafety(url, title) {
  return request.post('/ai/evaluate-url', { url, title }, { timeout: 30000 })
}
