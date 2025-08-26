<template>
  <div id="app" class="min-h-screen">
    <!-- Animated Background -->
    <div id="particles-js"></div>
    
    <!-- Navigation -->
    <nav class="relative z-10 bg-white/10 backdrop-blur-md border-b border-white/20">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <router-link to="/" class="flex items-center space-x-3">
              <div class="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clip-rule="evenodd" />
                </svg>
              </div>
              <span class="text-2xl font-bold gradient-text">ImageQualityAnalyzer</span>
            </router-link>
          </div>
          
          <div class="flex items-center space-x-6">
            <router-link 
              v-for="route in navRoutes" 
              :key="route.name"
              :to="route.path" 
              :class="[
                'px-3 py-2 rounded-lg text-sm font-medium transition-all duration-300',
                $route.path === route.path 
                  ? 'bg-white/20 text-gray-900' 
                  : 'text-gray-700 hover:bg-white/10 hover:text-gray-900'
              ]"
            >
              {{ route.name }}
            </router-link>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="relative z-10">
      <router-view v-slot="{ Component, route }">
        <transition 
          :name="route.meta.transition || 'fade'"
          mode="out-in"
          appear
        >
          <component :is="Component" :key="route.path" />
        </transition>
      </router-view>
    </main>

    <!-- Global Loading Overlay -->
    <div v-if="isLoading" class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center">
      <div class="bg-white rounded-2xl p-8 text-center max-w-sm mx-4">
        <div class="w-16 h-16 mx-auto mb-4">
          <div class="w-full h-full border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
        </div>
        <h3 class="text-lg font-semibold text-gray-900 mb-2">Processing...</h3>
        <p class="text-gray-600">{{ loadingMessage }}</p>
      </div>
    </div>

    <!-- Notifications -->
    <div class="fixed top-4 right-4 z-50 space-y-2">
      <div
        v-for="notification in notifications"
        :key="notification.id"
        :class="[
          'p-4 rounded-lg shadow-lg backdrop-blur-md transform transition-all duration-300',
          notification.type === 'success' ? 'bg-green-500/90 text-white' :
          notification.type === 'error' ? 'bg-red-500/90 text-white' :
          notification.type === 'warning' ? 'bg-yellow-500/90 text-white' :
          'bg-blue-500/90 text-white'
        ]"
      >
        <div class="flex items-center space-x-3">
          <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
          </svg>
          <span>{{ notification.message }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from './stores/app'

const router = useRouter()
const appStore = useAppStore()

// Navigation routes
const navRoutes = [
  { name: 'Home', path: '/' },
  { name: 'Analyze', path: '/analyze' },
  { name: 'Batch Analysis', path: '/batch' }
]

// Reactive state
const isLoading = ref(false)
const loadingMessage = ref('')
const notifications = ref([])

// Initialize particles.js for background animation
onMounted(async () => {
  try {
    // Dynamic import of particles.js
    const particlesJS = await import('particles.js')
    
    // Initialize particles
    window.particlesJS('particles-js', {
      particles: {
        number: { value: 80, density: { enable: true, value_area: 800 } },
        color: { value: '#ffffff' },
        shape: { type: 'circle' },
        opacity: { value: 0.1, random: false },
        size: { value: 3, random: true },
        line_linked: {
          enable: true,
          distance: 150,
          color: '#ffffff',
          opacity: 0.1,
          width: 1
        },
        move: {
          enable: true,
          speed: 2,
          direction: 'none',
          random: false,
          straight: false,
          out_mode: 'out',
          bounce: false
        }
      },
      interactivity: {
        detect_on: 'canvas',
        events: {
          onhover: { enable: true, mode: 'grab' },
          onclick: { enable: true, mode: 'push' },
          resize: true
        },
        modes: {
          grab: { distance: 140, line_linked: { opacity: 0.2 } },
          push: { particles_nb: 4 }
        }
      },
      retina_detect: true
    })
  } catch (error) {
    console.warn('Particles.js failed to load:', error)
  }
})

// Global event handlers
const showNotification = (message, type = 'info', duration = 3000) => {
  const id = Date.now()
  notifications.value.push({ id, message, type })
  
  setTimeout(() => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }, duration)
}

// Expose methods globally
window.showNotification = showNotification
window.setLoading = (loading, message = '') => {
  isLoading.value = loading
  loadingMessage.value = message
}
</script>

<style scoped>
/* Route transition animations */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from {
  transform: translateX(30px);
  opacity: 0;
}

.slide-leave-to {
  transform: translateX(-30px);
  opacity: 0;
}
</style>
