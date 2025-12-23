#!/usr/bin/env python3
"""
Auto Logger - Automatically detect and log bug fix attempts
Provides a simple interface to wrap around bug fix workflows
"""
from datetime import datetime
from bug_fix_tracker import BugFixTracker
from time_pattern_detector import is_interesting_time, format_time_analysis
import sys


class AutoLogger:
    """Context manager for automatic bug fix logging"""

    def __init__(self, description: str = "Bug fix attempt"):
        self.description = description
        self.tracker = BugFixTracker()
        self.start_time = None
        self.success = False

    def __enter__(self):
        """Called when entering the 'with' block"""
        self.start_time = datetime.now()
        print("\n" + "=" * 60)
        print("🐛 BUG FIX ATTEMPT STARTED")
        print("=" * 60)
        print(format_time_analysis(self.start_time))
        print(f"Description: {self.description}")
        print("=" * 60 + "\n")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Called when exiting the 'with' block"""
        # If no exception, consider it a success
        self.success = exc_type is None

        # Log the attempt
        attempt = self.tracker.add_attempt(
            successful=self.success,
            description=self.description,
            timestamp=self.start_time
        )

        # Display result
        print("\n" + "=" * 60)
        if self.success:
            print("✅ BUG FIX SUCCESSFUL!")
        else:
            print("❌ BUG FIX FAILED!")
        print("=" * 60)
        print(format_time_analysis(self.start_time))
        print(f"Description: {self.description}")

        if attempt.pattern_names:
            print(f"Patterns detected: {', '.join(attempt.pattern_names)}")

        print("=" * 60 + "\n")

        # Display quick stats
        stats = self.tracker.get_statistics()
        print(f"Session Stats:")
        print(f"  Total attempts: {stats['total_attempts']}")
        print(f"  Overall success rate: {stats['overall_success_rate']:.1f}%")
        print(f"  Interesting time success rate: {stats['interesting_time_success_rate']:.1f}%")
        print(f"  Boring time success rate: {stats['boring_time_success_rate']:.1f}%")

        if stats['interesting_time_success_rate'] > stats['boring_time_success_rate']:
            diff = stats['interesting_time_success_rate'] - stats['boring_time_success_rate']
            print(f"\n  🎯 Interesting times are {diff:.1f}% more successful!")
        elif stats['boring_time_success_rate'] > stats['interesting_time_success_rate']:
            diff = stats['boring_time_success_rate'] - stats['interesting_time_success_rate']
            print(f"\n  📉 Boring times are {diff:.1f}% more successful!")

        print()

        # Don't suppress exceptions
        return False

    def mark_success(self):
        """Manually mark as success (useful for manual tracking)"""
        self.success = True

    def mark_failure(self):
        """Manually mark as failure (useful for manual tracking)"""
        self.success = False


def log_bug_fix(description: str = "Bug fix attempt"):
    """
    Decorator to automatically log bug fix functions

    Usage:
        @log_bug_fix("Fix authentication timeout")
        def fix_auth_bug():
            # Your fix code here
            pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            with AutoLogger(description) as logger:
                try:
                    result = func(*args, **kwargs)
                    logger.mark_success()
                    return result
                except Exception as e:
                    logger.mark_failure()
                    raise
        return wrapper
    return decorator


def interactive_logger():
    """Interactive command-line logger for quick logging"""
    tracker = BugFixTracker()

    print("\n" + "=" * 60)
    print("🐛 BUG FIX TRACKER - Interactive Mode")
    print("=" * 60)

    # Show current time and patterns
    now = datetime.now()
    print(f"\n{format_time_analysis(now)}\n")

    # Get description
    description = input("📝 Enter bug description (or press Enter to skip): ").strip()
    if not description:
        description = "Bug fix attempt"

    print(f"\n💡 Working on: {description}")
    print("When done, come back here to log the result...\n")

    input("Press Enter when you're ready to log the result...")

    # Get result
    print("\nWas the bug fixed successfully?")
    print("  1. ✅ Success (fixed on first attempt)")
    print("  2. ❌ Failure (needed multiple attempts or didn't work)")

    while True:
        choice = input("\nYour choice (1 or 2): ").strip()
        if choice in ["1", "2"]:
            break
        print("Invalid choice. Please enter 1 or 2.")

    successful = choice == "1"

    # Log it
    attempt = tracker.add_attempt(
        successful=successful,
        description=description
    )

    # Show result
    print("\n" + "=" * 60)
    if successful:
        print("✅ SUCCESS LOGGED!")
    else:
        print("❌ FAILURE LOGGED!")
    print("=" * 60)
    print(format_time_analysis(attempt.timestamp))
    print(f"Description: {description}")

    if attempt.pattern_names:
        print(f"Patterns: {', '.join(attempt.pattern_names)}")

    # Show stats
    stats = tracker.get_statistics()
    print("\n" + "=" * 60)
    print("CURRENT STATISTICS:")
    print("=" * 60)
    print(f"Total attempts: {stats['total_attempts']}")
    print(f"Overall success rate: {stats['overall_success_rate']:.1f}%")
    print(f"\nInteresting time attempts: {stats['interesting_time_attempts']}")
    print(f"  → Success rate: {stats['interesting_time_success_rate']:.1f}%")
    print(f"\nBoring time attempts: {stats['boring_time_attempts']}")
    print(f"  → Success rate: {stats['boring_time_success_rate']:.1f}%")

    if stats['interesting_time_success_rate'] > stats['boring_time_success_rate']:
        diff = stats['interesting_time_success_rate'] - stats['boring_time_success_rate']
        print(f"\n🎯 HYPOTHESIS SUPPORTED! Interesting times are {diff:.1f}% more successful!")
    elif stats['boring_time_success_rate'] > stats['interesting_time_success_rate']:
        diff = stats['boring_time_success_rate'] - stats['interesting_time_success_rate']
        print(f"\n❌ HYPOTHESIS REJECTED! Boring times are {diff:.1f}% more successful!")
    else:
        print("\n➖ No correlation detected yet")

    print("=" * 60 + "\n")


if __name__ == "__main__":
    # Run interactive mode
    interactive_logger()
