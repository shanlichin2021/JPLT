<template>
  <Teleport to="body">
    <div
      ref="modalRef"
      class="fixed z-50 modal-container transition-all duration-200 ease-out pointer-events-auto"
      :style="modalStyle"
      @wheel.stop
    >
      <!-- Header with close button and word -->
      <div class="modal-header">
        <button
          @click="$emit('close')"
          class="modal-close-btn"
          aria-label="Close"
        >
          ×
        </button>

        <!-- Main word display -->
        <div class="pr-6">
          <div class="flex items-center gap-2">
            <ruby class="text-xl font-bold">
              {{ tokenData.surface }}
              <rt class="text-xs text-blue-300">{{ tokenData.furigana }}</rt>
            </ruby>
            
            <!-- Quick info badges -->
            <div class="flex gap-1">
              <span v-if="tokenData.grammar?.pos" 
                    class="px-2 py-0.5 bg-blue-500/20 text-blue-300 text-xs rounded-full border border-blue-500/30">
                {{ tokenData.grammar.pos }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Compact content area -->
      <div class="max-h-80 overflow-y-auto thin-scrollbar">
        
        <!-- Primary definition (most important) -->
        <div v-if="primaryDefinition" class="p-3 border-b border-gray-700/30">
          <div class="flex items-start gap-2">
            <div class="flex-shrink-0 w-5 h-5 bg-green-500/20 rounded-full flex items-center justify-center mt-0.5">
              <span class="text-green-400 text-xs font-bold">1</span>
            </div>
            <div class="flex-1 min-w-0">
              <div class="text-green-400 text-xs font-medium mb-1">
                {{ primaryDefinition.parts_of_speech.join(', ') }}
              </div>
              <div class="text-white text-sm font-medium">
                {{ primaryDefinition.english_definitions[0] }}
              </div>
              <!-- Additional meanings in compact format -->
              <div v-if="primaryDefinition.english_definitions.length > 1" 
                   class="mt-1 text-xs text-gray-300">
                {{ primaryDefinition.english_definitions.slice(1, 2).join('; ') }}
                <span v-if="primaryDefinition.english_definitions.length > 2" class="text-gray-500">
                  +{{ primaryDefinition.english_definitions.length - 2 }} more
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Enhanced Grammar details -->
        <div v-if="currentGrammar" class="p-3 bg-gray-800/30">
          <div class="flex items-start gap-2">
            <div class="flex-shrink-0 w-5 h-5 bg-purple-500/20 rounded-full flex items-center justify-center mt-0.5">
              <i class="fas fa-cog text-purple-400 text-xs"></i>
            </div>
            <div class="flex-1 min-w-0">
              <div class="text-purple-400 text-xs font-medium mb-2">Grammar Analysis</div>
              <div class="space-y-1 text-xs">
                <div class="flex justify-between">
                  <span class="text-gray-400">Part of Speech:</span>
                  <span class="text-blue-300 font-semibold">{{ currentGrammar.pos }}</span>
                </div>
                <div v-if="currentGrammar.lemma" class="flex justify-between">
                  <span class="text-gray-400">Lemma:</span>
                  <span class="text-green-300">{{ currentGrammar.lemma }}</span>
                </div>
                <div v-if="currentGrammar.inflectionType" class="flex justify-between">
                  <span class="text-gray-400">Inflection Type:</span>
                  <span class="text-blue-300">{{ currentGrammar.inflectionType }}</span>
                </div>
                <div v-if="currentGrammar.inflectionForm" class="flex justify-between">
                  <span class="text-gray-400">Inflection Form:</span>
                  <span class="text-green-300">{{ currentGrammar.inflectionForm }}</span>
                </div>
                <div v-if="currentGrammar.role" class="flex justify-between">
                  <span class="text-gray-400">Syntactic Role:</span>
                  <span class="text-orange-300">{{ currentGrammar.role }}</span>
                </div>
                <div v-if="currentGrammar.features && currentGrammar.features.length > 0" class="mt-2">
                  <span class="text-gray-400 text-xs">Features:</span>
                  <div class="flex flex-wrap gap-1 mt-1">
                    <span v-for="feature in currentGrammar.features.slice(0, 3)" :key="feature" 
                          class="px-1.5 py-0.5 bg-gray-700/50 text-gray-300 text-xs rounded">
                      {{ feature }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Dependency Analysis -->
        <div v-if="currentDependency" class="p-3 bg-gray-800/40 border-l-2 border-blue-500">
          <div class="flex items-start gap-2">
            <div class="flex-shrink-0 w-5 h-5 bg-blue-500/20 rounded-full flex items-center justify-center mt-0.5">
              <i class="fas fa-project-diagram text-blue-400 text-xs"></i>
            </div>
            <div class="flex-1 min-w-0">
              <div class="text-blue-400 text-xs font-medium mb-2">Dependency Relations</div>
              <div class="space-y-1 text-xs">
                <div class="flex justify-between">
                  <span class="text-gray-400">Relation:</span>
                  <span class="text-yellow-300 font-semibold">{{ formatDependencyRelation(currentDependency.relation) }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-400">Depth:</span>
                  <span class="text-cyan-300">{{ currentDependency.depth }}</span>
                </div>
                <div v-if="currentDependency.head_id !== -1" class="flex justify-between">
                  <span class="text-gray-400">Head ID:</span>
                  <span class="text-pink-300">{{ currentDependency.head_id }}</span>
                </div>
                <div v-if="currentDependency.children && currentDependency.children.length > 0" class="flex justify-between">
                  <span class="text-gray-400">Children:</span>
                  <span class="text-green-300">{{ currentDependency.children.length }} nodes</span>
                </div>
                <div v-if="currentDependency.semantic_role" class="flex justify-between">
                  <span class="text-gray-400">Semantic Role:</span>
                  <span class="text-purple-300 font-semibold">{{ formatSemanticRole(currentDependency.semantic_role) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Context Information -->
        <div v-if="tokenData.context" class="p-3 bg-gray-800/20">
          <div class="flex items-start gap-2">
            <div class="flex-shrink-0 w-5 h-5 bg-green-500/20 rounded-full flex items-center justify-center mt-0.5">
              <i class="fas fa-info-circle text-green-400 text-xs"></i>
            </div>
            <div class="flex-1 min-w-0">
              <div class="text-green-400 text-xs font-medium mb-2">Context</div>
              <div class="space-y-1 text-xs">
                <div v-if="tokenData.context.formality" class="flex justify-between">
                  <span class="text-gray-400">Formality:</span>
                  <span class="text-blue-300">{{ tokenData.context.formality }}</span>
                </div>
                <div v-if="tokenData.context.nuance" class="mt-1">
                  <span class="text-gray-400">Nuance:</span>
                  <p class="text-gray-300 text-xs mt-0.5 leading-relaxed">{{ tokenData.context.nuance }}</p>
                </div>
                <div v-if="tokenData.context.usage" class="mt-1">
                  <span class="text-gray-400">Usage:</span>
                  <p class="text-gray-300 text-xs mt-0.5 leading-relaxed">{{ tokenData.context.usage }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Semantic Suggestions -->  
        <div v-if="relatedWords.length > 0" class="p-3 bg-gray-800/30">
          <div class="flex items-start gap-2">
            <div class="flex-shrink-0 w-5 h-5 bg-yellow-500/20 rounded-full flex items-center justify-center mt-0.5">
              <i class="fas fa-brain text-yellow-400 text-xs"></i>
            </div>
            <div class="flex-1 min-w-0">
              <div class="text-yellow-400 text-xs font-medium mb-2">Related Words</div>
              <div class="flex flex-wrap gap-1">
                <button 
                  v-for="word in relatedWords.slice(0, 6)" 
                  :key="word.word"
                  @click="$emit('openWord', word)"
                  class="px-2 py-1 bg-yellow-600/20 hover:bg-yellow-600/30 text-yellow-300 text-xs rounded transition-colors border border-yellow-600/30"
                  :title="word.definitions.join('; ')"
                >
                  {{ word.word }}
                  <span class="text-yellow-500/70 ml-1">({{ Math.round(word.similarity * 100) }}%)</span>
                </button>
              </div>
              <div v-if="relatedWords.length > 6" class="text-xs text-gray-400 mt-1">
                +{{ relatedWords.length - 6 }} more related words
              </div>
            </div>
          </div>
        </div>

        <!-- Loading state for semantic suggestions -->
        <div v-if="loadingRelated" class="p-3 bg-gray-800/20">
          <div class="flex items-center gap-2">
            <div class="w-4 h-4 border-2 border-blue-400 border-t-transparent rounded-full animate-spin"></div>
            <span class="text-xs text-gray-400">Finding related words...</span>
          </div>
        </div>
      </div>

      <!-- No definition available -->
      <div v-if="!tokenData.definition && !tokenData.grammar" 
           class="p-4 text-center text-gray-500">
        <i class="fas fa-search text-xl mb-2 opacity-50"></i>
        <p class="text-sm">No dictionary information available</p>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue';

const props = defineProps({
  tokenData: { type: Object, required: true },
  position: { type: Object, required: true },
  dependencyInfo: { type: Object, default: null },
  grammarInfo: { type: Object, default: null }
});

const emit = defineEmits(['close', 'addToStudyList', 'openWord']);

const modalRef = ref(null);
const showGrammar = ref(false);
const showMore = ref(false);
const relatedWords = ref([]);
const loadingRelated = ref(false);

// Computed properties for better organization
const primaryDefinition = computed(() => {
  return props.tokenData.definition?.senses?.[0] || null;
});

const additionalDefinitions = computed(() => {
  return props.tokenData.definition?.senses?.slice(1) || [];
});

// Enhanced grammar and dependency info
const currentGrammar = computed(() => {
  return props.grammarInfo || props.tokenData.grammar || null;
});

const currentDependency = computed(() => {
  return props.dependencyInfo || props.tokenData.dependency || null;
});

// Helper functions
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

const formatSemanticRole = (role) => {
  const roleMap = {
    'agent': 'Agent (Performer)',
    'patient': 'Patient (Affected)',
    'theme': 'Theme',
    'location': 'Location',
    'time': 'Time',
    'manner': 'Manner',
    'instrument': 'Instrument'
  };
  return roleMap[role] || role.charAt(0).toUpperCase() + role.slice(1);
};

const modalStyle = computed(() => {
  const { top, left } = props.position;
  
  // Smart positioning to avoid viewport edges
  const modalWidth = 280;
  const modalMaxHeight = 320;
  const viewportWidth = window.innerWidth;
  const viewportHeight = window.innerHeight;
  
  let adjustedLeft = left - modalWidth / 2;
  let adjustedTop = top - 10;
  
  // Adjust horizontal position
  if (adjustedLeft < 10) adjustedLeft = 10;
  if (adjustedLeft + modalWidth > viewportWidth - 10) {
    adjustedLeft = viewportWidth - modalWidth - 10;
  }
  
  // Adjust vertical position
  if (adjustedTop + modalMaxHeight > viewportHeight - 10) {
    adjustedTop = top - modalMaxHeight - 10;
  }
  if (adjustedTop < 10) adjustedTop = 10;
  
  return {
    top: `${adjustedTop}px`,
    left: `${adjustedLeft}px`,
    width: `${modalWidth}px`,
    maxHeight: `${modalMaxHeight}px`,
  };
});

const getFormalityBadgeClass = (formality) => {
  const classes = {
    'formal': 'bg-blue-500/20 text-blue-300 border-blue-500/30',
    'informal': 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30',
    'polite': 'bg-green-500/20 text-green-300 border-green-500/30',
    'casual': 'bg-orange-500/20 text-orange-300 border-orange-500/30',
  };
  return classes[formality?.toLowerCase()] || 'bg-gray-500/20 text-gray-300 border-gray-500/30';
};

const copyToClipboard = async () => {
  const text = `${props.tokenData.surface} (${props.tokenData.furigana})`;
  try {
    await navigator.clipboard.writeText(text);
    // Could add a toast notification here
  } catch (err) {
    console.error('Failed to copy:', err);
  }
};

const addToStudyList = () => {
  emit('addToStudyList', props.tokenData);
  // Could add visual feedback here
};

const loadRelatedWords = async () => {
  if (!props.tokenData.surface || loadingRelated.value) return;
  
  try {
    loadingRelated.value = true;
    const response = await fetch('/api/related-words', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        word: props.tokenData.surface,
        top_k: 8,
        exclude_exact: true
      })
    });
    
    if (response.ok) {
      const data = await response.json();
      relatedWords.value = data.relatedWords || [];
    } else {
      console.warn('Failed to load related words:', response.statusText);
      relatedWords.value = [];
    }
  } catch (error) {
    console.warn('Error loading related words:', error);
    relatedWords.value = [];
  } finally {
    loadingRelated.value = false;
  }
};

const handleClickOutside = (event) => {
  if (modalRef.value && !modalRef.value.contains(event.target)) {
    emit('close');
  }
};

const handleEscape = (event) => {
  if (event.key === 'Escape') {
    emit('close');
  }
};

onMounted(async () => {
  document.addEventListener('mousedown', handleClickOutside);
  document.addEventListener('keydown', handleEscape);
  
  // Load semantic suggestions
  await loadRelatedWords();
});

onUnmounted(() => {
  document.removeEventListener('mousedown', handleClickOutside);
  document.removeEventListener('keydown', handleEscape);
});
</script>

<style scoped>
/* =====================================================
   MODERN MODAL CONTAINER
   ===================================================== */

.modal-container {
  background: var(--surface-medium);
  border: 1px solid var(--border-grey);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  color: var(--text-primary);
  backdrop-filter: blur(20px);
  overflow: hidden;
}

.modal-header {
  position: relative;
  background: linear-gradient(135deg, var(--accent-indigo) 0%, var(--accent-indigo-dark) 100%);
  padding: 1rem;
  border-bottom: 1px solid var(--border-grey);
}

.modal-close-btn {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  width: 2rem;
  height: 2rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.125rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  z-index: 10;
}

.modal-close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
  transform: scale(1.05);
}

/* Ruby text styling */
ruby {
  display: inline-flex;
  flex-direction: column-reverse;
  align-items: center;
  line-height: 1;
}

rt {
  font-size: 0.75rem;
  font-weight: normal;
  line-height: 1.2;
  margin-bottom: 2px;
  color: rgba(255, 255, 255, 0.8);
}

/* Content styling */
.modal-content {
  max-height: 20rem;
  overflow-y: auto;
}

/* POS badges */
.pos-badge {
  background: var(--accent-indigo);
  color: white;
  font-size: 0.75rem;
  padding: 0.25rem 0.75rem;
  border-radius: var(--radius-sm);
  font-weight: 500;
}

/* Definition sections */
.definition-section {
  padding: 1rem;
  border-bottom: 1px solid var(--border-grey);
}

.definition-section:last-child {
  border-bottom: none;
}

.definition-number {
  width: 1.5rem;
  height: 1.5rem;
  background: var(--success-green);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.75rem;
  font-weight: 600;
  flex-shrink: 0;
}

.definition-text {
  color: var(--text-primary);
  font-size: 0.875rem;
  font-weight: 500;
  line-height: 1.4;
}

.definition-additional {
  color: var(--text-secondary);
  font-size: 0.75rem;
  margin-top: 0.25rem;
}

/* Grammar section */
.grammar-section {
  background: var(--surface-overlay);
  padding: 1rem;
}

.grammar-icon {
  width: 1.5rem;
  height: 1.5rem;
  background: var(--accent-indigo);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.75rem;
  flex-shrink: 0;
}

.grammar-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.25rem 0;
  font-size: 0.75rem;
}

.grammar-label {
  color: var(--text-muted);
  font-weight: 500;
}

.grammar-value {
  color: var(--accent-indigo);
  font-weight: 600;
}

/* Action buttons */
.action-section {
  background: var(--surface-overlay);
  padding: 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.action-hint {
  color: var(--text-disabled);
  font-size: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  background: var(--surface-medium);
  border: 1px solid var(--border-grey);
  color: var(--text-secondary);
  font-size: 0.75rem;
  padding: 0.5rem 0.75rem;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.action-btn:hover {
  background: var(--surface-high);
  border-color: var(--border-light);
  color: var(--text-primary);
  transform: translateY(-1px);
}

.action-btn:active {
  transform: translateY(0);
}

.action-btn.copy {
  border-color: var(--accent-indigo);
  color: var(--accent-indigo);
}

.action-btn.copy:hover {
  background: rgba(91, 127, 255, 0.1);
}

.action-btn.study {
  border-color: var(--success-green);
  color: var(--success-green);
}

.action-btn.study:hover {
  background: rgba(0, 210, 106, 0.1);
}

/* No definition state */
.no-definition {
  padding: 2rem;
  text-align: center;
  color: var(--text-disabled);
}

.no-definition-icon {
  font-size: 1.5rem;
  margin-bottom: 0.75rem;
  opacity: 0.5;
}

.no-definition-text {
  font-size: 0.875rem;
}

/* Custom scrollbar for modal */
.thin-scrollbar::-webkit-scrollbar {
  width: 4px;
}

.thin-scrollbar::-webkit-scrollbar-track {
  background: var(--surface-low);
  border-radius: 2px;
}

.thin-scrollbar::-webkit-scrollbar-thumb {
  background: var(--accent-indigo);
  border-radius: 2px;
}

.thin-scrollbar::-webkit-scrollbar-thumb:hover {
  background: var(--accent-indigo-hover);
}

/* Smooth entrance animation */
@keyframes modalFadeIn {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(-10px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.modal-container {
  animation: modalFadeIn 0.2s ease-out;
}
</style>