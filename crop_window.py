import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
import cv2

class CropWindow(tk.Toplevel):
    def __init__(self, parent, image_cv, initial_points):
        super().__init__(parent)
        self.title("Sesuaikan Area Scan")
        self.transient(parent); self.grab_set()

        self.image_cv = image_cv
        self.points = [list(p) for p in initial_points]

        # Menentukan ukuran & posisi window penyesuaian secara dinamis
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        # Kita buat sedikit lebih kecil dari window utama, misal 70%
        win_width = int(screen_width * 0.7)
        win_height = int(screen_height * 0.7)
        
        center_x = int(screen_width/2 - win_width / 2)
        center_y = int(screen_height/2 - win_height / 2)
        
        self.geometry(f"{win_width}x{win_height}+{center_x}+{center_y}")

        self.image_tk = None
        self.dragging_point_index = None
        self.final_points = None
        self.display_scale = 1.0

        self._setup_ui()
        self.after(50, self._display_image_and_handles)
        self.protocol("WM_DELETE_WINDOW", self._cancel)
        self.wait_window(self)

    def _setup_ui(self):     

        # 1. Buat Frame Tombol TERLEBIH DAHULU
        button_frame = tk.Frame(self)
        # Pack ke bagian BAWAH window
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        ok_button = tk.Button(button_frame, text="Terapkan (Apply)", command=self._apply_crop)
        ok_button.pack(side=tk.RIGHT, padx=5)
        
        cancel_button = tk.Button(button_frame, text="Batal (Cancel)", command=self._cancel)
        cancel_button.pack(side=tk.RIGHT)

        # 2. SETELAH ITU, baru buat dan pack Canvas
        # Canvas akan secara otomatis mengisi sisa ruang yang ada
        self.canvas = tk.Canvas(self, bg="darkgray")
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # ============================================
        
        self.canvas.bind("<Button-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<Configure>", self.on_canvas_resize)

    def on_canvas_resize(self, event):
        self._display_image_and_handles()

    def _display_image_and_handles(self):
        img_rgb = cv2.cvtColor(self.image_cv, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        w, h = img_pil.size
        canvas_w, canvas_h = self.canvas.winfo_width(), self.canvas.winfo_height()
        if canvas_w < 2 or canvas_h < 2: return
        
        ratio = min(canvas_w / w, canvas_h / h)
        self.display_scale = ratio
        new_w, new_h = int(w * self.display_scale), int(h * self.display_scale)
        img_pil_resized = img_pil.resize((new_w, new_h), Image.LANCZOS)
        
        self.image_tk = ImageTk.PhotoImage(image=img_pil_resized)
        self.canvas.delete("all")
        self.canvas.create_image(canvas_w/2, canvas_h/2, anchor=tk.CENTER, image=self.image_tk)
        self.canvas.image = self.image_tk
        self._draw_handles()

    def _draw_handles(self):
        self.canvas.delete("handle")
        canvas_w, canvas_h = self.canvas.winfo_width(), self.canvas.winfo_height()
        if self.image_tk is None: return
        img_w, img_h = self.image_tk.width(), self.image_tk.height()
        offset_x = (canvas_w - img_w) / 2
        offset_y = (canvas_h - img_h) / 2
        display_points = [(p[0] * self.display_scale + offset_x, p[1] * self.display_scale + offset_y) for p in self.points]
        self.canvas.create_polygon(display_points, fill='', outline='cyan', width=2, tags="handle")
        for x, y in display_points:
            self.canvas.create_oval(x-7, y-7, x+7, y+7, fill='red', outline='white', width=2, tags="handle")

    def _on_press(self, event):
        canvas_w, canvas_h = self.canvas.winfo_width(), self.canvas.winfo_height()
        if self.image_tk is None: return
        img_w, img_h = self.image_tk.width(), self.image_tk.height()
        offset_x = (canvas_w - img_w) / 2
        offset_y = (canvas_h - img_h) / 2
        display_points = [(p[0] * self.display_scale + offset_x, p[1] * self.display_scale + offset_y) for p in self.points]
        for i, (px, py) in enumerate(display_points):
            if (event.x - px)**2 + (event.y - py)**2 < 15**2:
                self.dragging_point_index = i
                break

    def _on_drag(self, event):
        if self.dragging_point_index is not None:
            canvas_w, canvas_h = self.canvas.winfo_width(), self.canvas.winfo_height()
            if self.image_tk is None: return
            img_w, img_h = self.image_tk.width(), self.image_tk.height()
            offset_x = (canvas_w - img_w) / 2
            offset_y = (canvas_h - img_h) / 2
            new_x = (event.x - offset_x) / self.display_scale
            new_y = (event.y - offset_y) / self.display_scale
            self.points[self.dragging_point_index] = [new_x, new_y]
            self._draw_handles()

    def _on_release(self, event):
        self.dragging_point_index = None

    def _apply_crop(self):
        self.final_points = np.array(self.points, dtype="float32")
        self.destroy()

    def _cancel(self):
        self.final_points = None
        self.destroy()