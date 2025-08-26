<template>
  <div class="min-h-screen pt-8">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="text-center mb-12">
        <h1 class="text-5xl font-bold mb-4 gradient-text">Batch Analysis</h1>
        <p class="text-xl text-gray-600">Process multiple documents simultaneously with AI-powered quality analysis</p>
      </div>

      <!-- Upload Section -->
      <div class="card mb-8">
        <h2 class="text-2xl font-bold mb-6 flex items-center">
          <span class="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center text-white mr-3">📁</span>
          Upload Multiple Documents
        </h2>
        
        <!-- Multi-file Upload Zone -->
        <div 
          ref="uploadZone"
          @click="triggerFileInput"
          @dragover.prevent="handleDragOver"
          @dragleave.prevent="handleDragLeave"
          @drop.prevent="handleDrop"
          :class="[
            'upload-zone',
            { 'dragover': isDragOver }
          ]"
        >
          <div v-if="selectedFiles.length === 0">
            <div class="w-16 h-16 mx-auto mb-4 text-gray-400">
              <svg fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clip-rule="evenodd" />
              </svg>
            </div>
            <p class="text-lg font-medium text-gray-900 mb-2">Drop multiple documents here</p>
            <p class="text-gray-500">or click to browse files</p>
            <p class="text-sm text-gray-400 mt-4">Supports: JPG, PNG, PDF, TIFF (Max 20 files)</p>
          </div>
          
          <div v-else class="text-center">
            <div class="w-12 h-12 bg-green-500 rounded-lg flex items-center justify-center text-white mx-auto mb-4">
              ✓
            </div>
            <p class="font-medium text-gray-900">{{ selectedFiles.length }} files selected</p>
            <p class="text-sm text-gray-500">{{ getTotalFileSize() }}</p>
            <button 
              @click.stop="clearFiles"
              class="mt-2 text-red-500 hover:text-red-700 text-sm"
            >
              Clear All
            </button>
          </div>
        </div>
        
        <input 
          ref="fileInput"
          type="file" 
          accept="image/*,.pdf"
          multiple
          @change="handleFileSelect"
          class="hidden"
        />
      </div>

      <!-- File List -->
      <div v-if="selectedFiles.length > 0" class="card mb-8">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-xl font-bold">Selected Files ({{ selectedFiles.length }})</h3>
          <div class="flex items-center space-x-4">
            <label class="flex items-center">
              <input 
                v-model="selectedProfile"
                type="select"
                class="mr-2"
              />
              <select 
                v-model="selectedProfile"
                class="px-3 py-1 border border-gray-300 rounded-lg text-sm"
              >
                <option value="default">Default Profile</option>
                <option 
                  v-for="(profile, key) in profiles" 
                  :key="key"
                  :value="key"
                >
                  {{ profile.name }}
                </option>
              </select>
            </label>
            <button 
              @click="startBatchAnalysis"
              :disabled="selectedFiles.length === 0 || isBatchAnalyzing"
              class="btn-primary"
            >
              <span v-if="!isBatchAnalyzing">🚀 Start Batch Analysis</span>
              <span v-else class="flex items-center">
                <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                Processing...
              </span>
            </button>
          </div>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-h-96 overflow-y-auto">
          <div 
            v-for="(file, index) in selectedFiles" 
            :key="index"
            class="bg-gray-50 rounded-lg p-4 flex items-center space-x-3"
          >
            <div class="flex-shrink-0 w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clip-rule="evenodd" />
              </svg>
            </div>
            <div class="flex-1 min-w-0">
              <p class="font-medium text-gray-900 truncate">{{ file.name }}</p>
              <p class="text-sm text-gray-500">{{ formatFileSize(file.size) }}</p>
              <div v-if="batchProgress[index]" class="mt-2">
                <div class="progress-bar h-2">
                  <div 
                    class="progress-fill"
                    :style="{ width: `${batchProgress[index].progress}%` }"
                  ></div>
                </div>
                <p class="text-xs text-gray-500 mt-1">{{ batchProgress[index].stage }}</p>
              </div>
            </div>
            <button 
              @click="removeFile(index)"
              :disabled="isBatchAnalyzing"
              class="text-red-500 hover:text-red-700"
            >
              ✕
            </button>
          </div>
        </div>
      </div>

      <!-- Batch Progress -->
      <div v-if="isBatchAnalyzing" class="card mb-8">
        <h3 class="text-xl font-bold mb-4">Batch Progress</h3>
        <div class="mb-4">
          <div class="flex justify-between mb-2">
            <span class="text-sm font-medium text-gray-700">
              Processing {{ completedAnalyses }} of {{ selectedFiles.length }} files
            </span>
            <span class="text-sm text-gray-500">
              {{ Math.round((completedAnalyses / selectedFiles.length) * 100) }}%
            </span>
          </div>
          <div class="progress-bar h-4">
            <div 
              class="progress-fill"
              :style="{ width: `${(completedAnalyses / selectedFiles.length) * 100}%` }"
            ></div>
          </div>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="bg-blue-50 rounded-lg p-4 text-center">
            <div class="text-2xl font-bold text-blue-600">{{ completedAnalyses }}</div>
            <div class="text-sm text-blue-800">Completed</div>
          </div>
          <div class="bg-yellow-50 rounded-lg p-4 text-center">
            <div class="text-2xl font-bold text-yellow-600">{{ selectedFiles.length - completedAnalyses }}</div>
            <div class="text-sm text-yellow-800">Remaining</div>
          </div>
          <div class="bg-green-50 rounded-lg p-4 text-center">
            <div class="text-2xl font-bold text-green-600">{{ passedAnalyses }}</div>
            <div class="text-sm text-green-800">Passed</div>
          </div>
          <div class="bg-red-50 rounded-lg p-4 text-center">
            <div class="text-2xl font-bold text-red-600">{{ failedAnalyses }}</div>
            <div class="text-sm text-red-800">Failed</div>
          </div>
        </div>
      </div>

      <!-- Results Summary -->
      <div v-if="batchResults.length > 0" class="card">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-2xl font-bold">Batch Results</h3>
          <div class="flex space-x-2">
            <button @click="exportBatchResults" class="btn-secondary text-sm">
              📊 Export CSV
            </button>
            <button @click="generateBatchReport" class="btn-primary text-sm">
              📄 Generate Report
            </button>
          </div>
        </div>
        
        <!-- Results Table -->
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr class="border-b border-gray-200">
                <th class="text-left py-3 px-4 font-semibold text-gray-700">File</th>
                <th class="text-left py-3 px-4 font-semibold text-gray-700">Score</th>
                <th class="text-left py-3 px-4 font-semibold text-gray-700">Stars</th>
                <th class="text-left py-3 px-4 font-semibold text-gray-700">Status</th>
                <th class="text-left py-3 px-4 font-semibold text-gray-700">Issues</th>
                <th class="text-left py-3 px-4 font-semibold text-gray-700">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr 
                v-for="(result, index) in batchResults" 
                :key="index"
                class="border-b border-gray-100 hover:bg-gray-50"
              >
                <td class="py-3 px-4">
                  <div class="flex items-center space-x-3">
                    <div class="w-8 h-8 bg-gray-200 rounded flex items-center justify-center text-xs">
                      📄
                    </div>
                    <span class="font-medium truncate max-w-xs">{{ result.filename }}</span>
                  </div>
                </td>
                <td class="py-3 px-4">
                  <div class="font-medium">{{ formatScore(result.score) }}</div>
                </td>
                <td class="py-3 px-4">
                  <div class="text-yellow-500">{{ getStarDisplay(result.stars) }}</div>
                </td>
                <td class="py-3 px-4">
                  <span :class="[
                    'px-2 py-1 rounded-full text-xs font-medium',
                    result.status === 'PASS' ? 'bg-green-100 text-green-800' :
                    result.status === 'WARN' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  ]">
                    {{ result.status }}
                  </span>
                </td>
                <td class="py-3 px-4">
                  <div class="text-sm text-gray-600">
                    {{ getIssueCount(result) }} issues
                  </div>
                </td>
                <td class="py-3 px-4">
                  <button 
                    @click="viewResult(result.analysisId)"
                    class="text-blue-600 hover:text-blue-800 text-sm font-medium"
                  >
                    View Details →
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Batch Statistics -->
        <div class="mt-8 pt-6 border-t border-gray-200">
          <h4 class="text-lg font-semibold mb-4">Batch Statistics</h4>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="text-center">
              <div class="text-3xl font-bold text-blue-600 mb-2">
                {{ (batchResults.reduce((sum, r) => sum + r.score, 0) / batchResults.length * 100).toFixed(1) }}%
              </div>
              <div class="text-gray-600">Average Score</div>
            </div>
            <div class="text-center">
              <div class="text-3xl font-bold text-green-600 mb-2">
                {{ Math.round((passedAnalyses / batchResults.length) * 100) }}%
              </div>
              <div class="text-gray-600">Pass Rate</div>
            </div>
            <div class="text-center">
              <div class="text-3xl font-bold text-purple-600 mb-2">
                {{ batchResults.length }}
              </div>
              <div class="text-gray-600">Documents Processed</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

