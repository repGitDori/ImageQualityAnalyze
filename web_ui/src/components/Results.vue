<template>
  <div class="min-h-screen pt-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      
      <!-- Loading State -->
      <div v-if="isLoading" class="flex items-center justify-center py-20">
        <div class="text-center">
          <div class="w-16 h-16 mx-auto mb-4">
            <div class="w-full h-full border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
          </div>
          <p class="text-gray-600">Loading analysis results...</p>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="card-dark text-center py-20">
        <div class="w-16 h-16 mx-auto mb-4 text-red-500">❌</div>
        <h2 class="text-2xl font-bold mb-2">Analysis Not Found</h2>
        <p class="text-gray-400 mb-6">{{ error }}</p>
        <router-link to="/analyze" class="btn-primary">
          Start New Analysis
        </router-link>
      </div>

      <!-- Results Display -->
      <div v-else-if="results" class="space-y-8">
        
        <!-- Header with Score -->
        <div class="card text-center">
          <div class="flex items-center justify-between mb-6">
            <h1 class="text-3xl font-bold">Analysis Results</h1>
            <div class="flex items-center space-x-4">
              <button 
                @click="exportResults" 
                class="btn-secondary text-sm"
              >
                📄 Export Report
              </button>
              <router-link to="/analyze" class="btn-primary text-sm">
                🔍 Analyze Another
              </router-link>
            </div>
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div class="bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-2xl p-6">
              <div class="text-3xl font-bold mb-2">{{ formatScore(results.analysis.global.score) }}</div>
              <div class="text-blue-100">Overall Score</div>
            </div>
            <div class="bg-gradient-to-r from-yellow-400 to-yellow-600 text-white rounded-2xl p-6">
              <div class="text-3xl mb-2">{{ getStarDisplay(results.analysis.global.stars) }}</div>
              <div class="text-yellow-100">Star Rating</div>
            </div>
            <div :class="[
              'rounded-2xl p-6 text-white',
              results.analysis.global.status === 'PASS' ? 'bg-gradient-to-r from-green-500 to-green-600' :
              results.analysis.global.status === 'WARN' ? 'bg-gradient-to-r from-yellow-500 to-yellow-600' :
              'bg-gradient-to-r from-red-500 to-red-600'
            ]">
              <div class="text-2xl font-bold mb-2">{{ results.analysis.global.status }}</div>
              <div class="opacity-80">Quality Status</div>
            </div>
            <div class="bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-2xl p-6">
              <div class="text-3xl font-bold mb-2">{{ Object.keys(results.analysis.metrics).length }}</div>
              <div class="text-purple-100">Metrics Analyzed</div>
            </div>
          </div>
        </div>

        <!-- Metrics Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div 
            v-for="(metric, key) in results.analysis.metrics" 
            :key="key"
            class="card hover:shadow-2xl transform hover:scale-105"
          >
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-bold capitalize">{{ formatMetricName(key) }}</h3>
              <div :class="[
                'px-3 py-1 rounded-full text-sm font-medium',
                getMetricStatusClass(metric.status)
              ]">
                {{ metric.status }}
              </div>
            </div>
            
            <div class="space-y-3">
              <div v-if="metric.score !== undefined" class="flex justify-between">
                <span class="text-gray-600">Score:</span>
                <span class="font-medium">{{ formatScore(metric.score) }}</span>
              </div>
              
              <!-- Metric-specific details -->
              <div v-if="key === 'sharpness' && metric.variance" class="flex justify-between">
                <span class="text-gray-600">Variance:</span>
                <span class="font-medium">{{ metric.variance.toFixed(1) }}</span>
              </div>
              
              <div v-if="key === 'exposure' && metric.shadow_clipping !== undefined" class="flex justify-between">
                <span class="text-gray-600">Shadow Clipping:</span>
                <span class="font-medium">{{ (metric.shadow_clipping * 100).toFixed(1) }}%</span>
              </div>
              
              <div v-if="metric.message" class="text-sm text-gray-600 bg-gray-50 p-2 rounded">
                {{ metric.message }}
              </div>
            </div>
          </div>
        </div>

        <!-- Visualizations -->
        <div v-if="results.visualizations && results.visualizations.length > 0" class="card">
          <h2 class="text-2xl font-bold mb-6 flex items-center">
            <span class="w-8 h-8 bg-purple-500 rounded-lg flex items-center justify-center text-white mr-3">📊</span>
            Quality Visualizations
          </h2>
          
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div 
              v-for="viz in results.visualizations" 
              :key="viz.type"
              class="bg-gray-50 rounded-xl p-4 hover:bg-gray-100 transition-colors cursor-pointer"
              @click="openVisualization(viz)"
            >
              <div class="aspect-w-16 aspect-h-9 mb-3">
                <img 
                  :src="`/api/visualization/${viz.path}`"
                  :alt="viz.type"
                  class="w-full h-40 object-cover rounded-lg"
                  @error="handleImageError"
                />
              </div>
              <h3 class="font-semibold capitalize text-center">
                {{ formatVisualizationType(viz.type) }}
              </h3>
            </div>
          </div>
        </div>

        <!-- Recommendations -->
        <div v-if="recommendations.length > 0" class="card">
          <h2 class="text-2xl font-bold mb-6 flex items-center">
            <span class="w-8 h-8 bg-green-500 rounded-lg flex items-center justify-center text-white mr-3">💡</span>
            Recommendations
          </h2>
          
          <div class="space-y-3">
            <div 
              v-for="(rec, index) in recommendations" 
              :key="index"
              :class="[
                'flex items-start space-x-3 p-4 rounded-lg',
                rec.type === 'error' ? 'bg-red-50 border border-red-200' :
                rec.type === 'warning' ? 'bg-yellow-50 border border-yellow-200' :
                'bg-blue-50 border border-blue-200'
              ]"
            >
              <div :class="[
                'w-6 h-6 rounded-full flex items-center justify-center text-white text-sm font-bold',
                rec.type === 'error' ? 'bg-red-500' :
                rec.type === 'warning' ? 'bg-yellow-500' :
                'bg-blue-500'
              ]">
                {{ rec.type === 'error' ? '!' : rec.type === 'warning' ? '⚠' : 'i' }}
              </div>
              <div class="flex-1">
                <p :class="[
                  'font-medium',
                  rec.type === 'error' ? 'text-red-800' :
                  rec.type === 'warning' ? 'text-yellow-800' :
                  'text-blue-800'
                ]">
                  {{ rec.title }}
                </p>
                <p :class="[
                  'text-sm mt-1',
                  rec.type === 'error' ? 'text-red-600' :
                  rec.type === 'warning' ? 'text-yellow-600' :
                  'text-blue-600'
                ]">
                  {{ rec.message }}
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Metadata -->
        <div v-if="results.metadata" class="card">
          <h2 class="text-2xl font-bold mb-6">Analysis Details</h2>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div class="bg-gray-50 p-4 rounded-lg">
              <span class="text-gray-600">Filename:</span><br>
              <span class="font-medium">{{ results.metadata.filename }}</span>
            </div>
            <div class="bg-gray-50 p-4 rounded-lg">
              <span class="text-gray-600">Profile Used:</span><br>
              <span class="font-medium capitalize">{{ results.metadata.profile_used }}</span>
            </div>
            <div class="bg-gray-50 p-4 rounded-lg">
              <span class="text-gray-600">Analysis Time:</span><br>
              <span class="font-medium">{{ formatTimestamp(results.metadata.timestamp) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Visualization Modal -->
    <div 
      v-if="selectedVisualization" 
      class="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4"
      @click="closeVisualization"
    >
      <div class="bg-white rounded-2xl p-6 max-w-4xl max-h-full overflow-auto" @click.stop>
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-xl font-bold capitalize">{{ formatVisualizationType(selectedVisualization.type) }}</h3>
          <button 
            @click="closeVisualization"
            class="text-gray-500 hover:text-gray-700 text-2xl"
          >
            ✕
          </button>
        </div>
        <img 
          :src="`/api/visualization/${selectedVisualization.path}`"
          :alt="selectedVisualization.type"
          class="w-full h-auto rounded-lg"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()

// Props
const props = defineProps({
  id: String
})

// State
const isLoading = ref(true)
const error = ref(null)
const results = ref(null)
const selectedVisualization = ref(null)

// Computed
const recommendations = computed(() => {
  if (!results.value?.analysis?.metrics) return []
  
  const recs = []
  const metrics = results.value.analysis.metrics
  
  // Generate recommendations based on failed metrics
  Object.entries(metrics).forEach(([key, metric]) => {
    if (metric.status === 'FAIL') {
      recs.push(getRecommendation(key, metric))
    } else if (metric.status === 'WARN') {
      recs.push(getRecommendation(key, metric, 'warning'))
    }
  })
  
  return recs
})

// Methods
const loadResults = async () => {
  try {
    isLoading.value = true
    const analysisId = props.id || route.params.id
    
    const response = await axios.get(`/api/analysis/${analysisId}/progress`)
    
    if (response.data.success && response.data.status === 'complete') {
      results.value = response.data.results
    } else if (response.data.status === 'error') {
      error.value = response.data.error
    } else {
      error.value = 'Analysis not complete or not found'
    }
    
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to load results'
  } finally {
    isLoading.value = false
  }
}

const formatScore = (score) => {
  return typeof score === 'number' ? (score * 100).toFixed(0) + '%' : 'N/A'
}

const getStarDisplay = (stars) => {
  return '⭐'.repeat(stars || 0) + '☆'.repeat(Math.max(0, 4 - (stars || 0)))
}

const formatMetricName = (name) => {
  return name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const getMetricStatusClass = (status) => {
  switch (status) {
    case 'PASS':
      return 'bg-green-100 text-green-800'
    case 'WARN':
      return 'bg-yellow-100 text-yellow-800'
    case 'FAIL':
      return 'bg-red-100 text-red-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

const formatVisualizationType = (type) => {
  return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const formatTimestamp = (timestamp) => {
  return new Date(timestamp).toLocaleString()
}

const getRecommendation = (metricKey, metric, type = 'error') => {
  const recommendations = {
    sharpness: {
      title: 'Improve Image Sharpness',
      message: 'Use a tripod, ensure proper focus, or increase shutter speed to reduce blur.'
    },
    exposure: {
      title: 'Adjust Exposure Settings',
      message: 'Balance lighting conditions or adjust camera exposure settings.'
    },
    contrast: {
      title: 'Enhance Image Contrast',
      message: 'Improve lighting conditions or post-process to increase contrast.'
    },
    completeness: {
      title: 'Capture Complete Document',
      message: 'Ensure the entire document is visible with proper margins.'
    },
    geometry: {
      title: 'Correct Document Alignment',
      message: 'Hold camera parallel to document or use perspective correction.'
    },
    resolution: {
      title: 'Increase Image Resolution',
      message: 'Scan or photograph at higher DPI/resolution settings.'
    }
  }
  
  return {
    type,
    ...recommendations[metricKey] || {
      title: `Review ${formatMetricName(metricKey)}`,
      message: 'Check the quality settings for this metric.'
    }
  }
}

const openVisualization = (viz) => {
  selectedVisualization.value = viz
}

const closeVisualization = () => {
  selectedVisualization.value = null
}

const handleImageError = (event) => {
  event.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjEwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZGRkIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkltYWdlIG5vdCBhdmFpbGFibGU8L3RleHQ+PC9zdmc+'
}

const exportResults = () => {
  const dataStr = JSON.stringify(results.value, null, 2)
  const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr)
  
  const exportFileDefaultName = `analysis-results-${Date.now()}.json`
  
  const linkElement = document.createElement('a')
  linkElement.setAttribute('href', dataUri)
  linkElement.setAttribute('download', exportFileDefaultName)
  linkElement.click()
}

// Lifecycle
onMounted(() => {
  loadResults()
})
</script>
