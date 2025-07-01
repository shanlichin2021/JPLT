<template>
  <div class="semantic-search-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-title">
          <h1>Semantic Search</h1>
          <p class="header-description">
            Intelligent Japanese dictionary search powered by AI embeddings
          </p>
        </div>
        <div class="header-stats">
          <div class="stat-card">
            <i class="fas fa-brain"></i>
            <div class="stat-content">
              <span class="stat-number">212K+</span>
              <span class="stat-label">Vectorized Entries</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Search Interface -->
    <div class="search-section">
      <div class="search-form">
        <div class="search-input-group">
          <div class="search-icon">
            <i class="fas fa-search"></i>
          </div>
          <input
            v-model="searchQuery"
            @keyup.enter="performSearch"
            @input="handleInputChange"
            type="text"
            placeholder="Enter Japanese text or concept to search..."
            class="search-input"
            :disabled="isSearching"
          />
          <button 
            @click="performSearch"
            :disabled="!searchQuery.trim() || isSearching"
            class="search-button"
          >
            <i v-if="isSearching" class="fas fa-spinner fa-spin"></i>
            <i v-else class="fas fa-arrow-right"></i>
          </button>
        </div>

        <!-- Search Options -->
        <div class="search-options">
          <div class="option-group">
            <label>Results:</label>
            <select v-model="searchParams.top_k" class="search-select">
              <option value="5">5 results</option>
              <option value="10">10 results</option>
              <option value="20">20 results</option>
              <option value="50">50 results</option>
            </select>
          </div>
          
          <div class="option-group">
            <label>Similarity:</label>
            <select v-model="searchParams.similarity_threshold" class="search-select">
              <option value="0.3">Low (30%)</option>
              <option value="0.5">Medium (50%)</option>
              <option value="0.7">High (70%)</option>
              <option value="0.8">Very High (80%)</option>
            </select>
          </div>
          
          <div class="option-group" v-if="false">
            <label>Part of Speech:</label>
            <select v-model="searchParams.pos_filter" class="search-select">
              <option value="">All Types</option>
              <option value="noun">Nouns</option>
              <option value="verb">Verbs</option>
              <option value="adjective">Adjectives</option>
              <option value="adverb">Adverbs</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Search Results -->
    <div v-if="searchResults.length > 0" class="results-section">
      <div class="results-header">
        <h2>Search Results</h2>
        <div class="results-meta">
          <span class="results-count">{{ searchResults.length }} results</span>
          <span class="results-time">{{ searchTime }}ms</span>
        </div>
      </div>

      <div class="results-grid">
        <div 
          v-for="(result, index) in searchResults" 
          :key="index"
          class="result-card"
          @click="openResultModal(result)"
        >
          <!-- Word Header -->
          <div class="result-header">
            <div class="result-word-info">
              <ruby class="result-word">
                {{ result.word }}
                <rt v-if="result.reading && result.reading !== result.word">
                  {{ result.reading }}
                </rt>
              </ruby>
              <div class="similarity-score" :class="getSimilarityClass(result.similarity)">
                {{ Math.round(result.similarity * 100) }}%
              </div>
            </div>
            <div class="result-pos" v-if="result.pos && result.pos.length > 0">
              <span 
                v-for="pos in result.pos.slice(0, 2)" 
                :key="pos"
                class="pos-tag"
              >
                {{ pos }}
              </span>
            </div>
          </div>

          <!-- Definitions -->
          <div class="result-definitions">
            <div 
              v-for="(def, defIndex) in result.definitions.slice(0, 3)" 
              :key="defIndex"
              class="definition-item"
            >
              {{ def }}
            </div>
            <div v-if="result.definitions.length > 3" class="more-definitions">
              +{{ result.definitions.length - 3 }} more definitions
            </div>
          </div>

          <!-- Enhanced Info -->
          <div v-if="result.fullDefinition" class="result-enhanced">
            <div class="enhanced-info">
              <i class="fas fa-plus-circle"></i>
              Full definition available
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- No Results -->
    <div v-else-if="hasSearched && !isSearching" class="no-results">
      <div class="no-results-content">
        <i class="fas fa-search"></i>
        <h3>No Results Found</h3>
        <p>Try adjusting your search terms or similarity threshold.</p>
        <div class="search-suggestions">
          <h4>Suggestions:</h4>
          <ul>
            <li>Use Japanese characters (hiragana, katakana, or kanji)</li>
            <li>Try related concepts or synonyms</li>
            <li>Lower the similarity threshold</li>
            <li>Check for typos in your search query</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isSearching" class="loading-section">
      <div class="loading-content">
        <div class="loading-spinner">
          <i class="fas fa-brain fa-spin"></i>
        </div>
        <h3>Analyzing Semantic Similarity</h3>
        <p>Processing your query with AI embeddings...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="searchError" class="error-section">
      <div class="error-content">
        <i class="fas fa-exclamation-triangle"></i>
        <h3>Search Error</h3>
        <p>{{ searchError }}</p>
        <button @click="clearError" class="error-retry-btn">
          <i class="fas fa-redo"></i>
          Try Again
        </button>
      </div>
    </div>

    <!-- Result Detail Modal -->
    <div v-if="selectedResult" class="result-modal-overlay" @click="closeResultModal">
      <div class="result-modal" @click.stop>
        <div class="modal-header">
          <h2>{{ selectedResult.word }}</h2>
          <button @click="closeResultModal" class="modal-close">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-content">
          <div class="modal-word-info">
            <ruby class="modal-word">
              {{ selectedResult.word }}
              <rt v-if="selectedResult.reading">{{ selectedResult.reading }}</rt>
            </ruby>
            <div class="modal-similarity">
              Similarity: {{ Math.round(selectedResult.similarity * 100) }}%
            </div>
          </div>

          <div v-if="selectedResult.pos" class="modal-pos">
            <h4>Parts of Speech:</h4>
            <div class="pos-tags">
              <span v-for="pos in selectedResult.pos" :key="pos" class="pos-tag">
                {{ pos }}
              </span>
            </div>
          </div>

          <div class="modal-definitions">
            <h4>Definitions:</h4>
            <ol class="definition-list">
              <li v-for="(def, index) in selectedResult.definitions" :key="index">
                {{ def }}
              </li>
            </ol>
          </div>

          <div v-if="selectedResult.fullDefinition" class="modal-enhanced">
            <h4>Enhanced Definition:</h4>
            <div class="enhanced-definition">
              <!-- Display full definition data here -->
              <pre>{{ JSON.stringify(selectedResult.fullDefinition, null, 2) }}</pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'

