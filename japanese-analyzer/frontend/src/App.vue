<template>
  <div id="app" class="lofi-app">
    <!-- Vertical Toolbar (Left Side) -->
    <aside class="vertical-toolbar">
      <!-- Logo/Brand -->
      <div class="toolbar-brand">
        <div class="brand-symbol">日</div>
      </div>

      <!-- Main Navigation Icons -->
      <nav class="toolbar-nav">
        <button 
          v-for="tool in tools" 
          :key="tool.id"
          :class="['tool-btn', { active: currentTool === tool.id }]"
          :title="tool.title"
          @click="setCurrentTool(tool.id)"
        >
          <i :class="tool.icon"></i>
        </button>
      </nav>

      <!-- Secondary Actions -->
      <div class="toolbar-secondary">
        <button class="tool-btn" title="Settings" @click="showSettings = true">
          <i class="fas fa-cog"></i>
        </button>
        <button class="tool-btn" title="About" @click="showAbout = true">
          <i class="fas fa-info"></i>
        </button>
      </div>
    </aside>

    <!-- Main Content Area -->
    <main class="main-area">
      <!-- Central Input Section -->
      <div class="central-input">
        <h1 class="app-title">japanese text analyzer</h1>
        
        <div class="input-container">
          <div class="input-wrapper"
               @drop.prevent="handleDrop" 
               @dragover.prevent
               @dragenter.prevent="showDropZone = true"
               @dragleave.prevent="showDropZone = false"
               :class="{ 'drop-active': showDropZone }">
            <textarea
              v-model="inputText"
              @keydown.ctrl.enter="analyzeText"
              @keydown.meta.enter="analyzeText"
              placeholder="paste japanese text here or drop an image for ocr"
              class="main-input"
              :class="{ 'has-content': inputText.length > 0 }"
              rows="4"
              maxlength="5000"
            ></textarea>
            
            <div class="input-actions">
              <button 
                @click="analyzeText" 
                :disabled="!inputText.trim()"
                class="analyze-btn"
                title="Analyze Text (Ctrl+Enter)"
              >
                analyze
              </button>
              <button 
                @click="$refs.fileInput.click()"
                class="ocr-btn"
                title="Upload Image for OCR"
              >
                <i class="fas fa-image"></i>
              </button>
              <button 
                @click="clearInput" 
                v-if="inputText.length > 0"
                class="clear-btn"
                title="Clear Input"
              >
                clear
              </button>
            </div>
            
            <!-- Hidden file input for OCR -->
            <input 
              type="file" 
              @change="handleFileSelect" 
              accept="image/*" 
              ref="fileInput" 
              style="display: none"
            >
          </div>

          <!-- Character Counter -->
          <div class="input-meta">
            <span class="char-counter">{{ inputText.length }}/5000</span>
            <span class="input-hint">ctrl+enter to analyze • ctrl+u for ocr</span>
          </div>
        </div>

        <!-- Analysis Options -->
        <div class="analysis-options" v-if="inputText.length > 0">
          <div class="option-group">
            <label class="option-label">
              <input type="radio" v-model="analysisMode" value="auto" name="mode">
              <span>auto</span>
            </label>
            <label class="option-label">
              <input type="radio" v-model="analysisMode" value="detailed" name="mode">
              <span>detailed</span>
            </label>
            <label class="option-label">
              <input type="radio" v-model="analysisMode" value="simple" name="mode">
              <span>simple</span>
            </label>
          </div>
        </div>

      </div>

      <!-- Results Area -->
      <div class="results-area" v-if="analysisResults">
        <div class="results-header">
          <h2 class="results-title">analysis results</h2>
          <div class="results-meta">
            <span class="token-count">{{ analysisResults.chunks?.length || 0 }} tokens</span>
            <button @click="exportResults" class="export-btn">export</button>
          </div>
        </div>

        <!-- Token Display -->
        <div class="token-display">
          <span 
            v-for="(token, index) in analysisResults.chunks" 
            :key="index"
            class="token"
            :class="getTokenClass(token)"
            @click="selectToken(token)"
            :title="getTokenTooltip(token)"
          >
            <span class="token-text">{{ token.surface || token.text }}</span>
            <span v-if="token.furigana && token.furigana !== token.surface" class="token-reading">
              {{ token.furigana }}
            </span>
          </span>
        </div>

        <!-- Selected Token Info -->
        <div class="token-info" v-if="selectedToken">
          <div class="info-header">
            <span class="info-kanji">{{ selectedToken.surface || selectedToken.text }}</span>
            <span v-if="selectedToken.furigana" class="info-reading">{{ selectedToken.furigana }}</span>
          </div>
          <div class="info-definition" v-if="selectedToken.definition">
            {{ selectedToken.definition.glosses?.join(', ') || 'No definition available' }}
          </div>
          <div class="info-grammar" v-if="selectedToken.grammar">
            <span class="grammar-pos">{{ selectedToken.grammar.pos }}</span>
          </div>
        </div>
      </div>

      <!-- Processing Indicator -->
      <div class="processing-overlay" v-if="isProcessing">
        <div class="processing-content">
          <div class="processing-spinner"></div>
          <p class="processing-text">{{ processingText }}</p>
        </div>
      </div>
    </main>

    <!-- Footer Links -->
    <footer class="app-footer">
      <a href="#" @click.prevent="showServices = true" class="footer-link">supported features</a>
      <a href="#" @click.prevent="showTerms = true" class="footer-link">terms of use</a>
    </footer>

    <!-- Modals -->
    <div v-if="showSettings" class="modal-overlay" @click="showSettings = false">
      <div class="modal-content" @click.stop>
        <h3>settings</h3>
        <div class="setting-item">
          <label>
            <input type="checkbox" v-model="settings.showReadings">
            show furigana readings
          </label>
        </div>
        <div class="setting-item">
          <label>
            <input type="checkbox" v-model="settings.autoAnalyze">
            auto-analyze on paste
          </label>
        </div>
        <button @click="showSettings = false" class="modal-close">close</button>
      </div>
    </div>

    <div v-if="showAbout" class="modal-overlay" @click="showAbout = false">
      <div class="modal-content" @click.stop>
        <h3>japanese text analyzer</h3>
        <p>advanced morphological analysis for japanese text</p>
        <p>version 2.0.0</p>
        <button @click="showAbout = false" class="modal-close">close</button>
      </div>
    </div>

    <div v-if="showServices" class="modal-overlay" @click="showServices = false">
      <div class="modal-content" @click.stop>
        <h3>supported features</h3>
        <ul class="feature-list">
          <li>morphological tokenization</li>
          <li>furigana reading generation</li>
          <li>dictionary lookup</li>
          <li>grammar pattern recognition</li>
          <li>dependency parsing</li>
          <li>ocr text extraction</li>
        </ul>
        <button @click="showServices = false" class="modal-close">close</button>
      </div>
    </div>

    <div v-if="showTerms" class="modal-overlay" @click="showTerms = false">
      <div class="modal-content" @click.stop>
        <h3>terms of use</h3>
        <p>this tool is provided for educational and research purposes.</p>
        <p>text processing is performed locally and privately.</p>
        <p>no data is stored or transmitted to external servers.</p>
        <button @click="showTerms = false" class="modal-close">close</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'

