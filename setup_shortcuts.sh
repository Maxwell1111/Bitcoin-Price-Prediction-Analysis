#!/bin/bash
# Setup shortcuts for easy access to Bug Fix Tracker

PROJECT_DIR="/Users/aardeshiri/Design_ideas/Bug_fix_vs_time_theory"

echo "Setting up Bug Fix Tracker shortcuts..."
echo ""

# Add aliases to .zshrc
ZSHRC="$HOME/.zshrc"

# Check if aliases already exist
if grep -q "# Bug Fix Tracker shortcuts" "$ZSHRC" 2>/dev/null; then
    echo "⚠️  Shortcuts already exist in .zshrc"
else
    echo "Adding shortcuts to .zshrc..."
    cat >> "$ZSHRC" << 'EOF'

# Bug Fix Tracker shortcuts
alias bugfix-gui='cd ~/Design_ideas/Bug_fix_vs_time_theory && python3 gui_app.py'
alias bugfix-log='cd ~/Design_ideas/Bug_fix_vs_time_theory && python3 auto_logger.py'
alias bugfix-stats='cd ~/Design_ideas/Bug_fix_vs_time_theory && python3 -c "from bug_fix_tracker import BugFixTracker; s=BugFixTracker().get_statistics(); print(f\"Total: {s[\"total_attempts\"]} | Interesting: {s[\"interesting_time_success_rate\"]:.1f}% | Boring: {s[\"boring_time_success_rate\"]:.1f}%\")"'
alias bugfix-backup='cd ~/Design_ideas/Bug_fix_vs_time_theory && cp bug_fix_data.json "bug_fix_data_backup_$(date +%Y%m%d).json" && echo "✅ Backup created"'
alias bugfix-commit='cd ~/Design_ideas/Bug_fix_vs_time_theory && git add . && git commit -m "Data update: $(date +%Y-%m-%d)"'
alias bugfix-cd='cd ~/Design_ideas/Bug_fix_vs_time_theory'
EOF
    echo "✅ Shortcuts added to .zshrc"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "SHORTCUTS INSTALLED!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "After running 'source ~/.zshrc', you can use:"
echo ""
echo "  bugfix-gui       → Launch GUI app"
echo "  bugfix-log       → Quick CLI logging"
echo "  bugfix-stats     → Show current statistics"
echo "  bugfix-backup    → Create backup of data"
echo "  bugfix-commit    → Git commit with date"
echo "  bugfix-cd        → Navigate to project folder"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Run this now to activate:"
echo "  source ~/.zshrc"
echo ""
echo "Then try:"
echo "  bugfix-gui"
echo ""
