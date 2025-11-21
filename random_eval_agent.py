import asyncio
import argparse
import os
import json
from pathlib import Path
import random
import anyio
import httpx


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


async def evaluate_random_trade(coin_name, trade_number):
    """Evaluate a single random trading decision and return profit."""
    # Step 1: Randomly decide BUY or SELL
    decision = random.choice(["BUY", "SELL"])
    print(f"\nTrade #{trade_number}: Random decision: {decision}")
    
    # Step 2: Get price now
    price_before = await get_coin_price(coin_name)
    if price_before is None:
        print(f"Trade #{trade_number}: Failed to get initial price")
        return None
    
    print(f"Trade #{trade_number}: Price at T0: ${price_before}")
    
    # Wait 10 seconds
    print(f"Trade #{trade_number}: Waiting 10 seconds...")
    await asyncio.sleep(10)
    
    # Get price again
    price_after = await get_coin_price(coin_name)
    if price_after is None:
        print(f"Trade #{trade_number}: Failed to get price after wait")
        return None
    
    print(f"Trade #{trade_number}: Price at T1: ${price_after}")
    
    # Step 3: Calculate profit
    # For BUY: profit = price_after - price_before
    # For SELL: profit = price_before - price_after
    execution_price = price_before
    selling_price = price_after
    
    if decision == "BUY":
        profit = selling_price - execution_price
    else:  # SELL
        profit = execution_price - selling_price
    
    print(f"Trade #{trade_number}: Execution price: ${execution_price:.2f}")
    print(f"Trade #{trade_number}: Selling price: ${selling_price:.2f}")
    print(f"Trade #{trade_number}: Profit: ${profit:.2f}")
    
    return profit


async def evaluate_random_agent(coin_name, num_trades=10):
    """Evaluate random trading decisions and return profits and success list."""
    load_env_file()
    
    print(f"Starting random evaluation for {coin_name}")
    print(f"Will execute {num_trades} trades, each with 10 second intervals")
    
    profits = []
    success_list = []
    
    for i in range(1, num_trades + 1):
        profit = await evaluate_random_trade(coin_name, i)
        
        if profit is not None:
            profits.append(profit)
            # 1 means positive profit, 0 means loss
            success = 1 if profit > 0 else 0
            success_list.append(success)
            print(f"Trade #{i}: Result: {success} ({'Profit' if success == 1 else 'Loss'})")
        else:
            print(f"Trade #{i}: Failed to evaluate")
            # You might want to handle this differently - maybe skip or use 0
            profits.append(0.0)
            success_list.append(0)
    
    return profits, success_list


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate random trading decisions")
    parser.add_argument("--coin-name", required=True, help="Coin name to evaluate (e.g., BTC, ETH)")
    parser.add_argument("--num-trades", type=int, default=10, help="Number of trades to execute (default: 10)")
    args = parser.parse_args()
    
    profits, success_list = anyio.run(evaluate_random_agent, args.coin_name, args.num_trades)
    
    print("\n" + "="*50)
    print("FINAL RESULTS")
    print("="*50)
    print(f"\nProfits: {profits}")
    print(f"Success list (1=profit, 0=loss): {success_list}")
    print(f"\nTotal profitable trades: {sum(success_list)}/{len(success_list)}")
    print(f"Total profit: ${sum(profits):.2f}")