// State
const inputText = ref('')
const analysisMode = ref('auto')
const currentTool = ref('analyze')
const showDropZone = ref(false)
const analysisResults = ref(null)
const selectedToken = ref(null)
const isProcessing = ref(false)
const processingText = ref('')

// Modal states
const showSettings = ref(false)
const showAbout = ref(false)
const showServices = ref(false)
const showTerms = ref(false)

// Settings
const settings = reactive({
  showReadings: true,
  autoAnalyze: false
})

// Tools configuration
const tools = [
  { id: 'analyze', title: 'Text Analysis', icon: 'fas fa-search' },
  { id: 'history', title: 'History', icon: 'fas fa-history' },
  { id: 'export', title: 'Export', icon: 'fas fa-download' }
]

// Methods
const setCurrentTool = (toolId) => {
  currentTool.value = toolId
  
  if (toolId === 'history') {
    loadHistory()
  }
}

const analyzeText = async () => {
  if (!inputText.value.trim()) return
  
  isProcessing.value = true
  processingText.value = 'analyzing text...'
  selectedToken.value = null
  
  try {
    const response = await fetch('/api/full-analysis', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        text: inputText.value,
        mode: analysisMode.value 
      })
    })
    
    if (response.ok) {
      analysisResults.value = await response.json()
      processingText.value = 'analysis complete'
      
      // Save to history
      saveToHistory(inputText.value, analysisResults.value)
    } else {
      throw new Error(`Analysis failed: ${response.status}`)
    }
  } catch (error) {
    console.error('Analysis error:', error)
    processingText.value = 'analysis failed'
    setTimeout(() => {
      isProcessing.value = false
    }, 2000)
    return
  }
  
  setTimeout(() => {
    isProcessing.value = false
  }, 1000)
}

