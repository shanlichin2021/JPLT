<template>
  <div class="analysis-page">

    <!-- Drag Overlay -->
    <div v-if="isDragging" class="drag-overlay">
      <div class="drag-content">
        <div class="drag-icon">📄</div>
        <div class="drag-title">Drop image here</div>
        <div class="drag-description">OCR will extract the Japanese text</div>
      </div>
    </div>

    <!-- Error display -->
    <div v-if="error" class="error-message">
      <i class="fas fa-exclamation-triangle"></i>
      <div class="error-content">
        <strong>Analysis Error:</strong> 
        <span>{{ error }}</span>
      </div>
    </div>
    
    <!-- Processing status -->
    <div v-if="isExtracting" class="processing-status">
      <div class="processing-spinner">
        <i class="fas fa-cog fa-spin"></i>
      </div>
      <span class="processing-text">Extracting text from image...</span>
    </div>

    <!-- Enhanced Stats Overview -->
    <div v-if="analysisResult.length > 0" class="stats-section">
      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-list"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ analysisResult.length }}</div>
          <div class="stat-label">Tokens</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-book"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ kanjiList.length }}</div>
          <div class="stat-label">Vocabulary</div>
        </div>
      </div>
      <div v-if="syntacticPatterns.length > 0" class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-project-diagram"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ syntacticPatterns.length }}</div>
          <div class="stat-label">Patterns</div>
        </div>
      </div>
      <div v-if="parseValidation" class="stat-card" :class="{ 'stat-valid': parseValidation.is_valid, 'stat-invalid': !parseValidation.is_valid }">
        <div class="stat-icon">
          <i :class="parseValidation.is_valid ? 'fas fa-check-circle' : 'fas fa-exclamation-triangle'"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ Math.round(parseValidation.confidence * 100) }}%</div>
          <div class="stat-label">Parse Quality</div>
        </div>
      </div>
    </div>

    <!-- Analysis Results -->
    <section class="results-section">
      <div class="results-header">
        <h2 class="results-title">
          <i class="fas fa-chart-line"></i>
          Analysis Results
          <span v-if="isLoading" style="color: orange;">(Loading...)</span>
          <span v-else-if="analysisResult.length > 0" style="color: green;">({{ analysisResult.length }} tokens)</span>
          <span v-else style="color: gray;">(No results)</span>
        </h2>
        
        <!-- Result actions -->
        <div v-if="analysisResult.length > 0" class="results-actions">
          <button 
            @click="exportAnalysis"
            class="btn btn-secondary"
            title="Export analysis data"
          >
            <i class="fas fa-download"></i>
            Export
          </button>
          
          <button 
            @click="copyAnalysis"
            class="btn btn-secondary"
            title="Copy to clipboard"
          >
            <i class="fas fa-copy"></i>
            Copy
          </button>
        </div>
      </div>
      
      <div class="results-container">
        <AnalyzedText 
          :tokens="analysisResult" 
          :syntactic-patterns="syntacticPatterns"
          :parse-validation="parseValidation"
          :dependency-tree="dependencyTree"
        />
      </div>
      
      <!-- Empty state -->
      <div v-if="analysisResult.length === 0" class="empty-state">
        <div class="empty-icon">🔍</div>
        <h3 class="empty-title">Ready for Analysis</h3>
        <p class="empty-description">Use the text input in the top navigation bar to analyze Japanese text</p>
        <div class="empty-glow"></div>
      </div>
    </section>

    <!-- Debug Information (temporarily disabled) -->
    <!-- <DebugInfo 
      :input-text="inputText"
      :is-loading="isLoading"
      :error="error"
      :analysis-result="analysisResult"
    /> -->

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import AnalyzedText from '../components/AnalyzedText.vue'
import DebugInfo from '../components/DebugInfo.vue'

const route = useRoute()
const router = useRouter()

// State
const inputText = ref('')
const analysisResult = ref([])
const syntacticPatterns = ref([])
const parseValidation = ref(null)
const dependencyTree = ref(null)
const parsingInsights = ref(null)
const isLoading = ref(false)
const isUploading = ref(false)
const isExtracting = ref(false)
const error = ref('')
const isDragging = ref(false)
const dragCounter = ref(0)

// Debug: Watch all state changes
watch(analysisResult, (newVal, oldVal) => {
  console.log('✅ analysisResult changed:', { 
    oldLength: oldVal?.length, 
    newLength: newVal?.length, 
    newValue: newVal 
  })
}, { deep: true })

