#!/usr/bin/env python3
"""
Analyze Pattern Distribution - Calculate what percentage of all possible
timestamps are considered "interesting" based on our pattern criteria.
"""
from datetime import datetime, timedelta
from time_pattern_detector import is_interesting_time, detect_patterns
from collections import Counter


def analyze_all_timestamps():
    """
    Analyze all 86,400 possible timestamps in a day (24h * 60m * 60s)
    to determine what percentage are "interesting"
    """
    print("=" * 70)
    print("PATTERN DISTRIBUTION ANALYSIS")
    print("=" * 70)
    print("\nAnalyzing all 86,400 possible timestamps in a 24-hour period...\n")

    # Start at midnight
    start = datetime(2025, 12, 23, 0, 0, 0)

    interesting_count = 0
    boring_count = 0
    pattern_counter = Counter()
    interesting_times = []

    # Check every second in a 24-hour period
    for second in range(86400):  # 24 * 60 * 60 = 86,400 seconds
        current_time = start + timedelta(seconds=second)
        is_interesting, patterns = is_interesting_time(current_time)

        if is_interesting:
            interesting_count += 1
            interesting_times.append((current_time, patterns))
            # Count each pattern occurrence
            for pattern in patterns:
                pattern_counter[pattern] += 1
        else:
            boring_count += 1

    # Calculate percentages
    total = interesting_count + boring_count
    interesting_pct = (interesting_count / total) * 100
    boring_pct = (boring_count / total) * 100

    # Display results
    print("=" * 70)
    print("OVERALL DISTRIBUTION")
    print("=" * 70)
    print(f"Total possible timestamps: {total:,}")
    print(f"Interesting timestamps: {interesting_count:,} ({interesting_pct:.2f}%)")
    print(f"Boring timestamps: {boring_count:,} ({boring_pct:.2f}%)")

    print("\n" + "=" * 70)
    print("PATTERN FREQUENCY")
    print("=" * 70)
    print(f"{'Pattern':<30} {'Count':>10} {'% of Day':>12} {'% of Interesting':>18}")
    print("-" * 70)

    for pattern, count in pattern_counter.most_common():
        pct_of_day = (count / total) * 100
        pct_of_interesting = (count / interesting_count) * 100 if interesting_count > 0 else 0
        print(f"{pattern:<30} {count:>10,} {pct_of_day:>11.3f}% {pct_of_interesting:>17.2f}%")

    # Show some example interesting times
    print("\n" + "=" * 70)
    print("SAMPLE INTERESTING TIMES (first 20)")
    print("=" * 70)
    for i, (time, patterns) in enumerate(interesting_times[:20]):
        time_str = time.strftime("%H:%M:%S")
        pattern_str = ", ".join(patterns[:3])  # Show first 3 patterns
        if len(patterns) > 3:
            pattern_str += f" (+{len(patterns)-3} more)"
        print(f"{time_str} - {pattern_str}")

    # Analysis by hour
    print("\n" + "=" * 70)
    print("INTERESTING TIMESTAMPS BY HOUR")
    print("=" * 70)
    print(f"{'Hour':<8} {'Interesting':>12} {'% of Hour':>12}")
    print("-" * 70)

    hour_stats = {}
    for second in range(86400):
        current_time = start + timedelta(seconds=second)
        hour = current_time.hour
        is_interesting, _ = is_interesting_time(current_time)

        if hour not in hour_stats:
            hour_stats[hour] = {'interesting': 0, 'total': 0}

        hour_stats[hour]['total'] += 1
        if is_interesting:
            hour_stats[hour]['interesting'] += 1

    for hour in range(24):
        stats = hour_stats[hour]
        pct = (stats['interesting'] / stats['total']) * 100
        hour_str = f"{hour:02d}:XX:XX"
        print(f"{hour_str:<8} {stats['interesting']:>12,} {pct:>11.2f}%")

    # Statistical summary
    print("\n" + "=" * 70)
    print("STATISTICAL SUMMARY")
    print("=" * 70)

    # Calculate how many patterns each timestamp has on average
    pattern_counts = [len(patterns) for _, patterns in interesting_times]
    avg_patterns = sum(pattern_counts) / len(pattern_counts) if pattern_counts else 0
    max_patterns = max(pattern_counts) if pattern_counts else 0

    print(f"Average patterns per interesting timestamp: {avg_patterns:.2f}")
    print(f"Maximum patterns in a single timestamp: {max_patterns}")

    # Find timestamps with most patterns
    most_patterns = sorted(interesting_times, key=lambda x: len(x[1]), reverse=True)[:5]
    print(f"\nTop 5 timestamps with most patterns:")
    for time, patterns in most_patterns:
        time_str = time.strftime("%H:%M:%S")
        print(f"  {time_str} - {len(patterns)} patterns: {', '.join(patterns)}")

    print("\n" + "=" * 70)
    print("INTERPRETATION")
    print("=" * 70)
    print(f"\n✓ {interesting_pct:.2f}% of all timestamps are 'interesting'")
    print(f"✓ This means roughly 1 in {int(100/interesting_pct)} timestamps is interesting")
    print(f"✓ On average, you'll encounter an interesting time every {int(86400/interesting_count)} seconds")
    print(f"  (approximately every {int(86400/interesting_count/60)} minutes)")

    if interesting_pct < 10:
        print(f"\n💡 INSIGHT: Interesting times are RARE (< 10%)")
        print("   This makes them good candidates for testing correlation!")
        print("   If they predict success, it's likely NOT random chance.")
    elif interesting_pct < 30:
        print(f"\n💡 INSIGHT: Interesting times are UNCOMMON (10-30%)")
        print("   There's a reasonable balance for statistical testing.")
    else:
        print(f"\n💡 INSIGHT: Interesting times are COMMON (> 30%)")
        print("   May need to tighten criteria for better signal/noise ratio.")

    print("\n" + "=" * 70)

    return {
        'total': total,
        'interesting': interesting_count,
        'boring': boring_count,
        'interesting_pct': interesting_pct,
        'boring_pct': boring_pct,
        'pattern_counts': pattern_counter
    }


if __name__ == "__main__":
    stats = analyze_all_timestamps()
