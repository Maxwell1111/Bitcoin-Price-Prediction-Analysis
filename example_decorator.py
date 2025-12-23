#!/usr/bin/env python3
"""
Example: Using decorator for automatic logging

This shows how to use the @log_bug_fix decorator to automatically
track function-based bug fixes.
"""
from auto_logger import log_bug_fix


@log_bug_fix("Fix CSS layout issue")
def fix_css_layout():
    """Example: Fix CSS layout problem"""
    print("Analyzing CSS...")
    print("Found issue: missing flexbox property")
    print("Adding display: flex to container")
    print("✓ Layout fixed!")
    return "Fixed"


@log_bug_fix("Fix database query performance")
def fix_slow_query():
    """Example: Optimize database query"""
    print("Profiling database query...")
    print("Adding index to user_id column")
    print("Query time reduced from 2s to 0.1s")
    print("✓ Performance improved!")
    return "Optimized"


@log_bug_fix("Fix broken API endpoint")
def fix_api_endpoint():
    """Example: Failed fix that raises exception"""
    print("Testing API endpoint...")
    print("Checking request validation...")
    # Simulate a fix that didn't work
    raise ValueError("API still returning 500 error - need different approach")


@log_bug_fix("Fix memory leak")
def fix_memory_leak():
    """Example: Another failed attempt"""
    print("Monitoring memory usage...")
    print("Attempting to close connections...")
    raise RuntimeError("Memory still growing - leak not found yet")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("DECORATOR EXAMPLES")
    print("=" * 60)

    print("\nExample 1: Successful CSS fix")
    print("-" * 60)
    result1 = fix_css_layout()
    print(f"Result: {result1}")

    print("\n\nExample 2: Successful query optimization")
    print("-" * 60)
    result2 = fix_slow_query()
    print(f"Result: {result2}")

    print("\n\nExample 3: Failed API fix")
    print("-" * 60)
    try:
        fix_api_endpoint()
    except ValueError as e:
        print(f"Caught exception: {e}")

    print("\n\nExample 4: Failed memory leak fix")
    print("-" * 60)
    try:
        fix_memory_leak()
    except RuntimeError as e:
        print(f"Caught exception: {e}")

    print("\n\n" + "=" * 60)
    print("✅ All decorator examples completed!")
    print("Check bug_fix_data.json to see the logged attempts")
    print("=" * 60)
