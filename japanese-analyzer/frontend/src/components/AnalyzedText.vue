<template>
  <div class="analyzed-text-container">
    <!-- Analysis Controls -->
    <div class="analysis-controls">
      <div class="control-group">
        <label class="control-label">
          <input 
            type="checkbox" 
            v-model="showDependencies" 
            class="control-checkbox"
          /> 
          Dependency Relations
        </label>
        <label class="control-label">
          <input 
            type="checkbox" 
            v-model="showSemanticRoles" 
            class="control-checkbox"
          /> 
          Semantic Roles
        </label>
        <label class="control-label">
          <input 
            type="checkbox" 
            v-model="showGrammarHighlight" 
            class="control-checkbox"
          /> 
          Grammar Highlighting
        </label>
        <label class="control-label">
          <input 
            type="checkbox" 
            v-model="showUncertainty" 
            class="control-checkbox"
          /> 
          Uncertainty Visualization
        </label>
        <label class="control-label">
          <input 
            type="checkbox" 
            v-model="showCompoundAnalysis" 
            class="control-checkbox"
          /> 
          Compound Verb Analysis
        </label>
      </div>
      
      <!-- Advanced Analysis Mode Toggle -->
      <div class="advanced-controls">
        <label class="control-label">
          <input 
            type="checkbox" 
            v-model="useAdvancedFeatures" 
            class="control-checkbox"
            @change="onAdvancedFeaturesToggle"
          /> 
          Advanced Analysis Mode
        </label>
        <div v-if="useAdvancedFeatures" class="advanced-options">
          <select v-model="transformerMode" class="transformer-select">
            <option value="auto">Auto</option>
            <option value="fast">Fast</option>
            <option value="accurate">Accurate</option>
            <option value="context">Long Context</option>
          </select>
        </div>
      </div>
      
      <!-- Uncertainty Threshold Slider -->
      <div v-if="showUncertainty" class="uncertainty-controls">
        <label class="control-label">
          Uncertainty Threshold: {{ uncertaintyThreshold.toFixed(2) }}
        </label>
        <input 
          type="range" 
          v-model.number="uncertaintyThreshold" 
          min="0" 
          max="1" 
          step="0.01" 
          class="uncertainty-slider"
        />
      </div>
    </div>

    <!-- Syntactic Patterns Display -->
    <div v-if="syntacticPatterns && syntacticPatterns.length > 0" class="patterns-section">
      <h3 class="patterns-title">Detected Syntactic Patterns</h3>
      <div class="patterns-list">
        <div 
          v-for="(pattern, index) in syntacticPatterns" 
          :key="index" 
          class="pattern-badge"
          :class="getPatternClass(pattern.pattern_type)"
        >
          <span class="pattern-type">{{ formatPatternType(pattern.pattern_type) }}</span>
          <span class="pattern-confidence">{{ Math.round(pattern.confidence * 100) }}%</span>
          <div class="pattern-description">{{ pattern.description }}</div>
        </div>
      </div>
    </div>

    <!-- Parse Validation Display -->
    <div v-if="parseValidation" class="validation-section">
      <div class="validation-status" :class="{ 'valid': parseValidation.is_valid, 'invalid': !parseValidation.is_valid }">
        <i :class="parseValidation.is_valid ? 'fas fa-check-circle' : 'fas fa-exclamation-triangle'"></i>
        <span>{{ parseValidation.is_valid ? 'Valid Parse' : 'Parse Issues Found' }}</span>
        <span class="confidence-score">Confidence: {{ Math.round(parseValidation.confidence * 100) }}%</span>
      </div>
      <div v-if="parseValidation.errors && parseValidation.errors.length > 0" class="validation-errors">
        <div v-for="(error, index) in parseValidation.errors" :key="index" class="error-item">
          {{ error }}
        </div>
      </div>
    </div>

    <!-- Enhanced Token Display -->
    <div class="tokens-container">
      <span 
        v-for="(token, index) in tokens" 
        :key="index" 
        class="token-wrapper"
        :class="getTokenClasses(token, index)"
        @click="handleTokenClick(token, $event)"
        @mouseenter="showTokenTooltip(token, $event)"
        @mouseleave="hideTokenTooltip"
      >
        <!-- Dependency arrow (if showing dependencies) -->
        <div v-if="showDependencies && token.dependency && token.dependency.head_id !== -1" class="dependency-arrow">
          <div class="arrow-line" :style="getDependencyArrowStyle(token, index)"></div>
          <div class="dependency-label">{{ token.dependency.relation }}</div>
        </div>

        <!-- Semantic role indicator -->
        <div v-if="showSemanticRoles && token.dependency && token.dependency.semantic_role" class="semantic-role">
          <span class="role-badge" :class="getSemanticRoleClass(token.dependency.semantic_role)">
            {{ formatSemanticRole(token.dependency.semantic_role) }}
          </span>
        </div>

        <!-- Uncertainty indicator -->
        <div v-if="showUncertainty && token.uncertainty" class="uncertainty-indicator">
          <div 
            class="uncertainty-bar" 
            :class="getUncertaintyClass(token.uncertainty.overall_uncertainty)"
            :style="{ 
              opacity: token.uncertainty.overall_uncertainty,
              height: Math.max(2, token.uncertainty.overall_uncertainty * 6) + 'px'
            }"
          ></div>
          <span 
            v-if="token.uncertainty.overall_uncertainty > uncertaintyThreshold" 
            class="uncertainty-warning"
            :title="`High uncertainty: ${(token.uncertainty.overall_uncertainty * 100).toFixed(1)}%`"
          >
            ⚠️
          </span>
        </div>

        <!-- Compound verb analysis indicator -->
        <div v-if="showCompoundAnalysis && token.compound_analysis" class="compound-indicator">
          <span 
            class="compound-badge" 
            :class="getCompoundAnalysisClass(token.compound_analysis)"
            :title="token.compound_analysis.description || 'Compound construction detected'"
          >
            {{ getCompoundTypeSymbol(token.compound_analysis.type) }}
          </span>
        </div>

        <!-- Enhanced token with furigana (only for kanji with different reading) -->
        <span
          v-if="token.definition && token.furigana && token.furigana !== token.surface && token.isKanji"
          class="kanji-token"
          :class="getGrammarClass(token)"
        >
          <ruby>
            {{ token.surface }}
            <rt>{{ token.furigana }}</rt>
          </ruby>
        </span>
        <!-- Enhanced token without furigana (kanji without reading or non-kanji with definition) -->
        <span
          v-else-if="token.definition"
          class="kanji-token"
          :class="getGrammarClass(token)"
        >
          {{ token.surface }}
        </span>
        <!-- Non-clickable token with grammar highlighting -->
        <span v-else :class="getGrammarClass(token)">
          {{ token.surface }}
        </span>

        <!-- Depth indicator -->
        <div v-if="showDependencies && token.dependency" class="depth-indicator">
          <div class="depth-bar" :style="{ width: (token.dependency.depth * 3 + 2) + 'px' }"></div>
        </div>
      </span>
    </div>

    <!-- Enhanced Dictionary Modal -->
    <DictionaryModal
      v-if="selectedToken"
      :token-data="selectedToken"
      :position="modalPosition"
      :dependency-info="selectedToken.dependency"
      :grammar-info="selectedToken.grammar"
      @close="hideModal"
      @open-word="handleOpenWord"
    />

    <!-- Enhanced Token Tooltip -->
    <div v-if="tooltipToken" class="token-tooltip" :style="tooltipPosition">
      <div class="tooltip-content">
        <div class="tooltip-header">
          <div class="tooltip-text">{{ tooltipToken.surface }}</div>
          <div v-if="tooltipToken.furigana && tooltipToken.furigana !== tooltipToken.surface" class="tooltip-reading">
            {{ tooltipToken.furigana }}
          </div>
        </div>
        
        <div v-if="tooltipToken.grammar" class="tooltip-grammar">
          <span class="grammar-pos">{{ tooltipToken.grammar.pos }}</span>
          <span v-if="tooltipToken.grammar.lemma && tooltipToken.grammar.lemma !== tooltipToken.surface" class="grammar-lemma">
            Base: {{ tooltipToken.grammar.lemma }}
          </span>
          <span v-if="tooltipToken.grammar.role" class="grammar-role">{{ tooltipToken.grammar.role }}</span>
        </div>
        
        <div v-if="tooltipToken.dependency" class="tooltip-dependency">
          <span class="dep-relation">{{ formatDependencyRelation(tooltipToken.dependency.relation) }}</span>
          <span class="dep-depth">Depth: {{ tooltipToken.dependency.depth }}</span>
          <span v-if="tooltipToken.dependency.semantic_role" class="semantic-role">
            Role: {{ formatSemanticRole(tooltipToken.dependency.semantic_role) }}
          </span>
        </div>
        
        <div v-if="tooltipToken.definition" class="tooltip-definition">
          <span class="has-definition">📖 Click for definition</span>
        </div>
        
        <div v-if="tooltipToken.isKanji" class="tooltip-kanji-info">
          <span class="kanji-indicator">漢 Kanji character</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, computed } from 'vue';
