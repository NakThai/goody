"""Status panel component for displaying logs."""
import customtkinter as ctk
import logging
from datetime import datetime

class StatusPanel:
    def __init__(self, parent):
        self.frame = ctk.CTkFrame(parent)
        self.frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        # Configure grid
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(1, weight=1)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self.frame,
            text="Status Log",
            font=("Roboto", 16, "bold")
        )
        self.status_label.grid(row=0, column=0, pady=(10, 5))
        
        # Log text area
        self.log_text = ctk.CTkTextbox(
            self.frame,
            height=200,
            wrap="word"
        )
        self.log_text.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        # Setup custom logging handler
        self.setup_logging_handler()
        
    def log_message(self, level: str, message: str):
        """Log a message with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {level}: {message}\n"
        
        # Add color based on log level
        if level == "ERROR":
            formatted_message = f"\033[91m{formatted_message}\033[0m"  # Red
        elif level == "WARNING":
            formatted_message = f"\033[93m{formatted_message}\033[0m"  # Yellow
        elif level == "INFO":
            formatted_message = f"\033[92m{formatted_message}\033[0m"  # Green
            
        self.log_text.insert("end", formatted_message)
        self.log_text.see("end")
        
    def setup_logging_handler(self):
        """Setup custom logging handler."""
        class TextHandler(logging.Handler):
            def __init__(self, text_widget):
                logging.Handler.__init__(self)
                self.text_widget = text_widget
                
            def emit(self, record):
                msg = self.format(record)
                self.text_widget.log_message(record.levelname, msg)
                
        # Create and configure handler
        handler = TextHandler(self)
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        
        # Add handler to root logger to capture all logs
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        
    def clear_log(self):
        """Clear log text area."""
        self.log_text.delete("1.0", "end")