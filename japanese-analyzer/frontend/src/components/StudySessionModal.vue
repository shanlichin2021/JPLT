<template>
  <div class="leading-relaxed">
    <span 
      v-for="(token, tokenIndex) in tokens" 
      :key="tokenIndex" 
      class="token-block"
    >
      <span 
        class="inline-block transition-all duration-200"
        :class="getTokenClasses(token)"
        @click="token.definition ? selectToken(token, $event) : null"
      >
        <span v-for="(component, compIndex) in token.components" :key="compIndex">
          <ruby v-if="component.isKanji && component.furigana !== component.text" class="ruby-text">
            {{ component.text }}
            <rt>{{ component.furigana }}</rt>
          </ruby>
          <span v-else>
            {{ component.text }}
          </span>
        </span>
        
        <!-- Visual indicator for different token types -->
        <span v-if="token.definition" class="definition-indicator">
          <i :class="getIndicatorIcon(token)" class="text-xs opacity-60"></i>
        </span>
      </span>
    </span>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';

const props = defineProps({
  tokens: {
    type: Array,
    required: true,
  },
});

const emit = defineEmits(['tokenSelected']);

const selectToken = (token, event) => {
  emit('tokenSelected', token, event);
};

const getTokenClasses = (token) => {
  const classes = ['token-wrapper'];
  
  if (token.definition) {
    classes.push('interactive-token');
    
    // Add different styling based on part of speech
    const pos = token.definition?.senses?.[0]?.parts_of_speech?.[0]?.toLowerCase();
    if (pos?.includes('noun')) {
      classes.push('pos-noun');
    } else if (pos?.includes('verb')) {
      classes.push('pos-verb');
    } else if (pos?.includes('adj')) {
      classes.push('pos-adjective');
    } else {
      classes.push('pos-other');
    }
    
    // Add difficulty indicator
    const difficulty = getDifficultyLevel(token);
    classes.push(`difficulty-${difficulty}`);
  } else {
    classes.push('no-definition');
  }
  
  return classes.join(' ');
};

const getIndicatorIcon = (token) => {
  const pos = token.definition?.senses?.[0]?.parts_of_speech?.[0]?.toLowerCase();
  
  if (pos?.includes('noun')) return 'fas fa-cube';
  if (pos?.includes('verb')) return 'fas fa-running';
  if (pos?.includes('adj')) return 'fas fa-palette';
  if (pos?.includes('particle')) return 'fas fa-link';
  if (pos?.includes('adverb')) return 'fas fa-tachometer-alt';
  
  return 'fas fa-circle';
};

const getDifficultyLevel = (token) => {
  let score = 0;
  
  // Kanji complexity
  const kanjiCount = (token.surface.match(/[\u4e00-\u9faf]/g) || []).length;
  score += kanjiCount * 2;
  
  // Word length
  score += token.surface.length;
  
  // Multiple meanings
  const senseCount = token.definition?.senses?.length || 0;
  score += Math.min(senseCount, 3);
  
  if (score <= 3) return 'beginner';
  if (score <= 6) return 'intermediate';
  if (score <= 10) return 'advanced';
  return 'expert';
};
</script>

<style scoped>
.token-block {
  display: inline-block;
  margin-right: 0.5em;
  margin-bottom: 0.5em;
  line-height: 1.8;
  white-space: nowrap;
  vertical-align: baseline;
}

.token-wrapper {
  position: relative;
  border-radius: 6px;
  padding: 0.2em 0.3em;
  transition: all 0.2s ease;
}

.interactive-token {
  cursor: pointer;
  border-bottom: 2px solid transparent;
}

.interactive-token:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

/* Part of speech styling */
.pos-noun {
  border-bottom-color: rgba(139, 92, 246, 0.6); /* Purple */
  background: rgba(139, 92, 246, 0.1);
}

.pos-noun:hover {
  background: rgba(139, 92, 246, 0.2);
  border-bottom-color: rgba(139, 92, 246, 0.8);
}

.pos-verb {
  border-bottom-color: rgba(34, 197, 94, 0.6); /* Green */
  background: rgba(34, 197, 94, 0.1);
}

.pos-verb:hover {
  background: rgba(34, 197, 94, 0.2);
  border-bottom-color: rgba(34, 197, 94, 0.8);
}

