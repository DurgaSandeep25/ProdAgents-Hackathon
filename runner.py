import asyncio
import argparse
import os
import json
from pathlib import Path
from datetime import datetime
import anthropic
import httpx
import anyio
from agent import main as agent_main, load_system_prompt, load_env_file, setup_logging_directory


async def get_coin_price(coin_name):
    """Get current price of a coin from CoinGecko API."""
    coin_id_map = {
        "BTC": "bitcoin",
        "bitcoin": "bitcoin",
        "ETH": "ethereum",
        "ethereum": "ethereum",
        "USDT": "tether",
        "tether": "tether",
        "BNB": "binancecoin",
        "binancecoin": "binancecoin",
        "SOL": "solana",
        "solana": "solana",
        "USDC": "usd-coin",
        "usd-coin": "usd-coin",
        "XRP": "ripple",
        "ripple": "ripple",
        "DOGE": "dogecoin",
        "dogecoin": "dogecoin",
        "ADA": "cardano",
        "cardano": "cardano",
        "TRX": "tron",
        "tron": "tron"
    }
    
    coin_id = coin_id_map.get(coin_name.upper(), coin_name.lower())
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


def find_latest_log_file(coin_name, logs_dir):
    """Find the latest log file for a given coin."""
    log_files = list(logs_dir.glob(f"agent_log_{coin_name}_*.jsonl"))
    if not log_files:
        return None
    
    # Sort by modification time, newest first
    log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return log_files[0]


