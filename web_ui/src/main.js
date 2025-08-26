import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import './style.css'

// Import components
import Home from './components/Home.vue'
import Analyzer from './components/Analyzer.vue'
import Results from './components/Results.vue'
import BatchAnalysis from './components/BatchAnalysis.vue'

// Router configuration
const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/analyze', name: 'Analyzer', component: Analyzer },
  { path: '/results/:id', name: 'Results', component: Results, props: true },
  { path: '/batch', name: 'BatchAnalysis', component: BatchAnalysis },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Pinia store
const pinia = createPinia()

// Create and mount app
const app = createApp(App)

// Add global notification system
window.showNotification = (message, type = 'info') => {
  // Create notification element
  const notification = document.createElement('div')
  notification.className = `fixed top-4 right-4 z-50 px-6 py-4 rounded-lg shadow-lg text-white transform transition-all duration-500 translate-x-full ${
    type === 'error' ? 'bg-red-500' : 
    type === 'success' ? 'bg-green-500' : 
    type === 'warning' ? 'bg-yellow-500' : 'bg-blue-500'
  }`
  notification.textContent = message
  
  document.body.appendChild(notification)
  
  // Animate in
  setTimeout(() => {
    notification.style.transform = 'translateX(0)'
  }, 100)
  
  // Auto remove after 5 seconds
  setTimeout(() => {
    notification.style.transform = 'translateX(100%)'
    setTimeout(() => {
      if (notification.parentNode) {
        notification.parentNode.removeChild(notification)
      }
    }, 500)
  }, 5000)
}

app.use(pinia)
app.use(router)

app.mount('#app')
