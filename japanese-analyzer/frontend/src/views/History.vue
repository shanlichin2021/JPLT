<template>
  <div class="history-page">
    <section class="page-header">
      <div class="header-container">
        <div class="header-content">
          <div class="header-badge">
            <i class="fas fa-history"></i>
            <span>Text Analysis</span>
          </div>
          
          <h1 class="page-title">
            <span class="title-main">Analysis</span>
            <span class="title-accent">History</span>
          </h1>
          
          <p class="page-subtitle">
            Review and revisit your past Japanese text analysis sessions
          </p>
        </div>
      </div>
    </section>

    <section class="history-content">
      <div class="content-container">
        <div class="empty-state">
          <div class="empty-state-card">
            <div class="empty-icon">
              <i class="fas fa-clock"></i>
            </div>
            
            <div class="empty-content">
              <h3 class="empty-title">History Feature Coming Soon</h3>
              <p class="empty-description">
                We're building a comprehensive analysis history system to help you track and revisit your Japanese text analysis sessions.
              </p>
              
              <div class="empty-features">
                <div class="feature-item">
                  <i class="fas fa-bookmark"></i>
                  <span>Save analysis sessions</span>
                </div>
                <div class="feature-item">
                  <i class="fas fa-search"></i>
                  <span>Search through past results</span>
                </div>
                <div class="feature-item">
                  <i class="fas fa-chart-line"></i>
                  <span>Track learning progress</span>
                </div>
              </div>
              
              <div class="empty-actions">
                <router-link to="/analysis" class="btn btn-primary">
                  <i class="fas fa-play"></i>
                  Start New Analysis
                </router-link>
                <router-link to="/" class="btn btn-outline">
                  <i class="fas fa-home"></i>
                  Back to Home
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
// History functionality to be implemented
</script>

<style scoped>
.history-page {
  min-height: 100vh;
  background: var(--primary-black);
  color: var(--text-primary);
}

/* =====================================================
   HEADER SECTION
   ===================================================== */

.page-header {
  padding: 4rem 0 6rem;
  background: linear-gradient(135deg, var(--primary-black) 0%, var(--surface-low) 50%, var(--primary-black) 100%);
  position: relative;
  overflow: hidden;
}

.page-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 30% 50%, rgba(91, 127, 255, 0.1) 0%, transparent 50%);
  pointer-events: none;
}

.header-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  position: relative;
  z-index: 2;
}

.header-content {
  text-align: center;
}

.header-badge {
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

.header-badge i {
  color: var(--accent-indigo);
}

.page-title {
  font-size: 3.5rem;
  font-weight: 700;
  line-height: 1.1;
  margin-bottom: 1.5rem;
  color: var(--text-primary);
}

.title-main {
  color: var(--text-primary);
}

.title-accent {
  background: linear-gradient(135deg, var(--accent-indigo) 0%, var(--accent-indigo-light) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-subtitle {
  font-size: 1.25rem;
  line-height: 1.6;
  color: var(--text-secondary);
  max-width: 600px;
  margin: 0 auto;
}

/* =====================================================
   CONTENT SECTION
   ===================================================== */

.history-content {
  padding: 4rem 0 6rem;
  background: var(--surface-low);
}

.content-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
}

.empty-state-card {
  background: var(--surface-medium);
  border: 1px solid var(--border-grey);
  border-radius: var(--radius-xl);
  padding: 3rem;
  text-align: center;
  max-width: 600px;
  box-shadow: var(--shadow-xl);
  position: relative;
  overflow: hidden;
}

.empty-state-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--accent-indigo), transparent);
}

.empty-icon {
  width: 100px;
  height: 100px;
  background: linear-gradient(135deg, var(--accent-indigo) 0%, var(--accent-indigo-dark) 100%);
  border-radius: var(--radius-xl);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 2rem;
  color: white;
  font-size: 2.5rem;
  box-shadow: var(--shadow-lg);
}

.empty-content {
  text-align: center;
}

.empty-title {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.empty-description {
  font-size: 1.125rem;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 2.5rem;
}

.empty-features {
  display: grid;
  gap: 1rem;
  margin-bottom: 2.5rem;
  text-align: left;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: var(--surface-high);
  border: 1px solid var(--border-grey);
  border-radius: var(--radius-md);
  transition: all 0.2s ease;
}

.feature-item:hover {
  background: var(--surface-overlay);
  border-color: var(--border-light);
  transform: translateY(-2px);
}

.feature-item i {
  color: var(--accent-indigo);
  font-size: 1.25rem;
  width: 20px;
  text-align: center;
}

.feature-item span {
  color: var(--text-secondary);
  font-weight: 500;
}

.empty-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  align-items: center;
}

.empty-actions .btn {
  padding: 1rem 2rem;
  font-size: 1rem;
  font-weight: 600;
  min-width: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  text-decoration: none;
}

/* =====================================================
   RESPONSIVE DESIGN
   ===================================================== */

@media (max-width: 768px) {
  .page-title {
    font-size: 2.5rem;
  }
  
  .empty-state-card {
    padding: 2rem;
    margin: 0 1rem;
  }
  
  .empty-actions {
    flex-direction: column;
    align-items: stretch;
  }
  
  .empty-actions .btn {
    width: 100%;
  }
  
  .empty-features {
    gap: 0.75rem;
  }
  
  .feature-item {
    padding: 0.75rem;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 2rem;
  }
  
  .page-subtitle {
    font-size: 1rem;
  }
  
  .content-container {
    padding: 0 1rem;
  }
  
  .empty-icon {
    width: 80px;
    height: 80px;
    font-size: 2rem;
  }
  
  .empty-title {
    font-size: 1.5rem;
  }
  
  .empty-description {
    font-size: 1rem;
  }
}
</style>