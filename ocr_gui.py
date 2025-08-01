"""
Simple GUI Launcher untuk OCR ML Engine
=======================================

Simple GUI interface untuk launch web API dan show system info.

Author: AI Assistant
Date: August 2025
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import webbrowser
import threading
import time
from pathlib import Path

# Add project root ke Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class SimpleGUI:
    """Simple GUI untuk OCR ML Engine launcher"""
    
    def __init__(self):
        """Initialize GUI"""
        self.root = tk.Tk()
        self.root.title("OCR ML Engine - Launcher")
        self.root.geometry("500x400")
        
        # Center window
        self.root.geometry("+{}+{}".format(
            (self.root.winfo_screenwidth() // 2) - 250,
            (self.root.winfo_screenheight() // 2) - 200
        ))
        
        self.web_process = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="OCR ML Engine", 
                               font=("Arial", 18, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Description
        desc_label = ttk.Label(main_frame, 
                              text="Multi-interface OCR system with Tesseract and EasyOCR",
                              font=("Arial", 10))
        desc_label.pack(pady=(0, 30))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Web API button
        self.web_button = ttk.Button(buttons_frame, text="Start Web API Server", 
                                    command=self.start_web_api, style="Accent.TButton")
        self.web_button.pack(fill=tk.X, pady=(0, 10))
        
        # Stop web API button
        self.stop_button = ttk.Button(buttons_frame, text="Stop Web API Server", 
                                     command=self.stop_web_api, state=tk.DISABLED)
        self.stop_button.pack(fill=tk.X, pady=(0, 10))
        
        # Open web interface
        self.browser_button = ttk.Button(buttons_frame, text="Open Web Interface", 
                                        command=self.open_browser, state=tk.DISABLED)
        self.browser_button.pack(fill=tk.X, pady=(0, 10))
        
        # CLI button
        ttk.Button(buttons_frame, text="Open Command Line Interface", 
                  command=self.open_cli).pack(fill=tk.X, pady=(0, 10))
        
        # System info button
        ttk.Button(buttons_frame, text="Show System Information", 
                  command=self.show_system_info).pack(fill=tk.X, pady=(0, 10))
        
        # Install dependencies button
        ttk.Button(buttons_frame, text="Install Dependencies", 
                  command=self.install_dependencies).pack(fill=tk.X, pady=(0, 20))
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.pack(fill=tk.BOTH, expand=True)
        
        # Status text
        self.status_text = tk.Text(status_frame, height=8, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Initial status
        self.log_message("OCR ML Engine GUI ready")
        self.log_message("Click 'Start Web API Server' to begin")
    
    def log_message(self, message: str):
        """Log message to status area"""
        timestamp = time.strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        self.root.update_idletasks()
    
    def start_web_api(self):
        """Start web API server"""
        try:
            self.log_message("Starting web API server...")
            
            # Start server in background thread
            thread = threading.Thread(target=self._run_web_server)
            thread.daemon = True
            thread.start()
            
            # Update UI
            self.web_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            
            # Enable browser button after delay
            self.root.after(3000, lambda: self.browser_button.config(state=tk.NORMAL))
            
        except Exception as e:
            self.log_message(f"Error starting web server: {e}")
            messagebox.showerror("Error", f"Failed to start web server: {e}")
    
    def _run_web_server(self):
        """Run web server in background"""
        try:
            # Start web server using app_launcher
            self.web_process = subprocess.Popen(
                [sys.executable, "app_launcher.py", "--web", "--host", "127.0.0.1", "--port", "5000"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                cwd=str(project_root)
            )
            
            self.root.after(0, lambda: self.log_message("Web API server started on http://127.0.0.1:5000"))
            
            # Monitor process output
            for line in iter(self.web_process.stdout.readline, ''):
                if self.web_process.poll() is not None:
                    break
                self.root.after(0, lambda l=line: self.log_message(f"Server: {l.strip()}"))
            
        except Exception as e:
            self.root.after(0, lambda: self.log_message(f"Web server error: {e}"))
    
    def stop_web_api(self):
        """Stop web API server"""
        try:
            if self.web_process:
                self.web_process.terminate()
                self.web_process = None
                self.log_message("Web API server stopped")
            
            # Update UI
            self.web_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.browser_button.config(state=tk.DISABLED)
            
        except Exception as e:
            self.log_message(f"Error stopping web server: {e}")
    
    def open_browser(self):
        """Open web interface in browser"""
        try:
            webbrowser.open("http://127.0.0.1:5000")
            self.log_message("Opened web interface in browser")
        except Exception as e:
            self.log_message(f"Error opening browser: {e}")
    
    def open_cli(self):
        """Open CLI in new terminal"""
        try:
            if sys.platform.startswith('win'):
                # Windows
                subprocess.Popen(['cmd', '/c', 'start', 'cmd', '/k', 
                                f'cd /d "{project_root}" && python ocr_cli.py --help'])
            else:
                # Unix/Linux/Mac
                subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', 
                                f'cd "{project_root}" && python ocr_cli.py --help; exec bash'])
            
            self.log_message("Opened CLI in new terminal")
            
        except Exception as e:
            self.log_message(f"Error opening CLI: {e}")
            messagebox.showerror("Error", f"Failed to open CLI: {e}")
    
    def show_system_info(self):
        """Show system information"""
        try:
            self.log_message("Checking system information...")
            
            # Run system info check
            result = subprocess.run(
                [sys.executable, "app_launcher.py", "--info"],
                capture_output=True,
                text=True,
                cwd=str(project_root)
            )
            
            if result.returncode == 0:
                # Show in new window
                self.show_info_window("System Information", result.stdout)
            else:
                self.log_message(f"System info error: {result.stderr}")
                
        except Exception as e:
            self.log_message(f"Error getting system info: {e}")
    
    def install_dependencies(self):
        """Install dependencies"""
        try:
            self.log_message("Installing dependencies...")
            
            # Disable button during installation
            for widget in self.root.winfo_children():
                if isinstance(widget, ttk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.Button):
                            child.config(state=tk.DISABLED)
            
            # Run installation in background
            thread = threading.Thread(target=self._install_deps)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self.log_message(f"Error starting installation: {e}")
    
    def _install_deps(self):
        """Install dependencies in background"""
        try:
            # Run installation
            process = subprocess.Popen(
                [sys.executable, "app_launcher.py", "--install"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                cwd=str(project_root)
            )
            
            # Monitor output
            for line in iter(process.stdout.readline, ''):
                if process.poll() is not None:
                    break
                self.root.after(0, lambda l=line: self.log_message(f"Install: {l.strip()}"))
            
            process.wait()
            
            if process.returncode == 0:
                self.root.after(0, lambda: self.log_message("Dependencies installed successfully!"))
            else:
                self.root.after(0, lambda: self.log_message("Installation failed. Check logs."))
            
        except Exception as e:
            self.root.after(0, lambda: self.log_message(f"Installation error: {e}"))
        
        finally:
            # Re-enable buttons
            self.root.after(0, self._enable_buttons)
    
    def _enable_buttons(self):
        """Re-enable all buttons"""
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Button):
                        child.config(state=tk.NORMAL)
        
        # Update web server buttons based on current state
        if self.web_process and self.web_process.poll() is None:
            self.web_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.browser_button.config(state=tk.NORMAL)
        else:
            self.web_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.browser_button.config(state=tk.DISABLED)
    
    def show_info_window(self, title: str, content: str):
        """Show information in new window"""
        info_window = tk.Toplevel(self.root)
        info_window.title(title)
        info_window.geometry("600x500")
        
        # Text widget with scrollbar
        frame = ttk.Frame(info_window, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        text_widget = tk.Text(frame, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget.insert(tk.END, content)
        text_widget.config(state=tk.DISABLED)
        
        # Close button
        ttk.Button(info_window, text="Close", 
                  command=info_window.destroy).pack(pady=10)
    
    def on_closing(self):
        """Handle window closing"""
        if self.web_process:
            try:
                self.web_process.terminate()
            except:
                pass
        
        self.root.destroy()
    
    def run(self):
        """Start GUI application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()


def main():
    """Main entry point"""
    try:
        gui = SimpleGUI()
        gui.run()
    except Exception as e:
        print(f"Error starting GUI: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
