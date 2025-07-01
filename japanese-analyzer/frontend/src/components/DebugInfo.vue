<template>
  <div class="debug-info">
    <h3>Debug Information</h3>
    <div class="debug-section">
      <h4>Route Information</h4>
      <p><strong>Route Name:</strong> {{ $route.name }}</p>
      <p><strong>Route Path:</strong> {{ $route.path }}</p>
      <p><strong>Route Query:</strong> {{ JSON.stringify($route.query) }}</p>
      <p><strong>Route Query Text:</strong> "{{ $route.query.text }}"</p>
      <p><strong>Route Query Text Type:</strong> {{ typeof $route.query.text }}</p>
    </div>
    
    <div class="debug-section">
      <h4>Props/Data</h4>
      <p><strong>Input Text:</strong> "{{ inputText }}"</p>
      <p><strong>Input Text Type:</strong> {{ typeof inputText }}</p>
      <p><strong>Input Text Length:</strong> {{ inputText?.length }}</p>
      <p><strong>Is Loading:</strong> {{ isLoading }}</p>
      <p><strong>Error:</strong> {{ error }}</p>
      <p><strong>Analysis Result Length:</strong> {{ analysisResult?.length }}</p>
    </div>
    
    <div class="debug-section">
      <h4>Test Actions</h4>
      <button @click="testDirectAPI" class="debug-btn">Test Direct API</button>
      <button @click="testProxyAPI" class="debug-btn">Test Proxy API</button>
      <div v-if="apiTestResult" class="api-result">
        <strong>API Test Result:</strong>
        <pre>{{ apiTestResult }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  inputText: String,
  isLoading: Boolean,
  error: String,
  analysisResult: Array
})

const apiTestResult = ref('')

const testDirectAPI = async () => {
  try {
    const response = await fetch('http://localhost:3000/api/full-analysis', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: 'こんにちは' })
    })
    const data = await response.json()
    apiTestResult.value = `SUCCESS: ${data.chunks?.length || 0} chunks received`
  } catch (error) {
    apiTestResult.value = `ERROR: ${error.message}`
  }
}

const testProxyAPI = async () => {
  try {
    const response = await fetch('/api/full-analysis', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: 'こんにちは' })
    })
    const data = await response.json()
    apiTestResult.value = `SUCCESS: ${data.chunks?.length || 0} chunks received via proxy`
  } catch (error) {
    apiTestResult.value = `ERROR: ${error.message}`
  }
}
</script>

<style scoped>
.debug-info {
  background: #f5f5f5;
  border: 2px solid #ccc;
  padding: 1rem;
  margin: 1rem 0;
  border-radius: 8px;
  font-family: monospace;
  font-size: 14px;
}

.debug-section {
  margin-bottom: 1rem;
  padding: 0.5rem;
  background: white;
  border-radius: 4px;
}

.debug-btn {
  background: #007bff;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  margin: 0.25rem;
  border-radius: 4px;
  cursor: pointer;
}

.debug-btn:hover {
  background: #0056b3;
}

.api-result {
  margin-top: 0.5rem;
  padding: 0.5rem;
  background: #e9ecef;
  border-radius: 4px;
}

pre {
  white-space: pre-wrap;
  word-break: break-word;
}
</style>