const clearInput = () => {
  inputText.value = ''
  analysisResults.value = null
  selectedToken.value = null
}

const selectToken = (token) => {
  selectedToken.value = token
}

const getTokenClass = (token) => {
  const classes = []
  
  if (token.isKanji) classes.push('has-kanji')
  if (token.definition) classes.push('has-definition')
  if (selectedToken.value === token) classes.push('selected')
  
  // POS-based classes
  if (token.grammar?.pos) {
    classes.push(`pos-${token.grammar.pos.toLowerCase()}`)
  }
  
  return classes
}

const getTokenTooltip = (token) => {
  const parts = []
  if (token.furigana && token.furigana !== token.surface) {
    parts.push(token.furigana)
  }
  if (token.grammar?.pos) {
    parts.push(token.grammar.pos)
  }
  return parts.join(' • ')
}

const handleDrop = (event) => {
  showDropZone.value = false
  const file = event.dataTransfer.files[0]
  if (file && file.type.startsWith('image/')) {
    processImage(file)
  }
}

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    processImage(file)
  }
}

const processImage = async (file) => {
  isProcessing.value = true
  processingText.value = 'extracting text from image...'
  
  try {
    const formData = new FormData()
    formData.append('image', file)
    
    const response = await fetch('/api/analyze-image', {
      method: 'POST',
      body: formData
    })
    
    if (response.ok) {
      const result = await response.json()
      if (result.text) {
        inputText.value = result.text
        processingText.value = 'text extracted'
        
        if (settings.autoAnalyze) {
          setTimeout(analyzeText, 1000)
        }
      } else {
        throw new Error('No text found in image')
      }
    } else {
      throw new Error(`OCR failed: ${response.status}`)
    }
  } catch (error) {
    console.error('OCR error:', error)
    processingText.value = 'ocr failed'
    setTimeout(() => {
      isProcessing.value = false
    }, 2000)
    return
  }
  
  setTimeout(() => {
    isProcessing.value = false
  }, 1000)
}

const exportResults = () => {
  if (!analysisResults.value) return
  
  const data = {
    input: inputText.value,
    timestamp: new Date().toISOString(),
    results: analysisResults.value
  }
  
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `analysis_${Date.now()}.json`
  a.click()
  URL.revokeObjectURL(url)
}

const saveToHistory = (text, results) => {
  const history = JSON.parse(localStorage.getItem('analysisHistory') || '[]')
  history.unshift({
    text: text.substring(0, 100) + (text.length > 100 ? '...' : ''),
    timestamp: Date.now(),
    tokenCount: results.chunks?.length || 0
  })
  
  // Keep only last 20 items
  if (history.length > 20) {
    history.splice(20)
  }
  
  localStorage.setItem('analysisHistory', JSON.stringify(history))
}

