<template>
  <aside class="vocabulary-panel">
    <!-- Header with controls -->
    <div class="mb-4">
      <h2 class="text-xl font-bold text-white text-center mb-3">Vocabulary Analysis</h2>
      
      <!-- Filter and sort controls -->
      <div class="flex flex-col gap-2 mb-3">
        <select 
          v-model="selectedCategory" 
          class="bg-gray-800 text-white text-sm rounded px-2 py-1 border border-gray-600"
        >
          <option value="all">All Words ({{ totalWords }})</option>
          <option value="verbs">Verbs ({{ categoryStats.verbs }})</option>
          <option value="nouns">Nouns ({{ categoryStats.nouns }})</option>
          <option value="adjectives">Adjectives ({{ categoryStats.adjectives }})</option>
          <option value="particles">Particles ({{ categoryStats.particles }})</option>
          <option value="expressions">Expressions ({{ categoryStats.expressions }})</option>
        </select>
        
        <select 
          v-model="sortBy" 
          class="bg-gray-800 text-white text-sm rounded px-2 py-1 border border-gray-600"
        >
          <option value="appearance">Order of Appearance</option>
          <option value="frequency">Frequency in Text</option>
          <option value="difficulty">Difficulty Level</option>
          <option value="alphabetical">Alphabetical</option>
        </select>
      </div>

      <!-- Quick stats -->
      <div class="bg-gray-800 rounded-lg p-3 text-xs">
        <div class="grid grid-cols-2 gap-2 text-center">
          <div>
            <div class="text-blue-400 font-semibold">{{ uniqueWordsCount }}</div>
            <div class="text-gray-400">Unique Words</div>
          </div>
          <div>
            <div class="text-green-400 font-semibold">{{ knownWordsCount }}</div>
            <div class="text-gray-400">With Definitions</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Vocabulary list -->
    <div class="flex-1 overflow-y-auto thin-scrollbar">
      <div v-if="filteredKanjiList.length === 0" class="text-gray-500 text-center py-8">
        <div class="text-lg mb-2">📚</div>
        <div>No {{ selectedCategory === 'all' ? '' : selectedCategory }} found</div>
        <div class="text-xs mt-1">Try analyzing some Japanese text</div>
      </div>
      
      <!-- Vocabulary cards -->
      <div v-for="token in filteredKanjiList" :key="`${token.surface}-${token.index}`" 
           class="mb-3 p-3 bg-gray-800 rounded-lg hover:bg-gray-750 transition-all duration-200 cursor-pointer border border-gray-700 hover:border-gray-600"
           @click="selectWord(token)">
        
        <!-- Word header -->
        <div class="flex items-center justify-between mb-2">
          <div class="flex items-baseline">
            <ruby class="mr-2">
              <h3 class="text-lg font-semibold text-white">{{ token.surface }}</h3>
              <rt class="text-xs text-gray-400">{{ token.furigana }}</rt>
            </ruby>
            <div class="flex items-center gap-1">
              <!-- Frequency indicator -->
              <span v-if="token.frequency > 1" 
                    class="bg-blue-600 text-white text-xs px-1.5 py-0.5 rounded-full">
                {{ token.frequency }}×
              </span>
              <!-- Difficulty indicator -->
              <span :class="getDifficultyColor(token.difficulty)" 
                    class="text-xs px-1.5 py-0.5 rounded-full">
                {{ getDifficultyLabel(token.difficulty) }}
              </span>
            </div>
          </div>
          <button @click.stop="toggleWordDetails(token)" 
                  class="text-gray-400 hover:text-white transition-colors">
            <i :class="token.showDetails ? 'fa-chevron-up' : 'fa-chevron-down'" class="fas text-xs"></i>
          </button>
        </div>

        <!-- Grammar info -->
        <div class="mb-2">
          <div class="flex items-center gap-2 mb-1">
            <span class="bg-purple-600 text-white text-xs px-2 py-0.5 rounded">
              {{ getWordCategory(token) }}
            </span>
            <span v-if="token.grammar?.role" 
                  class="bg-orange-600 text-white text-xs px-2 py-0.5 rounded">
              {{ token.grammar.role }}
            </span>
          </div>
        </div>

        <!-- Basic definition -->
        <div v-if="token.definition && token.definition.senses" class="mb-2">
          <p class="text-sm text-gray-300 leading-relaxed">
            {{ getShortDefinition(token.definition) }}
          </p>
        </div>

        <!-- Contextual insight preview -->
        <div v-if="token.contextualInsight" class="bg-gray-750 rounded p-2 mb-2">
          <div class="text-xs text-blue-300 mb-1">💡 In this context:</div>
          <p class="text-xs text-gray-300 leading-relaxed">
            {{ token.contextualInsight.contextual_meaning?.substring(0, 100) }}...
          </p>
        </div>

        <!-- Expandable details -->
        <div v-if="token.showDetails" class="border-t border-gray-600 pt-2 mt-2">
          <!-- Alternative meanings -->
          <div v-if="token.definition && token.definition.senses.length > 1" class="mb-2">
            <div class="text-xs text-gray-400 mb-1">Other meanings:</div>
            <div class="text-xs text-gray-300">
              <span v-for="(sense, idx) in token.definition.senses.slice(1, 3)" :key="idx">
                {{ sense.english_definitions[0] }}{{ idx < Math.min(token.definition.senses.length - 2, 1) ? ', ' : '' }}
              </span>
            </div>
          </div>

          <!-- Usage examples -->
          <div v-if="token.contextualInsight?.similar_expressions?.length" class="mb-2">
            <div class="text-xs text-gray-400 mb-1">Similar expressions:</div>
            <div class="flex flex-wrap gap-1">
              <span v-for="expr in token.contextualInsight.similar_expressions.slice(0, 3)" 
                    :key="expr"
                    class="bg-gray-700 text-xs px-2 py-1 rounded">
                {{ expr }}
              </span>
            </div>
          </div>

          <!-- Learning tip -->
          <div v-if="token.contextualInsight?.learning_tips" class="mb-2">
            <div class="text-xs text-gray-400 mb-1">💡 Learning tip:</div>
            <div class="text-xs text-gray-300 italic">
              {{ token.contextualInsight.learning_tips }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import axios from 'axios';

const props = defineProps({
  kanjiList: {
    type: Array,
    required: true
  },
  fullSentence: {
    type: String,
    default: ''
  }
});

const emit = defineEmits(['wordSelected', 'showGrammarInsights']);

// State
const selectedCategory = ref('all');
const sortBy = ref('appearance');
const isExplaining = ref(false);

// Add reactive properties to tokens
const enhancedKanjiList = computed(() => {
  return props.kanjiList.map((token, index) => ({
    ...token,
    index,
    frequency: calculateFrequency(token.surface),
    difficulty: calculateDifficulty(token),
    showDetails: false,
    contextualInsight: null
  }));
});

// Computed properties
const totalWords = computed(() => props.kanjiList.length);

const categoryStats = computed(() => {
  const stats = { verbs: 0, nouns: 0, adjectives: 0, particles: 0, expressions: 0 };
  enhancedKanjiList.value.forEach(token => {
    const category = getWordCategory(token).toLowerCase();
    if (category.includes('verb')) stats.verbs++;
    else if (category.includes('noun')) stats.nouns++;
    else if (category.includes('adjective')) stats.adjectives++;
    else if (category.includes('particle')) stats.particles++;
    else stats.expressions++;
  });
  return stats;
});

const uniqueWordsCount = computed(() => {
  const unique = new Set(props.kanjiList.map(token => token.surface));
  return unique.size;
});

const knownWordsCount = computed(() => {
  return props.kanjiList.filter(token => token.definition).length;
});

const filteredKanjiList = computed(() => {
  let filtered = enhancedKanjiList.value;

  // Filter by category
  if (selectedCategory.value !== 'all') {
    filtered = filtered.filter(token => {
      const category = getWordCategory(token).toLowerCase();
      return category.includes(selectedCategory.value.slice(0, -1)); // Remove 's' from plural
    });
  }

  // Sort
  switch (sortBy.value) {
    case 'frequency':
      filtered.sort((a, b) => b.frequency - a.frequency);
      break;
    case 'difficulty':
      filtered.sort((a, b) => a.difficulty - b.difficulty);
      break;
    case 'alphabetical':
      filtered.sort((a, b) => a.surface.localeCompare(b.surface));
      break;
    // 'appearance' is default order
  }

  return filtered;
});

// Methods
function calculateFrequency(surface) {
  return props.kanjiList.filter(token => token.surface === surface).length;
}

function calculateDifficulty(token) {
  let difficulty = 1; // Basic
  
  // Increase difficulty based on various factors
  if (token.grammar?.features?.length > 2) difficulty++;
  if (token.definition?.senses?.length > 3) difficulty++;
  if (token.surface.length > 3) difficulty++;
  if (/[\u4e00-\u9faf]/.test(token.surface)) difficulty++; // Contains kanji
  
  return Math.min(difficulty, 5); // Cap at 5
}

function getDifficultyColor(difficulty) {
  const colors = {
    1: 'bg-green-600 text-white',
    2: 'bg-yellow-600 text-white', 
    3: 'bg-orange-600 text-white',
    4: 'bg-red-600 text-white',
    5: 'bg-purple-600 text-white'
  };
  return colors[difficulty] || colors[1];
}

function getDifficultyLabel(difficulty) {
  const labels = {
    1: 'Basic',
    2: 'Easy',
    3: 'Medium', 
    4: 'Hard',
    5: 'Expert'
  };
  return labels[difficulty] || 'Basic';
}

function getWordCategory(token) {
  if (!token.grammar?.pos) return 'Unknown';
  return token.grammar.pos;
}

function getShortDefinition(definition) {
  if (!definition?.senses?.[0]?.english_definitions?.[0]) return 'No definition available';
  const def = definition.senses[0].english_definitions[0];
  return def.length > 80 ? def.substring(0, 80) + '...' : def;
}

function toggleWordDetails(token) {
  token.showDetails = !token.showDetails;
}

function selectWord(token) {
  emit('wordSelected', token);
}

async function explainWord(token) {
  if (isExplaining.value) return;
  
  isExplaining.value = true;
  try {
    const response = await axios.post('http://localhost:8002/explain-word', {
      word: token.surface,
      sentence: props.fullSentence,
      grammar_info: token.grammar || {},
      context_info: token.context || {},
      definition: token.definition || {}
    });
    
    token.contextualInsight = response.data;
  } catch (error) {
    console.error('Failed to get explanation:', error);
    token.contextualInsight = {
      contextual_meaning: 'Unable to generate explanation at this time.',
      sentence_role: token.grammar?.role || 'Unknown',
      usage_notes: 'Please try again later.',
      similar_expressions: [],
      learning_tips: 'Practice using this word in context.'
    };
  } finally {
    isExplaining.value = false;
  }
}

function addToStudyList(token) {
  // TODO: Implement study list functionality
  console.log('Added to study list:', token.surface);
}

function hearPronunciation(token) {
  // TODO: Implement text-to-speech
  console.log('Playing pronunciation for:', token.surface);
}

function showGrammarInsights() {
  emit('showGrammarInsights');
}
</script>

<style scoped>
.vocabulary-panel {
  background: var(--surface-medium);
  border: 1px solid var(--border-grey);
  border-radius: var(--radius-lg);
  color: var(--text-primary);
  height: 100%;
  overflow: hidden;
}

ruby {
  display: inline-flex;
  flex-direction: column-reverse;
  line-height: 1.2;
}

.bg-gray-750 {
  background-color: var(--surface-high);
}

/* Enhanced scrollbar for sidebar */
.thin-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.thin-scrollbar::-webkit-scrollbar-track {
  background: #1f2937;
  border-radius: 3px;
}

.thin-scrollbar::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
  border-radius: 3px;
}

.thin-scrollbar::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
}
</style>