import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import cv2
import numpy as np

# Impor kelas dan fungsi dari file lain
from crop_window import CropWindow
from scanner_logic import scan_with_hough
from effects import apply_bw_filter

class ScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CV Document Scanner GUI")

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        app_width = int(screen_width * 0.8)
        app_height = int(screen_height * 0.8)
        
        # Hitung posisi x dan y agar window berada di tengah
        center_x = int(screen_width/2 - app_width / 2)
        center_y = int(screen_height/2 - app_height/1.8)
        
        self.root.geometry(f"{app_width}x{app_height}+{center_x}+{center_y}")
        self.root.minsize(800, 600)

        self.image_path = None
        self.original_image_cv = None
        self.processed_image_cv = None
        self.last_corners = None

        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        param_frame = ttk.LabelFrame(main_frame, text="Parameter Tuning (Untuk Deteksi Otomatis)", padding="10")
        param_frame.pack(fill=tk.X, pady=10)

        self.image_frame = ttk.Frame(main_frame)
        self.image_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.image_frame.columnconfigure(0, weight=1); self.image_frame.columnconfigure(1, weight=1)
        self.image_frame.rowconfigure(0, weight=1)

        self.btn_select = ttk.Button(control_frame, text="Pilih Gambar", command=self.select_image)
        self.btn_select.pack(side=tk.LEFT, padx=5)
        
        self.btn_process = ttk.Button(control_frame, text="Deteksi & Sesuaikan", command=self.process_image, state=tk.DISABLED)
        self.btn_process.pack(side=tk.LEFT, padx=5)

        self.bw_var = tk.BooleanVar()
        self.chk_bw = ttk.Checkbutton(control_frame, text="Terapkan Efek B&W", variable=self.bw_var, command=self.apply_effects_only, state=tk.DISABLED)
        self.chk_bw.pack(side=tk.LEFT, padx=15)
        
        self.btn_save = ttk.Button(control_frame, text="Simpan Gambar", command=self.save_image, state=tk.DISABLED)
        self.btn_save.pack(side=tk.LEFT, padx=5)
        
        self.canny1_val=tk.IntVar(value=50); self.canny2_val=tk.IntVar(value=150); self.hough_val=tk.IntVar(value=500)
        
        ttk.Label(param_frame, text="Canny 1:").grid(row=0, column=0, sticky="w", padx=5)
        ttk.Scale(param_frame, from_=0, to=255, orient=tk.HORIZONTAL, variable=self.canny1_val, length=200).grid(row=0, column=1, sticky="ew", padx=5)
        ttk.Label(param_frame, text="Canny 2:").grid(row=0, column=2, sticky="w", padx=5)
        ttk.Scale(param_frame, from_=0, to=255, orient=tk.HORIZONTAL, variable=self.canny2_val, length=200).grid(row=0, column=3, sticky="ew", padx=5)
        ttk.Label(param_frame, text="Hough Thresh:").grid(row=0, column=4, sticky="w", padx=5)
        ttk.Scale(param_frame, from_=50, to=500, orient=tk.HORIZONTAL, variable=self.hough_val, length=200).grid(row=0, column=5, sticky="ew", padx=5)

        param_frame.columnconfigure(1, weight=1); param_frame.columnconfigure(3, weight=1); param_frame.columnconfigure(5, weight=1)

        self.lbl_original = ttk.Label(self.image_frame, text="Gambar Asli", relief=tk.SUNKEN, anchor=tk.CENTER)
        self.lbl_original.grid(row=0, column=0, sticky="nsew", padx=5)
        self.lbl_processed = ttk.Label(self.image_frame, text="Hasil Scan", relief=tk.SUNKEN, anchor=tk.CENTER)
        self.lbl_processed.grid(row=0, column=1, sticky="nsew", padx=5)
        
        self.image_frame.bind("<Configure>", self.on_resize)

    def select_image(self):
        self.image_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
        if not self.image_path: return
        self.original_image_cv = cv2.imread(self.image_path)
        self.display_image(self.original_image_cv, self.lbl_original)
        self.btn_process.config(state=tk.NORMAL)
        self.btn_save.config(state=tk.DISABLED); self.chk_bw.config(state=tk.DISABLED)
        self.lbl_processed.config(image='', text="Hasil Scan"); self.processed_image_cv = None

    def process_image(self):
        if self.image_path is None: return
        
        canny1, canny2, hough = self.canny1_val.get(), self.canny2_val.get(), self.hough_val.get()
        detection_result = scan_with_hough(self.image_path, canny1, canny2, hough)

        if detection_result is None or 'corners' not in detection_result:
            h, w = self.original_image_cv.shape[:2]
            corners = np.array([[w*0.1, h*0.1], [w*0.9, h*0.1], [w*0.9, h*0.9], [w*0.1, h*0.9]], dtype="float32")
            messagebox.showwarning("Info", "Deteksi otomatis gagal. Silakan sesuaikan 4 sudutnya secara manual.")
        else:
            corners = detection_result['corners']

        crop_dialog = CropWindow(self.root, self.original_image_cv, corners)
        final_corners = crop_dialog.final_points
        
        if final_corners is None: return
        
        self.last_corners = final_corners
        self.warp_and_display()

    def apply_effects_only(self):
        if self.last_corners is not None:
            self.warp_and_display()

    def warp_and_display(self):
        (tl, tr, br, bl) = self.last_corners
        widthA = np.sqrt(((br[0] - bl[0])**2) + ((br[1] - bl[1])**2)); widthB = np.sqrt(((tr[0] - tl[0])**2) + ((tr[1] - tl[1])**2))
        maxWidth = max(int(widthA), int(widthB))
        heightA = np.sqrt(((tr[0] - br[0])**2) + ((tr[1] - br[1])**2)); heightB = np.sqrt(((tl[0] - bl[0])**2) + ((tl[1] - bl[1])**2))
        maxHeight = max(int(heightA), int(heightB))
        
        titik_tujuan = np.array([[0,0], [maxWidth-1,0], [maxWidth-1,maxHeight-1], [0,maxHeight-1]], dtype="float32")
        M = cv2.getPerspectiveTransform(self.last_corners, titik_tujuan)
        scanned = cv2.warpPerspective(self.original_image_cv, M, (maxWidth, maxHeight))

        if self.bw_var.get():
            self.processed_image_cv = apply_bw_filter(scanned)
        else:
            self.processed_image_cv = scanned
            
        self.display_image(self.processed_image_cv, self.lbl_processed)
        self.btn_save.config(state=tk.NORMAL); self.chk_bw.config(state=tk.NORMAL)
    
    def save_image(self):
        if self.processed_image_cv is None: return
        save_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png")])
        if not save_path: return
        try:
            cv2.imwrite(save_path, self.processed_image_cv)
            messagebox.showinfo("Sukses", f"Gambar berhasil disimpan di:\n{save_path}")
        except Exception as e: messagebox.showerror("Error", f"Gagal menyimpan gambar: {e}")

    def on_resize(self, event):
        if self.original_image_cv is not None: self._resize_image(self.original_image_cv, self.lbl_original)
        if self.processed_image_cv is not None: self._resize_image(self.processed_image_cv, self.lbl_processed)

    def display_image(self, img_cv, label):
        self._resize_image(img_cv, label)
    
    def _resize_image(self, cv_img, label):
        label_w, label_h = label.winfo_width(), label.winfo_height()
        if label_w < 2 or label_h < 2: return
        img_h, img_w = cv_img.shape[:2]
        if img_w == 0 or img_h == 0: return
        ratio = min(label_w / img_w, label_h / img_h)
        new_w, new_h = int(img_w * ratio), int(img_h * ratio)
        resized_img = cv2.resize(cv_img, (new_w, new_h), interpolation=cv2.INTER_AREA)
        img_rgb = cv2.cvtColor(resized_img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        img_tk = ImageTk.PhotoImage(image=img_pil)
        label.config(image=img_tk, text=""); label.image = img_tk

if __name__ == "__main__":
    root = tk.Tk()
    app = ScannerApp(root)
    root.mainloop()