watch(isLoading, (newVal, oldVal) => {
  console.log('✅ isLoading changed:', { old: oldVal, new: newVal })
})

watch(error, (newVal, oldVal) => {
  console.log('✅ error changed:', { old: oldVal, new: newVal })
})

watch(inputText, (newVal, oldVal) => {
  console.log('✅ inputText changed:', { old: oldVal, new: newVal })
})

// Debouncing for analysis requests
let analysisTimeout = null

// Debug watchers
watch(analysisResult, (newVal, oldVal) => {
  console.log('✅ analysisResult changed:', { 
    oldLength: oldVal?.length, 
    newLength: newVal?.length, 
    newValue: newVal 
  })
}, { deep: true })


// Computed properties
const kanjiList = computed(() => {
  const seen = new Set()
  return analysisResult.value.filter(token => {
    const key = `${token.surface}-${token.furigana}`
    if (seen.has(key)) return false
    seen.add(key)
    return token.isKanji || token.definition
  })
})

// Methods
const analyzeText = async () => {
  console.log('analyzeText called with inputText:', inputText.value)
  console.log('inputText length:', inputText.value?.length)
  console.log('inputText trimmed:', inputText.value?.trim())
  console.log('inputText trimmed length:', inputText.value?.trim()?.length)
  console.log('isLoading.value:', isLoading.value)
  
  if (!inputText.value.trim()) {
    console.log('No text to analyze, returning early')
    return
  }
  
  // Clear any existing timeout to prevent duplicate requests
  if (analysisTimeout) {
    console.log('Clearing analysis timeout')
    clearTimeout(analysisTimeout)
    analysisTimeout = null
  }
  
  // If already loading, don't start another request
  if (isLoading.value) {
    console.log('Analysis already in progress, skipping duplicate request')
    return
  }
  
  console.log('Starting analysis for text:', inputText.value.substring(0, 50) + '...')
  isLoading.value = true
  error.value = ''
  
  try {
    console.log('Making API request to full-analysis endpoint...')
    const response = await axios.post('/api/full-analysis', {
      text: inputText.value
    }, {
      timeout: 30000 // 30 second timeout
    })
    console.log('API response received:', response.data)
    
    // Handle new enhanced response format
    if (response.data.chunks) {
      // New format with dependency parsing
      analysisResult.value = response.data.chunks || []
      syntacticPatterns.value = response.data.syntactic_patterns || []
      parseValidation.value = response.data.parse_validation || null
      dependencyTree.value = response.data.dependency_tree || null
      parsingInsights.value = response.data.parsing_insights || null
    } else {
      // Legacy format fallback
      analysisResult.value = response.data || []
      syntacticPatterns.value = []
      parseValidation.value = null
      dependencyTree.value = null
      parsingInsights.value = null
    }
    
    // Update URL with current text (for sharing/bookmarking)
    if (route.query.text !== inputText.value) {
      await router.replace({
        name: 'Analysis',
        query: { text: inputText.value }
      })
    }
    
  } catch (err) {
    console.error('Analysis failed:', err)
    console.error('Error details:', {
      message: err.message,
      response: err.response?.data,
      status: err.response?.status,
      config: err.config
    })
    error.value = err.response?.data?.error || `Failed to analyze text: ${err.message}. Please try again.`
  } finally {
    isLoading.value = false
  }
}

const clearResults = () => {
  analysisResult.value = []
  syntacticPatterns.value = []
  parseValidation.value = null
  dependencyTree.value = null
  parsingInsights.value = null
  error.value = ''
  // Clear URL query params
  router.replace({ name: 'Analysis' })
}


const exportAnalysis = () => {
  const data = {
    originalText: inputText.value,
    analysisResult: analysisResult.value,
    syntacticPatterns: syntacticPatterns.value,
    parseValidation: parseValidation.value,
    timestamp: new Date().toISOString()
  }
  
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `japanese-analysis-${Date.now()}.json`
  a.click()
  URL.revokeObjectURL(url)
}

