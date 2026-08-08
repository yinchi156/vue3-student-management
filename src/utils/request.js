// src/utils/request.js
import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'


const request = axios.create({
  baseURL: '/api',  // 你的后端地址
  timeout: 10000
})

// 请求拦截器：自动添加 token
request.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

// 响应拦截器：处理 token 过期
request.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      ElMessage.error('登录已过期，请重新登录')
      localStorage.clear()
      router.push('/login')
    }
    return Promise.reject(error)
  }
)

export default request