const loadHistory = () => {
  // Implementation for history display
  console.log('Loading history...')
}

// Global paste handler
const handleGlobalPaste = async (event) => {
  const clipboardData = event.clipboardData
  if (!clipboardData) return
  
  const items = Array.from(clipboardData.items)
  const imageItem = items.find(item => item.type.startsWith('image/'))
  
  if (imageItem) {
    event.preventDefault()
    const file = imageItem.getAsFile()
    if (file) {
      await processImage(file)
    }
  }
}

// Keyboard shortcuts
const handleKeyboard = (event) => {
  if ((event.ctrlKey || event.metaKey)) {
    switch (event.key) {
      case 'l':
        event.preventDefault()
        clearInput()
        break
      case 'u':
        event.preventDefault()
        document.querySelector('input[type="file"]').click()
        break
      case '1':
        event.preventDefault()
        setCurrentTool('analyze')
        break
    }
  }
}

// Lifecycle
onMounted(() => {
  document.addEventListener('paste', handleGlobalPaste)
  document.addEventListener('keydown', handleKeyboard)
  
  // Focus input on load
  setTimeout(() => {
    document.querySelector('.main-input')?.focus()
  }, 100)
})

onUnmounted(() => {
  document.removeEventListener('paste', handleGlobalPaste)
  document.removeEventListener('keydown', handleKeyboard)
})
</script>

<style>
/* ===== GLOBAL RESET & BASE ===== */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Courier New', 'Monaco', 'Menlo', monospace;
  background: #000000;
  color: #ffffff;
  overflow-x: hidden;
}

/* ===== MAIN APP CONTAINER ===== */
.lofi-app {
  display: flex;
  min-height: 100vh;
  background: #000000;
  color: #ffffff;
}

/* ===== VERTICAL TOOLBAR ===== */
.vertical-toolbar {
  width: 60px;
  background: #111111;
  border-right: 1px solid #333333;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem 0;
  position: fixed;
  left: 0;
  top: 0;
  height: 100vh;
  z-index: 100;
}

.toolbar-brand {
  margin-bottom: 2rem;
}

.brand-symbol {
  width: 40px;
  background: #ff0000;
  border: 1px solid #ffffff;
  color: #ffffff;
  height: 40px;
  padding-bottom: 5px;
  text-align: center;
  line-height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: bold;
  border-radius: 5px;
}

.toolbar-nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.toolbar-secondary {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: auto;
  padding-top: 1rem;
  border-top: 1px solid #333333;
}

.tool-btn {
  width: 40px;
  height: 40px;
  background: transparent;
  border: 1px solid #333333;
  color: #888888;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.9rem;
}

.tool-btn:hover {
  background: #222222;
  color: #ffffff;
  border-color: #6366f1;
}

.tool-btn.active {
  background: #ff0000;
  color: #ffffff;
  border-color: #ff0000;
}

/* ===== MAIN CONTENT AREA ===== */
.main-area {
  flex: 1;
  margin-left: 60px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  min-height: 100vh;
  position: relative;
}

/* ===== CENTRAL INPUT SECTION ===== */
.central-input {
  width: 100%;
  max-width: 800px;
  text-align: center;
}

.app-title {
  font-size: 2rem;
  font-weight: normal;
  color: #ffffff;
  margin-bottom: 3rem;
  letter-spacing: 2px;
  text-transform: lowercase;
}

.input-container {
  margin-bottom: 2rem;
}

.input-wrapper {
  position: relative;
  margin-bottom: 1rem;
  transition: all 0.3s ease;
}

.input-wrapper.drop-active {
  border: 2px dashed #ff0000;
  background: rgba(255, 0, 0, 0.05);
  border-radius: 4px;
}