import DictionaryModal from './DictionaryModal.vue';

const props = defineProps({
  tokens: {
    type: Array,
    required: true,
  },
  syntacticPatterns: {
    type: Array,
    default: () => []
  },
  parseValidation: {
    type: Object,
    default: null
  },
  dependencyTree: {
    type: Object,
    default: null
  }
});

// State
const selectedToken = ref(null);
const modalPosition = ref({ top: 0, left: 0 });
const tooltipToken = ref(null);
const tooltipPosition = ref({ top: 0, left: 0 });

// Display controls
const showDependencies = ref(false);
const showSemanticRoles = ref(false);
const showGrammarHighlight = ref(true);
const showUncertainty = ref(false);
const showCompoundAnalysis = ref(false);

// Advanced analysis controls
const useAdvancedFeatures = ref(false);
const transformerMode = ref('auto');
const uncertaintyThreshold = ref(0.5);

// Emit for parent component communication
const emit = defineEmits(['update-analysis-options']);

// Methods
const handleTokenClick = (token, event) => {
  if (token.definition) {
    showModal(token, event);
  }
};

const showModal = (token, event) => {
  const targetElement = event.currentTarget;
  selectedToken.value = token;

  nextTick(() => {
    const rect = targetElement.getBoundingClientRect();
    modalPosition.value = {
      top: rect.top - 10,
      left: rect.left + (rect.width / 2)
    };
  });
};