// State
const searchQuery = ref('')
const searchResults = ref([])
const isSearching = ref(false)
const hasSearched = ref(false)
const searchError = ref('')
const searchTime = ref(0)
const selectedResult = ref(null)

// Search parameters
const searchParams = reactive({
  top_k: 10,
  similarity_threshold: 0.5,
  pos_filter: ''
})

// Methods
const performSearch = async () => {
  if (!searchQuery.value.trim() || isSearching.value) return
  
  isSearching.value = true
  searchError.value = ''
  hasSearched.value = true
  
  try {
    const startTime = Date.now()
    const response = await fetch('http://localhost:3000/api/semantic-search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: searchQuery.value,
        ...searchParams
      })
    })
    
    const endTime = Date.now()
    searchTime.value = endTime - startTime
    
    if (response.ok) {
      const data = await response.json()
      searchResults.value = data.results || []
      
      if (data.searchType === 'fallback') {
        searchError.value = `Fallback search used: ${data.fallbackReason}`
      }
    } else {
      const errorData = await response.json()
      searchError.value = errorData.error || 'Search failed'
      searchResults.value = []
    }
  } catch (error) {
    searchError.value = `Network error: ${error.message}`
    searchResults.value = []
  } finally {
    isSearching.value = false
  }
}

const handleInputChange = () => {
  // Clear previous error when user starts typing
  if (searchError.value) {
    searchError.value = ''
  }
}

const getSimilarityClass = (similarity) => {
  if (similarity >= 0.8) return 'similarity-excellent'
  if (similarity >= 0.6) return 'similarity-good'
  if (similarity >= 0.4) return 'similarity-fair'
  return 'similarity-poor'
}

const openResultModal = (result) => {
  selectedResult.value = result
}

const closeResultModal = () => {
  selectedResult.value = null
}

const clearError = () => {
  searchError.value = ''
}
</script>

<style scoped>
.semantic-search-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  min-height: 100vh;
}

/* Page Header */
.page-header {
  margin-bottom: 2rem;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1.5rem;
}

.header-title h1 {
  margin: 0 0 0.5rem 0;
  font-size: 2.25rem;
  font-weight: 700;
  color: var(--text-primary);
}

.header-description {
  margin: 0;
  font-size: 1.125rem;
  color: var(--text-muted);
}

.header-stats {
  display: flex;
  gap: 1rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  background: var(--surface-medium);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-grey);
}

.stat-card i {
  font-size: 1.5rem;
  color: var(--accent-indigo);
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-number {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-muted);
}

/* Search Interface */
.search-section {
  background: var(--surface-medium);
  border-radius: var(--radius-xl);
  padding: 2rem;
  margin-bottom: 2rem;
  border: 1px solid var(--border-grey);
}

.search-input-group {
  position: relative;
  display: flex;
  align-items: center;
  margin-bottom: 1.5rem;
}

.search-icon {
  position: absolute;
  left: 1rem;
  color: var(--text-muted);
  font-size: 1.125rem;
  z-index: 1;
}

.search-input {
  flex: 1;
  padding: 1rem 1rem 1rem 3rem;
  background: var(--surface-high);
  border: 2px solid var(--border-grey);
  border-radius: var(--radius-lg);
  font-size: 1.125rem;
  color: var(--text-primary);
  transition: all 0.2s ease;
}