// State
const uploadZone = ref(null)
const fileInput = ref(null)
const selectedFiles = ref([])
const isDragOver = ref(false)
const selectedProfile = ref('default')
const profiles = ref({})
const isBatchAnalyzing = ref(false)
const batchProgress = ref({})
const batchResults = ref([])

// Computed
const completedAnalyses = computed(() => batchResults.value.length)
const passedAnalyses = computed(() => batchResults.value.filter(r => r.status === 'PASS').length)
const failedAnalyses = computed(() => batchResults.value.filter(r => r.status === 'FAIL').length)

// Methods
const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event) => {
  const files = Array.from(event.target.files)
  addFiles(files)
}

const handleDragOver = () => {
  isDragOver.value = true
}

const handleDragLeave = () => {
  isDragOver.value = false
}

const handleDrop = (event) => {
  isDragOver.value = false
  const files = Array.from(event.dataTransfer.files)
  addFiles(files)
}

const addFiles = (files) => {
  const newFiles = files.filter(file => {
    const isValid = file.type.startsWith('image/') || file.type === 'application/pdf'
    const isUnique = !selectedFiles.value.some(existing => existing.name === file.name)
    return isValid && isUnique
  })

  selectedFiles.value = [...selectedFiles.value, ...newFiles].slice(0, 20) // Max 20 files
  
  if (newFiles.length !== files.length) {
    window.showNotification('Some files were skipped (duplicates or unsupported formats)', 'warning')
  }
}