const hideModal = () => {
  selectedToken.value = null;
};

const handleOpenWord = async (wordData) => {
  // Close current modal
  hideModal();
  
  // Fetch full definition for the related word
  try {
    const response = await fetch('/api/debug-lookup', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        word: wordData.word
      })
    });
    
    if (response.ok) {
      const data = await response.json();
      
      // Create a token-like object for the modal
      const tokenData = {
        surface: wordData.word,
        furigana: wordData.reading || wordData.word,
        definition: data.definition,
        grammar: {
          pos: wordData.pos && wordData.pos.length > 0 ? wordData.pos[0] : 'Unknown'
        },
        isKanji: /[\u4e00-\u9faf]/.test(wordData.word)
      };
      
      // Show modal at center of screen
      setTimeout(() => {
        selectedToken.value = tokenData;
        modalPosition.value = {
          top: window.innerHeight / 2 - 160,
          left: window.innerWidth / 2
        };
      }, 100);
    }
  } catch (error) {
    console.error('Error fetching word details:', error);
  }
};

const showTokenTooltip = (token, event) => {
  // Show tooltip for all tokens, not just those with grammar/dependency info
  tooltipToken.value = token;
  const rect = event.currentTarget.getBoundingClientRect();
  tooltipPosition.value = {
    top: rect.bottom + 5 + 'px',
    left: rect.left - 10 + 'px'
  };
};

const hideTokenTooltip = () => {
  tooltipToken.value = null;
};

// Style helpers
const getTokenClasses = (token, index) => {
  const classes = ['token-item'];
  
  if (token.definition) {
    classes.push('clickable-token');
  }
  
  if (showDependencies && token.dependency) {
    classes.push('has-dependency');
  }
  
  return classes;
};

const getGrammarClass = (token) => {
  if (!showGrammarHighlight || !token.grammar) return '';
  
  const posClasses = {
    'Noun': 'grammar-noun',
    'Verb': 'grammar-verb',
    'Adjective': 'grammar-adjective',
    'Adverb': 'grammar-adverb',
    'Particle': 'grammar-particle',
    'Auxiliary': 'grammar-auxiliary',
    'Pronoun': 'grammar-pronoun'
  };
  
  return posClasses[token.grammar.pos] || 'grammar-other';
};

