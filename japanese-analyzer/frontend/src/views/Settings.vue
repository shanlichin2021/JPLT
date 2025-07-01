<template>
  <div class="settings-page">
    <!-- Settings Header -->
    <section class="settings-header">
      <div class="header-container">
        <div class="header-content">
          <div class="header-badge">
            <i class="fas fa-cog"></i>
            <span>System Configuration</span>
          </div>
          
          <h1 class="header-title">Settings</h1>
          <p class="header-description">
            Customize your Japanese text analysis experience with advanced configuration options
          </p>
        </div>
      </div>
    </section>

    <!-- Settings Content -->
    <section class="settings-content">
      <div class="content-container">
        <!-- Settings Categories Grid -->
        <div class="settings-grid">
          <!-- Analysis Settings Card -->
          <div class="settings-card">
            <div class="card-header">
              <div class="card-icon">
                <i class="fas fa-brain text-purple-400"></i>
              </div>
              <div class="card-info">
                <h3 class="card-title">Analysis Engine</h3>
                <p class="card-description">Configure NLP analysis parameters</p>
              </div>
            </div>
            <div class="card-content">
              <div class="setting-item">
                <label class="setting-label">Tokenizer Models</label>
                <div class="setting-value">Multi-model consensus (4 models)</div>
              </div>
              <div class="setting-item">
                <label class="setting-label">Grammar Patterns</label>
                <div class="setting-value">50+ patterns active</div>
              </div>
            </div>
          </div>

          <!-- Dictionary Settings Card -->
          <div class="settings-card">
            <div class="card-header">
              <div class="card-icon">
                <i class="fas fa-book text-green-400"></i>
              </div>
              <div class="card-info">
                <h3 class="card-title">Dictionary System</h3>
                <p class="card-description">Manage dictionary preferences</p>
              </div>
            </div>
            <div class="card-content">
              <div class="setting-item">
                <label class="setting-label">Dictionary Entries</label>
                <div class="setting-value">212,380+ entries</div>
              </div>
              <div class="setting-item">
                <label class="setting-label">Cache Performance</label>
                <div class="setting-value">32x speedup enabled</div>
              </div>
            </div>
          </div>

          <!-- Display Settings Card -->
          <div class="settings-card">
            <div class="card-header">
              <div class="card-icon">
                <i class="fas fa-palette text-blue-400"></i>
              </div>
              <div class="card-info">
                <h3 class="card-title">Display & UI</h3>
                <p class="card-description">Customize visual appearance</p>
              </div>
            </div>
            <div class="card-content">
              <div class="setting-item">
                <label class="setting-label">Theme</label>
                <div class="setting-value">Modern Dark</div>
              </div>
              <div class="setting-item">
                <label class="setting-label">Furigana Display</label>
                <div class="setting-value">Always visible</div>
              </div>
            </div>
          </div>

          <!-- Performance Settings Card -->
          <div class="settings-card">
            <div class="card-header">
              <div class="card-icon">
                <i class="fas fa-tachometer-alt text-red-400"></i>
              </div>
              <div class="card-info">
                <h3 class="card-title">Performance</h3>
                <p class="card-description">System optimization settings</p>
              </div>
            </div>
            <div class="card-content">
              <div class="setting-item">
                <label class="setting-label">Response Time</label>
                <div class="setting-value">&lt;1 second</div>
              </div>
              <div class="setting-item">
                <label class="setting-label">Cache Size</label>
                <div class="setting-value">1000 entries (LRU)</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Coming Soon Section -->
        <div class="coming-soon-section">
          <div class="coming-soon-card">
            <div class="coming-soon-icon">
              <i class="fas fa-tools"></i>
            </div>
            <h3 class="coming-soon-title">Advanced Configuration Coming Soon</h3>
            <p class="coming-soon-description">
              Interactive settings panels with real-time configuration options will be available in the next update
            </p>
            <div class="coming-soon-features">
              <div class="feature-item">
                <i class="fas fa-check-circle"></i>
                <span>Custom tokenizer weights</span>
              </div>
              <div class="feature-item">
                <i class="fas fa-check-circle"></i>
                <span>Grammar pattern toggles</span>
              </div>
              <div class="feature-item">
                <i class="fas fa-check-circle"></i>
                <span>Theme customization</span>
              </div>
              <div class="feature-item">
                <i class="fas fa-check-circle"></i>
                <span>Performance tuning</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
// Settings functionality to be implemented
// Future features: theme switching, analysis preferences, performance tuning
</script>

