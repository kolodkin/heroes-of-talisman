import { signal, computed, effect } from '@preact/signals-core'

// Auth state signals
export const authToken = signal(null)
export const currentUser = signal(null)
export const authError = signal(null)
export const isLoading = signal(false)

// Computed values
export const isAuthenticated = computed(() => !!authToken.value)

// Session storage key
const AUTH_STORAGE_KEY = 'talis_auth_token'

// Initialize auth state from sessionStorage
function initializeAuthFromStorage() {
  const storedToken = sessionStorage.getItem(AUTH_STORAGE_KEY)
  if (storedToken) {
    try {
      const tokenData = JSON.parse(storedToken)
      // Check if token is not expired
      if (tokenData.expires && Date.now() < tokenData.expires) {
        authToken.value = tokenData.token
        // We'll fetch user data when we have the API client
      } else {
        // Token expired, clear it
        sessionStorage.removeItem(AUTH_STORAGE_KEY)
      }
    } catch (error) {
      console.error('Invalid token in sessionStorage:', error)
      sessionStorage.removeItem(AUTH_STORAGE_KEY)
    }
  }
}

// Effect to sync auth token to sessionStorage
effect(() => {
  if (authToken.value) {
    const tokenData = {
      token: authToken.value,
      expires: Date.now() + (24 * 60 * 60 * 1000), // 24 hours
      timestamp: Date.now()
    }
    sessionStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(tokenData))
  } else {
    sessionStorage.removeItem(AUTH_STORAGE_KEY)
    currentUser.value = null
  }
})

// API client with automatic token injection
async function apiRequest(endpoint, options = {}) {
  const baseUrl = '/api'
  const url = `${baseUrl}${endpoint}`

  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    },
    ...options
  }

  // Add Bearer token if authenticated
  if (authToken.value) {
    config.headers.Authorization = `Bearer ${authToken.value}`
  }

  try {
    const response = await fetch(url, config)

    if (!response.ok) {
      if (response.status === 401) {
        // Token expired or invalid, clear auth state
        logout()
        throw new Error('Authentication required')
      }
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    return await response.json()
  } catch (error) {
    console.error('API request failed:', error)
    throw error
  }
}

// Auth service functions
export const authService = {
  async login(email, password) {
    isLoading.value = true
    authError.value = null

    try {
      const response = await apiRequest('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password })
      })

      authToken.value = response.access_token
      currentUser.value = response.user

      return response
    } catch (error) {
      authError.value = error.message
      throw error
    } finally {
      isLoading.value = false
    }
  },

  async register(email, password) {
    isLoading.value = true
    authError.value = null

    try {
      const response = await apiRequest('/auth/register', {
        method: 'POST',
        body: JSON.stringify({ email, password })
      })

      authToken.value = response.access_token
      currentUser.value = response.user

      return response
    } catch (error) {
      authError.value = error.message
      throw error
    } finally {
      isLoading.value = false
    }
  },

  async getCurrentUser() {
    if (!authToken.value) return null

    try {
      const user = await apiRequest('/auth/me')
      currentUser.value = user
      return user
    } catch (error) {
      console.error('Failed to get current user:', error)
      return null
    }
  },

  logout() {
    authToken.value = null
    currentUser.value = null
    authError.value = null
  }
}

// Export logout function separately for convenience
export const logout = authService.logout

// Test signals for development
export const testSignals = {
  counter: signal(0),
  message: signal('Hello from signals!'),

  increment() {
    testSignals.counter.value++
  },

  updateMessage(newMessage) {
    testSignals.message.value = newMessage
  }
}

// Initialize auth state
initializeAuthFromStorage()
