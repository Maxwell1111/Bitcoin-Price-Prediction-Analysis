#!/usr/bin/env python3
"""
Time Pattern Detector - Analyzes time for interesting numerical patterns
"""
from datetime import datetime
from typing import Dict, List, Tuple


def is_prime(n: int) -> bool:
    """Check if a number is prime"""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return False
    return True


def detect_patterns(timestamp: datetime) -> Dict[str, bool]:
    """
    Detect interesting patterns in a timestamp

    Args:
        timestamp: datetime object to analyze

    Returns:
        Dictionary of pattern names and whether they were detected
    """
    # Get time components
    hour = timestamp.hour
    minute = timestamp.minute
    second = timestamp.second

    # Get all digits
    time_str = f"{hour:02d}{minute:02d}{second:02d}"
    digits = [int(d) for d in time_str]

    patterns = {}

    # 1. Repeating digits (all same)
    patterns['all_same_digits'] = len(set(digits)) == 1

    # 2. Repeating pairs (22:22:22, 11:11:11)
    patterns['repeating_pairs'] = (
        hour // 10 == hour % 10 and
        minute // 10 == minute % 10 and
        second // 10 == second % 10 and
        hour == minute == second
    )

    # 3. Hour:Minute match (12:12:XX, 23:23:XX)
    patterns['hour_minute_match'] = hour == minute

    # 4. Mirror time (12:21:XX, 13:31:XX)
    hour_str = f"{hour:02d}"
    minute_str = f"{minute:02d}"
    patterns['mirror_hour_minute'] = hour_str == minute_str[::-1]

    # 5. Sequential ascending (12:34:XX, 01:23:XX)
    hour_digits = [int(d) for d in f"{hour:02d}"]
    minute_digits = [int(d) for d in f"{minute:02d}"]
    time_digits = hour_digits + minute_digits
    is_sequential = all(time_digits[i] + 1 == time_digits[i+1] for i in range(len(time_digits)-1))
    patterns['sequential_ascending'] = is_sequential

    # 6. Sequential descending (43:21:XX, 32:10:XX)
    is_descending = all(time_digits[i] - 1 == time_digits[i+1] for i in range(len(time_digits)-1))
    patterns['sequential_descending'] = is_descending

    # 7. Sum of all digits is prime (REMOVED - too common)
    # digit_sum = sum(digits)
    # patterns['sum_is_prime'] = is_prime(digit_sum)

    # 8. Palindrome (reads same forwards and backwards)
    patterns['palindrome'] = time_str == time_str[::-1]

    # 9. All even digits
    patterns['all_even'] = all(d % 2 == 0 for d in digits if d != 0)

    # 10. All odd digits
    patterns['all_odd'] = all(d % 2 == 1 for d in digits)

    # 11. Alternating even/odd
    patterns['alternating_even_odd'] = all(
        (digits[i] % 2) != (digits[i+1] % 2)
        for i in range(len(digits)-1)
    )

    # 12. Repeating pattern (12:12:12, 23:23:23)
    patterns['repeating_pattern'] = (
        f"{hour:02d}" == f"{minute:02d}" == f"{second:02d}"
    )

    return patterns


def is_interesting_time(timestamp: datetime) -> Tuple[bool, List[str]]:
    """
    Check if timestamp has any interesting patterns

    Returns:
        Tuple of (is_interesting: bool, detected_patterns: List[str])
    """
    patterns = detect_patterns(timestamp)

    # Get list of detected patterns
    detected = [name for name, is_present in patterns.items() if is_present]

    # Time is interesting if ANY pattern is detected
    is_interesting = len(detected) > 0

    return is_interesting, detected


def format_time_analysis(timestamp: datetime) -> str:
    """Format a human-readable analysis of the timestamp"""
    is_interesting, patterns = is_interesting_time(timestamp)

    time_str = timestamp.strftime("%H:%M:%S")

    if is_interesting:
        pattern_list = ", ".join(patterns)
        return f"⭐ {time_str} - INTERESTING! Patterns: {pattern_list}"
    else:
        return f"➖ {time_str} - No special patterns detected"


if __name__ == "__main__":
    # Test with some interesting times
    test_times = [
        datetime(2025, 12, 23, 22, 22, 22),  # Repeating
        datetime(2025, 12, 23, 12, 21, 0),   # Mirror
        datetime(2025, 12, 23, 12, 34, 0),   # Sequential
        datetime(2025, 12, 23, 13, 37, 0),   # Prime sum
        datetime(2025, 12, 23, 15, 47, 0),   # Regular time
    ]

    print("Testing Time Pattern Detector:")
    print("=" * 60)

    for test_time in test_times:
        print(format_time_analysis(test_time))
        patterns = detect_patterns(test_time)
        for name, detected in patterns.items():
            if detected:
                print(f"  ✓ {name}")
        print()