<style scoped>
.settings-page {
  min-height: 100vh;
  background: var(--primary-black);
  color: var(--text-primary);
}

/* =====================================================
   SETTINGS HEADER
   ===================================================== */

.settings-header {
  padding: 3rem 0 4rem;
  background: linear-gradient(135deg, var(--primary-black) 0%, var(--surface-low) 50%, var(--primary-black) 100%);
  position: relative;
  overflow: hidden;
}

.settings-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 50% 50%, rgba(91, 127, 255, 0.08) 0%, transparent 70%);
  pointer-events: none;
}

.header-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

.header-content {
  text-align: center;
  position: relative;
  z-index: 2;
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
  margin-bottom: 1.5rem;
}

.header-badge i {
  color: var(--accent-indigo);
}

.header-title {
  font-size: 3rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 1rem;
  background: linear-gradient(135deg, var(--text-primary) 0%, var(--text-secondary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-description {
  font-size: 1.125rem;
  color: var(--text-secondary);
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.6;
}

/* =====================================================
   SETTINGS CONTENT
   ===================================================== */

.settings-content {
  padding: 2rem 0 4rem;
  background: var(--primary-black);
}

.content-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;
}

.settings-card {
  background: var(--surface-medium);
  border: 1px solid var(--border-grey);
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition: all 0.3s ease;
  position: relative;
}

.settings-card::before {
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

.settings-card:hover::before {
  transform: translateX(100%);
}

.settings-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-xl);
  border-color: var(--border-light);
}

.card-header {
  padding: 1.5rem;
  border-bottom: 1px solid var(--border-grey);
  display: flex;
  align-items: center;
  gap: 1rem;
}

.card-icon {
  width: 50px;
  height: 50px;
  background: var(--surface-high);
  border: 1px solid var(--border-grey);
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  flex-shrink: 0;
}

.card-info {
  flex: 1;
}

.card-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 0.25rem 0;
}

.card-description {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin: 0;
}

.card-content {
  padding: 1.5rem;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--border-grey);
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-label {
  font-size: 0.875rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.setting-value {
  font-size: 0.875rem;
  color: var(--text-primary);
  font-weight: 600;
  background: var(--surface-high);
  padding: 0.25rem 0.75rem;
  border-radius: var(--radius-sm);
}

/* =====================================================
   COMING SOON SECTION
   ===================================================== */

.coming-soon-section {
  text-align: center;
}

.coming-soon-card {
  background: var(--surface-low);
  border: 1px solid var(--border-grey);
  border-radius: var(--radius-xl);
  padding: 3rem 2rem;
  max-width: 600px;
  margin: 0 auto;
  position: relative;
  overflow: hidden;
}

.coming-soon-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at center, rgba(91, 127, 255, 0.05) 0%, transparent 70%);
  pointer-events: none;
}

.coming-soon-icon {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, var(--accent-indigo) 0%, var(--accent-indigo-dark) 100%);
  border-radius: var(--radius-xl);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1.5rem;
  color: white;
  font-size: 2rem;
  box-shadow: var(--shadow-lg);
}

.coming-soon-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.coming-soon-description {
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 2rem;
}

.coming-soon-features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  text-align: left;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: var(--surface-medium);
  border: 1px solid var(--border-grey);
  border-radius: var(--radius-md);
  transition: all 0.2s ease;
}

.feature-item:hover {
  background: var(--surface-high);
  border-color: var(--border-light);
}

.feature-item i {
  color: var(--accent-indigo);
  font-size: 1rem;
  flex-shrink: 0;
}

.feature-item span {
  font-size: 0.875rem;
  color: var(--text-secondary);
  font-weight: 500;
}

/* =====================================================
   RESPONSIVE DESIGN
   ===================================================== */

@media (max-width: 768px) {
  .header-title {
    font-size: 2.5rem;
  }
  
  .settings-grid {
    grid-template-columns: 1fr;
  }
  
  .card-header {
    flex-direction: column;
    text-align: center;
    gap: 0.75rem;
  }
  
  .card-info {
    text-align: center;
  }
  
  .coming-soon-features {
    grid-template-columns: 1fr;
  }
  
  .content-container {
    padding: 0 1rem;
  }
}

@media (max-width: 480px) {
  .header-title {
    font-size: 2rem;
  }
  
  .header-description {
    font-size: 1rem;
  }
  
  .coming-soon-card {
    padding: 2rem 1rem;
  }
  
  .setting-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .setting-value {
    align-self: flex-end;
  }
}
</style>