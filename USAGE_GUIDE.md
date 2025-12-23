# Usage Guide - Bug Fix vs Time Theory Tracker

Complete guide for using the automatic logging features.

## Quick Start Options

You have **4 ways** to track bug fixes:

### 1. 🖥️ GUI Application (Best for Visual Tracking)

**When to use**: You want to manually log attempts with real-time pattern visualization

```bash
python3 gui_app.py
```

- See current time and patterns updating every second
- Click buttons to log success/failure
- View charts and statistics in real-time
- Best for: Active tracking during work sessions

---

### 2. 💬 Interactive CLI (Best for Quick Logging)

**When to use**: You want to quickly log a single bug fix attempt

```bash
python3 auto_logger.py
```

**Interactive prompts:**
1. Shows current time and detected patterns
2. Enter bug description
3. Work on the fix
4. Come back and mark success/failure
5. See updated statistics

**Example session:**
```
🐛 BUG FIX TRACKER - Interactive Mode
============================================================

⭐ 22:22:22 - INTERESTING! Patterns: all_same_digits, repeating_pairs, ...

📝 Enter bug description: Fix login timeout

💡 Working on: Fix login timeout
When done, come back here to log the result...

Press Enter when you're ready to log the result...

Was the bug fixed successfully?
  1. ✅ Success (fixed on first attempt)
  2. ❌ Failure (needed multiple attempts or didn't work)

Your choice (1 or 2): 1

✅ SUCCESS LOGGED!
```

---

### 3. 🔧 Context Manager (Best for Programmatic Tracking)

**When to use**: You're writing scripts and want automatic success/failure detection

```python
from auto_logger import AutoLogger

# Automatic detection - success if no exception
with AutoLogger("Fix database connection"):
    # Your fix code here
    connection = fix_database_issue()
    test_connection(connection)
    # Automatically logged as SUCCESS if no exception

# Manual control - you decide success/failure
with AutoLogger("Fix API endpoint") as logger:
    result = test_api_fix()

    if result.status == 200:
        logger.mark_success()
    else:
        logger.mark_failure()
```

**Run example:**
```bash
python3 example_context_manager.py
```

**Output shows:**
- Start time with pattern analysis
- Your code execution
- End result (success/failure)
- Updated statistics

---

### 4. 🎯 Decorator (Best for Function-Based Fixes)

**When to use**: You have discrete functions for each bug fix

```python
from auto_logger import log_bug_fix

@log_bug_fix("Fix CSS layout issue")
def fix_css_layout():
    # Your fix code here
    apply_flexbox_fix()
    # Automatically SUCCESS if function completes
    # Automatically FAILURE if exception raised

# Use it
fix_css_layout()  # Automatically logged!
```

**Run example:**
```bash
python3 example_decorator.py
```

**Advantages:**
- Clean, minimal code
- Automatic exception handling
- No manual logging needed

---

## Choosing the Right Method

| Method | Best For | Automatic? | Code Required |
|--------|----------|------------|---------------|
| **GUI** | Visual tracking, exploration | Manual | None |
| **Interactive CLI** | Quick one-off logging | Semi-auto | None |
| **Context Manager** | Scripts, custom logic | Auto | Minimal |
| **Decorator** | Function-based fixes | Auto | Minimal |

---

## Workflow Examples

### Scenario 1: Daily Development Work

**Best approach**: GUI Application

```bash
# Start your day
python3 gui_app.py

# Keep it open in background
# When you fix a bug:
#   1. Check current time for patterns
#   2. Enter description
#   3. Click success/failure after attempting fix
#   4. Watch statistics update
```

---

### Scenario 2: Batch Bug Fixing Session

**Best approach**: Context Manager in Script

```python
from auto_logger import AutoLogger

bugs_to_fix = [
    ("Fix auth timeout", fix_auth),
    ("Fix CSS layout", fix_css),
    ("Fix API endpoint", fix_api),
]

for description, fix_function in bugs_to_fix:
    with AutoLogger(description):
        fix_function()  # Auto-logged!
```

---

### Scenario 3: Testing a Single Complex Fix

**Best approach**: Interactive CLI

```bash
# Start the interactive logger
python3 auto_logger.py

# Shows time patterns
# Enter description: "Fix memory leak in user service"
# Press Enter
# Go work on the fix for 30 minutes
# Come back, press Enter
# Mark as success/failure
# See immediate statistics
```

---

### Scenario 4: Automated Testing Pipeline

**Best approach**: Decorator

```python
from auto_logger import log_bug_fix

@log_bug_fix("Fix test suite failure")
def fix_failing_tests():
    run_tests()
    fix_broken_test()
    verify_all_pass()

@log_bug_fix("Fix build error")
def fix_build():
    update_dependencies()
    rebuild_project()

# Run them
fix_failing_tests()
fix_build()

# Both automatically logged with timestamps!
```

---

## Understanding the Output

### Pattern Detection

When you start a fix attempt, you'll see:

```
⭐ 22:22:22 - INTERESTING! Patterns: all_same_digits, repeating_pairs, palindrome
```

or

