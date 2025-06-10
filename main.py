import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import json
import os
from datetime import datetime
from ig import login_instagram, like_and_comment
from openai_client import set_api_key, generate_comment
from db import init_db, get_stats, log_action
from stats import create_stats_window
import threading

CONFIG_FILE = "config.json"

class InstaBotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("InstaBot")
        self.root.configure(bg="#0d1117")  # GitHub dark background
        self.root.resizable(False, False)
        
        # Set window size for better layout
        self.root.geometry("650x750")
        
        # Center the window on screen
        self.center_window()
        
        # Initialize database if needed
        init_db()
        
        # Set up variables
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.openai_var = tk.StringVar()
        self.hashtag_input_var = tk.StringVar()  # For new hashtag input
        self.hashtags_list = []  # List to store hashtags
        self.likes_var = tk.StringVar(value="50")
        self.comments_var = tk.StringVar(value="15")
        self.allow_sensitive_var = tk.BooleanVar(value=True)
        self.status_var = tk.StringVar(value="Ready")
        
        # Load existing config if available
        self.load_config_to_ui()
        
        # Create and configure style
        self.setup_style()
        
        # Create header with logo
        self.create_header()
        
        # Create main content frame
        self.create_content()
        
        # Update hashtag display after UI is created
        if hasattr(self, 'hashtag_display_frame'):
            self.update_hashtag_display()
        
        # Create status bar
        self.create_status_bar()
        
        # Add keyboard shortcuts
        self.setup_keyboard_shortcuts()
        
    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = 650
        height = 900
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2) - 50  # Slightly higher
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for better user experience"""
        # Cmd+S to save settings (Mac) / Ctrl+S (others)
        self.root.bind('<Command-s>', lambda e: self.save_settings())
        self.root.bind('<Control-s>', lambda e: self.save_settings())
        
        # Cmd+R to run bot (Mac) / Ctrl+R (others)
        self.root.bind('<Command-r>', lambda e: self.start_bot())
        self.root.bind('<Control-r>', lambda e: self.start_bot())
        
        # Cmd+T to show stats (Mac) / Ctrl+T (others)
        self.root.bind('<Command-t>', lambda e: self.show_stats())
        self.root.bind('<Control-t>', lambda e: self.show_stats())
        
        # ESC to close stats window if it exists
        self.root.bind('<Escape>', lambda e: self.root.focus_set())
        
    def setup_style(self):
        # Instagram-inspired dark palette (easy to tweak)
        self.PRIMARY_BG = "#10131a"       # Deep blue-black
        self.SECONDARY_BG = "#181c24"     # Card background
        self.INPUT_BG = "#232733"         # Input field background
        self.TEXT_COLOR = "#f5f6fa"       # Off-white text
        self.SECONDARY_TEXT = "#a1a6b2"   # Muted gray
        self.ACCENT_COLOR = "#0095f6"     # Instagram blue
        self.ACCENT_HOVER = "#1877f2"     # Hover blue
        self.BORDER_COLOR = "#232733"     # Subtle border
        self.SUCCESS_COLOR = "#1ecb7a"    # Green for success
        self.WARNING_COLOR = "#ffb300"    # Yellow for warnings
        self.ERROR_COLOR = "#ff4f4f"      # Red for errors

        self.style = ttk.Style(self.root)
        self.style.theme_use('clam')
        self.root.configure(bg=self.PRIMARY_BG)

        # Labels
        self.style.configure(
            'TLabel', 
            background=self.PRIMARY_BG, 
            foreground=self.TEXT_COLOR, 
            font=("SF Pro Display", 14) if self.is_macos() else ("Segoe UI", 12)
        )
        # Entry fields
        self.style.configure(
            'TEntry', 
            fieldbackground=self.INPUT_BG,
            foreground=self.TEXT_COLOR,
            insertcolor=self.TEXT_COLOR,
            bordercolor=self.BORDER_COLOR,
            lightcolor=self.BORDER_COLOR,
            darkcolor=self.BORDER_COLOR,
            font=("SF Pro Display", 14) if self.is_macos() else ("Segoe UI", 12),
            borderwidth=2,
            relief="solid"
        )
        self.style.map(
            'TEntry',
            fieldbackground=[('focus', self.INPUT_BG)],
            bordercolor=[('focus', self.ACCENT_COLOR)],
            lightcolor=[('focus', self.ACCENT_COLOR)],
            darkcolor=[('focus', self.ACCENT_COLOR)]
        )
        # Main buttons (Save, Run, etc)
        self.style.configure(
            'TButton',
            background=self.ACCENT_COLOR,
            foreground=self.PRIMARY_BG,
            font=("SF Pro Display", 15, "bold") if self.is_macos() else ("Segoe UI", 13, "bold"),
            borderwidth=0,
            relief="flat",
            focuscolor="none",
            padding=(18, 12)
        )
        self.style.map(
            'TButton',
            background=[('active', self.ACCENT_HOVER), ('pressed', self.ACCENT_HOVER)],
            foreground=[('active', self.PRIMARY_BG)]
        )
        # Secondary buttons (Clear All, Add, etc)
        self.style.configure(
            'Secondary.TButton',
            background=self.INPUT_BG,
            foreground=self.TEXT_COLOR,
            font=("SF Pro Display", 14) if self.is_macos() else ("Segoe UI", 12),
            borderwidth=1,
            relief="solid",
            bordercolor=self.BORDER_COLOR,
            padding=(18, 12)
        )
        self.style.map(
            'Secondary.TButton',
            background=[('active', self.BORDER_COLOR), ('pressed', self.BORDER_COLOR)],
            foreground=[('active', self.TEXT_COLOR)],
            bordercolor=[('active', self.ACCENT_COLOR)]
        )
        # Header
        self.style.configure(
            'Header.TLabel',
            font=("SF Pro Display", 26, "bold") if self.is_macos() else ("Segoe UI", 22, "bold"),
            background=self.PRIMARY_BG,
            foreground=self.TEXT_COLOR,
            padding=(0, 20, 0, 10)
        )
        self.style.configure(
            'Subheader.TLabel',
            font=("SF Pro Display", 15) if self.is_macos() else ("Segoe UI", 12),
            foreground=self.SECONDARY_TEXT,
            background=self.PRIMARY_BG,
            padding=(0, 0, 0, 5)
        )
        # Status/info
        self.style.configure(
            'Status.TLabel',
            font=("SF Pro Text", 12) if self.is_macos() else ("Segoe UI", 11),
            foreground=self.SECONDARY_TEXT,
            background=self.PRIMARY_BG
        )
        self.style.configure(
            'Stats.TLabel',
            font=("SF Pro Text", 12, "bold") if self.is_macos() else ("Segoe UI", 11, "bold"),
            foreground=self.ACCENT_COLOR,
            background=self.PRIMARY_BG
        )

    # --- Button creation helpers ---
    def create_modern_hashtag_section(self, parent, start_row):
        """Create a modern Instagram-like hashtag management section"""
        # Section title
        hashtag_label = ttk.Label(
            parent, 
            text="Hashtags",
            background=self.SECONDARY_BG
        )
        hashtag_label.grid(row=start_row, column=0, sticky="w", pady=(20, 8), padx=(0, 15))
        
        # Hashtag input container
        input_container = tk.Frame(parent, bg=self.SECONDARY_BG)
        input_container.grid(row=start_row, column=1, sticky="ew", pady=(20, 8))
        
        # Modern hashtag input with placeholder-like styling
        self.hashtag_entry = tk.Entry(
            input_container,
            textvariable=self.hashtag_input_var,
            bg=self.INPUT_BG,
            fg=self.TEXT_COLOR,
            insertbackground=self.TEXT_COLOR,
            font=("SF Pro Display", 13) if self.is_macos() else ("Segoe UI", 11),
            bd=1,
            relief="solid",
            highlightthickness=1,
            highlightcolor=self.ACCENT_COLOR,
            highlightbackground=self.BORDER_COLOR
        )
        self.hashtag_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, ipadx=12)
        
        # Bind Enter key and focus events
        self.hashtag_entry.bind('<Return>', lambda e: self.add_hashtag())
        self.hashtag_entry.bind('<FocusIn>', self.on_entry_focus_in)
        self.hashtag_entry.bind('<FocusOut>', self.on_entry_focus_out)
        
        # Modern button container
        button_container = tk.Frame(input_container, bg=self.SECONDARY_BG)
        button_container.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Add button with secondary style
        add_btn = ttk.Button(
            button_container,
            text="Add",
            command=self.add_hashtag,
            style="Secondary.TButton"
        )
        add_btn.pack(side=tk.RIGHT, padx=(0, 8))
        
        # Clear all button with secondary style
        clear_btn = ttk.Button(
            button_container,
            text="Clear All",
            command=self.clear_all_hashtags,
            style="Secondary.TButton"
        )
        clear_btn.pack(side=tk.RIGHT)
        
        # Container for hashtag display
        self.hashtag_display_frame = tk.Frame(parent, bg=self.SECONDARY_BG)
        self.hashtag_display_frame.grid(row=start_row+1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        
    def add_button_hover_effects(self, add_btn, clear_btn):
        """Add modern hover effects to buttons"""
        # Add button hover effects
        def on_add_enter(e):
            add_btn.configure(bg=self.ACCENT_HOVER)
        def on_add_leave(e):
            add_btn.configure(bg=self.ACCENT_COLOR)
            
        add_btn.bind("<Enter>", on_add_enter)
        add_btn.bind("<Leave>", on_add_leave)
        
        # Clear button hover effects
        def on_clear_enter(e):
            clear_btn.configure(bg=self.BORDER_COLOR, fg=self.TEXT_COLOR)
        def on_clear_leave(e):
            clear_btn.configure(bg=self.INPUT_BG, fg=self.SECONDARY_TEXT)
            
        clear_btn.bind("<Enter>", on_clear_enter)
        clear_btn.bind("<Leave>", on_clear_leave)
        
    def on_entry_focus_in(self, event):
        """Handle entry focus in - modern Instagram-like effect"""
        self.hashtag_entry.configure(highlightthickness=2)
        
    def on_entry_focus_out(self, event):
        """Handle entry focus out"""
        self.hashtag_entry.configure(highlightthickness=1)
        
    def create_modern_checkbox(self, parent, row):
        """Create a modern Instagram-like checkbox"""
        checkbox_frame = tk.Frame(parent, bg=self.SECONDARY_BG)
        checkbox_frame.grid(row=row, column=0, columnspan=2, sticky="w", pady=(20, 0))
        
        # Custom checkbox using a frame and label
        self.checkbox_container = tk.Frame(
            checkbox_frame,
            bg=self.INPUT_BG,
            width=20,
            height=20,
            relief="solid",
            bd=1
        )
        self.checkbox_container.pack(side=tk.LEFT, padx=(0, 12))
        self.checkbox_container.pack_propagate(False)
        
        # Checkmark label
        self.checkmark_label = tk.Label(
            self.checkbox_container,
            text="✓",
            bg=self.INPUT_BG,
            fg=self.ACCENT_COLOR,
            font=("SF Pro Display", 14, "bold") if self.is_macos() else ("Segoe UI", 12, "bold")
        )
        
        # Checkbox text
        self.checkbox_text = tk.Label(
            checkbox_frame,
            text="Allow comments on sensitive/NSFW images",
            bg=self.SECONDARY_BG,
            fg=self.TEXT_COLOR,
            font=("SF Pro Display", 13) if self.is_macos() else ("Segoe UI", 11),
        )
        self.checkbox_text.pack(side=tk.LEFT)
        
        # Bind click events
        self.checkbox_container.bind("<Button-1>", self.toggle_checkbox)
        self.checkbox_text.bind("<Button-1>", self.toggle_checkbox)
        
        # Update checkbox display
        self.update_checkbox_display()
        
    def toggle_checkbox(self, event=None):
        """Toggle the custom checkbox"""
        current_value = self.allow_sensitive_var.get()
        self.allow_sensitive_var.set(not current_value)
        self.update_checkbox_display()
        
    def update_checkbox_display(self):
        """Update the checkbox visual state"""
        if self.allow_sensitive_var.get():
            self.checkbox_container.configure(bg=self.ACCENT_COLOR, highlightbackground=self.ACCENT_COLOR)
            self.checkmark_label.configure(bg=self.ACCENT_COLOR, fg=self.TEXT_COLOR)
            self.checkmark_label.pack(expand=True)
        else:
            self.checkbox_container.configure(bg=self.INPUT_BG, highlightbackground=self.BORDER_COLOR)
            self.checkmark_label.configure(bg=self.INPUT_BG, fg=self.INPUT_BG)
            self.checkmark_label.pack(expand=True)
            
    def create_modern_buttons(self, parent, row):
        """Create modern Instagram-style action buttons"""
        button_section = tk.Frame(parent, bg=self.SECONDARY_BG)
        button_section.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(30, 10))
        
        # Configure grid weights
        button_section.grid_columnconfigure(0, weight=1)
        button_section.grid_columnconfigure(1, weight=1)
        
        # Save Settings button
        save_btn = ttk.Button(
            button_section,
            text="Save Settings",
            command=self.save_settings,
            style="TButton"
        )
        save_btn.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        
        # Run Bot button
        run_btn = ttk.Button(
            button_section,
            text="Run Bot",
            command=self.start_bot,
            style="TButton"
        )
        run_btn.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        
        # View Statistics button
        stats_btn = ttk.Button(
            button_section,
            text="View Statistics",
            command=self.show_stats,
            style="Secondary.TButton"
        )
        stats_btn.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        
    def is_macos(self):
        """Check if running on macOS for font selection"""
        import platform
        return platform.system() == "Darwin"
        
    def create_header(self):
        """Create a modern Instagram-like header"""
        header_frame = tk.Frame(self.root, bg=self.PRIMARY_BG, padx=30, pady=20)
        header_frame.pack(fill=tk.X)
        
        # Main title with Instagram-like styling
        title_frame = tk.Frame(header_frame, bg=self.PRIMARY_BG)
        title_frame.pack(fill=tk.X)
        
        title_label = tk.Label(
            title_frame,
            text="InstaBot",
            bg=self.PRIMARY_BG,
            fg=self.TEXT_COLOR,
            font=("SF Pro Display", 28, "bold") if self.is_macos() else ("Segoe UI", 24, "bold")
        )
        title_label.pack(side=tk.LEFT)
        
        # Stats section on the right
        stats_frame = tk.Frame(title_frame, bg=self.PRIMARY_BG)
        stats_frame.pack(side=tk.RIGHT)
        
        try:
            stats = get_stats()
            likes_count = stats.get('like', 0)
            comments_count = stats.get('comment', 0)
            
            stats_container = tk.Frame(stats_frame, bg=self.PRIMARY_BG)
            stats_container.pack(side=tk.RIGHT)
            
            # Likes stat
            likes_label = tk.Label(
                stats_container,
                text=f"Likes: {likes_count}",
                bg=self.PRIMARY_BG,
                fg=self.ACCENT_COLOR,
                font=("SF Pro Display", 14, "bold") if self.is_macos() else ("Segoe UI", 12, "bold")
            )
            likes_label.pack(side=tk.LEFT, padx=(0, 16))
            
            # Comments stat
            comments_label = tk.Label(
                stats_container,
                text=f"Comments: {comments_count}",
                bg=self.PRIMARY_BG,
                fg=self.ACCENT_COLOR,
                font=("SF Pro Display", 14, "bold") if self.is_macos() else ("Segoe UI", 12, "bold")
            )
            comments_label.pack(side=tk.LEFT)
            
        except Exception:
            # If no stats available, show placeholder with better contrast
            placeholder_label = tk.Label(
                stats_frame,
                text="No activity yet",
                bg=self.PRIMARY_BG,
                fg=self.TEXT_COLOR,  # Better contrast
                font=("SF Pro Display", 13) if self.is_macos() else ("Segoe UI", 11)  # Increased size
            )
            placeholder_label.pack(side=tk.RIGHT)
            
        # Add subtle separator line
        separator = tk.Frame(header_frame, bg=self.BORDER_COLOR, height=1)
        separator.pack(fill=tk.X, pady=(10, 0))
            
    def create_content(self):
        # Main container with padding
        main_container = tk.Frame(
            self.root,
            bg=self.PRIMARY_BG,
            padx=30,
            pady=20
        )
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create a card-like container for the form
        card_frame = tk.Frame(
            main_container,
            bg=self.SECONDARY_BG,
            relief="flat",
            bd=0
        )
        card_frame.pack(fill=tk.BOTH, padx=20, pady=10)
        
        # Add subtle border effect
        border_frame = tk.Frame(
            card_frame,
            bg=self.BORDER_COLOR,
            height=1
        )
        border_frame.pack(fill=tk.X, side=tk.TOP)
        
        # Inner content with proper padding
        content_frame = tk.Frame(
            card_frame,
            bg=self.SECONDARY_BG,
            padx=30,
            pady=25
        )
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights for responsive design
        content_frame.grid_columnconfigure(1, weight=1)
        
        # Form fields with modern styling
        fields = [
            ("Instagram Username", self.username_var, False),
            ("Instagram Password", self.password_var, True),
            ("OpenAI API Key", self.openai_var, True),
            ("Likes per day", self.likes_var, False),
            ("Comments per day", self.comments_var, False)
        ]
        
        for i, (field_label, field_var, is_password) in enumerate(fields):
            # Field label with modern styling
            label = ttk.Label(
                content_frame, 
                text=field_label,
                background=self.SECONDARY_BG
            )
            label.grid(row=i, column=0, sticky="w", pady=(12, 4), padx=(0, 15))
            
            # Entry field with modern styling
            entry = ttk.Entry(
                content_frame, 
                textvariable=field_var,
                show="•" if is_password else None,
                width=35,
                font=("SF Pro Display", 13) if self.is_macos() else ("Segoe UI", 11)
            )
            entry.grid(row=i, column=1, pady=(12, 4), sticky="ew")
        
        # Custom hashtag section with modern design
        self.create_modern_hashtag_section(content_frame, len(fields))
        
        # Modern checkbox for sensitive content
        self.create_modern_checkbox(content_frame, len(fields) + 2)
        
        # Action buttons with modern styling
        self.create_modern_buttons(content_frame, len(fields) + 3)
        
    def remove_hashtag(self, hashtag):
        """Remove a hashtag from the list"""
        if hashtag in self.hashtags_list:
            self.hashtags_list.remove(hashtag)
            self.update_hashtag_display()
            self.status_var.set(f"Removed #{hashtag}")
            
    def clear_all_hashtags(self):
        """Clear all hashtags after confirmation"""
        if not self.hashtags_list:
            self.status_var.set("No hashtags to clear")
            return
            
        if messagebox.askyesno("Clear All Hashtags", 
                              f"Are you sure you want to remove all {len(self.hashtags_list)} hashtags?"):
            self.hashtags_list.clear()
            self.update_hashtag_display()
            self.status_var.set("All hashtags cleared")
            
    def add_hashtag(self):
        """Add a hashtag to the list with modern validation"""
        hashtag = self.hashtag_input_var.get().strip()
        
        # Remove # if user included it
        if hashtag.startswith('#'):
            hashtag = hashtag[1:]
            
        # Validate hashtag
        if not hashtag:
            self.status_var.set("Please enter a hashtag")
            return
            
        # Check for invalid characters
        if not hashtag.replace('_', '').isalnum():
            self.show_modern_message("Invalid Hashtag", "Hashtags can only contain letters, numbers, and underscores!", "warning")
            return
            
        if hashtag.lower() in [h.lower() for h in self.hashtags_list]:
            self.show_modern_message("Duplicate", f"Hashtag '{hashtag}' already exists!", "warning")
            self.hashtag_input_var.set("")  # Clear input even on duplicate
            return
            
        # Check maximum hashtags (Instagram allows up to 30)
        if len(self.hashtags_list) >= 30:
            self.show_modern_message("Too Many Hashtags", "Maximum 30 hashtags allowed!", "warning")
            return
            
        # Add to list
        self.hashtags_list.append(hashtag)
        self.hashtag_input_var.set("")  # Clear input
        self.update_hashtag_display()
        self.update_status_bar()
        self.status_var.set(f"Added #{hashtag}")
        
    def show_modern_message(self, title, message, msg_type="info"):
        """Show a modern message dialog"""
        if msg_type == "warning":
            messagebox.showwarning(title, message)
        elif msg_type == "error":
            messagebox.showerror(title, message)
        else:
            messagebox.showinfo(title, message)
            
    def update_status_bar(self):
        """Update the status bar with current information"""
        # This will be called to refresh hashtag count in status bar
        pass
        
    def update_hashtag_display(self):
        """Update the display of hashtags with modern Instagram-like design"""
        # Clear existing widgets
        for widget in self.hashtag_display_frame.winfo_children():
            widget.destroy()
            
        if not self.hashtags_list:
            # Show elegant placeholder
            placeholder_frame = tk.Frame(self.hashtag_display_frame, bg=self.SECONDARY_BG)
            placeholder_frame.pack(fill=tk.X, pady=(16, 8))
            
            placeholder = tk.Label(
                placeholder_frame,
                text="No hashtags added yet",
                bg=self.SECONDARY_BG,
                fg=self.TEXT_COLOR,  # Better contrast
                font=("SF Pro Display", 13) if self.is_macos() else ("Segoe UI", 11),  # Increased size
                pady=12
            )
            placeholder.pack()
            return
            
        # Responsive hashtag container using grid
        hashtag_container = tk.Frame(self.hashtag_display_frame, bg=self.SECONDARY_BG)
        hashtag_container.pack(fill=tk.BOTH, expand=True, pady=(16, 8))
        max_cols = 3  # Number of pills per row before wrapping
        for i, hashtag in enumerate(self.hashtags_list):
            pill_frame = tk.Frame(
                hashtag_container,
                bg=self.INPUT_BG,
                relief="flat",
                bd=0,
                highlightbackground=self.BORDER_COLOR,
                highlightthickness=1
            )
            pill_frame.grid(row=i // max_cols, column=i % max_cols, padx=6, pady=4, sticky="w")
            hashtag_label = tk.Label(
                pill_frame,
                text=f"#{hashtag}",
                bg=self.INPUT_BG,
                fg=self.TEXT_COLOR,
                font=("SF Pro Display", 12) if self.is_macos() else ("Segoe UI", 11),
                padx=10,
                pady=6,
                wraplength=120,  # Prevents overflow, wraps long hashtags
                anchor="w"
            )
            hashtag_label.pack(side=tk.LEFT)
            remove_btn = tk.Label(
                pill_frame,
                text="×",
                bg=self.INPUT_BG,
                fg=self.SECONDARY_TEXT,
                font=("SF Pro Display", 16) if self.is_macos() else ("Segoe UI", 14),
                padx=8,
                pady=6
            )
            remove_btn.pack(side=tk.RIGHT)
            remove_btn.bind("<Button-1>", lambda e, h=hashtag: self.remove_hashtag(h))
            def create_hover_effects(pill, label, btn, hashtag_text):
                def on_enter(e):
                    pill.configure(bg=self.BORDER_COLOR)
                    label.configure(bg=self.BORDER_COLOR)
                    btn.configure(bg=self.BORDER_COLOR, fg=self.ERROR_COLOR)
                def on_leave(e):
                    pill.configure(bg=self.INPUT_BG)
                    label.configure(bg=self.INPUT_BG)
                    btn.configure(bg=self.INPUT_BG, fg=self.SECONDARY_TEXT)
                for widget in [pill, label, btn]:
                    widget.bind("<Enter>", on_enter)
                    widget.bind("<Leave>", on_leave)
            create_hover_effects(pill_frame, hashtag_label, remove_btn, hashtag)
        
    def create_status_bar(self):
        """Create a modern Instagram-like status bar"""
        # Top border
        border_frame = tk.Frame(self.root, bg=self.BORDER_COLOR, height=1)
        border_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Status bar container
        status_bar = tk.Frame(self.root, bg=self.PRIMARY_BG, padx=30, pady=12)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Status message on the left with better contrast
        status_label = tk.Label(
            status_bar,
            textvariable=self.status_var,
            bg=self.PRIMARY_BG,
            fg=self.TEXT_COLOR,
            font=("SF Pro Text", 12) if self.is_macos() else ("Segoe UI", 11)
        )
        status_label.pack(side=tk.LEFT)
        info_frame = tk.Frame(status_bar, bg=self.PRIMARY_BG)
        info_frame.pack(side=tk.LEFT, padx=(30, 0))
        try:
            stats = get_stats()
            total_actions = sum(stats.values())
            info_text = f"Total actions: {total_actions}"
        except:
            info_text = "Total actions: 0"
        info_label = tk.Label(
            info_frame,
            text=info_text,
            bg=self.PRIMARY_BG,
            fg=self.TEXT_COLOR,  # Use TEXT_COLOR for readability
            font=("SF Pro Text", 12) if self.is_macos() else ("Segoe UI", 11)
        )
        info_label.pack(side=tk.LEFT)
        hashtag_info = tk.Label(
            info_frame,
            text=f" • Hashtags: {len(self.hashtags_list)}/30",
            bg=self.PRIMARY_BG,
            fg=self.TEXT_COLOR,  # Use TEXT_COLOR for readability
            font=("SF Pro Text", 12, "bold") if self.is_macos() else ("Segoe UI", 11, "bold")
        )
        hashtag_info.pack(side=tk.LEFT)
        # Timestamp on the right with better contrast
        timestamp = datetime.now().strftime("%H:%M")
        time_label = tk.Label(
            status_bar,
            text=timestamp,
            bg=self.PRIMARY_BG,
            fg=self.TEXT_COLOR,  # Use TEXT_COLOR for readability
            font=("SF Pro Text", 12) if self.is_macos() else ("Segoe UI", 11)
        )
        time_label.pack(side=tk.RIGHT)
    
    def load_config_to_ui(self):
        """Load configuration to UI with error handling"""
        try:
            with open(CONFIG_FILE) as f:
                cfg = json.load(f)
                
            self.username_var.set(cfg.get("instagram_username", ""))
            self.password_var.set(cfg.get("instagram_password", ""))
            self.openai_var.set(cfg.get("openai_api_key", ""))
            self.hashtags_list = cfg.get("hashtags", [])
            self.likes_var.set(str(cfg.get("likes_per_day", 50)))
            self.comments_var.set(str(cfg.get("comments_per_day", 15)))
            self.allow_sensitive_var.set(cfg.get("allow_sensitive", True))
            
            # Update checkbox display if it exists
            if hasattr(self, 'checkbox_container'):
                self.update_checkbox_display()
                
        except Exception:
            # Set defaults if config doesn't exist or is invalid
            self.hashtags_list = []
            self.allow_sensitive_var.set(True)
            
    def save_config(self, cfg):
        with open(CONFIG_FILE, "w") as f:
            json.dump(cfg, f, indent=2)
            
    def save_settings(self):
        """Save settings with modern validation and feedback"""
        # Validate hashtags
        if not self.hashtags_list:
            if not messagebox.askyesno("No Hashtags", "You haven't added any hashtags. Continue saving?"):
                return
                
        try:
            cfg = {
                "instagram_username": self.username_var.get(),
                "instagram_password": self.password_var.get(),
                "openai_api_key": self.openai_var.get(),
                "hashtags": self.hashtags_list,
                "likes_per_day": int(self.likes_var.get()) if self.likes_var.get().isdigit() else 50,
                "comments_per_day": int(self.comments_var.get()) if self.comments_var.get().isdigit() else 15,
                "allow_sensitive": self.allow_sensitive_var.get()
            }
            self.save_config(cfg)
            self.status_var.set("Settings saved!")
            self.show_modern_message("Success", "Settings saved successfully!")
        except Exception as e:
            self.show_modern_message("Error", f"Failed to save settings: {str(e)}", "error")
        
    def start_bot(self):
        try:
            # Validate hashtags
            if not self.hashtags_list:
                messagebox.showerror("Error", "Please add at least one hashtag before running the bot!")
                return
                
            # Get current config
            cfg = {
                "instagram_username": self.username_var.get(),
                "instagram_password": self.password_var.get(),
                "openai_api_key": self.openai_var.get(),
                "hashtags": self.hashtags_list,
                "likes_per_day": int(self.likes_var.get()),
                "comments_per_day": int(self.comments_var.get()),
                "allow_sensitive": self.allow_sensitive_var.get()
            }
            
            # Save before running
            self.save_config(cfg)
            
            # Setup OpenAI
            set_api_key(cfg['openai_api_key'])
            
            # Update status
            self.status_var.set("Logging in to Instagram...")
            self.root.update()
            
            # Login to Instagram
            cl = login_instagram(cfg['instagram_username'], cfg['instagram_password'])
            
            # Update status
            self.status_var.set("Running bot actions...")
            self.root.update()
            
            # Run the bot in a background thread
            def bot_task():
                try:
                    # Run the bot
                    like_and_comment(
                        cl,
                        cfg['hashtags'],
                        cfg['likes_per_day'],
                        cfg['comments_per_day'],
                        generate_comment,
                        allow_sensitive=cfg['allow_sensitive']
                    )
                    
                    # Update status
                    self.root.after(0, lambda: self.status_var.set("Completed! Check logs for details."))
                    messagebox.showinfo("Success", "Bot actions completed successfully!")
                    
                except Exception as e:
                    self.root.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
                    messagebox.showerror("Error", str(e))
            
            threading.Thread(target=bot_task, daemon=True).start()
            
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", str(e))
            
    def show_stats(self):
        """Open the statistics window"""
        try:
            stats_window = create_stats_window(self.root)
            self.status_var.set("Viewing statistics...")
        except Exception as e:
            self.status_var.set(f"Error showing stats: {str(e)}")
            messagebox.showerror("Error", f"Could not display statistics: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = InstaBotApp(root)
    root.mainloop()
