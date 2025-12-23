#!/usr/bin/env python3
"""
Bug Fix vs Time Theory - GUI Application
Simple interface for tracking and visualizing bug fix success patterns
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from bug_fix_tracker import BugFixTracker
import numpy as np


class BugFixApp:
    """Main GUI application"""

    def __init__(self, root):
        self.root = root
        self.root.title("Bug Fix vs Time Theory Tracker")
        self.root.geometry("1000x700")

        # Initialize tracker
        self.tracker = BugFixTracker()

        # Build UI
        self.build_ui()

        # Initial update
        self.refresh_stats()

    def build_ui(self):
        """Build the user interface"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # === SECTION 1: MANUAL ENTRY ===
        entry_frame = ttk.LabelFrame(main_frame, text="Log Bug Fix Attempt", padding="10")
        entry_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # Current time display
        self.current_time_label = ttk.Label(
            entry_frame,
            text="Current Time: --:--:--",
            font=("Arial", 16, "bold")
        )
        self.current_time_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))

        # Pattern detection display
        self.pattern_label = ttk.Label(
            entry_frame,
            text="Patterns: None detected",
            font=("Arial", 10)
        )
        self.pattern_label.grid(row=1, column=0, columnspan=3, pady=(0, 10))

        # Description entry
        ttk.Label(entry_frame, text="Description:").grid(row=2, column=0, sticky=tk.W)
        self.description_entry = ttk.Entry(entry_frame, width=40)
        self.description_entry.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Buttons
        success_btn = ttk.Button(
            entry_frame,
            text="✅ Log Success",
            command=lambda: self.log_attempt(True)
        )
        success_btn.grid(row=3, column=0, padx=5, pady=5)

        fail_btn = ttk.Button(
            entry_frame,
            text="❌ Log Failure",
            command=lambda: self.log_attempt(False)
        )
        fail_btn.grid(row=3, column=1, padx=5, pady=5)

        refresh_btn = ttk.Button(
            entry_frame,
            text="🔄 Refresh",
            command=self.refresh_stats
        )
        refresh_btn.grid(row=3, column=2, padx=5, pady=5)

        # === SECTION 2: STATISTICS ===
        stats_frame = ttk.LabelFrame(main_frame, text="Statistics", padding="10")
        stats_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # Stats labels
        self.stats_text = tk.Text(stats_frame, height=8, width=80, wrap=tk.WORD)
        self.stats_text.grid(row=0, column=0, sticky=(tk.W, tk.E))

        # === SECTION 3: CHARTS ===
        chart_frame = ttk.LabelFrame(main_frame, text="Correlation Chart", padding="10")
        chart_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Matplotlib figure
        self.fig = Figure(figsize=(10, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Start time update loop
        self.update_time()

    def update_time(self):
        """Update current time and pattern detection"""
        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")

        self.current_time_label.config(text=f"Current Time: {time_str}")

        # Detect patterns
        from time_pattern_detector import is_interesting_time
        is_interesting, patterns = is_interesting_time(now)

        if is_interesting:
            pattern_text = f"⭐ INTERESTING! Patterns: {', '.join(patterns)}"
            self.pattern_label.config(text=pattern_text, foreground="green")
        else:
            self.pattern_label.config(text="➖ No special patterns", foreground="gray")

        # Update every second
        self.root.after(1000, self.update_time)

    def log_attempt(self, successful: bool):
        """Log a bug fix attempt"""
        description = self.description_entry.get()

        if not description:
            messagebox.showwarning("Missing Info", "Please enter a description")
            return

        # Add attempt
        attempt = self.tracker.add_attempt(
            successful=successful,
            description=description
        )

        # Clear entry
        self.description_entry.delete(0, tk.END)

        # Show confirmation
        status = "SUCCESS" if successful else "FAILURE"
        pattern_info = f"\nPatterns: {', '.join(attempt.pattern_names)}" if attempt.pattern_names else ""
        messagebox.showinfo(
            "Logged",
            f"Bug fix attempt logged as {status}\n"
            f"Time: {attempt.timestamp.strftime('%H:%M:%S')}"
            f"{pattern_info}"
        )

        # Refresh display
        self.refresh_stats()

    def refresh_stats(self):
        """Refresh statistics and charts"""
        stats = self.tracker.get_statistics()

        # Update stats text
        self.stats_text.delete(1.0, tk.END)

        stats_content = f"""
Total Attempts: {stats['total_attempts']}
Successful: {stats['successful_attempts']} ({stats['overall_success_rate']:.1f}%)
Failed: {stats['failed_attempts']}

═══════════════════════════════════════════════════════════

INTERESTING TIME vs BORING TIME:

Interesting Time Attempts: {stats['interesting_time_attempts']}
  → Success Rate: {stats['interesting_time_success_rate']:.1f}%

Boring Time Attempts: {stats['boring_time_attempts']}
  → Success Rate: {stats['boring_time_success_rate']:.1f}%

HYPOTHESIS: {"Interesting times predict success! ⭐" if stats['interesting_time_success_rate'] > stats['boring_time_success_rate'] else "Boring times predict success! 📉" if stats['boring_time_success_rate'] > stats['interesting_time_success_rate'] else "No correlation detected yet"}
"""

        self.stats_text.insert(1.0, stats_content)

        # Update chart
        self.update_chart(stats)

    def update_chart(self, stats):
        """Update correlation chart"""
        self.fig.clear()

        if stats['total_attempts'] == 0:
            ax = self.fig.add_subplot(111)
            ax.text(
                0.5, 0.5, 'No data yet\nLog some bug fix attempts to see patterns!',
                ha='center', va='center', fontsize=14, color='gray'
            )
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            self.canvas.draw()
            return

        # Create subplots
        ax1 = self.fig.add_subplot(121)
        ax2 = self.fig.add_subplot(122)

        # Chart 1: Interesting vs Boring time success rates
        categories = ['Interesting\nTime', 'Boring\nTime']
        success_rates = [
            stats['interesting_time_success_rate'],
            stats['boring_time_success_rate']
        ]
        colors = ['#4CAF50', '#FF9800']

        bars = ax1.bar(categories, success_rates, color=colors, alpha=0.7)
        ax1.set_ylabel('Success Rate (%)')
        ax1.set_title('Success Rate by Time Type')
        ax1.set_ylim(0, 100)
        ax1.axhline(y=50, color='red', linestyle='--', alpha=0.3, label='50% baseline')
        ax1.legend()

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax1.text(
                bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%',
                ha='center', va='bottom'
            )

        # Chart 2: Pattern-specific success rates
        pattern_stats = stats.get('pattern_stats', {})
        if pattern_stats:
            # Get top 5 patterns by frequency
            sorted_patterns = sorted(
                pattern_stats.items(),
                key=lambda x: x[1]['total'],
                reverse=True
            )[:5]

            if sorted_patterns:
                pattern_names = [p[0].replace('_', '\n') for p, _ in sorted_patterns]
                pattern_rates = [data['success_rate'] for _, data in sorted_patterns]

                bars2 = ax2.barh(pattern_names, pattern_rates, color='#2196F3', alpha=0.7)
                ax2.set_xlabel('Success Rate (%)')
                ax2.set_title('Top 5 Pattern Success Rates')
                ax2.set_xlim(0, 100)
                ax2.axvline(x=50, color='red', linestyle='--', alpha=0.3)

                # Add value labels
                for bar in bars2:
                    width = bar.get_width()
                    ax2.text(
                        width, bar.get_y() + bar.get_height()/2.,
                        f' {width:.1f}%',
                        va='center'
                    )
        else:
            ax2.text(
                0.5, 0.5, 'No pattern data yet',
                ha='center', va='center', fontsize=12, color='gray'
            )
            ax2.set_xlim(0, 1)
            ax2.set_ylim(0, 1)
            ax2.axis('off')

        self.fig.tight_layout()
        self.canvas.draw()


def main():
    """Main entry point"""
    root = tk.Tk()
    app = BugFixApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
