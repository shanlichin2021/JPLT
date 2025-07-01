<template>
  <div class="about-page">
    <!-- Hero Header -->
    <section class="hero-header">
      <div class="hero-container">
        <div class="hero-badge">
          <i class="fas fa-info-circle"></i>
          <span>System Information</span>
        </div>
        
        <h1 class="hero-title">
          About <span class="hero-accent">Japanese Analyzer</span>
        </h1>
        
        <p class="hero-description">
          Discover the advanced technology powering comprehensive Japanese text analysis and language processing
        </p>
      </div>
    </section>

    <!-- Main Content -->
    <section class="about-content">
      <div class="content-container">
        <!-- Overview Card -->
        <div class="overview-card card">
          <div class="card-header">
            <h2 class="card-title">
              <i class="fas fa-language text-accent"></i>
              Advanced Japanese Text Analysis
            </h2>
          </div>
          
          <div class="card-content">
            <p class="overview-text">
              Our system combines cutting-edge artificial intelligence with comprehensive linguistic databases 
              to deliver precise Japanese text analysis. From OCR extraction to morphological parsing, 
              we provide tools that bridge the gap between complex Japanese language structures and accessible understanding.
            </p>
            
            <div class="capabilities-grid">
              <div class="capability-item">
                <div class="capability-icon">
                  <i class="fas fa-camera text-blue-400"></i>
                </div>
                <div class="capability-content">
                  <h3 class="capability-title">OCR Recognition</h3>
                  <p class="capability-description">High-accuracy text extraction from images with preprocessing optimization</p>
                </div>
              </div>
              
              <div class="capability-item">
                <div class="capability-icon">
                  <i class="fas fa-brain text-purple-400"></i>
                </div>
                <div class="capability-content">
                  <h3 class="capability-title">NLP Analysis</h3>
                  <p class="capability-description">Multi-model consensus tokenization with advanced grammar pattern recognition</p>
                </div>
              </div>
              
              <div class="capability-item">
                <div class="capability-icon">
                  <i class="fas fa-book text-green-400"></i>
                </div>
                <div class="capability-content">
                  <h3 class="capability-title">Dictionary Lookup</h3>
                  <p class="capability-description">Comprehensive database with 212,000+ entries and contextual definitions</p>
                </div>
              </div>
              
              <div class="capability-item">
                <div class="capability-icon">
                  <i class="fas fa-ruby text-red-400"></i>
                </div>
                <div class="capability-content">
                  <h3 class="capability-title">Furigana Support</h3>
                  <p class="capability-description">Automatic reading assistance with intelligent ruby text generation</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Technical Architecture -->
        <div class="tech-architecture card">
          <div class="card-header">
            <h2 class="card-title">
              <i class="fas fa-cogs text-accent"></i>
              Technical Architecture
            </h2>
          </div>
          
          <div class="card-content">
            <div class="tech-stack-grid">
              <div class="tech-stack-item">
                <div class="tech-icon">
                  <i class="fab fa-vuejs text-green-400"></i>
                </div>
                <div class="tech-details">
                  <h3 class="tech-name">Frontend</h3>
                  <p class="tech-description">Vue.js 3 with Composition API, modern component architecture</p>
                  <div class="tech-features">
                    <span class="tech-feature">Reactive UI</span>
                    <span class="tech-feature">Tailwind CSS</span>
                    <span class="tech-feature">Vite Build</span>
                  </div>
                </div>
              </div>

              <div class="tech-stack-item">
                <div class="tech-icon">
                  <i class="fab fa-node-js text-green-600"></i>
                </div>
                <div class="tech-details">
                  <h3 class="tech-name">Backend API</h3>
                  <p class="tech-description">Node.js with Express, circuit breaker patterns, performance optimization</p>
                  <div class="tech-features">
                    <span class="tech-feature">RESTful API</span>
                    <span class="tech-feature">Circuit Breaker</span>
                    <span class="tech-feature">Error Handling</span>
                  </div>
                </div>
              </div>

              <div class="tech-stack-item">
                <div class="tech-icon">
                  <i class="fab fa-python text-yellow-400"></i>
                </div>
                <div class="tech-details">
                  <h3 class="tech-name">NLP Engine</h3>
                  <p class="tech-description">Python with GiNZA, SudachiPy, and Fugashi for multi-model consensus</p>
                  <div class="tech-features">
                    <span class="tech-feature">FastAPI</span>
                    <span class="tech-feature">spaCy</span>
                    <span class="tech-feature">Multi-tokenizer</span>
                  </div>
                </div>
              </div>

              <div class="tech-stack-item">
                <div class="tech-icon">
                  <i class="fas fa-database text-blue-400"></i>
                </div>
                <div class="tech-details">
                  <h3 class="tech-name">Database</h3>
                  <p class="tech-description">SQLite with JMdict integration, comprehensive linguistic metadata</p>
                  <div class="tech-features">
                    <span class="tech-feature">212K+ entries</span>
                    <span class="tech-feature">Fast queries</span>
                    <span class="tech-feature">Optimized indexes</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Performance Stats -->
        <div class="performance-stats card">
          <div class="card-header">
            <h2 class="card-title">
              <i class="fas fa-tachometer-alt text-accent"></i>
              Performance & Capabilities
            </h2>
          </div>
          
          <div class="card-content">
            <div class="stats-grid">
              <div class="stat-item">
                <div class="stat-number">212,380+</div>
                <div class="stat-label">Dictionary Entries</div>
                <div class="stat-description">Comprehensive JMdict database</div>
              </div>
              
              <div class="stat-item">
                <div class="stat-number">50+</div>
                <div class="stat-label">Grammar Patterns</div>
                <div class="stat-description">Advanced pattern recognition</div>
              </div>
              
              <div class="stat-item">
                <div class="stat-number">&lt;1s</div>
                <div class="stat-label">Response Time</div>
                <div class="stat-description">Optimized processing pipeline</div>
              </div>
              
              <div class="stat-item">
                <div class="stat-number">4</div>
                <div class="stat-label">Tokenizers</div>
                <div class="stat-description">Multi-model consensus algorithm</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
