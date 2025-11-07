import socket
import tkinter as tk
import threading
from datetime import datetime
from pygame import mixer
import os

SERVER_IP = "10.1.251.129"
SERVER_PORT = 49152

# Sound file path - adjust username if needed
SOUND_FILE = r"C:\Users\sperumea\Downloads\print alert.mp3"

class PrinterAlertClient:
    def __init__(self):
        # Initialize pygame mixer for MP3 playback
        mixer.init()
        
        # Check if sound file exists
        if not os.path.exists(SOUND_FILE):
            print(f"WARNING: Sound file not found: {SOUND_FILE}")
        
        self.window = tk.Tk()
        self.window.title("")
        self.window.overrideredirect(True)  # Remove title bar and borders
        self.window.attributes('-topmost', True)
        
        # Get screen dimensions
        screen_width = self.window.winfo_screenwidth()
        
        # Set window size and position (upper right corner)
        window_width = 180
        window_height = 60
        x_position = screen_width - window_width - 10  # 10px from right edge
        y_position = 10  # 10px from top
        
        self.window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        
        # Add a background color and border for visibility
        self.window.configure(bg='#2c2c2c', highlightthickness=1, highlightbackground='#444444')
        
        # Status label (smaller font, light text)
        self.status_label = tk.Label(
            self.window, 
            text="Connecting...", 
            font=("Arial", 7),
            bg='#2c2c2c',
            fg='#cccccc'
        )
        self.status_label.pack(pady=3)
        
        # Job label
        self.job_label = tk.Label(
            self.window, 
            text="Waiting...", 
            font=("Arial", 7, "bold"),
            bg='#2c2c2c',
            fg='#00ff00'
        )
        self.job_label.pack(pady=2)
        
        # Counter label
        self.counter_label = tk.Label(
            self.window, 
            text="Jobs: 0", 
            font=("Arial", 7),
            bg='#2c2c2c',
            fg='#cccccc'
        )
        self.counter_label.pack(pady=2)
        
        # Close button (small X in corner)
        self.close_btn = tk.Button(
            self.window,
            text="×",
            font=("Arial", 10, "bold"),
            command=self.on_close,
            bg='#2c2c2c',
            fg='#ff4444',
            bd=0,
            highlightthickness=0,
            padx=2,
            pady=0,
            cursor="hand2"
        )
        self.close_btn.place(x=window_width-20, y=2)
        
        # Make window draggable
        self.window.bind('<Button-1>', self.start_drag)
        self.window.bind('<B1-Motion>', self.on_drag)
        
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        self.client_socket = None
        self.connected = False
        self.total_detected = 0
        self.running = True
        
        # Start connection thread
        self.thread = threading.Thread(target=self.listen_for_jobs, daemon=True)
        self.thread.start()
        
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        self.window.mainloop()
    
    def start_drag(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y
    
    def on_drag(self, event):
        x = self.window.winfo_x() + event.x - self.drag_start_x
        y = self.window.winfo_y() + event.y - self.drag_start_y
        self.window.geometry(f"+{x}+{y}")
    
    def connect_to_server(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((SERVER_IP, SERVER_PORT))
            self.client_socket.settimeout(1.0)
            self.connected = True
            self.update_status("Connected", "#00ff00")
            return True
        except Exception as e:
            self.update_status("No connection", "#ff4444")
            self.connected = False
            return False
    
    def listen_for_jobs(self):
        import time
        while self.running:
            try:
                if not self.connected:
                    if not self.connect_to_server():
                        time.sleep(2)
                        continue
                
                # Listen for messages from server
                try:
                    data = self.client_socket.recv(1024)
                    if data:
                        message = data.decode('ascii').strip()
                        if message == "PRINT_JOB":
                            self.on_print_job_detected()
                    else:
                        # Connection closed
                        self.connected = False
                        if self.client_socket:
                            self.client_socket.close()
                        self.update_status("Reconnecting...", "#ffaa00")
                except socket.timeout:
                    pass  # No data, continue
                except:
                    self.connected = False
                    if self.client_socket:
                        self.client_socket.close()
                    self.update_status("Reconnecting...", "#ffaa00")
                    
            except Exception as e:
                time.sleep(1)
    
    def on_print_job_detected(self):
        # Play custom MP3 sound
        try:
            if os.path.exists(SOUND_FILE):
                mixer.music.load(SOUND_FILE)
                mixer.music.play()
            else:
                print(f"Sound file not found: {SOUND_FILE}")
        except Exception as e:
            print(f"Error playing sound: {e}")
        
        self.total_detected += 1
        current_time = datetime.now().strftime("%I:%M %p")  # Shorter time format
        
        self.job_label.config(
            text=f"Job! {current_time}", 
            fg="#00ff00"
        )
        self.counter_label.config(text=f"Jobs: {self.total_detected}")
        self.status_label.config(text="Monitoring", fg="#00ff00")
    
    def update_status(self, text, color):
        self.status_label.config(text=text, fg=color)
    
    def on_close(self):
        self.running = False
        if self.client_socket:
            self.client_socket.close()
        mixer.quit()
        self.window.destroy()

if __name__ == "__main__":
    import time
    app = PrinterAlertClient()