```
➖ 15:47:23 - No special patterns detected
```

**Interesting patterns include:**
- All same digits (22:22:22)
- Repeating pairs (11:11:11)
- Mirror times (12:21:XX)
- Sequential (12:34:XX)
- Palindromes (12:34:21)
- Prime sums
- And 6 more...

### Statistics Display

After logging, you'll see:

```
Session Stats:
  Total attempts: 16
  Overall success rate: 56.2%
  Interesting time success rate: 75.0%
  Boring time success rate: 37.5%

  🎯 Interesting times are 37.5% more successful!
```

**Interpretation:**
- **Higher interesting rate** → Theory supported! ⭐
- **Higher boring rate** → Theory rejected ❌
- **Similar rates** → No correlation yet ➖

---

## Data Management

### Where Data is Stored

```
bug_fix_data.json
```

**Format:**
```json
{
  "attempts": [
    {
      "attempt_id": "20251223_222222",
      "timestamp": "2025-12-23T22:22:22",
      "successful": true,
      "description": "Fix authentication bug",
      "patterns": {
        "all_same_digits": true,
        "repeating_pairs": true
      },
      "is_interesting": true,
      "pattern_names": ["all_same_digits", "repeating_pairs"]
    }
  ],
  "last_updated": "2025-12-23T22:22:30"
}
```

### Backing Up Data

```bash
# Backup your data
cp bug_fix_data.json bug_fix_data_backup.json

# Restore from backup
cp bug_fix_data_backup.json bug_fix_data.json
```

### Starting Fresh

```bash
# Delete existing data
rm bug_fix_data.json

# Next run will start fresh
```

### Adding Test Data

```bash
# Populate with sample data
python3 add_test_data.py

# Adds 16 attempts with mix of interesting/boring and success/failure
```

---

## Advanced Usage

### Custom Pattern Detection

Edit `time_pattern_detector.py` to add your own patterns:

```python
def detect_patterns(timestamp: datetime) -> Dict[str, bool]:
    # ... existing patterns ...

    # Add your custom pattern
    patterns['custom_pattern'] = your_logic_here

    return patterns
```

### Filtering Statistics

```python
from bug_fix_tracker import BugFixTracker

tracker = BugFixTracker()

# Get all attempts
all_attempts = tracker.attempts

# Filter by success
successful = [a for a in all_attempts if a.successful]

# Filter by specific pattern
mirror_attempts = [
    a for a in all_attempts
    if 'mirror_hour_minute' in a.pattern_names
]

# Calculate custom stats
mirror_success_rate = sum(1 for a in mirror_attempts if a.successful) / len(mirror_attempts) * 100
```

### Exporting Data

```python
from bug_fix_tracker import BugFixTracker
import json

tracker = BugFixTracker()
stats = tracker.get_statistics()

# Export to JSON
with open('stats_export.json', 'w') as f:
    json.dump(stats, f, indent=2)

# Export attempts to CSV
import csv
with open('attempts_export.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Timestamp', 'Success', 'Interesting', 'Description', 'Patterns'])
    for attempt in tracker.attempts:
        writer.writerow([
            attempt.timestamp,
            attempt.successful,
            attempt.is_interesting,
            attempt.description,
            ', '.join(attempt.pattern_names)
        ])
```

---

## Tips for Best Results

### 1. Be Consistent

- Log **every** bug fix attempt, not just successes
- Use the same method throughout a session
- Don't skip "boring" times - they're important for comparison!

### 2. Clear Descriptions

Good: `"Fix authentication timeout on login page"`
Bad: `"Fixed stuff"`

### 3. Honest Success/Failure

- **Success** = Fixed on first attempt
- **Failure** = Needed multiple tries OR didn't work
- Don't inflate success rate - it ruins the data!

### 4. Collect Enough Data

- Minimum: 20-30 attempts for meaningful patterns
- Ideal: 50+ attempts for strong correlation
- Current sample: 16 attempts → 75% vs 37.5% difference

### 5. Review Periodically

```bash
# Check progress weekly
python3 gui_app.py
# Review charts and statistics
# Look for emerging patterns
```

---

## Troubleshooting

### GUI won't start

```bash
# Check if tkinter is installed
python3 -c "import tkinter"

# On macOS, make sure you have Python with tkinter
brew install python-tk
```

### Data not saving

```bash
# Check file permissions
ls -la bug_fix_data.json

# Check for errors in tracker
python3 -c "from bug_fix_tracker import BugFixTracker; BugFixTracker()"
```

### Charts not displaying

```bash
# Install matplotlib
pip3 install matplotlib

# Verify installation
python3 -c "import matplotlib; print(matplotlib.__version__)"
```

---

## Next Steps

1. **Start tracking**: Choose your preferred method
2. **Collect data**: Log at least 20-30 bug fixes
3. **Analyze results**: Watch for correlation patterns
4. **Optimize timing**: If theory holds, attempt important fixes at "interesting" times
5. **Share findings**: Compare with other developers!

---

**Remember**: The goal is to discover if time patterns actually correlate with success. Keep an open mind and let the data tell the story! 📊✨
