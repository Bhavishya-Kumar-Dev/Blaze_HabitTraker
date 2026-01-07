import customtkinter as ctk
from tkinter import messagebox
import csv
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import seaborn as sns

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class HabitTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Habit Tracker")
        self.root.geometry("1600x800")
        
        # Modern dark theme colors (inspired by the mobile app)
        self.bg_dark = "#1a1a1a"
        self.bg_medium = "#252525"
        self.bg_light = "#2a2a2a"
        self.accent = "#FFD700"
        self.accent_hover = "#e6c200"
        self.success = "#FFD700"
        self.warning = "#fbbf24"
        self.danger = "#780404"
        self.text = "#ffffff"
        self.text_dim = "#999999"
        self.checkbox_empty = "#3a3a3a"
        self.checkbox_filled = "#FFD700"
        
        self.root.configure(fg_color=self.bg_dark)
        
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
        main_frame = ctk.CTkFrame(self.root, fg_color=self.bg_dark)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left panel - Habit list and calendar
        left_frame = ctk.CTkFrame(main_frame, fg_color=self.bg_dark,width=900)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Title
        title = ctk.CTkLabel(left_frame, text="HABIT TRACKER", 
                            font=ctk.CTkFont(size=24, weight="bold"),
                            text_color=self.text)
        title.pack(pady=(0, 20))
        
        # Add habit section
        add_frame = ctk.CTkFrame(left_frame, fg_color=self.bg_medium, corner_radius=10)
        add_frame.pack(fill="x", pady=(0, 20), padx=5)
        
        add_content = ctk.CTkFrame(add_frame, fg_color=self.bg_medium)
        add_content.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(add_content, text="Habit:", fg_color=self.bg_medium, 
                    text_color=self.text, font=ctk.CTkFont(size=10)).grid(row=0, column=0, padx=10, pady=5)
        self.habit_entry = ctk.CTkEntry(add_content, fg_color=self.bg_light, 
                                        text_color=self.text, border_width=0,
                                        font=ctk.CTkFont(size=10),height=40)
        self.habit_entry.grid(row=0, column=1, padx=5, pady=5,sticky="ew")
        
        ctk.CTkLabel(add_content, text="Goal:", fg_color=self.bg_medium, 
                    text_color=self.text, font=ctk.CTkFont(size=10)).grid(row=1, column=0, padx=10, pady=5)
        self.goal_entry = ctk.CTkEntry(add_content, fg_color=self.bg_light, 
                                       text_color=self.text, border_width=0,
                                       font=ctk.CTkFont(size=10), width=80,height=40)
        self.goal_entry.grid(row=1, column=1, padx=5, pady=5,sticky="w")
        
        add_btn = ctk.CTkButton(add_content, text="Add Habit", command=self.add_habit,
                               fg_color=self.accent, text_color="black",
                               hover_color=self.accent_hover,
                               font=ctk.CTkFont(size=10, weight="bold"),
                               corner_radius=8,height=40)
        add_btn.grid(row=1, column=1, padx=100, pady=5,sticky="w" )
        
        add_content.columnconfigure(1, weight=1)
        
        # Habits scrollable frame
        self.scrollable_frame = ctk.CTkScrollableFrame(left_frame,width=700, fg_color=self.bg_dark)
        self.scrollable_frame.pack(fill="both", expand=True)
        
        # Right panel - Statistics
        right_frame = ctk.CTkFrame(main_frame, fg_color=self.bg_dark, width=400)
        right_frame.pack(side="right", fill="both", padx=(10, 0))
        right_frame.pack_propagate(False)
        
        stats_title = ctk.CTkLabel(right_frame, text="STATISTICS", 
                                   font=ctk.CTkFont(size=18, weight="bold"),
                                   text_color=self.text)
        stats_title.pack(pady=(0, 15))
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(4, 8), facecolor=self.bg_dark)
        self.canvas_plot = FigureCanvasTkAgg(self.fig, master=right_frame)
        self.canvas_plot.get_tk_widget().pack(fill="both", expand=True)
        
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
        self.habit_entry.delete(0, 'end')
        self.goal_entry.delete(0, 'end')
        self.refresh_data()
        
    def mark_habit(self, habit_name, date, checkbox):
        date_str = date.strftime("%Y-%m-%d")
        
        # Check if already marked
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
        
        # Load completion data
        completion_data = {}
        with open(self.csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['habit'] and row['date']:
                    key = (row['habit'], row['date'])
                    completion_data[key] = True
        
        # Create header with day numbers and weekday names
        header_frame = ctk.CTkFrame(self.scrollable_frame, fg_color=self.bg_medium, 
                                   corner_radius=8, border_width=1, border_color=self.bg_light)
        header_frame.pack(fill="x", pady=(0, 2))
        
        # Habit column header
        ctk.CTkLabel(header_frame, text="HABIT", font=ctk.CTkFont(size=9, weight="bold"), 
                    fg_color=self.bg_medium, text_color=self.text, 
                    width=150, anchor="w").grid(row=0, column=0, rowspan=2, sticky="nsew", padx=5)
        
        # Goal column header
        ctk.CTkLabel(header_frame, text="GOAL", font=ctk.CTkFont(size=9, weight="bold"), 
                    fg_color=self.bg_medium, text_color=self.text, 
                    width=50).grid(row=0, column=1, rowspan=2, sticky="nsew")
        
        # Day headers - numbers and weekdays
        weekdays = ['M', 'T', 'W', 'T', 'F', 'S', 'S']
        for day in range(1, days_in_month + 1):
            date = datetime(self.current_year, self.current_month, day)
            weekday = weekdays[date.weekday()]
            
            # Day number (top row)
            ctk.CTkLabel(header_frame, text=str(day), font=ctk.CTkFont(size=8, weight="bold"), 
                        fg_color=self.bg_medium, text_color=self.text, 
                        width=25).grid(row=0, column=2 + day, padx=1, sticky="nsew")
            
            # Weekday initial (bottom row)
            ctk.CTkLabel(header_frame, text=weekday, font=ctk.CTkFont(size=7), 
                        fg_color=self.bg_medium, text_color=self.text_dim, 
                        width=25).grid(row=1, column=2 + day, padx=1, sticky="nsew")
        
        # Progress column header
        ctk.CTkLabel(header_frame, text="PROGRESS", font=ctk.CTkFont(size=9, weight="bold"), 
                    fg_color=self.bg_medium, text_color=self.text, 
                    width=80).grid(row=0, column=3 + days_in_month, rowspan=2, sticky="nsew")
        
        # Create rows for each habit
        for idx, habit in enumerate(self.habits):
            row_bg = self.bg_light if idx % 2 == 0 else self.bg_medium
            row_frame = ctk.CTkFrame(self.scrollable_frame, fg_color=row_bg, 
                                    corner_radius=8, border_width=1, border_color=self.bg_light)
            row_frame.pack(fill="x", pady=1)
            
            # Habit name with wrapping
            wrapped_name = self.wrap_text(habit['name'], 18)
            habit_label = ctk.CTkLabel(row_frame, text=wrapped_name, font=ctk.CTkFont(size=9), 
                                       fg_color=row_bg, text_color=self.text, 
                                       width=150, anchor="w")
            habit_label.grid(row=0, column=0, sticky="nsew", pady=4, padx=5)
            
            # Goal
            ctk.CTkLabel(row_frame, text=str(habit['goal']), font=ctk.CTkFont(size=9), 
                        fg_color=row_bg, text_color=self.text, 
                        width=50).grid(row=0, column=1, sticky="nsew", pady=4)
            
            # Day checkboxes
            completed = 0
            for day in range(1, days_in_month + 1):
                date = datetime(self.current_year, self.current_month, day)
                date_str = date.strftime("%Y-%m-%d")
                is_completed = (habit['name'], date_str) in completion_data
                
                if is_completed:
                    completed += 1
                
                # Create checkbox button
                if is_completed:
                    # Filled box with checkmark
                    btn = ctk.CTkButton(row_frame, text="✓", font=ctk.CTkFont(size=10, weight="bold"),
                                       fg_color=self.checkbox_filled, text_color="black",
                                       hover_color=self.accent_hover,
                                       width=25, height=25, corner_radius=5,
                                       command=lambda h=habit['name'], d=date, cb=None: self.mark_habit(h, d, cb))
                else:
                    # Empty box
                    btn = ctk.CTkButton(row_frame, text="", font=ctk.CTkFont(size=8),
                                       fg_color=self.checkbox_empty, text_color=self.text,
                                       hover_color="#4a4a4a",
                                       width=25, height=25, corner_radius=5,
                                       command=lambda h=habit['name'], d=date, cb=None: self.mark_habit(h, d, cb))
                
                btn.grid(row=0, column=2 + day, padx=2, pady=4)
            
            # Progress
            progress = int((completed / habit['goal']) * 100) if habit['goal'] > 0 else 0
            progress_color = self.danger if progress < 30 else self.warning if progress < 70 else self.success
            
            progress_label = ctk.CTkLabel(row_frame, text=f"{progress}%", 
                                         font=ctk.CTkFont(size=9, weight="bold"), 
                                         fg_color=row_bg, text_color=progress_color, width=80)
            progress_label.grid(row=0, column=3 + days_in_month, sticky="nsew", pady=4)
        
        self.update_graphs()
        
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
            habits_list = [h['name'] for h in self.habits]
            progress_pct = []
            for h in self.habits:
                completed = monthly_progress.get(h['name'], 0)
                pct = (completed / h['goal']) * 100 if h['goal'] > 0 else 0
                progress_pct.append(pct)
            
            colors = [self.danger if p < 30 else self.warning if p < 70 else self.success for p in progress_pct]
            bars = ax1.barh(habits_list, progress_pct, color=colors,edgecolor="none")
            ax1.set_xlabel('Progress (%)', color=self.text, fontsize=9)
            ax1.set_title('MONTHLY PROGRESS', color=self.text, fontsize=11, fontweight='bold', pad=10)
            ax1.set_xlim(0, 100)
            ax1.tick_params(colors=self.text, labelsize=8)
            ax1.set_facecolor(self.bg_medium)
            ax1.spines['bottom'].set_color(self.text_dim)
            ax1.spines['left'].set_color(self.text_dim)
            ax1.spines['top'].set_visible(False)
            ax1.spines['right'].set_visible(False)
            ax1.grid(False)
        
        # Last 3 Days
        ax2 = self.fig.add_subplot(gs[1])
        if self.habits and last_3_days:
            habits_list = [h['name'] for h in self.habits]
            days_data = [last_3_days.get(h['name'], 0) for h in self.habits]
            
            bars = ax2.barh(habits_list, days_data, color=self.accent,edgecolor="none")
            ax2.set_xlabel('Days Completed', color=self.text, fontsize=9)
            ax2.set_title('LAST 3 DAYS', color=self.text, fontsize=11, fontweight='bold', pad=10)
            ax2.tick_params(colors=self.text, labelsize=8)
            ax2.set_facecolor(self.bg_medium)
            ax2.spines['bottom'].set_color(self.text_dim)
            ax2.spines['left'].set_color(self.text_dim)
            ax2.spines['top'].set_visible(False)
            ax2.spines['right'].set_visible(False)
            ax2.grid(False)
        
        # Momentum (pie chart)
        ax3 = self.fig.add_subplot(gs[2])
        if momentum:
            labels = list(momentum.keys())
            sizes = list(momentum.values())
            colors_pie = ['#6366F1', '#8B5CF6', '#22D3EE', '#F43F5E', '#FBBF24'][:len(labels)]
            
            wedges, texts, autotexts = ax3.pie(sizes, labels=labels, autopct='%1.0f%%',
                                                colors=colors_pie, startangle=90,wedgeprops={'linewidth': 0, 'edgecolor': 'none'})
            for text in texts:
                text.set_color(self.text)
                text.set_fontsize(8)
            for autotext in autotexts:
                autotext.set_color('snow')
                autotext.set_fontsize(10)
                autotext.set_fontweight('bold')
            
            ax3.set_title('MOMENTUM', color=self.text, fontsize=11, fontweight='bold', pad=10)
            ax3.set_facecolor(self.bg_medium)
        
        self.fig.patch.set_facecolor(self.bg_dark)
        self.canvas_plot.draw()

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    root = ctk.CTk()
    app = HabitTrackerApp(root)
    root.mainloop()