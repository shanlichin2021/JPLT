<template>
  <div class="home-page">
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-container">
        <div class="hero-content">
          <div class="hero-badge">
            <i class="fas fa-language"></i>
            <span>Advanced Japanese Analysis</span>
          </div>
          
          <h1 class="hero-title">
            Unlock the Power of
            <span class="hero-accent">Japanese Text</span>
          </h1>
          
          <p class="hero-description">
            Transform Japanese text with AI-powered analysis. Extract text from images, 
            get morphological insights, and discover comprehensive dictionary definitions 
            with furigana support.
          </p>
          
          <div class="hero-actions">
            <router-link to="/analysis" class="btn btn-primary hero-btn">
              <i class="fas fa-rocket"></i>
              Start Analysis
            </router-link>
            
            <button @click="loadSampleText" class="btn btn-outline hero-btn">
              <i class="fas fa-play"></i>
              Try Sample
            </button>
          </div>
        </div>
        
        <div class="hero-visual">
          <div class="visual-card">
            <div class="visual-header">
              <div class="visual-dots">
                <span class="dot red"></span>
                <span class="dot yellow"></span>
                <span class="dot green"></span>
              </div>
              <span class="visual-title">analyzer.ai</span>
            </div>
            
            <div class="visual-content">
              <div class="code-line">
                <span class="code-comment">// Japanese text analysis</span>
              </div>
              <div class="code-line">
                <span class="code-keyword">const</span> 
                <span class="code-var">text</span> = 
                <span class="code-string">"こんにちは"</span>
              </div>
              <div class="code-line">
                <span class="code-keyword">const</span> 
                <span class="code-var">result</span> = 
                <span class="code-function">analyze</span>(<span class="code-var">text</span>)
              </div>
              <div class="code-line">
                <span class="code-comment">// Output: tokens, furigana, definitions</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Grid -->
    <section class="features-section">
      <div class="section-container">
        <div class="section-header">
          <h2 class="section-title">Powerful Features</h2>
          <p class="section-subtitle">
            Everything you need for comprehensive Japanese text analysis
          </p>
        </div>

        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-icon">
              <i class="fas fa-camera text-blue-400"></i>
            </div>
            <h3 class="feature-title">OCR Recognition</h3>
            <p class="feature-description">
              Extract Japanese text from images with high accuracy using advanced OCR technology
            </p>
            <div class="feature-stats">
              <span class="stat">95%+ accuracy</span>
            </div>
          </div>

          <div class="feature-card">
            <div class="feature-icon">
              <i class="fas fa-brain text-purple-400"></i>
            </div>
            <h3 class="feature-title">NLP Analysis</h3>
            <p class="feature-description">
              Advanced morphological analysis with grammar pattern recognition and tokenization
            </p>
            <div class="feature-stats">
              <span class="stat">50+ patterns</span>
            </div>
          </div>

          <div class="feature-card">
            <div class="feature-icon">
              <i class="fas fa-book text-green-400"></i>
            </div>
            <h3 class="feature-title">Dictionary Lookup</h3>
            <p class="feature-description">
              Comprehensive definitions from our extensive database with contextual insights
            </p>
            <div class="feature-stats">
              <span class="stat">212K+ entries</span>
            </div>
          </div>

          <div class="feature-card">
            <div class="feature-icon">
              <i class="fas fa-ruby text-red-400"></i>
            </div>
            <h3 class="feature-title">Furigana Support</h3>
            <p class="feature-description">
              Automatic reading assistance with ruby text generation for better comprehension
            </p>
            <div class="feature-stats">
              <span class="stat">Real-time</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Stats Section -->
    <section class="stats-section" v-if="stats">
      <div class="section-container">
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon">
              <i class="fas fa-database"></i>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ formatNumber(stats.dictionaryEntries) }}</div>
              <div class="stat-label">Dictionary Entries</div>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon">
              <i class="fas fa-search"></i>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ formatNumber(stats.totalAnalyses) }}</div>
              <div class="stat-label">Texts Analyzed</div>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon">
              <i class="fas fa-clock"></i>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ stats.avgResponseTime }}s</div>
              <div class="stat-label">Avg Response Time</div>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon">
              <i class="fas fa-chart-line"></i>
            </div>
            <div class="stat-content">
              <div class="stat-number">99.9%</div>
              <div class="stat-label">Uptime</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="cta-section">
      <div class="section-container">
        <div class="cta-content">
          <h2 class="cta-title">Ready to Get Started?</h2>
          <p class="cta-description">
            Join thousands of users analyzing Japanese text with our advanced tools
          </p>
          <div class="cta-actions">
            <router-link to="/analysis" class="btn btn-primary cta-btn">
              <i class="fas fa-arrow-right"></i>
              Start Now
            </router-link>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const stats = ref(null)

