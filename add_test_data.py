#!/usr/bin/env python3
"""
Add Test Data - Populate the tracker with sample bug fix attempts
This helps test the statistics and visualization features
"""
from datetime import datetime
from bug_fix_tracker import BugFixTracker


def add_sample_data():
    """Add realistic sample data to test the system"""
    tracker = BugFixTracker()

    print("Adding sample bug fix attempts...")
    print("=" * 60)

    # Sample data: (timestamp, successful, description)
    # Mix of interesting and boring times with various outcomes
    test_data = [
        # Interesting times with SUCCESS
        (datetime(2025, 12, 23, 22, 22, 22), True, "Fixed authentication bug - repeating 2s!"),
        (datetime(2025, 12, 23, 12, 12, 12), True, "Resolved API timeout - repeating pattern"),
        (datetime(2025, 12, 23, 12, 21, 0), True, "Fixed database connection - mirror time"),
        (datetime(2025, 12, 23, 13, 31, 0), True, "Resolved memory leak - mirror pattern"),
        (datetime(2025, 12, 23, 12, 34, 56), True, "Fixed CSS rendering - sequential!"),
        (datetime(2025, 12, 23, 23, 32, 0), True, "Resolved race condition - palindrome"),

        # Interesting times with FAILURE
        (datetime(2025, 12, 23, 11, 11, 11), False, "Tried to fix caching issue - repeating 1s"),
        (datetime(2025, 12, 23, 10, 1, 0), False, "Attempted deploy fix - palindrome time"),

        # Boring times with SUCCESS
        (datetime(2025, 12, 23, 15, 47, 23), True, "Fixed typo in config"),
        (datetime(2025, 12, 23, 9, 18, 44), True, "Resolved import error"),
        (datetime(2025, 12, 23, 16, 29, 51), True, "Fixed validation bug"),

        # Boring times with FAILURE
        (datetime(2025, 12, 23, 14, 37, 19), False, "Tried to fix async issue"),
        (datetime(2025, 12, 23, 10, 43, 7), False, "Attempted to resolve CORS"),
        (datetime(2025, 12, 23, 17, 52, 33), False, "Tried fixing performance issue"),
        (datetime(2025, 12, 23, 8, 26, 41), False, "Attempted database migration fix"),
        (datetime(2025, 12, 23, 19, 15, 8), False, "Tried to fix websocket connection"),
    ]

    for timestamp, success, description in test_data:
        attempt = tracker.add_attempt(
            successful=success,
            description=description,
            timestamp=timestamp
        )

        # Display what was added
        status_icon = "✅" if success else "❌"
        time_str = timestamp.strftime("%H:%M:%S")
        interesting_marker = "⭐" if attempt.is_interesting else "  "
        patterns = f" ({', '.join(attempt.pattern_names)})" if attempt.pattern_names else ""

        print(f"{interesting_marker} {time_str} {status_icon} {description[:40]}{patterns}")

    print("\n" + "=" * 60)
    print("Sample data added successfully!")
    print("=" * 60)

    # Display statistics
    stats = tracker.get_statistics()
    print(f"\nTotal Attempts: {stats['total_attempts']}")
    print(f"Overall Success Rate: {stats['overall_success_rate']:.1f}%")
    print(f"\nInteresting Time Success Rate: {stats['interesting_time_success_rate']:.1f}%")
    print(f"Boring Time Success Rate: {stats['boring_time_success_rate']:.1f}%")

    # Show hypothesis
    if stats['interesting_time_success_rate'] > stats['boring_time_success_rate']:
        print(f"\n🎯 HYPOTHESIS SUPPORTED! Interesting times have {stats['interesting_time_success_rate'] - stats['boring_time_success_rate']:.1f}% higher success rate!")
    elif stats['boring_time_success_rate'] > stats['interesting_time_success_rate']:
        print(f"\n❌ HYPOTHESIS REJECTED! Boring times have {stats['boring_time_success_rate'] - stats['interesting_time_success_rate']:.1f}% higher success rate!")
    else:
        print("\n➖ No correlation detected yet - need more data!")

    print("\n💡 Now refresh the GUI to see updated statistics and charts!")


if __name__ == "__main__":
    add_sample_data()
