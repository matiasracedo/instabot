import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import sqlite3
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np

DB_PATH = 'instabot.db'

def get_action_history(days=7):
    """Get action history for the last X days"""
    conn = sqlite3.connect(DB_PATH)
    
    # Calculate date for X days ago
    date_from = (datetime.utcnow() - timedelta(days=days)).isoformat()
    
    # Get actions by date and type
    query = """
    SELECT 
        substr(timestamp, 1, 10) as date, 
        action_type, 
        COUNT(*) as count 
    FROM actions 
    WHERE timestamp >= ? 
    GROUP BY date, action_type
    ORDER BY date ASC
    """
    
    df = pd.read_sql_query(query, conn, params=(date_from,))
    conn.close()
    
    return df

def get_hashtag_stats():
    """Get statistics by hashtag"""
    conn = sqlite3.connect(DB_PATH)
    
    query = """
    SELECT 
        hashtag, 
        action_type, 
        COUNT(*) as count 
    FROM actions 
    WHERE hashtag IS NOT NULL 
    GROUP BY hashtag, action_type
    ORDER BY count DESC
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    return df

def create_stats_window(parent):
    """Create a window displaying statistics"""
    try:
        stats_window = tk.Toplevel(parent)
        stats_window.title("InstaBot Stats")
        stats_window.geometry("800x600")
        stats_window.configure(bg="#121212")
        
        # Make window modal
        stats_window.transient(parent)
        stats_window.grab_set()
        
        # Center the window
        stats_window.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # Define Instagram-inspired colors
        PRIMARY_BG = "#121212"
        TEXT_COLOR = "#f5f5f5"
        ACCENT_COLOR = "#0095f6"
        SECONDARY_BG = "#1a1a1a"
        
        # Check if database exists and has data
        if not os.path.exists(DB_PATH):
            # Show message if no database
            message_frame = tk.Frame(stats_window, bg=PRIMARY_BG, padx=40, pady=40)
            message_frame.pack(expand=True, fill="both")
            
            message_label = tk.Label(
                message_frame,
                text="📊 No Statistics Available\n\nStart using the bot to see your statistics here!",
                bg=PRIMARY_BG,
                fg=TEXT_COLOR,
                font=("Segoe UI", 14),
                justify="center"
            )
            message_label.pack(expand=True)
            
            close_button = tk.Button(
                message_frame,
                text="Close",
                command=stats_window.destroy,
                bg=ACCENT_COLOR,
                fg=TEXT_COLOR,
                font=("Segoe UI", 11, "bold"),
                padx=20,
                pady=8,
                border=0
            )
            close_button.pack(pady=20)
            
            return stats_window
    except ImportError as e:
        messagebox.showerror("Missing Dependencies", 
                           f"Statistics feature requires additional packages:\n{str(e)}\n\nRun: pip install matplotlib pandas numpy")
        return None
    except Exception as e:
        messagebox.showerror("Error", f"Could not create statistics window:\n{str(e)}")
        return None
    
    # Create notebook for different stats views
    notebook = ttk.Notebook(stats_window)
    
    # Style for the notebook
    style = ttk.Style()
    style.configure("TNotebook", background=PRIMARY_BG, borderwidth=0)
    style.configure("TNotebook.Tab", background=SECONDARY_BG, foreground=TEXT_COLOR, padding=[10, 5], font=("Segoe UI", 10))
    style.map("TNotebook.Tab", background=[("selected", ACCENT_COLOR)], foreground=[("selected", TEXT_COLOR)])
    
    # Activity Tab
    activity_frame = tk.Frame(notebook, bg=PRIMARY_BG)
    notebook.add(activity_frame, text="Activity History")
    
    # Hashtags Tab
    hashtags_frame = tk.Frame(notebook, bg=PRIMARY_BG)
    notebook.add(hashtags_frame, text="Hashtag Performance")
    
    # Success Rate Tab
    success_frame = tk.Frame(notebook, bg=PRIMARY_BG)
    notebook.add(success_frame, text="Success Rate")
    
    notebook.pack(expand=True, fill="both", padx=15, pady=15)
    
    # Create Activity History Chart
    fig1 = plt.figure(figsize=(7, 4), facecolor=PRIMARY_BG)
    ax1 = fig1.add_subplot(111)
    ax1.set_facecolor(PRIMARY_BG)
    
    # Format the plot with Instagram-inspired styling
    ax1.spines['bottom'].set_color('#555555')
    ax1.spines['top'].set_color('#555555')
    ax1.spines['left'].set_color('#555555')
    ax1.spines['right'].set_color('#555555')
    ax1.tick_params(axis='x', colors=TEXT_COLOR)
    ax1.tick_params(axis='y', colors=TEXT_COLOR)
    ax1.set_title('Activity History (Last 7 Days)', color=TEXT_COLOR, fontsize=12)
    ax1.set_xlabel('Date', color=TEXT_COLOR)
    ax1.set_ylabel('Count', color=TEXT_COLOR)
    
    # Get activity data
    activity_data = get_action_history()
    
    # If we have data, plot it
    if not activity_data.empty:
        # Pivot the data to have dates as index, action_types as columns
        pivoted = activity_data.pivot(index='date', columns='action_type', values='count').fillna(0)
        
        # Plot the data
        pivoted.plot(kind='bar', ax=ax1, color=['#0095f6', '#44bec7', '#ff5e3a'])
        
        # Add legend
        ax1.legend(facecolor=PRIMARY_BG, labelcolor=TEXT_COLOR)
    else:
        ax1.text(0.5, 0.5, 'No activity data available', 
                horizontalalignment='center',
                verticalalignment='center',
                transform=ax1.transAxes,
                color=TEXT_COLOR)
    
    # Create canvas for the plot
    canvas1 = FigureCanvasTkAgg(fig1, activity_frame)
    canvas1.draw()
    canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Create Hashtag Performance Chart
    fig2 = plt.figure(figsize=(7, 4), facecolor=PRIMARY_BG)
    ax2 = fig2.add_subplot(111)
    ax2.set_facecolor(PRIMARY_BG)
    
    # Format the plot with Instagram-inspired styling
    ax2.spines['bottom'].set_color('#555555')
    ax2.spines['top'].set_color('#555555')
    ax2.spines['left'].set_color('#555555')
    ax2.spines['right'].set_color('#555555')
    ax2.tick_params(axis='x', colors=TEXT_COLOR)
    ax2.tick_params(axis='y', colors=TEXT_COLOR)
    ax2.set_title('Hashtag Performance', color=TEXT_COLOR, fontsize=12)
    
    # Get hashtag data
    hashtag_data = get_hashtag_stats()
    
    # If we have data, plot it
    if not hashtag_data.empty:
        # Pivot the data to have hashtags as index, action_types as columns
        pivoted = hashtag_data.pivot(index='hashtag', columns='action_type', values='count').fillna(0)
        
        # Sort by total interactions
        if 'like' in pivoted.columns and 'comment' in pivoted.columns:
            pivoted['total'] = pivoted['like'] + pivoted['comment']
            pivoted = pivoted.sort_values('total', ascending=False).head(10)
            pivoted = pivoted.drop('total', axis=1)
        
        # Plot the data
        pivoted.plot(kind='barh', ax=ax2, color=['#0095f6', '#44bec7'])
        
        # Add legend
        ax2.legend(facecolor=PRIMARY_BG, labelcolor=TEXT_COLOR)
    else:
        ax2.text(0.5, 0.5, 'No hashtag data available', 
                horizontalalignment='center',
                verticalalignment='center',
                transform=ax2.transAxes,
                color=TEXT_COLOR)
    
    # Create canvas for the plot
    canvas2 = FigureCanvasTkAgg(fig2, hashtags_frame)
    canvas2.draw()
    canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Create Success Rate Chart (pie chart)
    fig3 = plt.figure(figsize=(7, 4), facecolor=PRIMARY_BG)
    ax3 = fig3.add_subplot(111)
    ax3.set_facecolor(PRIMARY_BG)
    
    # Calculate success rate from database
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Get total actions
    c.execute('SELECT action_type, COUNT(*) FROM actions GROUP BY action_type')
    action_counts = dict(c.fetchall())
    conn.close()
    
    # Define success and error counts
    success_count = action_counts.get('like', 0) + action_counts.get('comment', 0)
    error_count = action_counts.get('error', 0)
    total = success_count + error_count
    
    # Plot pie chart if we have data
    if total > 0:
        labels = ['Success', 'Errors']
        sizes = [success_count, error_count]
        colors = ['#0095f6', '#ff5e3a']
        ax3.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, 
               textprops={'color': TEXT_COLOR})
        ax3.set_title('Success vs Error Rate', color=TEXT_COLOR, fontsize=12)
    else:
        ax3.text(0.5, 0.5, 'No action data available', 
                horizontalalignment='center',
                verticalalignment='center',
                transform=ax3.transAxes,
                color=TEXT_COLOR)
    
    # Create canvas for the plot
    canvas3 = FigureCanvasTkAgg(fig3, success_frame)
    canvas3.draw()
    canvas3.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Add a button to close the window
    close_button = ttk.Button(
        stats_window, 
        text="Close", 
        command=stats_window.destroy,
        style="TButton"
    )
    close_button.pack(pady=10)
    
    return stats_window

if __name__ == "__main__":
    # Test the stats window
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    stats_window = create_stats_window(root)
    root.mainloop()