def read_log_file(log_file_path):
    """Read and return the content of a log file."""
    if not log_file_path or not log_file_path.exists():
        return None
    
    try:
        with open(log_file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Error reading log file: {e}")
        return None


async def get_updated_prompt(log_content, system_prompt, coin_name):
    """Call Claude to get an updated prompt based on failure analysis."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Warning: ANTHROPIC_API_KEY not found in environment")
        return None, None
    
    client = anthropic.Anthropic(api_key=api_key)
    
    # Prepare the input for Claude
    input_text = f"""The agent failed to make a profitable trading decision for {coin_name}.

LOG FILE CONTENT:
{log_content}

CURRENT SYSTEM PROMPT:
{system_prompt}

FAILURE INDICATION: The agent's decision resulted in a loss (profit <= 0).

Please analyze the log file and current system prompt, then provide an updated system prompt that should help the agent make better decisions. Focus on what went wrong and how to improve the decision-making process."""

    try:
        response = client.beta.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=2048,
            betas=["structured-outputs-2025-11-13"],
            messages=[
                {
                    "role": "user",
                    "content": input_text
                }
            ],
            output_format={
                "type": "json_schema",
                "schema": {
                    "type": "object",
                    "properties": {
                        "updated_prompt": {
                            "type": "string",
                            "description": "The updated system prompt that should replace the current one"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Brief explanation (within 30 words) of why the prompt was updated"
                        }
                    },
                    "required": ["updated_prompt", "reason"],
                    "additionalProperties": False
                }
            }
        )
        
        structured_output = json.loads(response.content[0].text)
        return structured_output.get("updated_prompt"), structured_output.get("reason")
        
    except Exception as e:
        print(f"Error getting updated prompt: {e}")
        return None, None


async def evaluate_decision(coin_name, decision, system_prompt=None, callback=None):
    """Evaluate a trading decision and return success status."""
    print(f"\n{'='*60}")
    print(f"Evaluating decision: {decision}")
    print(f"{'='*60}")
    
    if callback:
        await callback.send_update("status", {"message": f"Evaluating decision: {decision}"})
    
    # Get price before
    print("Getting current price (T0)...")
    if callback:
        await callback.send_update("status", {"message": "Getting current price (T0)..."})
    
    price_before = await get_coin_price(coin_name)
    if price_before is None:
        print("Failed to get initial price")
        if callback:
            await callback.send_update("error", {"message": "Failed to get initial price"})
        return False, None, None
    
    print(f"Price at T0: ${price_before:.2f}")
    if callback:
        await callback.send_update("price_update", {
            "price": price_before,
            "time": "T0",
            "label": "Initial Price"
        })
    
    # Wait 30 seconds with countdown updates
    print("Waiting 30 seconds...")
    if callback:
        await callback.send_update("status", {"message": "Waiting 30 seconds..."})
    
    # Send countdown updates every 5 seconds
    for i in range(30, 0, -5):
        await asyncio.sleep(5)
        if callback:
            await callback.send_update("countdown", {"seconds_remaining": i})
    
    # Get price after
    print("Getting price after 30 seconds (T1)...")
    if callback:
        await callback.send_update("status", {"message": "Getting price after 30 seconds (T1)..."})
    
    price_after = await get_coin_price(coin_name)
    if price_after is None:
        print("Failed to get price after wait")
        if callback:
            await callback.send_update("error", {"message": "Failed to get price after wait"})
        return False, None, None
    
    print(f"Price at T1: ${price_after:.2f}")
    if callback:
        await callback.send_update("price_update", {
            "price": price_after,
            "time": "T1",
            "label": "Final Price"
        })
    
    # Calculate profit
    if decision == "BUY":
        profit = price_after - price_before
    else:  # SELL
        profit = price_before - price_after
    
    print(f"Execution price: ${price_before:.2f}")
    print(f"Selling price: ${price_after:.2f}")
    print(f"Profit: ${profit:.2f}")
    
    # Success if profit > 0
    success = profit > 0
    print(f"Result: {'SUCCESS' if success else 'FAILURE'} ({'Profit' if success else 'Loss'})")
    
    if callback:
        await callback.send_update("evaluation_result", {
            "success": success,
            "profit": profit,
            "price_before": price_before,
            "price_after": price_after
        })
    
    return success, price_before, price_after


async def run_agent_with_prompt(coin_name, system_prompt):
    """Run the agent with a specific system prompt."""
    # Temporarily modify the system prompt file
    prompt_path = Path(__file__).parent / "prompts" / "system.j2"
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save original prompt if it exists
    original_prompt = None
    if prompt_path.exists():
        with open(prompt_path, "r", encoding="utf-8") as f:
            original_prompt = f.read()
    
    # Write new prompt
    try:
        with open(prompt_path, "w", encoding="utf-8") as f:
            f.write(system_prompt)
        
        # Run agent (it will load the prompt from file)
        result = await agent_main(coin_name)
        
        return result
    finally:
        # Always restore original prompt
        if original_prompt is not None:
            with open(prompt_path, "w", encoding="utf-8") as f:
                f.write(original_prompt)
        elif prompt_path.exists():
            # If there was no original, we might want to keep the new one
            # But for safety, let's restore the default
            pass


async def run_with_feedback_loop(coin_name, max_retries=3, callback=None):
    """Run the agent with feedback loop for up to max_retries times."""
    load_env_file()
    
    logs_dir = setup_logging_directory()
    system_prompt = load_system_prompt()
    
    print(f"\n{'='*60}")
    print(f"Starting runner for {coin_name}")
    print(f"Max retries: {max_retries}")
    print(f"{'='*60}\n")
    
    if callback:
        await callback.send_update("status", {
            "message": f"Starting runner for {coin_name}",
            "coin_name": coin_name,
            "max_retries": max_retries
        })
    
    attempt = 0
    current_prompt = system_prompt
    last_successful_prompt = None
    overall_success = False
    
    while attempt < max_retries:
        attempt += 1
        print(f"\n{'='*60}")
        print(f"ATTEMPT {attempt}/{max_retries}")
        print(f"{'='*60}\n")
        
        if callback:
            await callback.send_update("attempt_start", {
                "attempt": attempt,
                "max_retries": max_retries
            })
        
        # Run agent with current prompt
        print(f"Running agent with current system prompt...")
        if callback:
            await callback.send_update("status", {
                "message": f"Running agent (Attempt {attempt}/{max_retries})..."
            })
        
        agent_result = await run_agent_with_prompt(coin_name, current_prompt)
        
        # Get the latest log file right after agent run
        log_file = find_latest_log_file(coin_name, logs_dir)
        
        if not agent_result or not agent_result.get("structured_decision"):
            print("Failed to get decision from agent")
            if callback:
                await callback.send_update("status", {
                    "message": "Failed to get decision from agent",
                    "level": "warning"
                })
            
            if attempt < max_retries:
                print("Will retry with updated prompt...")
                if callback:
                    await callback.send_update("status", {
                        "message": "Will retry with updated prompt..."
                    })
                
                # Still try to update prompt based on failure
                if log_file:
                    log_content = read_log_file(log_file)
                    if log_content:
                        if callback:
                            await callback.send_update("status", {
                                "message": "Calling Claude to get updated prompt..."
                            })
                        
                        updated_prompt, reason = await get_updated_prompt(
                            log_content, current_prompt, coin_name
                        )
                        if updated_prompt:
                            current_prompt = updated_prompt
                            print(f"Updated prompt. Reason: {reason}")
                            if callback:
                                await callback.send_update("prompt_updated", {
                                    "reason": reason,
                                    "attempt": attempt
                                })
            continue
        
        decision = agent_result["structured_decision"]["decision"]
        reason = agent_result["structured_decision"].get("reason", "")
        print(f"Agent decision: {decision}")
        
        if callback:
            await callback.send_update("decision", {
                "decision": decision,
                "reason": reason,
                "attempt": attempt
            })
        
        # Evaluate the decision
        success, price_before, price_after = await evaluate_decision(
            coin_name, decision, current_prompt, callback
        )
        
        if success:
            print(f"\n{'='*60}")
            print("SUCCESS! Decision was profitable.")
            print(f"{'='*60}\n")
            
            if price_before and price_after:
                profit = price_after - price_before if decision == "BUY" else price_before - price_after
                if callback:
                    await callback.send_update("evaluation", {
                        "success": True,
                        "decision": decision,
                        "price_before": price_before,
                        "price_after": price_after,
                        "profit": profit,
                        "attempt": attempt
                    })
            
            # Track successful prompt
            last_successful_prompt = current_prompt
            overall_success = True
            
            if callback:
                await callback.send_update("success", {
                    "message": "Decision was profitable!",
                    "attempt": attempt
                })
            
            # If not the last attempt, continue to next attempt
            if attempt < max_retries:
                print(f"Continuing to attempt {attempt + 1} with same system prompt...\n")
                if callback:
                    await callback.send_update("status", {
                        "message": f"Continuing to attempt {attempt + 1}..."
                    })
                continue
            else:
                # Last attempt was successful
                break
        
        else:
            print(f"\n{'='*60}")
            print("FAILURE! Decision resulted in a loss.")
            print(f"{'='*60}\n")
            
            if price_before and price_after:
                profit = price_after - price_before if decision == "BUY" else price_before - price_after
                if callback:
                    await callback.send_update("evaluation", {
                        "success": False,
                        "decision": decision,
                        "price_before": price_before,
                        "price_after": price_after,
                        "profit": profit,
                        "attempt": attempt
                    })
            
            if callback:
                await callback.send_update("failure", {
                    "message": "Decision resulted in a loss.",
                    "attempt": attempt
                })
            
            if attempt < max_retries:
                # Use the log file we already found
                if log_file:
                    print(f"Found log file: {log_file}")
                    log_content = read_log_file(log_file)
                    
                    if log_content:
                        print("Calling Claude to get updated prompt...")
                        if callback:
                            await callback.send_update("status", {
                                "message": "Calling Claude to get updated prompt..."
                            })
                        
                        updated_prompt, reason = await get_updated_prompt(
                            log_content, current_prompt, coin_name
                        )
                        
                        if updated_prompt:
                            print(f"Updated prompt received.")
                            print(f"Reason: {reason}")
                            current_prompt = updated_prompt
                            print("Will retry with updated prompt...\n")
                            
                            if callback:
                                await callback.send_update("prompt_updated", {
                                    "reason": reason,
                                    "attempt": attempt
                                })
                        else:
                            print("Failed to get updated prompt. Will retry with same prompt...\n")
                    else:
                        print("Failed to read log file. Will retry with same prompt...\n")
                else:
                    print("No log file found. Will retry with same prompt...\n")
    
    # Write final successful prompt back to file if we had success
    if last_successful_prompt:
        prompt_path = Path(__file__).parent / "prompts" / "system.j2"
        prompt_path.parent.mkdir(parents=True, exist_ok=True)
        with open(prompt_path, "w", encoding="utf-8") as f:
            f.write(last_successful_prompt)
        print(f"\n{'='*60}")
        print("Final successful prompt written to prompts/system.j2")
        print(f"{'='*60}\n")
        
        if callback:
            await callback.send_update("status", {
                "message": "Final successful prompt written to prompts/system.j2"
            })
    
    if not overall_success:
        print(f"\n{'='*60}")
        print(f"All {max_retries} attempts exhausted without success.")
        print(f"{'='*60}\n")
    
    if callback:
        await callback.send_update("complete", {
            "success": overall_success,
            "attempts": attempt,
            "coin_name": coin_name
        })
    
    return overall_success, attempt


async def main(coin_name):
    """Main entry point."""
    success, attempts = await run_with_feedback_loop(coin_name, max_retries=3)
    
    print(f"\n{'='*60}")
    print("FINAL SUMMARY")
    print(f"{'='*60}")
    print(f"Coin: {coin_name}")
    print(f"Success: {success}")
    print(f"Attempts: {attempts}")
    print(f"{'='*60}\n")
    
    return success, attempts


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run agent with feedback loop")
    parser.add_argument("--coin-name", required=True, help="Coin name to run (e.g., BTC, ETH)")
    args = parser.parse_args()
    
    result = anyio.run(main, args.coin_name)
    success, attempts = result
    
    if success:
        print("✓ Runner completed successfully!")
    else:
        print("✗ Runner completed but did not achieve success within retry limit.")