const copyAnalysis = async () => {
  try {
    const text = analysisResult.value.map(token => token.surface).join('')
    await navigator.clipboard.writeText(text)
    // Could show a toast notification here
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}

// Drag and drop handlers
const handleDragEnter = (e) => {
  e.preventDefault()
  dragCounter.value++
  isDragging.value = true
}

const handleDragLeave = (e) => {
  e.preventDefault()
  dragCounter.value--
  if (dragCounter.value === 0) {
    isDragging.value = false
  }
}

const handleDragOver = (e) => {
  e.preventDefault()
}

const handleFileDrop = async (e) => {
  e.preventDefault()
  isDragging.value = false
  dragCounter.value = 0
  
  const files = Array.from(e.dataTransfer.files)
  if (files.length > 0) {
    await handleImageUpload(files[0])
  }
}

const handleImageUpload = async (file) => {
  if (!file.type.startsWith('image/')) {
    error.value = 'Please upload an image file.'
    return
  }
  
  isUploading.value = true
  isExtracting.value = true
  error.value = ''
  
  try {
    const formData = new FormData()
    formData.append('image', file)
    
    const response = await axios.post('/api/analyze-image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    inputText.value = response.data.text
    await analyzeText()
    
  } catch (err) {
    console.error('OCR failed:', err)
    error.value = err.response?.data?.error || 'Failed to extract text from image.'
  } finally {
    isUploading.value = false
    isExtracting.value = false
  }
}

// Handle paste events
const handlePaste = async (e) => {
  const items = Array.from(e.clipboardData.items)
  const imageItem = items.find(item => item.type.startsWith('image/'))
  
  if (imageItem) {
    e.preventDefault()
    const file = imageItem.getAsFile()
    await handleImageUpload(file)
  }
}

// Initialize from route query
onMounted(() => {
  console.log('Analysis page mounted. Route query:', route.query)
  console.log('Route query text type:', typeof route.query.text)
  console.log('Route query text length:', route.query.text?.length)
  
  if (route.query.text) {
    console.log('Found text in route query:', route.query.text)
    inputText.value = route.query.text
    console.log('Set inputText to:', inputText.value)
    console.log('inputText value type:', typeof inputText.value)
    console.log('inputText value length:', inputText.value?.length)
    analyzeText()
  } else {
    console.log('No text found in route query')
  }
  
  // Add global paste listener
  document.addEventListener('paste', handlePaste)
  
  // Add drag and drop listeners
  document.addEventListener('dragenter', handleDragEnter)
  document.addEventListener('dragleave', handleDragLeave)
  document.addEventListener('dragover', handleDragOver)
  document.addEventListener('drop', handleFileDrop)
})

// Watch for route changes
watch(
  () => route.query.text,
  (newText, oldText) => {
    console.log('Route query text changed from:', oldText, 'to:', newText)
    console.log('Current inputText.value:', inputText.value)
    console.log('newText === inputText.value:', newText === inputText.value)
    
    if (newText && newText !== inputText.value) {
      console.log('Updating inputText from route query:', newText)
      inputText.value = newText
      
      // Clear any existing analysis timeout
      if (analysisTimeout) {
        console.log('Clearing existing analysis timeout')
        clearTimeout(analysisTimeout)
      }
      
      // Debounce the analysis call
      console.log('Setting up debounced analysis call')
      analysisTimeout = setTimeout(() => {
        console.log('Executing debounced analysis call')
        analyzeText()
      }, 300)
    } else if (newText) {
      console.log('Text exists but equals current inputText, skipping analysis')
    } else {
      console.log('No text in route query')
    }
  }
)

// Cleanup on unmount
import { onUnmounted } from 'vue'
onUnmounted(() => {
  document.removeEventListener('paste', handlePaste)
  document.removeEventListener('dragenter', handleDragEnter)
  document.removeEventListener('dragleave', handleDragLeave)
  document.removeEventListener('dragover', handleDragOver)
  document.removeEventListener('drop', handleFileDrop)
  
  // Clean up analysis timeout
  if (analysisTimeout) {
    clearTimeout(analysisTimeout)
  }
})
</script>

<style scoped>
/* =====================================================
   ANALYSIS PAGE STYLES
   ===================================================== */

.analysis-page {
  min-height: 100vh;
  background: var(--primary-black);
  color: var(--text-primary);
  display: flex;
  flex-direction: column;
}



/* =====================================================
   DRAG AND DROP OVERLAY
   ===================================================== */

.drag-overlay {
  position: fixed;
  inset: 0;
  background: rgba(10, 10, 10, 0.9);
  backdrop-filter: blur(4px);
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
}

.drag-content {
  text-align: center;
  padding: 2rem;
  border: 2px dashed var(--accent-indigo);
  border-radius: var(--radius-xl);
  background: var(--surface-medium);
}

.drag-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.drag-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.drag-description {
  color: var(--text-secondary);
}

/* =====================================================
   STATUS MESSAGES
   ===================================================== */

.error-message {
  max-width: 1000px;
  margin: 0 auto 2rem;
  padding: 1rem 2rem;
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  background: rgba(255, 71, 87, 0.1);
  border: 1px solid rgba(255, 71, 87, 0.3);
  color: #ff9999;
  border-radius: var(--radius-lg);
}

.error-message i {
  color: var(--danger-red);
  margin-top: 0.125rem;
}

.error-content {
  flex: 1;
}

.processing-status {
  max-width: 1000px;
  margin: 0 auto 2rem;
  padding: 1rem 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  background: var(--surface-medium);
  border: 1px solid var(--border-grey);
  color: var(--text-secondary);
  border-radius: var(--radius-lg);
}

.processing-spinner i {
  color: var(--accent-indigo);
}

.processing-text {
  font-weight: 500;
}

/* =====================================================
   STATS SECTION
   ===================================================== */

.stats-section {
  display: flex;
  justify-content: center;
  gap: 2rem;
  padding: 2rem;
  max-width: 1000px;
  margin: 0 auto;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: var(--surface-medium);
  border: 1px solid var(--border-grey);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  box-shadow: var(--shadow-sm);
  transition: all 0.2s ease;
}

.stat-card:hover {
  border-color: var(--border-light);
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

.stat-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, var(--accent-indigo) 0%, var(--accent-indigo-dark) 100%);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon i {
  color: white;
  font-size: 1.125rem;
}

.stat-content {
  text-align: left;
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  color: var(--accent-indigo);
  line-height: 1;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-muted);
  margin-top: 0.25rem;
}

.stat-card.stat-valid {
  border-color: rgba(34, 197, 94, 0.3);
  background: linear-gradient(135deg, var(--surface-medium) 0%, rgba(34, 197, 94, 0.05) 100%);
}

.stat-card.stat-valid .stat-icon {
  background: linear-gradient(135deg, rgb(34, 197, 94) 0%, rgb(22, 163, 74) 100%);
}

.stat-card.stat-valid .stat-number {
  color: rgb(34, 197, 94);
}

.stat-card.stat-invalid {
  border-color: rgba(239, 68, 68, 0.3);
  background: linear-gradient(135deg, var(--surface-medium) 0%, rgba(239, 68, 68, 0.05) 100%);
}

.stat-card.stat-invalid .stat-icon {
  background: linear-gradient(135deg, rgb(239, 68, 68) 0%, rgb(220, 38, 38) 100%);
}

.stat-card.stat-invalid .stat-number {
  color: rgb(239, 68, 68);
}

/* =====================================================
   RESULTS SECTION - MAIN FOCUS
   ===================================================== */

.results-section {
  padding: 1rem 0 4rem;
  flex: 1;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
  padding: 0 2rem;
}

.results-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.results-title i {
  color: var(--accent-indigo);
}

.results-actions {
  display: flex;
  gap: 0.75rem;
}

.results-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}


