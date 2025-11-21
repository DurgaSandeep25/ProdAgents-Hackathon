#!/bin/bash

# Start script for Crypto Agent UI
# This script starts both the backend API server and frontend dev server

echo "🚀 Starting Crypto Agent UI..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please create one first."
    exit 1
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

# Start backend in background
echo "🔧 Starting backend API server on port 8000..."
source venv/bin/activate
python api_server.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 2

# Start frontend
echo "🎨 Starting frontend dev server on port 3000..."
echo ""
echo "✅ Backend running on http://localhost:8000"
echo "✅ Frontend will be available at http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

npm run dev

# Cleanup on exit
kill $BACKEND_PID 2>/dev/null

