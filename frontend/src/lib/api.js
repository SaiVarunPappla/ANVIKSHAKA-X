import axios from 'axios'

// Use environment variable for backend URL
// Development: http://localhost:8000/api (set in frontend/.env)
// Production: https://<backend-project>.vercel.app/api (set in Vercel dashboard)
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

// Debug: Log the resolved API URL (helps verify production environment variable)
console.log('[ANVIKSHAKA-X] API Base URL:', API_BASE_URL)
console.log('[ANVIKSHAKA-X] Environment:', import.meta.env.MODE)
console.log('[ANVIKSHAKA-X] VITE_API_URL:', import.meta.env.VITE_API_URL)

// Expose API_BASE_URL to browser console for inspection
window.__ANVIKSHAKA_API_BASE_URL__ = API_BASE_URL
window.__ANVIKSHAKA_ENV__ = import.meta.env.MODE
window.__ANVIKSHAKA_VITE_API_URL__ = import.meta.env.VITE_API_URL

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Debug: Log each request
    console.log('[ANVIKSHAKA-X] API Request:', config.method?.toUpperCase(), config.baseURL + config.url)
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export default api