.main-input {
  width: 100%;
  background: #111111;
  border: 2px solid #333333;
  color: #ffffff;
  font-family: inherit;
  font-size: 1.1rem;
  padding: 1.5rem;
  resize: vertical;
  min-height: 120px;
  outline: none;
  transition: all 0.3s ease;
}

.main-input:focus {
  border-color: #ff0000;
  box-shadow: 0 0 0 2px rgba(255, 0, 0, 0.2);
}

.main-input.has-content {
  border-color: #6366f1;
}

.main-input::placeholder {
  color: #666666;
  font-style: italic;
}

.input-actions {
  position: absolute;
  bottom: 1rem;
  right: 1rem;
  display: flex;
  gap: 0.5rem;
}

.analyze-btn, .clear-btn, .ocr-btn {
  background: #ff0000;
  color: #ffffff;
  border: none;
  padding: 0.5rem 1rem;
  font-family: inherit;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
  text-transform: lowercase;
  display: flex;
  align-items: center;
  justify-content: center;
}

.analyze-btn:hover:not(:disabled), .clear-btn:hover, .ocr-btn:hover {
  background: #cc0000;
}

.analyze-btn:disabled {
  background: #333333;
  color: #666666;
  cursor: not-allowed;
}

.clear-btn {
  background: #333333;
  color: #cccccc;
}

.clear-btn:hover {
  background: #555555;
}

.ocr-btn {
  background: #005577;
  color: #ffffff;
  min-width: 40px;
}

.ocr-btn:hover {
  background: #007799;
}

.input-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.8rem;
  color: #666666;
}

.char-counter {
  color: #888888;
}

.input-hint {
  color: #666666;
  font-style: italic;
}

/* ===== ANALYSIS OPTIONS ===== */
.analysis-options {
  margin-bottom: 2rem;
  padding: 1rem;
  background: #111111;
  border: 1px solid #333333;
}

.option-group {
  display: flex;
  justify-content: center;
  gap: 2rem;
}

.option-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #cccccc;
  cursor: pointer;
  font-size: 0.9rem;
}

.option-label input[type="radio"] {
  accent-color: #ff0000;
}


/* ===== RESULTS AREA ===== */
.results-area {
  width: 100%;
  max-width: 1000px;
  margin-top: 3rem;
  padding: 2rem;
  background: #111111;
  border: 1px solid #333333;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #333333;
}

.results-title {
  font-size: 1.5rem;
  color: #ffffff;
  text-transform: lowercase;
  font-weight: normal;
}

.results-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.token-count {
  color: #888888;
  font-size: 0.9rem;
}

.export-btn {
  background: #005577;
  color: #ffffff;
  border: none;
  padding: 0.5rem 1rem;
  font-family: inherit;
  cursor: pointer;
  font-size: 0.9rem;
  text-transform: lowercase;
}

.export-btn:hover {
  background: #007799;
}

/* ===== TOKEN DISPLAY ===== */
.token-display {
  line-height: 2;
  margin-bottom: 2rem;
}

.token {
  display: inline-block;
  margin: 0.25rem;
  padding: 0.5rem;
  background: #222222;
  border: 1px solid #333333;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.token:hover {
  background: #333333;
  border-color: #555555;
}

.token.selected {
  background: #ff0000;
  color: #ffffff;
  border-color: #ff0000;
}

.token.has-kanji {
  border-color: #005577;
}

.token.has-definition {
  border-left: 3px solid #ff0000;
}

.token-text {
  display: block;
  font-size: 1.1rem;
}

.token-reading {
  display: block;
  font-size: 0.8rem;
  color: #888888;
  margin-top: 0.25rem;
}

.token.selected .token-reading {
  color: #cccccc;
}