.search-input:focus {
  outline: none;
  border-color: var(--accent-indigo);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.search-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.search-button {
  padding: 1rem 1.5rem;
  background: var(--accent-indigo);
  color: white;
  border: none;
  border-radius: var(--radius-lg);
  margin-left: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 60px;
}

.search-button:hover:not(:disabled) {
  background: var(--accent-indigo-hover);
  transform: translateY(-1px);
}

.search-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.search-options {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.option-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.option-group label {
  font-size: 0.875rem;
  color: var(--text-muted);
  font-weight: 500;
}

.search-select {
  padding: 0.5rem 0.75rem;
  background: var(--surface-high);
  border: 1px solid var(--border-grey);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: 0.875rem;
}

/* Results Section */
.results-section {
  margin-bottom: 2rem;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.results-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: var(--text-primary);
}

.results-meta {
  display: flex;
  gap: 1rem;
  align-items: center;
  font-size: 0.875rem;
  color: var(--text-muted);
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.result-card {
  background: var(--surface-medium);
  border: 1px solid var(--border-grey);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.result-card:hover {
  background: var(--surface-high);
  border-color: var(--accent-indigo);
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.result-word-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.result-word {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
}

.result-word rt {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.similarity-score {
  padding: 0.25rem 0.5rem;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 600;
}

.similarity-excellent {
  background: rgba(34, 197, 94, 0.2);
  color: rgb(34, 197, 94);
}

.similarity-good {
  background: rgba(59, 130, 246, 0.2);
  color: rgb(59, 130, 246);
}

.similarity-fair {
  background: rgba(251, 191, 36, 0.2);
  color: rgb(251, 191, 36);
}

.similarity-poor {
  background: rgba(239, 68, 68, 0.2);
  color: rgb(239, 68, 68);
}

.result-pos {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.pos-tag {
  background: var(--surface-overlay);
  color: var(--text-muted);
  padding: 0.25rem 0.5rem;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 500;
}

.result-definitions {
  margin-bottom: 1rem;
}

.definition-item {
  color: var(--text-primary);
  font-size: 0.875rem;
  line-height: 1.5;
  margin-bottom: 0.5rem;
}

.more-definitions {
  color: var(--text-muted);
  font-size: 0.75rem;
  font-style: italic;
}

.result-enhanced {
  padding-top: 1rem;
  border-top: 1px solid var(--border-grey);
}

.enhanced-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--accent-indigo);
  font-size: 0.75rem;
}

/* States */
.loading-section,
.no-results,
.error-section {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}

.loading-content,
.no-results-content,
.error-content {
  text-align: center;
  max-width: 400px;
}

.loading-spinner i {
  font-size: 3rem;
  color: var(--accent-indigo);
  margin-bottom: 1rem;
}

.no-results-content i,
.error-content i {
  font-size: 3rem;
  color: var(--text-muted);
  margin-bottom: 1rem;
}

.no-results h3,
.error-content h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
}

.search-suggestions {
  margin-top: 1.5rem;
  text-align: left;
}

.search-suggestions h4 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
}

.search-suggestions ul {
  margin: 0;
  padding-left: 1.5rem;
}

.search-suggestions li {
  color: var(--text-muted);
  margin-bottom: 0.25rem;
}

.error-retry-btn {
  margin-top: 1rem;
  padding: 0.75rem 1.5rem;
  background: var(--accent-indigo);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-left: auto;
  margin-right: auto;
}

/* Modal */
.result-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.result-modal {
  background: var(--surface-medium);
  border-radius: var(--radius-xl);
  max-width: 600px;
  width: 100%;
  max-height: 80vh;
  overflow-y: auto;
  border: 1px solid var(--border-grey);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid var(--border-grey);
}

.modal-header h2 {
  margin: 0;
  color: var(--text-primary);
}

.modal-close {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 0.5rem;
  border-radius: var(--radius-md);
}

.modal-close:hover {
  background: var(--surface-overlay);
  color: var(--text-primary);
}

.modal-content {
  padding: 1.5rem;
}

.modal-word-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.modal-word {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
}

.modal-similarity {
  padding: 0.5rem 1rem;
  background: var(--surface-overlay);
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  color: var(--text-muted);
}

.modal-pos,
.modal-definitions,
.modal-enhanced {
  margin-bottom: 1.5rem;
}

.modal-pos h4,
.modal-definitions h4,
.modal-enhanced h4 {
  margin: 0 0 0.75rem 0;
  color: var(--text-primary);
  font-size: 1rem;
}

.pos-tags {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.definition-list {
  margin: 0;
  padding-left: 1.5rem;
}

.definition-list li {
  color: var(--text-primary);
  margin-bottom: 0.5rem;
  line-height: 1.5;
}

.enhanced-definition pre {
  background: var(--surface-low);
  padding: 1rem;
  border-radius: var(--radius-md);
  overflow-x: auto;
  font-size: 0.75rem;
  color: var(--text-muted);
}

/* Responsive */
@media (max-width: 768px) {
  .semantic-search-container {
    padding: 1rem;
  }
  
  .header-content {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .search-options {
    flex-direction: column;
    gap: 1rem;
  }
  
  .results-grid {
    grid-template-columns: 1fr;
  }
  
  .result-modal {
    margin: 1rem;
    max-height: calc(100vh - 2rem);
  }
}
</style>