// About page - system information display
</script>

<style scoped>
.about-page {
  min-height: 100vh;
  background: var(--primary-black);
  color: var(--text-primary);
}

/* =====================================================
   HERO HEADER
   ===================================================== */

.hero-header {
  padding: 4rem 0 2rem;
  background: linear-gradient(135deg, var(--primary-black) 0%, var(--surface-low) 50%, var(--primary-black) 100%);
  position: relative;
  overflow: hidden;
}

.hero-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 50% 50%, rgba(91, 127, 255, 0.08) 0%, transparent 70%);
  pointer-events: none;
}

.hero-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 2rem;
  text-align: center;
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
  font-size: 2.5rem;
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
  font-size: 1.125rem;
  line-height: 1.6;
  color: var(--text-secondary);
  margin-bottom: 2rem;
}

/* =====================================================
   CONTENT SECTIONS
   ===================================================== */

.about-content {
  padding: 2rem 0 4rem;
  background: var(--primary-black);
}

.content-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.text-accent {
  color: var(--accent-indigo);
}

.overview-card {
  background: var(--surface-medium);
  border: 1px solid var(--border-grey);
}

.overview-text {
  font-size: 1rem;
  line-height: 1.7;
  color: var(--text-secondary);
  margin-bottom: 2rem;
}

.capabilities-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

.capability-item {
  display: flex;
  gap: 1rem;
  padding: 1.5rem;
  background: var(--surface-high);
  border: 1px solid var(--border-grey);
  border-radius: var(--radius-lg);
  transition: all 0.3s ease;
}

.capability-item:hover {
  background: var(--surface-overlay);
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.capability-icon {
  width: 48px;
  height: 48px;
  background: var(--surface-low);
  border: 1px solid var(--border-grey);
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  flex-shrink: 0;
}

.capability-content {
  flex: 1;
}

.capability-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.capability-description {
  font-size: 0.875rem;
  color: var(--text-muted);
  line-height: 1.5;
}

/* Tech Architecture */
.tech-architecture {
  background: var(--surface-medium);
  border: 1px solid var(--border-grey);
}

.tech-stack-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.tech-stack-item {
  background: var(--surface-high);
  border: 1px solid var(--border-grey);
  border-radius: var(--radius-lg);
  padding: 2rem;
  transition: all 0.3s ease;
}

.tech-stack-item:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
  border-color: var(--border-light);
}

.tech-icon {
  width: 64px;
  height: 64px;
  background: var(--surface-low);
  border: 1px solid var(--border-grey);
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  margin-bottom: 1.5rem;
}

.tech-name {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.tech-description {
  color: var(--text-secondary);
  font-size: 0.875rem;
  line-height: 1.5;
  margin-bottom: 1rem;
}

.tech-features {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tech-feature {
  background: var(--accent-indigo);
  color: white;
  font-size: 0.75rem;
  font-weight: 500;
  padding: 0.25rem 0.5rem;
  border-radius: var(--radius-sm);
}

/* Performance Stats */
.performance-stats {
  background: var(--surface-medium);
  border: 1px solid var(--border-grey);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2rem;
}

.stat-item {
  text-align: center;
  padding: 1.5rem;
  background: var(--surface-high);
  border: 1px solid var(--border-grey);
  border-radius: var(--radius-lg);
  transition: all 0.3s ease;
}

.stat-item:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  border-color: var(--border-light);
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  color: var(--accent-indigo);
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.25rem;
}

.stat-description {
  font-size: 0.75rem;
  color: var(--text-muted);
}

/* =====================================================
   RESPONSIVE DESIGN
   ===================================================== */

@media (max-width: 768px) {
  .hero-title {
    font-size: 2rem;
  }
  
  .hero-description {
    font-size: 1rem;
  }
  
  .content-container {
    padding: 0 1rem;
  }
  
  .capabilities-grid {
    grid-template-columns: 1fr;
  }
  
  .tech-stack-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .hero-title {
    font-size: 1.75rem;
  }
  
  .capability-item {
    flex-direction: column;
    text-align: center;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .tech-stack-item {
    padding: 1.5rem;
  }
}
</style>