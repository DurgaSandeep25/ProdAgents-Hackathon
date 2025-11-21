# Crypto Agent Runner - UI Setup

This project includes a professional web UI for running the crypto agent with real-time updates.

## Prerequisites

- Python 3.8+ with virtual environment
- Node.js 16+ and npm
- All Python dependencies from the main project

## Setup Instructions

### 1. Backend Setup

The backend API server is already set up. Make sure you have FastAPI installed:

```bash
# Activate your virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Install FastAPI and uvicorn if not already installed
pip install fastapi uvicorn
```

### 2. Frontend Setup

Install frontend dependencies:

```bash
npm install
```

## Running the Application

### Start the Backend API Server

In one terminal:

```bash
# Activate virtual environment
source venv/bin/activate

# Run the API server
python api_server.py
```

The API server will run on `http://localhost:8000`

### Start the Frontend Development Server

In another terminal:

```bash
npm run dev
```

The frontend will run on `http://localhost:3000` and automatically proxy API requests to the backend.

## Usage

1. Open your browser to `http://localhost:3000`
2. Select a cryptocurrency from the dropdown (top 10 coins available)
3. Click "Run Agent" to start the execution
4. Watch real-time updates in the log viewer:
   - Current attempt number
   - Agent decisions (BUY/SELL)
   - Price updates (T0 and T1)
   - Countdown timer during 30-second wait
   - Evaluation results with profit/loss
   - Prompt updates when retrying
   - Final completion status

## Features

- **Real-time Updates**: Server-Sent Events (SSE) for live progress updates
- **Professional UI**: Modern design with Tailwind CSS
- **Status Panel**: Shows current execution status with color-coded indicators
- **Detailed Logs**: Complete execution log with timestamps and icons
- **Responsive Design**: Works on desktop and tablet devices

## API Endpoints

- `GET /api/coins` - Get list of available cryptocurrencies
- `POST /api/run` - Start agent execution (returns SSE stream)
- `GET /api/health` - Health check endpoint

## Troubleshooting

- If the frontend can't connect to the backend, make sure `api_server.py` is running on port 8000
- Check browser console for any connection errors
- Ensure CORS is properly configured (already set to allow all origins for development)

