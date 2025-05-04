import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
from panorama import extract_frames, create_panorama

class PanoramaUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Panorama Generator")
        self.root.geometry("700x500")
        self.root.configure(bg='#f0f0f0')
        
        # Configure style
        style = ttk.Style()
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10), padding=5)
        style.configure('TEntry', padding=5)
        style.configure('Header.TLabel', font=('Arial', 16, 'bold'), background='#f0f0f0')
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        ttk.Label(header_frame, text="Panorama Generator", style='Header.TLabel').pack()
        
        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="Input Settings", padding="10")
        input_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Input video file
        ttk.Label(input_frame, text="Input MP4 File:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.input_path = tk.StringVar()
        input_entry = ttk.Entry(input_frame, textvariable=self.input_path, width=50)
        input_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(0, 5))
        ttk.Button(input_frame, text="Browse", command=self.browse_input, style='TButton').grid(row=0, column=2, padx=5)
        
        # Key frames directory
        ttk.Label(input_frame, text="Key Frames Directory:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.frames_dir = tk.StringVar()
        frames_entry = ttk.Entry(input_frame, textvariable=self.frames_dir, width=50)
        frames_entry.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(0, 5))
        ttk.Button(input_frame, text="Browse", command=self.browse_frames, style='TButton').grid(row=1, column=2, padx=5)
        
        # Output section
        output_frame = ttk.LabelFrame(main_frame, text="Output Settings", padding="10")
        output_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Output file
        ttk.Label(output_frame, text="Output File:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.output_path = tk.StringVar()
        output_entry = ttk.Entry(output_frame, textvariable=self.output_path, width=50)
        output_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(0, 5))
        ttk.Button(output_frame, text="Browse", command=self.browse_output, style='TButton').grid(row=0, column=2, padx=5)
        
        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(progress_frame, length=500, mode='determinate', style='TProgressbar')
        self.progress.grid(row=0, column=0, columnspan=3, pady=10)
        
        # Status label
        self.status = tk.StringVar()
        self.status.set("Ready")
        status_label = ttk.Label(progress_frame, textvariable=self.status, style='TLabel')
        status_label.grid(row=1, column=0, columnspan=3, pady=5)
        
        # Generate button
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=20)
        ttk.Button(button_frame, text="Generate Panorama", command=self.generate_panorama, 
                  style='TButton').pack(pady=10)
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=1)
        
        # Make the window resizable
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
    
    def browse_input(self):
        filename = filedialog.askopenfilename(
            title="Select MP4 File",
            filetypes=[("MP4 files", "*.mp4")]
        )
        if filename:
            self.input_path.set(filename)
    
    def browse_frames(self):
        directory = filedialog.askdirectory(title="Select Key Frames Directory")
        if directory:
            self.frames_dir.set(directory)
    
    def browse_output(self):
        filename = filedialog.asksaveasfilename(
            title="Save Panorama As",
            defaultextension=".jpg",
            filetypes=[("JPEG files", "*.jpg")]
        )
        if filename:
            self.output_path.set(filename)
    
    def generate_panorama(self):
        # Validate inputs
        if not self.input_path.get():
            messagebox.showerror("Error", "Please select an input MP4 file")
            return
        
        if not self.frames_dir.get():
            messagebox.showerror("Error", "Please select a key frames directory")
            return
        
        if not self.output_path.get():
            messagebox.showerror("Error", "Please select an output file")
            return
        
        try:
            # Update status
            self.status.set("Extracting frames...")
            self.root.update()
            
            # Extract frames
            num_frames = extract_frames(self.input_path.get(), self.frames_dir.get())
            
            if num_frames <= 1:
                messagebox.showerror("Error", "Not enough frames extracted from the video")
                return
            
            # Update status
            self.status.set("Creating panorama...")
            self.root.update()
            
            # Create panorama
            create_panorama(self.frames_dir.get(), self.output_path.get())
            
            # Update status
            self.status.set("Panorama created successfully!")
            messagebox.showinfo("Success", "Panorama has been created successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status.set("Error occurred")
        finally:
            self.progress['value'] = 100

if __name__ == "__main__":
    root = tk.Tk()
    app = PanoramaUI(root)
    root.mainloop() 