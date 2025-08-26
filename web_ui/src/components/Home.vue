<template>
  <div class="min-h-screen pt-8">
    <!-- Hero Section -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="text-center mb-16">
        <div class="animate-fadeInUp">
          <h1 class="text-6xl font-bold mb-6">
            <span class="gradient-text">AI-Powered</span><br>
            Document Quality Analysis
          </h1>
          <p class="text-xl text-gray-700 mb-8 max-w-3xl mx-auto">
            Experience the future of document analysis with real-time AI insights, 
            stunning visualizations, and professional-grade quality assessments.
          </p>
          
          <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <router-link 
              to="/analyze" 
              class="btn-primary text-lg px-8 py-4"
            >
              🚀 Start Analysis
            </router-link>
            <button 
              @click="scrollToFeatures" 
              class="btn-secondary text-lg px-8 py-4"
            >
              📖 Learn More
            </button>
          </div>
        </div>
      </div>

      <!-- Stats Section -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-8 mb-20">
        <div 
          v-for="(stat, index) in stats" 
          :key="stat.label"
          class="card text-center transform hover:scale-105"
          :style="{ animationDelay: `${index * 0.1}s` }"
        >
          <div class="text-4xl mb-2">{{ stat.icon }}</div>
          <div class="text-3xl font-bold text-blue-600 mb-1">{{ stat.value }}</div>
          <div class="text-gray-600">{{ stat.label }}</div>
        </div>
      </div>

      <!-- Features Section -->
      <div ref="featuresSection" class="mb-20">
        <h2 class="text-4xl font-bold text-center mb-12 gradient-text">
          Revolutionary Features
        </h2>
        
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-12">
          <div 
            v-for="(feature, index) in features" 
            :key="feature.title"
            class="card flex items-start space-x-6"
            :class="{ 'animate-slideInRight': index % 2 === 0, 'animate-fadeInUp': index % 2 === 1 }"
          >
            <div class="flex-shrink-0">
              <div class="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center text-2xl">
                {{ feature.icon }}
              </div>
            </div>
            <div>
              <h3 class="text-2xl font-bold mb-3">{{ feature.title }}</h3>
              <p class="text-gray-600 mb-4">{{ feature.description }}</p>
              <ul class="space-y-2">
                <li 
                  v-for="point in feature.points" 
                  :key="point"
                  class="flex items-center text-sm text-gray-700"
                >
                  <svg class="w-4 h-4 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                  </svg>
                  {{ point }}
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <!-- Demo Section -->
      <div class="bg-gradient-to-r from-blue-600 to-purple-700 rounded-3xl p-12 text-white text-center mb-20">
        <h2 class="text-4xl font-bold mb-6">See It In Action</h2>
        <p class="text-xl mb-8 opacity-90">
          Upload a document and watch our AI analyze it in real-time with stunning visualizations
        </p>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
          <div 
            v-for="(step, index) in demoSteps" 
            :key="step.title"
            class="text-center"
          >
            <div class="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center text-2xl mb-4 mx-auto">
              {{ step.icon }}
            </div>
            <h3 class="text-xl font-semibold mb-2">{{ step.title }}</h3>
            <p class="text-white/80">{{ step.description }}</p>
          </div>
        </div>
        
        <router-link 
          to="/analyze" 
          class="inline-block bg-white text-blue-600 px-8 py-4 rounded-xl font-semibold hover:bg-blue-50 transform hover:scale-105 transition-all duration-300"
        >
          Try Demo Now →
        </router-link>
      </div>

      <!-- Technology Stack -->
      <div class="text-center mb-20">
        <h2 class="text-3xl font-bold mb-8 gradient-text">Powered by Cutting-Edge Technology</h2>
        <div class="flex flex-wrap justify-center items-center gap-8 opacity-70">
          <div v-for="tech in technologies" :key="tech.name" class="flex items-center space-x-2">
            <span class="text-2xl">{{ tech.icon }}</span>
            <span class="font-medium">{{ tech.name }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const featuresSection = ref(null)

const stats = [
  { icon: '⚡', value: '<1s', label: 'Analysis Time' },
  { icon: '🎯', value: '11+', label: 'Quality Metrics' },
  { icon: '📊', value: '6', label: 'Visualizations' },
  { icon: '🌟', value: '99%', label: 'Accuracy' }
]

const features = [
  {
    icon: '🧠',
    title: 'AI-Powered Analysis',
    description: 'Advanced computer vision algorithms analyze every aspect of your document',
    points: [
      'Real-time quality assessment',
      'Machine learning optimization',
      'Professional-grade accuracy'
    ]
  },
  {
    icon: '📊',
    title: 'Stunning Visualizations',
    description: 'Interactive charts and heatmaps reveal quality insights instantly',
    points: [
      'Sharpness heatmaps',
      'Illumination analysis',
      'Document structure overlay'
    ]
  },
  {
    icon: '⚙️',
    title: 'Configurable Profiles',
    description: 'Tailored analysis profiles for different document types and requirements',
    points: [
      'Archival quality standards',
      'Document-specific settings',
      'Custom thresholds'
    ]
  },
  {
    icon: '📱',
    title: 'Modern Interface',
    description: 'Intuitive, responsive design with real-time progress tracking',
    points: [
      'Drag & drop upload',
      'Live progress updates',
      'Mobile-friendly design'
    ]
  }
]

const demoSteps = [
  {
    icon: '📤',
    title: 'Upload',
    description: 'Drag & drop your document or click to browse'
  },
  {
    icon: '🔍',
    title: 'Analyze',
    description: 'AI processes your document in real-time'
  },
  {
    icon: '📊',
    title: 'Results',
    description: 'Get detailed insights with stunning visualizations'
  }
]

const technologies = [
  { name: 'Vue 3', icon: '💚' },
  { name: 'Python', icon: '🐍' },
  { name: 'OpenCV', icon: '👁️' },
  { name: 'TailwindCSS', icon: '🎨' },
  { name: 'Chart.js', icon: '📈' },
  { name: 'Three.js', icon: '🌐' }
]

const scrollToFeatures = () => {
  featuresSection.value?.scrollIntoView({ behavior: 'smooth' })
}

onMounted(() => {
  // Add entrance animations
  const cards = document.querySelectorAll('.card')
  cards.forEach((card, index) => {
    card.style.animationDelay = `${index * 0.1}s`
    card.classList.add('animate-fadeInUp')
  })
})
</script>

<style scoped>
/* Additional component-specific styles */
.hero-bg {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
}
</style>
