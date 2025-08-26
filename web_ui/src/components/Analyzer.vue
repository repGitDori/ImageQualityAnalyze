<template>
  <div class="min-h-screen pt-8">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="text-center mb-12">
        <h1 class="text-5xl font-bold mb-4 gradient-text">AI Document Analyzer</h1>
        <p class="text-xl text-gray-600">Upload your document for instant quality analysis with AI-powered insights</p>
      </div>

      <!-- Main Analysis Interface -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-12">
        
        <!-- Upload Section -->
        <div class="card">
          <h2 class="text-2xl font-bold mb-6 flex items-center">
            <span class="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center text-white mr-3">📁</span>
            Upload Document
          </h2>
          
          <!-- File Upload Zone -->
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
            <div v-if="!selectedFile">
              <div class="w-16 h-16 mx-auto mb-4 text-gray-400">
                <svg fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clip-rule="evenodd" />
                </svg>
              </div>
              <p class="text-lg font-medium text-gray-900 mb-2">Drop your document here</p>
              <p class="text-gray-500">or click to browse files</p>
              <p class="text-sm text-gray-400 mt-4">Supports: JPG, PNG, PDF, TIFF</p>
            </div>
            
            <div v-else class="flex items-center justify-center space-x-4">
              <div class="w-12 h-12 bg-green-500 rounded-lg flex items-center justify-center text-white">
                ✓
              </div>
              <div>
                <p class="font-medium text-gray-900">{{ selectedFile.name }}</p>
                <p class="text-sm text-gray-500">{{ formatFileSize(selectedFile.size) }}</p>
              </div>
              <button 
                @click.stop="clearFile"
                class="text-red-500 hover:text-red-700"
              >
                ✕
              </button>
            </div>
          </div>
          
          <input 
            ref="fileInput"
            type="file" 
            accept="image/*,.pdf"
            @change="handleFileSelect"
            class="hidden"
          />
          
          <!-- Configuration Options -->
          <div class="mt-8">
            <h3 class="text-lg font-semibold mb-4">Analysis Settings</h3>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Quality Profile
                </label>
                <select 
                  v-model="selectedProfile"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="default">Default</option>
                  <option 
                    v-for="(profile, key) in profiles" 
                    :key="key"
                    :value="key"
                  >
                    {{ profile.name }}
                  </option>
                </select>
              </div>
              
              <div class="flex items-center">
                <input 
                  id="generateViz"
                  v-model="generateVisualizations"
                  type="checkbox" 
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label for="generateViz" class="ml-2 block text-sm text-gray-900">
                  Generate Visualizations
                </label>
              </div>
            </div>
          </div>
          
          <!-- Action Button -->
          <div class="mt-8">
            <button 
              @click="startAnalysis"
              :disabled="!selectedFile || isAnalyzing"
              :class="[
                'w-full btn-primary text-lg py-4',
                !selectedFile || isAnalyzing ? 'opacity-50 cursor-not-allowed' : ''
              ]"
            >
              <span v-if="!isAnalyzing">🚀 Start Analysis</span>
              <span v-else class="flex items-center justify-center">
                <div class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                Analyzing...
              </span>
            </button>
          </div>
        </div>
        
        <!-- Progress/Preview Section -->
        <div class="card">
          <h2 class="text-2xl font-bold mb-6 flex items-center">
            <span class="w-8 h-8 bg-purple-500 rounded-lg flex items-center justify-center text-white mr-3">📊</span>
            Analysis Progress
          </h2>
          
          <!-- File Preview -->
          <div v-if="selectedFile && previewUrl" class="mb-6">
            <img 
              :src="previewUrl" 
              :alt="selectedFile.name"
              class="w-full max-h-64 object-contain rounded-lg border border-gray-200"
            />
          </div>
          
          <!-- Progress Display -->
          <div v-if="isAnalyzing && analysisProgress" class="space-y-4">
            <div>
              <div class="flex justify-between mb-2">
                <span class="text-sm font-medium text-gray-700">{{ analysisProgress.stage }}</span>
                <span class="text-sm text-gray-500">{{ analysisProgress.progress }}%</span>
              </div>
              <div class="progress-bar">
                <div 
                  class="progress-fill"
                  :style="{ width: `${analysisProgress.progress}%` }"
                ></div>
              </div>
            </div>
            
            <!-- Live Updates -->
            <div class="bg-gray-50 rounded-lg p-4">
              <div class="flex items-center space-x-2">
                <div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span class="text-sm text-gray-700">Live Analysis Updates</span>
              </div>
            </div>
          </div>
          
          <!-- Results Preview -->
          <div v-else-if="!isAnalyzing && !selectedFile" class="text-center py-12">
            <div class="w-16 h-16 mx-auto mb-4 text-gray-300">
              <svg fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd" />
              </svg>
            </div>
            <p class="text-gray-500">Upload a document to see analysis progress</p>
          </div>
          
          <!-- Quick Stats -->
          <div v-if="selectedFile && !isAnalyzing" class="grid grid-cols-2 gap-4 mt-6">
            <div class="bg-blue-50 rounded-lg p-4 text-center">
              <div class="text-2xl font-bold text-blue-600">11</div>
              <div class="text-sm text-blue-800">Quality Metrics</div>
            </div>
            <div class="bg-purple-50 rounded-lg p-4 text-center">
              <div class="text-2xl font-bold text-purple-600">6</div>
              <div class="text-sm text-purple-800">Visualizations</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Recent Analyses -->
      <div v-if="recentAnalyses.length > 0" class="mt-12">
        <h2 class="text-2xl font-bold mb-6">Recent Analyses</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div 
            v-for="analysis in recentAnalyses" 
            :key="analysis.id"
            @click="viewResults(analysis.id)"
            class="card cursor-pointer hover:shadow-2xl transform hover:scale-105"
          >
            <div class="flex items-center justify-between mb-3">
              <h3 class="font-semibold truncate">{{ analysis.filename }}</h3>
              <div :class="[
                'px-2 py-1 rounded text-xs font-medium',
                analysis.status === 'PASS' ? 'bg-green-100 text-green-800' :
                analysis.status === 'WARN' ? 'bg-yellow-100 text-yellow-800' :
                'bg-red-100 text-red-800'
              ]">
                {{ analysis.status }}
              </div>
            </div>
            <div class="flex items-center justify-between text-sm text-gray-500">
              <span>Score: {{ analysis.score }}/1.0</span>
              <span>{{ analysis.stars }} ⭐</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

