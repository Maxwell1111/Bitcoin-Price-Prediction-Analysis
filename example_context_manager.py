#!/usr/bin/env python3
"""
Example: Using context manager for automatic logging

This shows how to use the 'with' statement to automatically
log bug fix attempts and their outcomes.
"""
from auto_logger import AutoLogger


def example_successful_fix():
    """Example of a successful bug fix"""
    with AutoLogger("Fix API timeout issue"):
        # Your bug fix code here
        print("Debugging API timeout...")
        print("Found issue: connection pool not closed")
        print("Applying fix: added connection.close()")
        print("Testing fix...")
        print("✓ Fix verified!")
        # If code reaches end without exception = SUCCESS


def example_failed_fix():
    """Example of a failed bug fix attempt"""
    try:
        with AutoLogger("Fix database connection bug"):
            # Your bug fix code here
            print("Attempting to fix database connection...")
            print("Trying solution 1...")
            # Simulate a failure
            raise Exception("Solution didn't work, need to try different approach")
    except Exception as e:
        print(f"Need to try again: {e}")


def example_manual_control():
    """Example with manual success/failure control"""
    with AutoLogger("Fix authentication flow") as logger:
        print("Testing authentication...")
        print("Checking user credentials...")

        # Manually decide success/failure
        test_passed = True  # Your test result here

        if test_passed:
            logger.mark_success()
            print("✓ Authentication working!")
        else:
            logger.mark_failure()
            print("✗ Still broken, need more work")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Successful fix (no exception)")
    print("=" * 60)
    example_successful_fix()

    print("\n\n" + "=" * 60)
    print("EXAMPLE 2: Failed fix (exception raised)")
    print("=" * 60)
    example_failed_fix()

    print("\n\n" + "=" * 60)
    print("EXAMPLE 3: Manual control")
    print("=" * 60)
    example_manual_control()

    print("\n\n" + "=" * 60)
    print("✅ All examples completed!")
    print("Check bug_fix_data.json to see the logged attempts")
    print("=" * 60)
