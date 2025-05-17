import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk

class ImageViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("🖼️ Modern Image Viewer")
        self.root.geometry("1000x700")
        
        # Set background color (dark blue)
        self.root.configure(bg='#1a1a3a')
        
        # Main container frame with lighter blue background
        self.main_frame = tk.Frame(root, bg='#2d2d4d', bd=2, relief=tk.RAISED)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.image_list = []
        self.current_image = 0
        self.zoom_level = 1.0
        self.slideshow_active = False
        self.fullscreen = False

        # Resample method
        try:
            self.resample_method = Image.Resampling.LANCZOS
        except AttributeError:
            self.resample_method = Image.ANTIALIAS

        # Title label with matching color scheme
        self.label = tk.Label(self.main_frame, text="Image View Project", 
                            font=("Lucida Handwriting", 18, "bold"),
                            bg="#3d3d5d", fg="#e0e0f0", pady=10)
        self.label.pack(fill=tk.X, pady=(0,10))

        # Canvas for displaying images with dark background
        self.canvas_frame = tk.Frame(self.main_frame, bg="#1a1a2a")
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg="black", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Frame for navigation buttons
        btn_frame = tk.Frame(self.main_frame, bg="#2d2d4d")
        btn_frame.pack(fill=tk.X, pady=(10,0))

        # Custom button style with blue color scheme
        style = ttk.Style()
        style.theme_use('clam')
        
        # Base button style (blue)
        style.configure("Blue.TButton",
                      font=("Lucida Handwriting", 10, "bold"),
                      foreground="white",
                      background="#3a3a9d",
                      borderwidth=0,
                      focusthickness=3,
                      focuscolor='none',
                      padding=8,
                      relief=tk.FLAT)
        style.map("Blue.TButton",
                background=[('active', '#2a2a8d'), ('pressed', '#1a1a7d')],
                foreground=[('active', 'white')])
        
        # Accent button style (red for important actions)
        style.configure("Red.TButton",
                      font=("Lucida Handwriting", 10, "bold"),
                      foreground="white",
                      background="#ff6b6b",
                      borderwidth=0,
                      focusthickness=3,
                      focuscolor='none',
                      padding=8,
                      relief=tk.FLAT)
        style.map("Red.TButton",
                background=[('active', '#ff5b5b'), ('pressed', '#ff4b4b')],
                foreground=[('active', 'white')])

        # Button definitions with different styles
        buttons = [
            ("📂 Open", self.open_folder, "Blue"),
            ("◀ Prev", self.prev_image, "Blue"),
            ("Next ▶", self.next_image, "Blue"),
            ("🔍 +", self.zoom_in, "Blue"),
            ("🔍 -", self.zoom_out, "Blue"),
            ("▶ Slideshow", self.start_slideshow, "Red"),
            ("⏹ Stop", self.stop_slideshow, "Red"),
            ("⛶ Fullscreen", self.toggle_fullscreen, "Blue"),
            ("🚪 Exit", self.root.quit, "Red")
        ]

        # Create buttons with different styles
        for col, (text, command, style_name) in enumerate(buttons):
            btn = ttk.Button(btn_frame, text=text, command=command, 
                           style=f"{style_name}.TButton")
            btn.grid(row=0, column=col, padx=5, pady=5, sticky='ew')
            btn_frame.grid_columnconfigure(col, weight=1)

        # Status bar with dark background
        self.status = tk.Label(self.main_frame, text="Ready", 
                             font=("Arial", 9), 
                             bg="#1a1a2a", fg="#bdc3c7", 
                             anchor=tk.W, bd=1, relief=tk.SUNKEN)
        self.status.pack(side=tk.BOTTOM, fill=tk.X, pady=(5,0))

        # Make canvas expand with window
        self.root.bind("<Configure>", self.on_resize)

    def on_resize(self, event=None):
        """Handle window resize events"""
        if hasattr(self, 'image_list') and self.image_list:
            self.display_image()

    def open_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            supported_formats = (".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp")
            self.image_list = [os.path.join(folder_selected, f) for f in os.listdir(folder_selected)
                             if f.lower().endswith(supported_formats)]
            self.image_list.sort()

            if self.image_list:
                self.current_image = 0
                self.zoom_level = 1.0
                self.display_image()
                self.status.config(text=f"Loaded {len(self.image_list)} images from {os.path.basename(folder_selected)}")
            else:
                messagebox.showwarning("No Images", "No supported image files found in this folder.")
                self.status.config(text="No images found in selected folder")

    def display_image(self):
        try:
            image_path = self.image_list[self.current_image]
            img = Image.open(image_path)

            # Get canvas dimensions
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            # Calculate new size while maintaining aspect ratio
            img_width, img_height = img.size
            scale = min((canvas_width / img_width), (canvas_height / img_height)) * self.zoom_level
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)

            # Resize and display image
            img = img.resize((new_width, new_height), self.resample_method)
            self.tk_img = ImageTk.PhotoImage(img)
            
            self.canvas.delete("all")
            self.canvas.create_image(canvas_width//2, canvas_height//2, 
                                   anchor=tk.CENTER, image=self.tk_img)

            self.label.config(text=os.path.basename(image_path))
            self.status.config(text=f"Image {self.current_image+1}/{len(self.image_list)} | {img_width}x{img_height} | Zoom: {self.zoom_level:.1f}x")
        except Exception as e:
            messagebox.showerror("Error", f"Unable to load image.\n{str(e)}")
            self.status.config(text=f"Error: {str(e)}")

    def next_image(self):
        if self.image_list:
            self.current_image = (self.current_image + 1) % len(self.image_list)
            self.zoom_level = 1.0
            self.display_image()

    def prev_image(self):
        if self.image_list:
            self.current_image = (self.current_image - 1) % len(self.image_list)
            self.zoom_level = 1.0
            self.display_image()

    def zoom_in(self):
        if self.image_list:
            self.zoom_level = min(self.zoom_level * 1.25, 5.0)
            self.display_image()

    def zoom_out(self):
        if self.image_list:
            self.zoom_level = max(self.zoom_level / 1.25, 0.2)
            self.display_image()

    def start_slideshow(self):
        if not self.slideshow_active and self.image_list:
            self.slideshow_active = True
            self.status.config(text="Slideshow started (2s interval)")
            self.run_slideshow()

    def stop_slideshow(self):
        if self.slideshow_active:
            self.slideshow_active = False
            self.status.config(text="Slideshow stopped")

    def run_slideshow(self):
        if self.slideshow_active and self.image_list:
            self.next_image()
            self.root.after(2000, self.run_slideshow)

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)
        self.status.config(text="Fullscreen mode" if self.fullscreen else "Windowed mode")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageViewer(root)
    root.mainloop()