// Refs
const uploadZone = ref(null)
const fileInput = ref(null)
const selectedFile = ref(null)
const previewUrl = ref(null)
const isDragOver = ref(false)
const isAnalyzing = ref(false)
const selectedProfile = ref('default')
const generateVisualizations = ref(true)
const profiles = ref({})
const analysisProgress = ref(null)
const recentAnalyses = ref([])

// Methods
const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event) => {
  const files = event.target.files
  if (files && files[0]) {
    setSelectedFile(files[0])
  }
}

const handleDragOver = (event) => {
  isDragOver.value = true
}

const handleDragLeave = (event) => {
  isDragOver.value = false
}

const handleDrop = (event) => {
  isDragOver.value = false
  const files = event.dataTransfer.files
  if (files && files[0]) {
    setSelectedFile(files[0])
  }
}

const setSelectedFile = (file) => {
  selectedFile.value = file
  
  // Create preview URL
  if (file.type.startsWith('image/')) {
    previewUrl.value = URL.createObjectURL(file)
  }
}

const clearFile = () => {
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
  }
  selectedFile.value = null
  previewUrl.value = null
  fileInput.value.value = ''
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const startAnalysis = async () => {
  if (!selectedFile.value) return
  
  try {
    isAnalyzing.value = true
    
    const formData = new FormData()
    formData.append('image', selectedFile.value)
    formData.append('profile', selectedProfile.value)
    formData.append('generate_viz', generateVisualizations.value)
    
    const response = await axios.post('/api/analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    if (response.data.success) {
      const analysisId = response.data.analysis_id
      
      // Poll for progress
      const pollProgress = async () => {
        try {
          const progressResponse = await axios.get(`/api/analysis/${analysisId}/progress`)
          if (progressResponse.data.success) {
            analysisProgress.value = progressResponse.data
            
            if (progressResponse.data.status === 'complete') {
              // Analysis complete, navigate to results
              isAnalyzing.value = false
              router.push(`/results/${analysisId}`)
            } else if (progressResponse.data.status === 'error') {
              // Handle error
              isAnalyzing.value = false
              window.showNotification(`Analysis failed: ${progressResponse.data.error}`, 'error')
            } else {
              // Continue polling
              setTimeout(pollProgress, 1000)
            }
          }
        } catch (error) {
          console.error('Progress polling error:', error)
          isAnalyzing.value = false
          window.showNotification('Failed to get analysis progress', 'error')
        }
      }
      
      // Start polling
      setTimeout(pollProgress, 1000)
      
    } else {
      throw new Error(response.data.error || 'Analysis failed')
    }
    
  } catch (error) {
    console.error('Analysis error:', error)
    isAnalyzing.value = false
    window.showNotification(error.response?.data?.error || 'Analysis failed', 'error')
  }
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

const viewResults = (analysisId) => {
  router.push(`/results/${analysisId}`)
}

// Lifecycle
onMounted(() => {
  loadProfiles()
  
  // Load recent analyses from localStorage
  const stored = localStorage.getItem('recentAnalyses')
  if (stored) {
    try {
      recentAnalyses.value = JSON.parse(stored)
    } catch (error) {
      console.error('Failed to load recent analyses:', error)
    }
  }
})

// Cleanup preview URL when component unmounts
watch(() => selectedFile.value, (newFile, oldFile) => {
  if (oldFile && previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
    previewUrl.value = null
  }
})
</script>
