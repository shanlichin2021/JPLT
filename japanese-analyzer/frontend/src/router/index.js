// router/index.js - Vue Router configuration for Japanese Forest Analyzer

import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Analysis from '../views/Analysis.vue'
import SemanticSearch from '../views/SemanticSearch.vue'
import History from '../views/History.vue'
import Settings from '../views/Settings.vue'
import About from '../views/About.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: {
      title: 'Home - Japanese Text Analyzer',
      icon: 'fas fa-home',
      description: 'Welcome to the Japanese text analysis platform'
    }
  },
  {
    path: '/analysis',
    name: 'Analysis',
    component: Analysis,
    meta: {
      title: 'Text Analysis',
      icon: 'fas fa-brain',
      description: 'Analyze Japanese text with advanced NLP'
    }
  },
  {
    path: '/semantic-search',
    name: 'SemanticSearch',
    component: SemanticSearch,
    meta: {
      title: 'Semantic Search',
      icon: 'fas fa-search',
      description: 'AI-powered semantic search through Japanese dictionary'
    }
  },
  {
    path: '/history',
    name: 'History',
    component: History,
    meta: {
      title: 'Analysis History',
      icon: 'fas fa-history',
      description: 'View your past analyses and results'
    }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings,
    meta: {
      title: 'Settings',
      icon: 'fas fa-cog',
      description: 'Configure your analysis preferences'
    }
  },
  {
    path: '/about',
    name: 'About',
    component: About,
    meta: {
      title: 'About',
      icon: 'fas fa-info-circle',
      description: 'Learn about the Japanese text analyzer'
    }
  },
  {
    // Catch-all redirect to home
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// Navigation guards
router.beforeEach((to, from, next) => {
  // Update document title based on route meta
  if (to.meta.title) {
    document.title = to.meta.title
  }
  
  // Log navigation for debugging
  console.log(`Navigating from ${from.name || 'unknown'} to ${to.name}`)
  
  next()
})

export default router