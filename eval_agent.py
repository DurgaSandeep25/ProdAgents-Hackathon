import asyncio
import argparse
import os
from pathlib import Path
import httpx
from agent import main as agent_main
import anyio


def load_env_file():
    """Load environment variables from .env file."""
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()


async def get_coin_price(coin_name):
    """Get current price of a coin from CoinGecko API."""
    # Map common coin symbols to CoinGecko IDs (Top 10 cryptocurrencies)
    coin_id_map = {
        # Bitcoin
        "BTC": "bitcoin",
        "bitcoin": "bitcoin",
        # Ethereum
        "ETH": "ethereum",
        "ethereum": "ethereum",
        # Tether
        "USDT": "tether",
        "tether": "tether",
        # BNB
        "BNB": "binancecoin",
        "binancecoin": "binancecoin",
        # Solana
        "SOL": "solana",
        "solana": "solana",
        # USDC
        "USDC": "usd-coin",
        "usd-coin": "usd-coin",
        # XRP
        "XRP": "ripple",
        "ripple": "ripple",
        # Dogecoin
        "DOGE": "dogecoin",
        "dogecoin": "dogecoin",
        # Cardano
        "ADA": "cardano",
        "cardano": "cardano",
        # TRON
        "TRX": "tron",
        "tron": "tron"
    }
    
    # Get CoinGecko ID (default to lowercase coin_name if not in map)
    coin_id = coin_id_map.get(coin_name.upper(), coin_name.lower())
    
    # Get API key from environment (optional, but recommended)
    api_key = os.environ.get("COINGECKO_API_KEY")
    
    async with httpx.AsyncClient() as client:
        try:
            headers = {}
            if api_key:
                headers["x-cg-api-key"] = api_key
            
            response = await client.get(
                "https://api.coingecko.com/api/v3/simple/price",
                params={"ids": coin_id, "vs_currencies": "usd"},
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            
            if coin_id in data:
                return data[coin_id]["usd"]
            
            return None
        except Exception as e:
            print(f"Error fetching price: {e}")
            return None


async def evaluate_agent(coin_name):
    """Evaluate the agent's decision and return profit status."""
    load_env_file()
    
    # Step 1: Call agent.py to get buy/sell decision
    print(f"Calling agent for {coin_name}...")
    agent_result = await agent_main(coin_name)
    
    if not agent_result or not agent_result.get("structured_decision"):
        print("Failed to get decision from agent")
        return 0
    
    decision = agent_result["structured_decision"]["decision"]
    print(f"Agent decision: {decision}")
    
    # Step 2: Get price now
    print("Getting current price...")
    price_before = await get_coin_price(coin_name)
    if price_before is None:
        print("Failed to get initial price")
        return 0
    
    print(f"Price at T0: ${price_before}")
    
    # Wait 10 seconds
    print("Waiting 10 seconds...")
    await asyncio.sleep(30)
    
    # Get price again
    print("Getting price after 10 seconds...")
    price_after = await get_coin_price(coin_name)
    if price_after is None:
        print("Failed to get price after wait")
        return 0
    
    print(f"Price at T1: ${price_after}")
    
    # Step 3: Calculate profit using prices directly
    execution_price = price_before
    selling_price = price_after
    
    print(f"Execution price: ${execution_price:.2f}")
    print(f"Selling price: ${selling_price:.2f}")
    
    # Step 4: Calculate profit
    if decision == "BUY":
        profit = selling_price - execution_price
    else:  # SELL
        profit = execution_price - selling_price
    
    print(f"Profit: ${profit:.2f}")
    
    # Return 1 if profit > 0, else 0
    result = 1 if profit > 0 else 0
    print(f"Result: {result} ({'Profit' if result == 1 else 'No profit'})")
    
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate crypto agent decision")
    parser.add_argument("--coin-name", required=True, help="Coin name to evaluate (e.g., BTC, ETH)")
    args = parser.parse_args()
    
    result = anyio.run(evaluate_agent, args.coin_name)
    print(f"\nFinal result: {result}")

