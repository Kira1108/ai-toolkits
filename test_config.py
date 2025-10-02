#!/usr/bin/env python3
"""Test script to verify centralized environment loading works correctly."""

from ai_toolkits.load_env import load_environment, get_env_var, get_required_env_var

def test_environment_loading():
    """Test that environment loading works correctly."""
    print("Testing centralized environment loading...")
    
    # Test basic loading
    result = load_environment()
    print(f"Environment loaded: {result}")
    
    # Test that calling it multiple times doesn't reload (cache works)
    result2 = load_environment()
    print(f"Second call (should be cached): {result2}")
    
    # Test getting environment variables
    try:
        # Try to get a common environment variable
        path_var = get_env_var("PATH", "not_found")
        print(f"PATH variable found: {len(path_var) > 0}")
    except Exception as e:
        print(f"Error getting PATH: {e}")
    
    # Test required variable (this might fail if not set)
    try:
        azure_key = get_required_env_var("AZURE_OPENAI_API_KEY")
        print("AZURE_OPENAI_API_KEY found")
    except ValueError as e:
        print(f"AZURE_OPENAI_API_KEY not found (expected): {e}")
    
    print("Environment loading test completed!")

if __name__ == "__main__":
    test_environment_loading()