/* =====================================================
   EMPTY STATE - ENHANCED
   ===================================================== */

.empty-state {
  position: relative;
  text-align: center;
  padding: 6rem 2rem;
  max-width: 600px;
  margin: 0 auto;
  background: var(--surface-low);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-grey);
}

.empty-icon {
  font-size: 5rem;
  margin-bottom: 2rem;
  opacity: 0.7;
}

.empty-title {
  font-size: 1.75rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.empty-description {
  color: var(--text-secondary);
  line-height: 1.6;
  max-width: 400px;
  margin: 0 auto;
  font-size: 1rem;
}


.empty-glow {
  position: absolute;
  inset: 0;
  opacity: 0.03;
  filter: blur(80px);
  background: linear-gradient(135deg, var(--accent-indigo) 0%, var(--accent-indigo-light) 100%);
  border-radius: var(--radius-lg);
  pointer-events: none;
}

/* =====================================================
   RESPONSIVE DESIGN
   ===================================================== */

@media (max-width: 768px) {
  .stats-section {
    flex-direction: column;
    gap: 1rem;
  }
  
  .results-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .results-actions {
    flex-direction: column;
    width: 100%;
    gap: 1rem;
  }
  
  .results-actions .btn {
    width: 100%;
    justify-content: center;
  }
  
}

@media (max-width: 480px) {
  .stat-card {
    padding: 1rem;
  }
  
  .stat-icon {
    width: 40px;
    height: 40px;
  }
  
  .stat-number {
    font-size: 1.5rem;
  }
}

</style>