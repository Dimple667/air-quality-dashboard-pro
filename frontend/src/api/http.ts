import axios from 'axios'

/** 后端统一响应结构 */
export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

/**
 * 统一 Axios 实例：
 * 所有请求都走 /api 前缀，由 Vite dev proxy 转发到 Flask(127.0.0.1:5000)，
 * 各组件禁止再写死 http://localhost:5000 / http://127.0.0.1:5000。
 */
export const http = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 请求拦截器：打印开发期请求日志
http.interceptors.request.use(config => {
  console.debug('[api]', config.method?.toUpperCase(), config.url, config.params || '')
  return config
})

// 响应拦截器：统一处理业务码与网络错误
http.interceptors.response.use(
  response => {
    const body = response.data as ApiResponse<unknown>
    if (body && typeof body.code === 'number' && body.code !== 0) {
      console.error('[api] 业务错误:', body)
      return Promise.reject(new Error(body.message || '请求失败'))
    }
    return response
  },
  error => {
    let message: string
    if (error?.response) {
      // 后端已返回响应（如 404/500），优先读取统一 message
      message = error.response.data?.message || `请求失败(${error.response.status})`
    } else if (error?.code === 'ECONNABORTED') {
      message = '请求超时，请稍后重试'
    } else if (error?.request) {
      message = '无法连接到服务器，请检查后端服务是否启动'
    } else {
      message = error?.message || '网络请求失败'
    }
    console.error('[api] 请求失败:', error)
    return Promise.reject(new Error(message))
  }
)