const getSemanticRoleClass = (role) => {
  const roleClasses = {
    'agent': 'role-agent',
    'patient': 'role-patient',
    'theme': 'role-theme',
    'location': 'role-location',
    'time': 'role-time',
    'manner': 'role-manner',
    'instrument': 'role-instrument'
  };
  
  return roleClasses[role] || 'role-other';
};

const getPatternClass = (patternType) => {
  const patternClasses = {
    'sov_basic': 'pattern-sov',
    'relative_clause': 'pattern-relative',
    'honorific_pattern': 'pattern-honorific',
    'te_form_chain': 'pattern-te-form'
  };
  
  return patternClasses[patternType] || 'pattern-default';
};

const formatPatternType = (type) => {
  const formatMap = {
    'sov_basic': 'SOV Pattern',
    'relative_clause': 'Relative Clause',
    'honorific_pattern': 'Honorific',
    'te_form_chain': 'Te-form Chain'
  };
  
  return formatMap[type] || type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
};

const formatSemanticRole = (role) => {
  return role.charAt(0).toUpperCase() + role.slice(1);
};

// New methods for advanced features
const onAdvancedFeaturesToggle = () => {
  emit('update-analysis-options', {
    useAdvancedFeatures: useAdvancedFeatures.value,
    uncertaintyEstimation: showUncertainty.value,
    compoundVerbAnalysis: showCompoundAnalysis.value,
    transformerMode: transformerMode.value
  });
};

const getUncertaintyClass = (uncertainty) => {
  if (uncertainty < 0.3) return 'uncertainty-low';
  if (uncertainty < 0.6) return 'uncertainty-medium';
  return 'uncertainty-high';
};

const getCompoundAnalysisClass = (compoundAnalysis) => {
  const typeClasses = {
    'aspectual': 'compound-aspectual',
    'causative': 'compound-causative',
    'passive': 'compound-passive',
    'compound_verb': 'compound-verb',
    'lexicalized': 'compound-lexicalized'
  };
  
  return typeClasses[compoundAnalysis.type] || 'compound-general';
};

const getCompoundTypeSymbol = (type) => {
  const symbols = {
    'aspectual': '⏳',
    'causative': '🔄',
    'passive': '🔽',
    'compound_verb': '🔗',
    'lexicalized': '📚',
    'compositional': '🧩'
  };
  
  return symbols[type] || '🔍';
};

const formatDependencyRelation = (relation) => {
  const relationMap = {
    'nsubj': 'Subject',
    'obj': 'Object',
    'omod': 'Object Modifier',
    'nmod': 'Nominal Modifier',
    'amod': 'Adjectival Modifier',
    'advmod': 'Adverbial Modifier',
    'aux': 'Auxiliary',
    'cop': 'Copula',
    'case': 'Case Marker',
    'mark': 'Marker',
    'root': 'Root',
    'compound': 'Compound',
    'acl': 'Adjectival Clause',
    'advcl': 'Adverbial Clause'
  };
  return relationMap[relation] || relation;
};

const getDependencyArrowStyle = (token, index) => {
  // Simplified arrow styling - would need more complex logic for proper positioning
  return {
    transform: `rotate(${token.dependency.depth * 15}deg)`,
    opacity: 0.7
  };
};
</script>

<style scoped>
/* =====================================================
   ANALYSIS CONTAINER
   ===================================================== */

.analyzed-text-container {
  background: var(--surface-low);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  margin: 1rem 0;
}

/* =====================================================
   ANALYSIS CONTROLS
   ===================================================== */

.analysis-controls {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: var(--surface-medium);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-grey);
}

.control-group {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.control-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--text-primary);
  cursor: pointer;
  user-select: none;
}

.control-checkbox {
  width: 16px;
  height: 16px;
  accent-color: var(--accent-blue);
}

/* =====================================================
   SYNTACTIC PATTERNS
   ===================================================== */

.patterns-section {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: var(--surface-medium);
  border-radius: var(--radius-md);
  border-left: 4px solid var(--accent-blue);
}

.patterns-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 0.75rem 0;
}

.patterns-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.pattern-badge {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 0.5rem 0.75rem;
  border-radius: var(--radius-md);
  font-size: 0.75rem;
  border: 1px solid;
  transition: all 0.2s ease;
}