/* POS-based token colors */
.token.pos-noun { border-left-color: #00aa00; }
.token.pos-verb { border-left-color: #aa0000; }
.token.pos-adjective { border-left-color: #aaaa00; }
.token.pos-particle { border-left-color: #aa00aa; }
.token.pos-adverb { border-left-color: #00aaaa; }

/* ===== TOKEN INFO ===== */
.token-info {
  padding: 1.5rem;
  background: #222222;
  border: 1px solid #333333;
}

.info-header {
  display: flex;
  align-items: baseline;
  gap: 1rem;
  margin-bottom: 1rem;
}

.info-kanji {
  font-size: 2rem;
  color: #ffffff;
}

.info-reading {
  font-size: 1.2rem;
  color: #888888;
}

.info-definition {
  color: #cccccc;
  margin-bottom: 1rem;
  line-height: 1.5;
}

.info-grammar {
  font-size: 0.9rem;
  color: #888888;
}

.grammar-pos {
  background: #333333;
  padding: 0.25rem 0.5rem;
  border-radius: 2px;
}

/* ===== PROCESSING OVERLAY ===== */
.processing-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.processing-content {
  text-align: center;
  padding: 2rem;
}

.processing-spinner {
  width: 40px;
  height: 40px;
  border: 2px solid #333333;
  border-top: 2px solid #ff0000;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.processing-text {
  color: #cccccc;
  font-size: 1.1rem;
}

/* ===== FOOTER ===== */
.app-footer {
  position: fixed;
  bottom: 1rem;
  right: 1rem;
  display: flex;
  gap: 1rem;
  z-index: 50;
}

.footer-link {
  color: #666666;
  text-decoration: none;
  font-size: 0.8rem;
  transition: color 0.2s ease;
}

.footer-link:hover {
  color: #ffffff;
}

/* ===== MODALS ===== */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal-content {
  background: #111111;
  border: 1px solid #333333;
  padding: 2rem;
  max-width: 500px;
  width: 90%;
}

.modal-content h3 {
  color: #ffffff;
  margin-bottom: 1.5rem;
  font-size: 1.3rem;
  text-transform: lowercase;
  font-weight: normal;
}

.modal-content p {
  color: #cccccc;
  line-height: 1.5;
  margin-bottom: 1rem;
}

.setting-item {
  margin-bottom: 1rem;
}

.setting-item label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #cccccc;
  cursor: pointer;
}

.feature-list {
  list-style: none;
  margin-bottom: 1.5rem;
}

.feature-list li {
  color: #cccccc;
  margin-bottom: 0.5rem;
  padding-left: 1rem;
  position: relative;
}

.feature-list li::before {
  content: '→';
  position: absolute;
  left: 0;
  color: #ff0000;
}

.modal-close {
  background: #333333;
  color: #ffffff;
  border: none;
  padding: 0.75rem 1.5rem;
  font-family: inherit;
  cursor: pointer;
  text-transform: lowercase;
  margin-top: 1rem;
}

.modal-close:hover {
  background: #555555;
}

/* ===== RESPONSIVE ===== */
@media (max-width: 768px) {
  .vertical-toolbar {
    width: 50px;
  }
  
  .main-area {
    margin-left: 50px;
    padding: 1rem;
  }
  
  .app-title {
    font-size: 1.5rem;
    margin-bottom: 2rem;
  }
  
  .main-input {
    font-size: 1rem;
    padding: 1rem;
    min-height: 100px;
  }
  
  .option-group {
    gap: 1rem;
  }
  
  .results-area {
    padding: 1rem;
  }
  
  .token {
    margin: 0.125rem;
    padding: 0.375rem;
  }
  
  .token-text {
    font-size: 1rem;
  }
  
  .info-kanji {
    font-size: 1.5rem;
  }
  
  .app-footer {
    position: relative;
    bottom: auto;
    right: auto;
    margin-top: 2rem;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .main-area {
    padding: 0.5rem;
  }
  
  .app-title {
    font-size: 1.3rem;
  }
  
  .results-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .info-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}
</style>