"""
FastAPI server for running the crypto agent with real-time updates via SSE.
"""
import asyncio
import json
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn
from runner import run_with_feedback_loop
import os


class RunRequest(BaseModel):
    coin_name: str
    max_retries: int = 3


class ProgressCallback:
    """Callback class to capture progress updates from runner."""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.queue = asyncio.Queue()
    
    async def send_update(self, update_type: str, data: dict):
        """Send an update to the frontend."""
        update = {
            "type": update_type,
            "data": data,
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.queue.put(update)
    
    async def get_updates(self):
        """Generator that yields updates."""
        while True:
            try:
                update = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                yield f"data: {json.dumps(update)}\n\n"
                # If we get a complete or error, break the loop
                if update.get("type") in ["complete", "error"]:
                    break
            except asyncio.TimeoutError:
                # Send heartbeat to keep connection alive
                yield f": heartbeat\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'data': {'message': str(e)}})}\n\n"
                break


async def run_agent_with_updates(coin_name: str, max_retries: int, callback: ProgressCallback):
    """Run the agent with progress callbacks."""
    try:
        await run_with_feedback_loop(coin_name, max_retries, callback)
    except Exception as e:
        await callback.send_update("error", {
            "message": f"Error during execution: {str(e)}"
        })


app = FastAPI(title="Crypto Agent Runner API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Crypto Agent Runner API", "status": "running"}


@app.get("/api/coins")
async def get_coins():
    """Get list of top 10 cryptocurrencies."""
    coins = [
        {"symbol": "BTC", "name": "Bitcoin"},
        {"symbol": "ETH", "name": "Ethereum"},
        {"symbol": "USDT", "name": "Tether"},
        {"symbol": "BNB", "name": "BNB"},
        {"symbol": "SOL", "name": "Solana"},
        {"symbol": "USDC", "name": "USD Coin"},
        {"symbol": "XRP", "name": "Ripple"},
        {"symbol": "DOGE", "name": "Dogecoin"},
        {"symbol": "ADA", "name": "Cardano"},
        {"symbol": "TRX", "name": "TRON"},
    ]
    return {"coins": coins}


@app.post("/api/run")
async def run_agent(request: RunRequest):
    """Start running the agent and return SSE stream."""
    import uuid
    session_id = str(uuid.uuid4())
    
    callback = ProgressCallback(session_id)
    
    # Start the agent run in background
    asyncio.create_task(
        run_agent_with_updates(request.coin_name, request.max_retries, callback)
    )
    
    return StreamingResponse(
        callback.get_updates(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@app.get("/api/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
