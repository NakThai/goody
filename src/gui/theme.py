"""GUI theme configuration."""
import customtkinter as ctk

def setup_theme():
    """Configure the application theme."""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    # Custom colors
    ctk.ThemeManager.theme["CTkButton"]["fg_color"] = ["#2B87D3", "#1B77C3"]
    ctk.ThemeManager.theme["CTkButton"]["hover_color"] = ["#1B77C3", "#0B67B3"]
    
    # Custom fonts
    ctk.ThemeManager.theme["CTkLabel"]["font"] = ("Roboto", 12)
    ctk.ThemeManager.theme["CTkButton"]["font"] = ("Roboto", 12, "bold")
    ctk.ThemeManager.theme["CTkCheckBox"]["font"] = ("Roboto", 12)
    ctk.ThemeManager.theme["CTkEntry"]["font"] = ("Roboto", 12)