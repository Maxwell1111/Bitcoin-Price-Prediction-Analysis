#!/usr/bin/env python3
"""
Bug Fix Tracker - Core data management for tracking bug fix attempts
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from time_pattern_detector import detect_patterns, is_interesting_time


class BugFixAttempt:
    """Represents a single bug fix attempt"""

    def __init__(
        self,
        timestamp: datetime,
        successful: bool,
        description: str = "",
        attempt_id: Optional[str] = None
    ):
        self.timestamp = timestamp
        self.successful = successful
        self.description = description
        self.attempt_id = attempt_id or datetime.now().strftime("%Y%m%d_%H%M%S")

        # Detect patterns at time of attempt
        self.patterns = detect_patterns(timestamp)
        self.is_interesting, self.pattern_names = is_interesting_time(timestamp)

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON storage"""
        return {
            'attempt_id': self.attempt_id,
            'timestamp': self.timestamp.isoformat(),
            'successful': self.successful,
            'description': self.description,
            'patterns': self.patterns,
            'is_interesting': self.is_interesting,
            'pattern_names': self.pattern_names
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'BugFixAttempt':
        """Create from dictionary"""
        timestamp = datetime.fromisoformat(data['timestamp'])
        attempt = cls(
            timestamp=timestamp,
            successful=data['successful'],
            description=data.get('description', ''),
            attempt_id=data.get('attempt_id')
        )
        # Restore saved pattern data
        attempt.patterns = data.get('patterns', {})
        attempt.is_interesting = data.get('is_interesting', False)
        attempt.pattern_names = data.get('pattern_names', [])
        return attempt


class BugFixTracker:
    """Main tracker for all bug fix attempts"""

    def __init__(self, data_file: str = "bug_fix_data.json"):
        self.data_file = data_file
        self.attempts: List[BugFixAttempt] = []
        self.load_data()

    def load_data(self):
        """Load existing data from file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.attempts = [
                        BugFixAttempt.from_dict(attempt_data)
                        for attempt_data in data.get('attempts', [])
                    ]
                print(f"✓ Loaded {len(self.attempts)} previous attempts")
            except Exception as e:
                print(f"! Error loading data: {e}")
                self.attempts = []
        else:
            print("! No previous data found, starting fresh")
            self.attempts = []

    def save_data(self):
        """Save data to file"""
        try:
            data = {
                'attempts': [attempt.to_dict() for attempt in self.attempts],
                'last_updated': datetime.now().isoformat()
            }
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"✓ Saved {len(self.attempts)} attempts")
        except Exception as e:
            print(f"! Error saving data: {e}")

    def add_attempt(
        self,
        successful: bool,
        description: str = "",
        timestamp: Optional[datetime] = None
    ) -> BugFixAttempt:
        """Add a new bug fix attempt"""
        if timestamp is None:
            timestamp = datetime.now()

        attempt = BugFixAttempt(
            timestamp=timestamp,
            successful=successful,
            description=description
        )

        self.attempts.append(attempt)
        self.save_data()

        return attempt

    def get_statistics(self) -> Dict:
        """Calculate statistics across all attempts"""
        if not self.attempts:
            return {
                'total_attempts': 0,
                'successful_attempts': 0,
                'failed_attempts': 0,
                'overall_success_rate': 0.0,
                'interesting_time_attempts': 0,
                'boring_time_attempts': 0,
                'interesting_time_success_rate': 0.0,
                'boring_time_success_rate': 0.0
            }

        total = len(self.attempts)
        successful = sum(1 for a in self.attempts if a.successful)
        failed = total - successful

        interesting = [a for a in self.attempts if a.is_interesting]
        boring = [a for a in self.attempts if not a.is_interesting]

        interesting_successful = sum(1 for a in interesting if a.successful)
        boring_successful = sum(1 for a in boring if a.successful)

        stats = {
            'total_attempts': total,
            'successful_attempts': successful,
            'failed_attempts': failed,
            'overall_success_rate': (successful / total * 100) if total > 0 else 0,

            'interesting_time_attempts': len(interesting),
            'boring_time_attempts': len(boring),

            'interesting_time_success_rate': (
                (interesting_successful / len(interesting) * 100)
                if len(interesting) > 0 else 0
            ),
            'boring_time_success_rate': (
                (boring_successful / len(boring) * 100)
                if len(boring) > 0 else 0
            )
        }

        # Pattern-specific stats
        pattern_stats = {}
        all_pattern_types = set()
        for attempt in self.attempts:
            all_pattern_types.update(attempt.pattern_names)

        for pattern_name in all_pattern_types:
            pattern_attempts = [
                a for a in self.attempts
                if pattern_name in a.pattern_names
            ]
            pattern_successful = sum(1 for a in pattern_attempts if a.successful)

            pattern_stats[pattern_name] = {
                'total': len(pattern_attempts),
                'successful': pattern_successful,
                'success_rate': (
                    (pattern_successful / len(pattern_attempts) * 100)
                    if len(pattern_attempts) > 0 else 0
                )
            }

        stats['pattern_stats'] = pattern_stats

        return stats

    def get_recent_attempts(self, limit: int = 10) -> List[BugFixAttempt]:
        """Get most recent attempts"""
        return sorted(self.attempts, key=lambda a: a.timestamp, reverse=True)[:limit]


if __name__ == "__main__":
    # Test the tracker
    print("Testing Bug Fix Tracker")
    print("=" * 60)

    tracker = BugFixTracker()

    # Add some test attempts
    test_attempts = [
        (datetime(2025, 12, 23, 22, 22, 22), True, "Fixed API endpoint"),
        (datetime(2025, 12, 23, 15, 47, 0), False, "Database connection issue"),
        (datetime(2025, 12, 23, 12, 12, 12), True, "Fixed authentication bug"),
        (datetime(2025, 12, 23, 16, 30, 0), True, "Resolved memory leak"),
    ]

    for timestamp, success, desc in test_attempts:
        attempt = tracker.add_attempt(
            successful=success,
            description=desc,
            timestamp=timestamp
        )
        pattern_info = f" ({', '.join(attempt.pattern_names)})" if attempt.pattern_names else ""
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{timestamp.strftime('%H:%M:%S')} - {status}{pattern_info}")

    print("\n" + "=" * 60)
    print("STATISTICS:")
    print("=" * 60)

    stats = tracker.get_statistics()
    print(f"\nTotal Attempts: {stats['total_attempts']}")
    print(f"Success Rate: {stats['overall_success_rate']:.1f}%")
    print(f"\nInteresting Time Success Rate: {stats['interesting_time_success_rate']:.1f}%")
    print(f"Boring Time Success Rate: {stats['boring_time_success_rate']:.1f}%")
