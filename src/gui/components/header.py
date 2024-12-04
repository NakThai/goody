import customtkinter as ctk
from PIL import Image
import os

def create_header(parent):
    """Create the application header."""
    header_frame = ctk.CTkFrame(parent, fg_color="transparent")
    header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 0))
    
    # Title
    title = ctk.CTkLabel(
        header_frame,
        text="Bot Manager Pro",
        font=("Roboto", 24, "bold")
    )
    title.pack(pady=10)
    
    # Subtitle
    subtitle = ctk.CTkLabel(
        header_frame,
        text="Automated Browser Management System",
        font=("Roboto", 14)
    )
    subtitle.pack(pady=(0, 10))
    
    return header_frame