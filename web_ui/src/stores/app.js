import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAppStore = defineStore('app', () => {
  // State
  const isLoading = ref(false)
  const currentAnalysis = ref(null)
  const analyses = ref([])
  const profiles = ref({})
  
  // Getters
  const analysisCount = computed(() => analyses.value.length)
  const hasAnalyses = computed(() => analyses.value.length > 0)
  
  // Actions
  const setLoading = (loading) => {
    isLoading.value = loading
  }
  
  const addAnalysis = (analysis) => {
    analyses.value.unshift(analysis)
    
    // Keep only last 10 analyses
    if (analyses.value.length > 10) {
      analyses.value = analyses.value.slice(0, 10)
    }
    
    // Save to localStorage
    localStorage.setItem('recentAnalyses', JSON.stringify(analyses.value))
  }
  
  const setCurrentAnalysis = (analysis) => {
    currentAnalysis.value = analysis
  }
  
  const setProfiles = (profileData) => {
    profiles.value = profileData
  }
  
  const getAnalysisById = (id) => {
    return analyses.value.find(analysis => analysis.id === id)
  }
  
  const loadFromStorage = () => {
    const stored = localStorage.getItem('recentAnalyses')
    if (stored) {
      try {
        analyses.value = JSON.parse(stored)
      } catch (error) {
        console.error('Failed to load analyses from storage:', error)
      }
    }
  }
  
  const clearAnalyses = () => {
    analyses.value = []
    localStorage.removeItem('recentAnalyses')
  }
  
  return {
    // State
    isLoading,
    currentAnalysis,
    analyses,
    profiles,
    
    // Getters
    analysisCount,
    hasAnalyses,
    
    // Actions
    setLoading,
    addAnalysis,
    setCurrentAnalysis,
    setProfiles,
    getAnalysisById,
    loadFromStorage,
    clearAnalyses
  }
})
