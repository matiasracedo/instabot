#!/usr/bin/env python3
"""
Preview script to show the new Instagram-like UI
"""
import tkinter as tk
from main import InstaBotApp

def preview_ui():
    """Launch the UI for preview"""
    root = tk.Tk()
    app = InstaBotApp(root)
    
    # Add some sample hashtags for preview
    app.hashtags_list = ["photography", "travel", "food", "lifestyle"]
    app.update_hashtag_display()
    
    print("🎨 Instagram-like UI Preview Launched!")
    print("📱 The new design features:")
    print("   • True black Instagram-inspired background")
    print("   • Modern card-based layout")
    print("   • Custom checkbox with hover effects") 
    print("   • Instagram-style hashtag pills")
    print("   • SF Pro Display fonts on macOS")
    print("   • Proper spacing and modern buttons")
    print("")
    print("Close the window when you're done previewing.")
    
    root.mainloop()

if __name__ == "__main__":
    preview_ui()
