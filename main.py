import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import seaborn as sns

class HabitTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Habit Tracker")
        self.root.geometry("1400x800")
        
        # Dark theme colors
        self.bg_dark = "#1e1e1e"
        self.bg_medium = "#2d2d2d"
        self.bg_light = "#3d3d3d"
        self.accent = "#4a9eff"
        self.success = "#4ade80"
        self.warning = "#fbbf24"
        self.danger = "#f87171"
        self.text = "#e0e0e0"
        self.text_dim = "#a0a0a0"
        
        self.root.configure(bg=self.bg_dark)
        
        # Set seaborn style
        sns.set_style("darkgrid")
        plt.style.use('dark_background')
        
        # CSV file
        self.csv_file = "habits_data.csv"
        self.init_csv()
        
        # Load data
        self.habits = self.load_habits()
        self.current_month = datetime.now().month
        self.current_year = datetime.now().year
        
        self.create_widgets()
        self.refresh_data()
        
    def init_csv(self):
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['habit', 'goal', 'date', 'completed'])
                
    def load_habits(self):
        habits = []
        if os.path.exists(self.csv_file):
            with open(self.csv_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    habit_name = row['habit']
                    if habit_name and not any(h['name'] == habit_name for h in habits):
                        habits.append({'name': habit_name, 'goal': int(row['goal'])})
        return habits
    
    def create_widgets(self):
        # Main container
        main_frame = tk.Frame(self.root, bg=self.bg_dark)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Habit list and calendar
        left_frame = tk.Frame(main_frame, bg=self.bg_dark)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Title
        title = tk.Label(left_frame, text="HABIT TRACKER", font=("Arial", 24, "bold"),
                        bg=self.bg_dark, fg=self.text)
        title.pack(pady=(0, 20))
        
        # Add habit section
        add_frame = tk.Frame(left_frame, bg=self.bg_medium)
        add_frame.pack(fill=tk.X, pady=(0, 20), padx=5, ipady=10)
        
        tk.Label(add_frame, text="Habit:", bg=self.bg_medium, fg=self.text,
                font=("Arial", 10)).grid(row=0, column=0, padx=10, pady=5)
        self.habit_entry = tk.Entry(add_frame, bg=self.bg_light, fg=self.text,
                                    insertbackground=self.text, relief=tk.FLAT, font=("Arial", 10))
        self.habit_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        tk.Label(add_frame, text="Goal:", bg=self.bg_medium, fg=self.text,
                font=("Arial", 10)).grid(row=0, column=2, padx=10, pady=5)
        self.goal_entry = tk.Entry(add_frame, bg=self.bg_light, fg=self.text,
                                   insertbackground=self.text, relief=tk.FLAT, font=("Arial", 10), width=8)
        self.goal_entry.grid(row=0, column=3, padx=5, pady=5)
        
        add_btn = tk.Button(add_frame, text="Add Habit", command=self.add_habit,
                           bg=self.accent, fg="white", relief=tk.FLAT, font=("Arial", 10, "bold"),
                           cursor="hand2", padx=20)
        add_btn.grid(row=0, column=4, padx=10, pady=5)
        
        add_frame.columnconfigure(1, weight=1)
        
        # Habits canvas with scrollbar
        canvas_frame = tk.Frame(left_frame, bg=self.bg_dark)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, bg=self.bg_dark, highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.bg_dark)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Right panel - Statistics
        right_frame = tk.Frame(main_frame, bg=self.bg_dark, width=400)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        right_frame.pack_propagate(False)
        
        stats_title = tk.Label(right_frame, text="STATISTICS", font=("Arial", 18, "bold"),
                              bg=self.bg_dark, fg=self.text)
        stats_title.pack(pady=(0, 15))
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(4, 8), facecolor=self.bg_dark)
        self.canvas_plot = FigureCanvasTkAgg(self.fig, master=right_frame)
        self.canvas_plot.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def add_habit(self):
        habit_name = self.habit_entry.get().strip()
        goal = self.goal_entry.get().strip()
        
        if not habit_name or not goal:
            messagebox.showwarning("Input Error", "Please enter both habit name and goal")
            return
        
        try:
            goal = int(goal)
        except ValueError:
            messagebox.showwarning("Input Error", "Goal must be a number")
            return
        
        if any(h['name'] == habit_name for h in self.habits):
            messagebox.showwarning("Duplicate", "Habit already exists")
            return
        
        self.habits.append({'name': habit_name, 'goal': goal})
        self.habit_entry.delete(0, tk.END)
        self.goal_entry.delete(0, tk.END)
        self.refresh_data()
        
    def mark_habit(self, habit_name, date):
        date_str = date.strftime("%Y-%m-%d")
        
        # Check if already marked
        rows = []
        found = False
        with open(self.csv_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            for row in rows:
                if row['habit'] == habit_name and row['date'] == date_str:
                    found = True
                    break
        
        if not found:
            with open(self.csv_file, 'a', newline='') as f:
                writer = csv.writer(f)
                habit = next(h for h in self.habits if h['name'] == habit_name)
                writer.writerow([habit_name, habit['goal'], date_str, 1])
        
        self.refresh_data()
    
    def wrap_text(self, text, max_length=15):
        """Wrap text if it exceeds max_length"""
        if len(text) <= max_length:
            return text
        return text[:max_length-2] + ".."
        
    def refresh_data(self):
        # Clear scrollable frame
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Days in current month
        first_day = datetime(self.current_year, self.current_month, 1)
        if self.current_month == 12:
            last_day = datetime(self.current_year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = datetime(self.current_year, self.current_month + 1, 1) - timedelta(days=1)
        
        days_in_month = last_day.day
        first_weekday = first_day.weekday()  # 0=Monday, 6=Sunday
        
        # Load completion data
        completion_data = {}
        with open(self.csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['habit'] and row['date']:
                    key = (row['habit'], row['date'])
                    completion_data[key] = True
        
        # Create header with day numbers and weekday names
        header_frame = tk.Frame(self.scrollable_frame, bg=self.bg_medium, relief=tk.RIDGE, bd=1)
        header_frame.pack(fill=tk.X, pady=(0, 2))
        
        # Habit column header
        tk.Label(header_frame, text="HABIT", font=("Arial", 9, "bold"), bg=self.bg_medium,
                fg=self.text, width=18, anchor="w", padx=5).grid(row=0, column=0, rowspan=2, sticky="nsew")
        
        # Goal column header
        tk.Label(header_frame, text="GOAL", font=("Arial", 9, "bold"), bg=self.bg_medium,
                fg=self.text, width=5).grid(row=0, column=1, rowspan=2, sticky="nsew")
        
        # Day headers - numbers and weekdays
        weekdays = ['M', 'T', 'W', 'T', 'F', 'S', 'S']
        for day in range(1, days_in_month + 1):
            date = datetime(self.current_year, self.current_month, day)
            weekday = weekdays[date.weekday()]
            
            # Day number (top row)
            day_label = tk.Label(header_frame, text=str(day), font=("Arial", 8, "bold"), 
                               bg=self.bg_medium, fg=self.text, width=3)
            day_label.grid(row=0, column=2 + day, padx=1, sticky="nsew")
            
            # Weekday initial (bottom row)
            wd_label = tk.Label(header_frame, text=weekday, font=("Arial", 7), 
                               bg=self.bg_medium, fg=self.text_dim, width=3)
            wd_label.grid(row=1, column=2 + day, padx=1, sticky="nsew")
        
        # Progress column header
        tk.Label(header_frame, text="PROGRESS", font=("Arial", 9, "bold"), bg=self.bg_medium,
                fg=self.text, width=10).grid(row=0, column=3 + days_in_month, rowspan=2, sticky="nsew")
        
        # Create rows for each habit
        for idx, habit in enumerate(self.habits):
            row_bg = self.bg_light if idx % 2 == 0 else self.bg_medium
            row_frame = tk.Frame(self.scrollable_frame, bg=row_bg, relief=tk.RIDGE, bd=1)
            row_frame.pack(fill=tk.X, pady=1)
            
            # Habit name with wrapping
            wrapped_name = self.wrap_text(habit['name'], 18)
            habit_label = tk.Label(row_frame, text=wrapped_name, font=("Arial", 9), bg=row_bg,
                    fg=self.text, width=18, anchor="w", padx=5)
            habit_label.grid(row=0, column=0, sticky="nsew", pady=4)
            
            # Add tooltip for full name if wrapped
            if len(habit['name']) > 18:
                self.create_tooltip(habit_label, habit['name'])
            
            # Goal
            tk.Label(row_frame, text=str(habit['goal']), font=("Arial", 9), bg=row_bg,
                    fg=self.text, width=5).grid(row=0, column=1, sticky="nsew", pady=4)
            
            # Day checkboxes
            completed = 0
            for day in range(1, days_in_month + 1):
                date = datetime(self.current_year, self.current_month, day)
                date_str = date.strftime("%Y-%m-%d")
                is_completed = (habit['name'], date_str) in completion_data
                
                if is_completed:
                    completed += 1
                
                # Create checkbox frame
                box_frame = tk.Frame(row_frame, bg=row_bg)
                box_frame.grid(row=0, column=2 + day, padx=2, pady=4)
                
                # Checkbox button
                if is_completed:
                    # Filled box with X mark
                    btn = tk.Label(box_frame, text="X", font=("Arial", 8, "bold"),
                                 bg=self.success, fg="white", width=2, height=1,
                                 relief=tk.FLAT, cursor="hand2")
                else:
                    # Empty box
                    btn = tk.Label(box_frame, text="", font=("Arial", 8),
                                 bg=self.bg_dark, fg=self.text, width=2, height=1,
                                 relief=tk.SOLID, bd=1, cursor="hand2")
                
                btn.pack()
                btn.bind("<Button-1>", lambda e, h=habit['name'], d=date: self.mark_habit(h, d))
            
            # Progress
            progress = int((completed / habit['goal']) * 100) if habit['goal'] > 0 else 0
            progress_color = self.danger if progress < 30 else self.warning if progress < 70 else self.success
            
            progress_label = tk.Label(row_frame, text=f"{progress}%", font=("Arial", 9, "bold"), 
                                     bg=row_bg, fg=progress_color, width=10)
            progress_label.grid(row=0, column=3 + days_in_month, sticky="nsew", pady=4)
        
        self.update_graphs()
    
    def create_tooltip(self, widget, text):
        """Create a tooltip for wrapped text"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = tk.Label(tooltip, text=text, background=self.bg_light, 
                           foreground=self.text, relief=tk.SOLID, borderwidth=1,
                           font=("Arial", 9), padx=5, pady=3)
            label.pack()
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
        
    def update_graphs(self):
        self.fig.clear()
        
        # Calculate statistics
        monthly_progress = {}
        last_3_days = {}
        momentum = {}
        
        with open(self.csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['habit'] and row['date']:
                    habit = row['habit']
                    date = datetime.strptime(row['date'], "%Y-%m-%d")
                    
                    if date.month == self.current_month and date.year == self.current_year:
                        monthly_progress[habit] = monthly_progress.get(habit, 0) + 1
                    
                    days_ago = (datetime.now() - date).days
                    if days_ago <= 3:
                        last_3_days[habit] = last_3_days.get(habit, 0) + 1
                    
                    if days_ago <= 3:
                        momentum[habit] = momentum.get(habit, 0) + 1
        
        # Create three subplots
        gs = self.fig.add_gridspec(3, 1, hspace=0.4, top=0.95, bottom=0.05)
        
        # Monthly Progress
        ax1 = self.fig.add_subplot(gs[0])
        if self.habits and monthly_progress:
            habits_list = [self.wrap_text(h['name'], 12) for h in self.habits]
            progress_pct = []
            for h in self.habits:
                completed = monthly_progress.get(h['name'], 0)
                pct = (completed / h['goal']) * 100 if h['goal'] > 0 else 0
                progress_pct.append(pct)
            
            colors = [self.danger if p < 30 else self.warning if p < 70 else self.success for p in progress_pct]
            bars = ax1.barh(habits_list, progress_pct, color=colors, alpha=0.8)
            ax1.set_xlabel('Progress (%)', color=self.text, fontsize=9)
            ax1.set_title('MONTHLY PROGRESS', color=self.text, fontsize=11, fontweight='bold', pad=10)
            ax1.set_xlim(0, 100)
            ax1.tick_params(colors=self.text, labelsize=8)
            ax1.spines['bottom'].set_color(self.text)
            ax1.spines['left'].set_color(self.text)
            ax1.spines['top'].set_visible(False)
            ax1.spines['right'].set_visible(False)
            ax1.grid(axis='x', alpha=0.3)
        
        # Last 3 Days
        ax2 = self.fig.add_subplot(gs[1])
        if self.habits and last_3_days:
            habits_list = [self.wrap_text(h['name'], 12) for h in self.habits]
            days_data = [last_3_days.get(h['name'], 0) for h in self.habits]
            
            bars = ax2.barh(habits_list, days_data, color=self.accent, alpha=0.8)
            ax2.set_xlabel('Days Completed', color=self.text, fontsize=9)
            ax2.set_title('LAST 3 DAYS', color=self.text, fontsize=11, fontweight='bold', pad=10)
            ax2.tick_params(colors=self.text, labelsize=8)
            ax2.spines['bottom'].set_color(self.text)
            ax2.spines['left'].set_color(self.text)
            ax2.spines['top'].set_visible(False)
            ax2.spines['right'].set_visible(False)
            ax2.grid(axis='x', alpha=0.3)
        
        # Momentum (pie chart)
        ax3 = self.fig.add_subplot(gs[2])
        if momentum:
            labels = [self.wrap_text(k, 10) for k in momentum.keys()]
            sizes = list(momentum.values())
            colors_pie = plt.cm.Set3(range(len(labels)))
            
            wedges, texts, autotexts = ax3.pie(sizes, labels=labels, autopct='%1.0f%%',
                                                colors=colors_pie, startangle=90)
            for text in texts:
                text.set_color(self.text)
                text.set_fontsize(8)
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontsize(8)
                autotext.set_fontweight('bold')
            
            ax3.set_title('MOMENTUM', color=self.text, fontsize=11, fontweight='bold', pad=10)
        
        self.canvas_plot.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = HabitTrackerApp(root)
    root.mainloop()