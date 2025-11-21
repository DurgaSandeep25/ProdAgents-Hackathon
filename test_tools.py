"""
Simple test script to verify custom tools are working
"""
import asyncio
from tools.html_fetcher import fetch_html
from tools.html_parser import parse_html_with_selectors
from tools.pattern_storage import store_iteration_result, get_previous_iterations
from tools.metrics_tracker import calculate_completeness, calculate_quality_score


async def test_tools():
    """Test custom tools."""
    print("Testing custom tools...\n")
    
    # Test HTML fetcher
    print("1. Testing fetch_html...")
    result = await fetch_html({"url": "https://www.example.com"})
    print(f"   Result: {result['content'][0]['text'][:100]}...\n")
    
    # Test HTML parser
    print("2. Testing parse_html_with_selectors...")
    html = "<html><body><h1>Test Product</h1><p class='price'>$99.99</p></body></html>"
    selectors = {
        "product_name": "h1",
        "price": ".price"
    }
    result = await parse_html_with_selectors({"html": html, "selectors": selectors})
    print(f"   Result: {result['content'][0]['text']}\n")
    
    # Test completeness calculator
    print("3. Testing calculate_completeness...")
    extracted_data = {
        "product_name": "Test Product",
        "price": "$99.99",
        "description": None
    }
    expected_fields = ["product_name", "price", "description"]
    result = await calculate_completeness({
        "extracted_data": extracted_data,
        "expected_fields": expected_fields
    })
    print(f"   Result: {result['content'][0]['text']}\n")
    
    # Test quality score
    print("4. Testing calculate_quality_score...")
    result = await calculate_quality_score({
        "extracted_data": extracted_data,
        "expected_fields": expected_fields
    })
    print(f"   Result: {result['content'][0]['text']}\n")
    
    # Test pattern storage
    print("5. Testing store_iteration_result...")
    result = await store_iteration_result({
        "iteration": 1,
        "strategies_tried": ["strategy1", "strategy2"],
        "best_strategy": {"selectors": {"product_name": "h1"}},
        "success_rate": 0.85,
        "metrics": {"completeness": 0.9, "quality": 0.8}
    })
    print(f"   Result: {result['content'][0]['text']}\n")
    
    # Test get previous iterations
    print("6. Testing get_previous_iterations...")
    result = await get_previous_iterations({})
    print(f"   Result: {result['content'][0]['text'][:200]}...\n")
    
    print("All tests completed!")


if __name__ == "__main__":
    asyncio.run(test_tools())

