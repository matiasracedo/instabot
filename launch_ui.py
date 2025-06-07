#!/usr/bin/env python3
"""
Quick launcher for the new Instagram-inspired InstaBot UI
"""
import tkinter as tk
from main import InstaBotApp

if __name__ == "__main__":
    print("🚀 Launching Instagram-inspired InstaBot UI...")
    print("✨ Features:")
    print("   • True Instagram black background")
    print("   • Modern hashtag pill management") 
    print("   • Custom checkbox with animations")
    print("   • Professional button styling")
    print("   • SF Pro Display fonts (macOS)")
    print("   • Smooth hover effects")
    print("")
    
    root = tk.Tk()
    app = InstaBotApp(root)
    
    print("📱 UI launched! Check your screen for the application.")
    root.mainloop()
    print("👋 Thanks for using InstaBot!")