.pattern-sov {
  background: rgba(34, 197, 94, 0.1);
  border-color: rgb(34, 197, 94);
  color: rgb(34, 197, 94);
}

.pattern-relative {
  background: rgba(168, 85, 247, 0.1);
  border-color: rgb(168, 85, 247);
  color: rgb(168, 85, 247);
}

.pattern-honorific {
  background: rgba(251, 191, 36, 0.1);
  border-color: rgb(251, 191, 36);
  color: rgb(251, 191, 36);
}

.pattern-te-form {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgb(239, 68, 68);
  color: rgb(239, 68, 68);
}

.pattern-default {
  background: var(--surface-overlay);
  border-color: var(--border-light);
  color: var(--text-muted);
}

.pattern-type {
  font-weight: 600;
}

.pattern-confidence {
  font-size: 0.625rem;
  opacity: 0.8;
}

.pattern-description {
  font-size: 0.625rem;
  opacity: 0.7;
  line-height: 1.3;
}

/* =====================================================
   PARSE VALIDATION
   ===================================================== */

.validation-section {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: var(--surface-medium);
  border-radius: var(--radius-md);
}

.validation-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.validation-status.valid {
  color: rgb(34, 197, 94);
}

.validation-status.invalid {
  color: rgb(239, 68, 68);
}

.confidence-score {
  margin-left: auto;
  font-size: 0.75rem;
  opacity: 0.8;
}

.validation-errors {
  margin-top: 0.5rem;
}

.error-item {
  padding: 0.25rem 0.5rem;
  background: rgba(239, 68, 68, 0.1);
  border-left: 3px solid rgb(239, 68, 68);
  font-size: 0.75rem;
  color: rgb(239, 68, 68);
  margin-bottom: 0.25rem;
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
}

/* =====================================================
   ENHANCED TOKEN DISPLAY
   ===================================================== */

.tokens-container {
  line-height: 2.5;
  font-size: 1.1rem;
  position: relative;
}

.token-wrapper {
  position: relative;
  display: inline-block;
  margin: 0.25rem 0.5rem;
  transition: all 0.2s ease;
}

.token-item {
  position: relative;
}

.clickable-token {
  cursor: pointer;
}

.clickable-token:hover {
  transform: translateY(-1px);
}

/* =====================================================
   DEPENDENCY VISUALIZATION
   ===================================================== */

.dependency-arrow {
  position: absolute;
  top: -20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
}

.arrow-line {
  width: 2px;
  height: 15px;
  background: var(--accent-blue);
  position: relative;
}

.arrow-line::after {
  content: '';
  position: absolute;
  top: 0;
  left: -3px;
  width: 0;
  height: 0;
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  border-bottom: 6px solid var(--accent-blue);
}

.dependency-label {
  position: absolute;
  top: -20px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 0.625rem;
  color: var(--accent-blue);
  background: var(--surface-medium);
  padding: 0.125rem 0.25rem;
  border-radius: var(--radius-sm);
  white-space: nowrap;
  border: 1px solid var(--accent-blue);
}

.depth-indicator {
  position: absolute;
  bottom: -8px;
  left: 0;
}

.depth-bar {
  height: 2px;
  background: linear-gradient(to right, var(--accent-blue), transparent);
  border-radius: 1px;
}

/* =====================================================
   SEMANTIC ROLES
   ===================================================== */

.semantic-role {
  position: absolute;
  top: -30px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 5;
}