const removeFile = (index) => {
  selectedFiles.value.splice(index, 1)
}

const clearFiles = () => {
  selectedFiles.value = []
  batchProgress.value = {}
  fileInput.value.value = ''
}

const getTotalFileSize = () => {
  const total = selectedFiles.value.reduce((sum, file) => sum + file.size, 0)
  return formatFileSize(total)
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatScore = (score) => {
  return typeof score === 'number' ? (score * 100).toFixed(0) + '%' : 'N/A'
}

const getStarDisplay = (stars) => {
  return '⭐'.repeat(stars || 0) + '☆'.repeat(Math.max(0, 4 - (stars || 0)))
}

const getIssueCount = (result) => {
  if (!result.analysis?.metrics) return 0
  return Object.values(result.analysis.metrics).filter(m => m.status === 'FAIL').length
}

const startBatchAnalysis = async () => {
  if (selectedFiles.value.length === 0) return
  
  isBatchAnalyzing.value = true
  batchResults.value = []
  
  // Process files one by one (or implement parallel processing)
  for (let i = 0; i < selectedFiles.value.length; i++) {
    const file = selectedFiles.value[i]
    
    try {
      // Initialize progress for this file
      batchProgress.value[i] = {
        progress: 0,
        stage: 'Starting analysis...',
        status: 'processing'
      }
      
      // Create FormData
      const formData = new FormData()
      formData.append('image', file)
      formData.append('profile', selectedProfile.value)
      formData.append('generate_viz', 'false') // Skip visualizations for batch
      
      // Start analysis
      const response = await axios.post('/api/analyze', formData)
      
      if (response.data.success) {
        const analysisId = response.data.analysis_id
        
        // Poll for completion
        await pollAnalysisProgress(analysisId, i, file.name)
      }
      
    } catch (error) {
      batchProgress.value[i] = {
        progress: 100,
        stage: 'Error: ' + error.message,
        status: 'error'
      }
    }
  }
  
  isBatchAnalyzing.value = false
  window.showNotification('Batch analysis completed!', 'success')
}

const pollAnalysisProgress = async (analysisId, fileIndex, filename) => {
  return new Promise((resolve, reject) => {
    const poll = async () => {
      try {
        const response = await axios.get(`/api/analysis/${analysisId}/progress`)
        
        if (response.data.success) {
          const progress = response.data.progress
          
          batchProgress.value[fileIndex] = {
            progress: progress.progress,
            stage: progress.stage,
            status: progress.status
          }
          
          if (progress.status === 'complete') {
            // Add to results
            batchResults.value.push({
              filename,
              analysisId,
              score: progress.results.analysis.global.score,
              stars: progress.results.analysis.global.stars,
              status: progress.results.analysis.global.status,
              analysis: progress.results.analysis
            })
            resolve()
          } else if (progress.status === 'error') {
            reject(new Error(progress.error))
          } else {
            setTimeout(poll, 1000)
          }
        }
      } catch (error) {
        reject(error)
      }
    }
    
    setTimeout(poll, 1000)
  })
}

const viewResult = (analysisId) => {
  router.push(`/results/${analysisId}`)
}

const exportBatchResults = () => {
  // Create CSV data
  const csvData = [
    ['Filename', 'Score', 'Stars', 'Status', 'Failed Metrics'],
    ...batchResults.value.map(result => [
      result.filename,
      (result.score * 100).toFixed(1) + '%',
      result.stars,
      result.status,
      Object.values(result.analysis.metrics || {}).filter(m => m.status === 'FAIL').length
    ])
  ]
  
  const csvContent = csvData.map(row => row.map(field => `"${field}"`).join(',')).join('\n')
  const blob = new Blob([csvContent], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  
  const a = document.createElement('a')
  a.href = url
  a.download = `batch-analysis-${Date.now()}.csv`
  a.click()
  
  URL.revokeObjectURL(url)
}

const generateBatchReport = () => {
  const reportData = {
    summary: {
      totalFiles: batchResults.value.length,
      averageScore: batchResults.value.reduce((sum, r) => sum + r.score, 0) / batchResults.value.length,
      passRate: passedAnalyses.value / batchResults.value.length,
      profile: selectedProfile.value,
      timestamp: new Date().toISOString()
    },
    results: batchResults.value
  }
  
  const dataStr = JSON.stringify(reportData, null, 2)
  const blob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  
  const a = document.createElement('a')
  a.href = url
  a.download = `batch-report-${Date.now()}.json`
  a.click()
  
  URL.revokeObjectURL(url)
}

const loadProfiles = async () => {
  try {
    const response = await axios.get('/api/profiles')
    if (response.data.success) {
      profiles.value = response.data.profiles
    }
  } catch (error) {
    console.error('Failed to load profiles:', error)
  }
}

// Lifecycle
onMounted(() => {
  loadProfiles()
})
</script>
