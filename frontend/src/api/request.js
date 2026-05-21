import axios from 'axios'
import { getToken, removeToken } from '@/utils/auth'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

request.interceptors.request.use(
  (config) => {
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

request.interceptors.response.use(
  (response) => {
    const res = response.data
    if (res.code && res.code !== 200) {
      ElMessage.error(res.msg || '请求失败')
      if (res.code === 401) {
        removeToken()
        window.location.hash = '#/login'
      }
      return Promise.reject(new Error(res.msg || '请求失败'))
    }
    return res
  },
  (error) => {
    if (error.response) {
      const { status, data } = error.response
      if (status === 401 || status === 422) {
        removeToken()
        window.location.hash = '#/login'
        ElMessage.error(status === 422 ? '登录状态异常，请重新登录' : '登录已过期，请重新登录')
      } else if (status === 403) {
        ElMessage.error(data.msg || '没有权限')
      } else {
        ElMessage.error(data.msg || '请求失败')
      }
    } else {
      if (error.code === 'ECONNABORTED' || (error.message && error.message.includes('timeout'))) {     
        ElMessage.error('请求超时，可能由于 AI 分析较慢，请稍后重试或检查配置') 
      } else {
        ElMessage.error('网络错误')
      }
    }
    return Promise.reject(error)
  }
)

export default request