.role-badge {
  font-size: 0.625rem;
  padding: 0.125rem 0.375rem;
  border-radius: var(--radius-sm);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.role-agent {
  background: rgba(59, 130, 246, 0.2);
  color: rgb(59, 130, 246);
}

.role-patient {
  background: rgba(239, 68, 68, 0.2);
  color: rgb(239, 68, 68);
}

.role-theme {
  background: rgba(168, 85, 247, 0.2);
  color: rgb(168, 85, 247);
}

.role-location {
  background: rgba(34, 197, 94, 0.2);
  color: rgb(34, 197, 94);
}

.role-time {
  background: rgba(251, 191, 36, 0.2);
  color: rgb(251, 191, 36);
}

.role-manner {
  background: rgba(236, 72, 153, 0.2);
  color: rgb(236, 72, 153);
}

.role-instrument {
  background: rgba(20, 184, 166, 0.2);
  color: rgb(20, 184, 166);
}

.role-other {
  background: var(--surface-overlay);
  color: var(--text-muted);
}

/* =====================================================
   GRAMMAR HIGHLIGHTING
   ===================================================== */

.grammar-noun {
  color: rgb(59, 130, 246);
  border-bottom: 2px solid rgba(59, 130, 246, 0.3);
}

.grammar-verb {
  color: rgb(239, 68, 68);
  border-bottom: 2px solid rgba(239, 68, 68, 0.3);
  font-weight: 600;
}

.grammar-adjective {
  color: rgb(168, 85, 247);
  border-bottom: 2px solid rgba(168, 85, 247, 0.3);
}

.grammar-adverb {
  color: rgb(34, 197, 94);
  border-bottom: 2px solid rgba(34, 197, 94, 0.3);
}

.grammar-particle {
  color: rgb(251, 191, 36);
  border-bottom: 1px dotted rgba(251, 191, 36, 0.5);
  font-size: 0.9em;
}

.grammar-auxiliary {
  color: rgb(236, 72, 153);
  border-bottom: 1px dotted rgba(236, 72, 153, 0.5);
}

.grammar-pronoun {
  color: rgb(20, 184, 166);
  border-bottom: 2px solid rgba(20, 184, 166, 0.3);
}

.grammar-other {
  color: var(--text-muted);
  border-bottom: 1px dotted var(--border-grey);
}

/* =====================================================
   ENHANCED KANJI TOKENS
   ===================================================== */

.kanji-token {
  display: inline-block;
  line-height: 1.5;
  transition: all 0.2s ease;
  padding: 0.125rem 0.25rem;
  border-radius: var(--radius-sm);
  position: relative;
}

.kanji-token:hover {
  background: var(--surface-overlay);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

ruby {
  display: inline-flex;
  flex-direction: column-reverse;
  line-height: 1.2;
}

rt {
  font-size: 0.75rem;
  color: var(--text-muted);
  user-select: none;
  font-weight: normal;
  text-align: center;
  margin-bottom: 0.125rem;
}

/* =====================================================
   TOKEN TOOLTIP
   ===================================================== */

.token-tooltip {
  position: fixed;
  z-index: 1000;
  background: var(--surface-high);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  padding: 0.75rem;
  box-shadow: var(--shadow-lg);
  max-width: 250px;
  pointer-events: none;
}

.tooltip-content {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.tooltip-text {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 1rem;
}

.tooltip-grammar {
  display: flex;
  gap: 0.5rem;
  font-size: 0.75rem;
}

.grammar-pos {
  background: var(--accent-blue);
  color: white;
  padding: 0.125rem 0.375rem;
  border-radius: var(--radius-sm);
  font-weight: 600;
}

.grammar-role {
  background: var(--surface-overlay);
  color: var(--text-muted);
  padding: 0.125rem 0.375rem;
  border-radius: var(--radius-sm);
}

.tooltip-dependency {
  display: flex;
  gap: 0.5rem;
  font-size: 0.75rem;
  flex-wrap: wrap;
}

/* Enhanced tooltip styles */
.tooltip-header {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  border-bottom: 1px solid var(--border-grey);
  padding-bottom: 0.5rem;
  margin-bottom: 0.5rem;
}

.tooltip-reading {
  font-size: 0.875rem;
  color: var(--accent-blue);
  font-style: italic;
}

.grammar-lemma {
  background: var(--surface-overlay);
  color: var(--text-secondary);
  padding: 0.125rem 0.375rem;
  border-radius: var(--radius-sm);
  font-size: 0.7rem;
}

.dep-relation {
  background: var(--accent-purple);
  color: white;
  padding: 0.125rem 0.375rem;
  border-radius: var(--radius-sm);
  font-weight: 600;
}

.dep-depth {
  background: var(--surface-overlay);
  color: var(--text-muted);
  padding: 0.125rem 0.375rem;
  border-radius: var(--radius-sm);
}

.semantic-role {
  background: var(--accent-green);
  color: white;
  padding: 0.125rem 0.375rem;
  border-radius: var(--radius-sm);
  font-weight: 600;
}

.tooltip-definition {
  padding: 0.25rem 0;
  border-top: 1px solid var(--border-grey);
}

.has-definition {
  color: var(--accent-blue);
  font-size: 0.75rem;
  font-weight: 600;
}

.tooltip-kanji-info {
  padding: 0.25rem 0;
  border-top: 1px solid var(--border-grey);
}

.kanji-indicator {
  color: var(--accent-orange);
  font-size: 0.75rem;
  font-weight: 600;
}

.dep-depth {
  background: var(--surface-overlay);
  color: var(--text-muted);
  padding: 0.125rem 0.375rem;
  border-radius: var(--radius-sm);
}

/* =====================================================
   RESPONSIVE DESIGN
   ===================================================== */

@media (max-width: 768px) {
  .control-group {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .patterns-list {
    flex-direction: column;
  }
  
  .tokens-container {
    font-size: 1rem;
    line-height: 2.2;
  }
  
  .token-wrapper {
    margin: 0.125rem 0.25rem;
  }
  
  .dependency-arrow,
  .semantic-role {
    display: none;
  }
}

/* =====================================================
   ADVANCED FEATURES - UNCERTAINTY & COMPOUND ANALYSIS
   ===================================================== */

/* Advanced Controls */
.advanced-controls {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-grey);
}

.advanced-options {
  margin-top: 0.5rem;
  margin-left: 1.5rem;
}

.transformer-select {
  padding: 0.25rem 0.5rem;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-grey);
  background: var(--surface-low);
  color: var(--text-primary);
  font-size: 0.875rem;
}

.uncertainty-controls {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-grey);
}

.uncertainty-slider {
  width: 200px;
  margin-left: 1rem;
  accent-color: var(--accent-blue);
}

/* Uncertainty Visualization */
.uncertainty-indicator {
  position: absolute;
  top: -8px;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

.uncertainty-bar {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  border-radius: 1px;
  transition: all 0.2s ease;
}

.uncertainty-low {
  background: rgba(34, 197, 94, 0.6);
}

.uncertainty-medium {
  background: rgba(251, 191, 36, 0.7);
}

.uncertainty-high {
  background: rgba(239, 68, 68, 0.8);
}

.uncertainty-warning {
  position: absolute;
  top: -12px;
  right: -8px;
  font-size: 0.7rem;
  background: rgba(239, 68, 68, 0.9);
  color: white;
  border-radius: 50%;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.7; transform: scale(1.1); }
}

/* Compound Analysis Visualization */
.compound-indicator {
  position: absolute;
  top: -6px;
  right: -6px;
  z-index: 10;
}

.compound-badge {
  display: inline-block;
  font-size: 0.7rem;
  padding: 2px 4px;
  border-radius: var(--radius-sm);
  border: 1px solid;
  font-weight: 600;
  transition: all 0.2s ease;
}

.compound-aspectual {
  background: rgba(168, 85, 247, 0.1);
  border-color: rgb(168, 85, 247);
  color: rgb(168, 85, 247);
}

.compound-causative {
  background: rgba(34, 197, 94, 0.1);
  border-color: rgb(34, 197, 94);
  color: rgb(34, 197, 94);
}

.compound-passive {
  background: rgba(59, 130, 246, 0.1);
  border-color: rgb(59, 130, 246);
  color: rgb(59, 130, 246);
}

.compound-verb {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgb(239, 68, 68);
  color: rgb(239, 68, 68);
}

.compound-lexicalized {
  background: rgba(251, 191, 36, 0.1);
  border-color: rgb(251, 191, 36);
  color: rgb(251, 191, 36);
}

.compound-general {
  background: rgba(107, 114, 128, 0.1);
  border-color: rgb(107, 114, 128);
  color: rgb(107, 114, 128);
}

/* Enhanced Token Wrapper for Advanced Features */
.token-wrapper {
  position: relative;
}

.token-wrapper.has-uncertainty {
  padding-top: 8px;
}

.token-wrapper.has-compound {
  padding-right: 8px;
}

/* Responsive adjustments for advanced features */
@media (max-width: 768px) {
  .advanced-controls {
    margin-top: 0.5rem;
  }
  
  .uncertainty-controls {
    margin-top: 0.5rem;
  }
  
  .uncertainty-slider {
    width: 150px;
  }
  
  .compound-badge {
    font-size: 0.6rem;
    padding: 1px 3px;
  }
  
  .uncertainty-warning {
    width: 14px;
    height: 14px;
    font-size: 0.6rem;
  }
}
</style>