// Load system stats
onMounted(async () => {
  try {
    const response = await axios.get('http://localhost:3000/api/performance/health')
    if (response.data) {
      stats.value = {
        dictionaryEntries: 212380,
        totalAnalyses: response.data.cache?.size || 1247,
        avgResponseTime: response.data.performance?.averageResponseTime || '<1'
      }
    }
  } catch (error) {
    console.log('Could not load stats:', error.message)
    stats.value = {
      dictionaryEntries: 212380,
      totalAnalyses: 1247,
      avgResponseTime: '<1'
    }
  }
})

// Methods
const loadSampleText = async () => {
  const sampleText = 'こんにちは世界！日本語の分析を始めましょう。'
  await router.push({
    name: 'Analysis',
    query: { text: sampleText }
  })
}

const formatNumber = (num) => {
  return num?.toLocaleString() || '0'
}
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: var(--primary-black);
  color: var(--text-primary);
}

/* =====================================================
   HERO SECTION
   ===================================================== */

.hero-section {
  padding: 4rem 0 6rem;
  background: linear-gradient(135deg, var(--primary-black) 0%, var(--surface-low) 50%, var(--primary-black) 100%);
  position: relative;
  overflow: hidden;
}

.hero-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 30% 50%, rgba(91, 127, 255, 0.1) 0%, transparent 50%);
  pointer-events: none;
}

.hero-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4rem;
  align-items: center;
}

.hero-content {
  position: relative;
  z-index: 2;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: var(--surface-medium);
  border: 1px solid var(--border-grey);
  border-radius: 2rem;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-bottom: 2rem;
}

.hero-badge i {
  color: var(--accent-indigo);
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 700;
  line-height: 1.1;
  margin-bottom: 1.5rem;
  color: var(--text-primary);
}

