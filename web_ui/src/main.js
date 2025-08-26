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

app.use(pinia)
app.use(router)

app.mount('#app')
