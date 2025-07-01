#!/bin/bash
# Instant test script that runs as soon as vector service starts

echo "🚀 STARTING INSTANT VECTOR DATABASE TESTS"
echo "============================================"

# Wait for service to be ready
echo "⏳ Waiting for vector service to respond..."
for i in {1..30}; do
    if curl -s http://localhost:8002/health > /dev/null 2>&1; then
        echo "✅ Vector service is ready!"
        break
    fi
    echo "   Attempt $i/30..."
    sleep 1
done

echo ""
echo "🧪 TEST 1: Health Check"
curl -s http://localhost:8002/health | head -c 200
echo ""
echo ""

echo "🧪 TEST 2: Vector Database Stats"
curl -s http://localhost:8002/vector/stats | head -c 300
echo ""
echo ""

echo "🧪 TEST 3: Japanese BERT Embedding Test"
curl -s -X POST "http://localhost:8002/vector/embed" \
  -H "Content-Type: application/json" \
  -d '{"text": "こんにちは"}' | head -c 200
echo ""
echo ""

echo "🧪 TEST 4: Semantic Search - Food Concept"
curl -s -X POST "http://localhost:8002/vector/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "食べる", "top_k": 3, "similarity_threshold": 0.3}' | head -c 500
echo ""
echo ""

echo "🧪 TEST 5: Backend Integration Test"
curl -s -X POST "http://localhost:3000/api/semantic-search" \
  -H "Content-Type: application/json" \
  -d '{"query": "食べる", "top_k": 3}' | head -c 300
echo ""
echo ""

echo "🎉 QUICK TESTS COMPLETE!"
echo "🏃‍♂️ Running comprehensive test suite..."

# Run the full test suite
source venv/bin/activate
python test_real_vector_database.py