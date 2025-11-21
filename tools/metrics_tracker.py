"""
Metrics Tracker Tool - Custom MCP tool for tracking and calculating metrics
"""
from typing import Dict, Any, List
from claude_agent_sdk import tool


@tool(
    "calculate_completeness",
    "Calculate completeness percentage of extracted data based on expected fields.",
    {
        "extracted_data": {
            "type": "object",
            "description": "Dictionary of extracted data (field_name -> value)"
        },
        "expected_fields": {
            "type": "array",
            "description": "List of expected field names"
        }
    }
)
async def calculate_completeness(args: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate completeness percentage."""
    extracted_data = args.get("extracted_data", {})
    expected_fields = args.get("expected_fields", [])
    
    if not expected_fields:
        return {
            "content": [{
                "type": "text",
                "text": "Error: Expected fields list is required"
            }]
        }
    
    # Count how many fields were successfully extracted (not None and not empty)
    extracted_count = 0
    for field in expected_fields:
        value = extracted_data.get(field)
        if value is not None and value != "" and not str(value).startswith("Error:"):
            extracted_count += 1
    
    completeness = extracted_count / len(expected_fields) if expected_fields else 0.0
    
    return {
        "content": [{
            "type": "text",
            "text": f"Completeness: {extracted_count}/{len(expected_fields)} fields extracted ({completeness:.2%})"
        }]
    }


@tool(
    "calculate_quality_score",
    "Calculate a quality score for extracted data based on various factors.",
    {
        "extracted_data": {
            "type": "object",
            "description": "Dictionary of extracted data"
        },
        "expected_fields": {
            "type": "array",
            "description": "List of expected field names"
        }
    }
)
async def calculate_quality_score(args: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate quality score."""
    extracted_data = args.get("extracted_data", {})
    expected_fields = args.get("expected_fields", [])
    
    if not expected_fields:
        return {
            "content": [{
                "type": "text",
                "text": "Error: Expected fields list is required"
            }]
        }
    
    # Calculate completeness
    extracted_count = 0
    error_count = 0
    
    for field in expected_fields:
        value = extracted_data.get(field)
        if value is not None and value != "":
            if str(value).startswith("Error:"):
                error_count += 1
            else:
                extracted_count += 1
    
    total_fields = len(expected_fields)
    completeness = extracted_count / total_fields if total_fields > 0 else 0.0
    
    # Quality score: completeness weighted by error rate
    error_rate = error_count / total_fields if total_fields > 0 else 0.0
    quality_score = completeness * (1 - error_rate * 0.5)  # Penalize errors
    
    return {
        "content": [{
            "type": "text",
            "text": f"Quality Score: {quality_score:.3f} (Completeness: {completeness:.2%}, Errors: {error_count}/{total_fields})"
        }]
    }


@tool(
    "compare_iterations",
    "Compare metrics between two iterations to measure improvement.",
    {
        "iteration1_metrics": {
            "type": "object",
            "description": "Metrics from first iteration"
        },
        "iteration2_metrics": {
            "type": "object",
            "description": "Metrics from second iteration"
        }
    }
)
async def compare_iterations(args: Dict[str, Any]) -> Dict[str, Any]:
    """Compare metrics between iterations."""
    metrics1 = args.get("iteration1_metrics", {})
    metrics2 = args.get("iteration2_metrics", {})
    
    comparison = {}
    
    for key in set(list(metrics1.keys()) + list(metrics2.keys())):
        val1 = metrics1.get(key, 0)
        val2 = metrics2.get(key, 0)
        
        if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
            improvement = val2 - val1
            improvement_pct = (improvement / val1 * 100) if val1 != 0 else 0
            comparison[key] = {
                "iteration1": val1,
                "iteration2": val2,
                "improvement": improvement,
                "improvement_pct": improvement_pct
            }
    
    import json
    return {
        "content": [{
            "type": "text",
            "text": json.dumps(comparison, indent=2)
        }]
    }