.pos-adjective {
  border-bottom-color: rgba(251, 191, 36, 0.6); /* Yellow */
  background: rgba(251, 191, 36, 0.1);
}

.pos-adjective:hover {
  background: rgba(251, 191, 36, 0.2);
  border-bottom-color: rgba(251, 191, 36, 0.8);
}

.pos-other {
  border-bottom-color: rgba(59, 130, 246, 0.6); /* Blue */
  background: rgba(59, 130, 246, 0.1);
}

.pos-other:hover {
  background: rgba(59, 130, 246, 0.2);
  border-bottom-color: rgba(59, 130, 246, 0.8);
}

/* Difficulty indicators */
.difficulty-beginner {
  box-shadow: 0 0 0 1px rgba(34, 197, 94, 0.3);
}

.difficulty-intermediate {
  box-shadow: 0 0 0 1px rgba(251, 191, 36, 0.3);
}

.difficulty-advanced {
  box-shadow: 0 0 0 1px rgba(249, 115, 22, 0.3);
}

.difficulty-expert {
  box-shadow: 0 0 0 1px rgba(239, 68, 68, 0.3);
}

/* No definition styling */
.no-definition {
  color: rgba(156, 163, 175, 0.8);
  border-bottom: 1px dotted rgba(75, 85, 99, 0.5);
}

/* Ruby text styling */
.ruby-text {
  display: inline-flex;
  flex-direction: column-reverse;
  align-items: center;
  line-height: 1.2;
  vertical-align: baseline;
}

.ruby-text rt {
  font-size: 0.75rem;
  color: rgba(147, 197, 253, 0.9);
  user-select: none;
  font-weight: normal;
  text-align: center;
  margin-bottom: 2px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

/* Definition indicator */
.definition-indicator {
  position: absolute;
  top: -2px;
  right: -2px;
  width: 12px;
  height: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.7);
  border-radius: 50%;
  opacity: 0;
  transition: opacity 0.2s ease;
  pointer-events: none;
}

.interactive-token:hover .definition-indicator {
  opacity: 1;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .token-block {
    margin-right: 0.3em;
    margin-bottom: 0.3em;
    line-height: 1.6;
  }
  
  .token-wrapper {
    padding: 0.1em 0.2em;
  }
  
  .ruby-text rt {
    font-size: 0.7rem;
  }
}

/* Dark mode optimizations */
@media (prefers-color-scheme: dark) {
  .ruby-text rt {
    color: rgba(147, 197, 253, 0.9);
  }
  
  .definition-indicator {
    background: rgba(0, 0, 0, 0.8);
  }
}

/* High contrast mode */
@media (prefers-contrast: high) {
  .interactive-token {
    border-bottom-width: 3px;
  }
  
  .pos-noun:hover,
  .pos-verb:hover,
  .pos-adjective:hover,
  .pos-other:hover {
    background: rgba(255, 255, 255, 0.2);
  }
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  .token-wrapper,
  .definition-indicator {
    transition: none;
  }
  
  .interactive-token:hover {
    transform: none;
  }
}

/* Focus styles for accessibility */
.interactive-token:focus {
  outline: 2px solid rgba(59, 130, 246, 0.8);
  outline-offset: 2px;
}

/* Selection styling */
.token-wrapper::selection {
  background: rgba(59, 130, 246, 0.3);
}

/* Animation for newly analyzed text */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.token-block {
  animation: fadeInUp 0.3s ease-out;
  animation-fill-mode: both;
}

/* Stagger animation delay for tokens */
.token-block:nth-child(1) { animation-delay: 0ms; }
.token-block:nth-child(2) { animation-delay: 50ms; }
.token-block:nth-child(3) { animation-delay: 100ms; }
.token-block:nth-child(4) { animation-delay: 150ms; }
.token-block:nth-child(5) { animation-delay: 200ms; }
.token-block:nth-child(6) { animation-delay: 250ms; }
.token-block:nth-child(7) { animation-delay: 300ms; }
.token-block:nth-child(8) { animation-delay: 350ms; }
.token-block:nth-child(9) { animation-delay: 400ms; }
.token-block:nth-child(10) { animation-delay: 450ms; }

/* For tokens beyond 10, use a base delay */
.token-block:nth-child(n+11) { animation-delay: 500ms; }
</style>