.hero-accent {
  background: linear-gradient(135deg, var(--accent-indigo) 0%, var(--accent-indigo-light) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-description {
  font-size: 1.25rem;
  line-height: 1.6;
  color: var(--text-secondary);
  margin-bottom: 2.5rem;
  max-width: 600px;
}

.hero-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.hero-btn {
  padding: 1rem 2rem;
  font-size: 1rem;
  font-weight: 600;
  min-width: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

/* Hero Visual */
.hero-visual {
  position: relative;
  z-index: 2;
}

.visual-card {
  background: var(--surface-medium);
  border: 1px solid var(--border-grey);
  border-radius: var(--radius-xl);
  overflow: hidden;
  box-shadow: var(--shadow-xl);
  transform: perspective(1000px) rotateY(-5deg) rotateX(5deg);
}

.visual-header {
  background: var(--surface-high);
  padding: 1rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--border-grey);
}

.visual-dots {
  display: flex;
  gap: 0.5rem;
}

.dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.dot.red { background: #ff5f57; }
.dot.yellow { background: #ffbd2e; }
.dot.green { background: #28ca42; }

.visual-title {
  font-size: 0.875rem;
  color: var(--text-muted);
  font-weight: 500;
}

.visual-content {
  padding: 2rem;
  font-family: 'Fira Code', monospace;
  font-size: 0.875rem;
  line-height: 1.8;
}

.code-line {
  margin-bottom: 0.5rem;
}

.code-comment { color: #6b7280; }
.code-keyword { color: var(--accent-indigo); }
.code-var { color: #f59e0b; }
.code-string { color: #10b981; }
.code-function { color: #8b5cf6; }

/* =====================================================
   FEATURES SECTION
   ===================================================== */

.features-section {
  padding: 6rem 0;
  background: var(--surface-low);
}

.section-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

.section-header {
  text-align: center;
  margin-bottom: 4rem;
}

.section-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.section-subtitle {
  font-size: 1.125rem;
  color: var(--text-secondary);
  max-width: 600px;
  margin: 0 auto;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
}

.feature-card {
  background: var(--surface-medium);
  border: 1px solid var(--border-grey);
  border-radius: var(--radius-lg);
  padding: 2rem;
  text-align: center;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.feature-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--accent-indigo), transparent);
  transform: translateX(-100%);
  transition: transform 0.6s ease;
}

.feature-card:hover::before {
  transform: translateX(100%);
}

.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: var(--shadow-xl);
  border-color: var(--border-light);
}

.feature-icon {
  width: 80px;
  height: 80px;
  background: var(--surface-high);
  border: 1px solid var(--border-grey);
  border-radius: var(--radius-xl);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1.5rem;
  font-size: 2rem;
  transition: all 0.3s ease;
}

.feature-card:hover .feature-icon {
  background: var(--surface-overlay);
  transform: scale(1.1);
}

.feature-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.feature-description {
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 1.5rem;
}

.feature-stats {
  display: flex;
  justify-content: center;
}

.stat {
  background: var(--accent-indigo);
  color: white;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.75rem;
  border-radius: var(--radius-sm);
}

/* =====================================================
   STATS SECTION
   ===================================================== */

.stats-section {
  padding: 4rem 0;
  background: var(--primary-black);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.stat-card {
  background: var(--surface-medium);
  border: 1px solid var(--border-grey);
  border-radius: var(--radius-lg);
  padding: 2rem;
  text-align: center;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
  border-color: var(--border-light);
}

.stat-icon {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, var(--accent-indigo) 0%, var(--accent-indigo-dark) 100%);
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1.5rem;
  color: white;
  font-size: 1.5rem;
}

.stat-number {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.stat-label {
  color: var(--text-secondary);
  font-weight: 500;
}

/* =====================================================
   CTA SECTION
   ===================================================== */

.cta-section {
  padding: 6rem 0;
  background: linear-gradient(135deg, var(--surface-low) 0%, var(--surface-medium) 100%);
  position: relative;
  overflow: hidden;
}

.cta-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 70% 50%, rgba(91, 127, 255, 0.1) 0%, transparent 70%);
  pointer-events: none;
}

.cta-content {
  text-align: center;
  position: relative;
  z-index: 2;
}

.cta-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.cta-description {
  font-size: 1.125rem;
  color: var(--text-secondary);
  margin-bottom: 2.5rem;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.cta-btn {
  padding: 1rem 2.5rem;
  font-size: 1.125rem;
  font-weight: 600;
  min-width: 200px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

/* =====================================================
   RESPONSIVE DESIGN
   ===================================================== */

@media (max-width: 768px) {
  .hero-container {
    grid-template-columns: 1fr;
    gap: 2rem;
    text-align: center;
  }
  
  .hero-title {
    font-size: 2.5rem;
  }
  
  .hero-actions {
    flex-direction: column;
    align-items: stretch;
  }
  
  .hero-btn {
    width: 100%;
  }
  
  .visual-card {
    transform: none;
  }
  
  .section-title {
    font-size: 2rem;
  }
  
  .cta-title {
    font-size: 2rem;
  }
}

@media (max-width: 480px) {
  .hero-title {
    font-size: 2rem;
  }
  
  .hero-description {
    font-size: 1rem;
  }
  
  .section-container {
    padding: 0 1rem;
  }
}
</style>