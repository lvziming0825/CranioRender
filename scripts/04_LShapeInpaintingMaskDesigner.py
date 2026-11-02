import os
import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk


class MaskEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("L-Shaped Inpainting Mask Designer")
        self.root.geometry("800x800")

        self.img_cv = None
        self.img_display = None
        self.image_path = ""

        self.current_y = tk.IntVar(value=0)
        self.current_x = tk.IntVar(value=0)
        self.current_blur = tk.IntVar(value=15)

        control_frame = tk.Frame(root, pady=10)
        control_frame.pack(side=tk.TOP, fill=tk.X)

        btn_open = tk.Button(
            control_frame,
            text="Open Image",
            command=self.load_image,
            bg="#dddddd",
            font=("Arial", 10)
        )
        btn_open.pack(side=tk.LEFT, padx=20)

        btn_save = tk.Button(
            control_frame,
            text="Save Mask (S)",
            command=self.save_result,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold")
        )
        btn_save.pack(side=tk.LEFT, padx=10)

        param_frame = tk.Frame(root, pady=10, relief=tk.GROOVE, bd=2)
        param_frame.pack(side=tk.BOTTOM, fill=tk.X)

        tk.Label(
            param_frame,
            text="Horizontal boundary (Y):",
            font=("Arial", 10, "bold")
        ).grid(row=0, column=0, padx=10, sticky="e")

        self.entry_y = tk.Entry(
            param_frame,
            textvariable=self.current_y,
            width=6,
            font=("Arial", 12)
        )
        self.entry_y.grid(row=0, column=1, padx=5)
        self.entry_y.bind("<Return>", self.on_entry_update)

        self.scale_y = tk.Scale(
            param_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.current_y,
            command=self.on_slider_update,
            length=400
        )
        self.scale_y.grid(row=0, column=2, padx=10)

        tk.Label(
            param_frame,
            text="Vertical boundary (X):",
            font=("Arial", 10, "bold")
        ).grid(row=1, column=0, padx=10, sticky="e")

        self.entry_x = tk.Entry(
            param_frame,
            textvariable=self.current_x,
            width=6,
            font=("Arial", 12)
        )
        self.entry_x.grid(row=1, column=1, padx=5)
        self.entry_x.bind("<Return>", self.on_entry_update)

        self.scale_x = tk.Scale(
            param_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.current_x,
            command=self.on_slider_update,
            length=400
        )
        self.scale_x.grid(row=1, column=2, padx=10)

        tk.Label(
            param_frame,
            text="Edge blur:",
            font=("Arial", 10, "bold")
        ).grid(row=2, column=0, padx=10, sticky="e")

        self.entry_blur = tk.Entry(
            param_frame,
            textvariable=self.current_blur,
            width=6,
            font=("Arial", 12)
        )
        self.entry_blur.grid(row=2, column=1, padx=5)
        self.entry_blur.bind("<Return>", self.on_entry_update)

        self.scale_blur = tk.Scale(
            param_frame,
            from_=0,
            to=50,
            orient=tk.HORIZONTAL,
            variable=self.current_blur,
            command=self.on_slider_update,
            length=400
        )
        self.scale_blur.grid(row=2, column=2, padx=10)

        self.canvas_area = tk.Label(
            root,
            text="Open an aligned profile image",
            bg="#eeeeee"
        )
        self.canvas_area.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        self.root.bind("<s>", lambda event: self.save_result())
        self.root.bind("<S>", lambda event: self.save_result())

    def load_image(self):
        file_path = filedialog.askopenfilename(
            title="Select aligned profile image",
            filetypes=[("Image files", "*.jpg;*.png;*.jpeg;*.bmp;*.tif;*.tiff")]
        )

        if not file_path:
            return

        self.image_path = file_path
        self.img_cv = cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), -1)

        if self.img_cv is None:
            messagebox.showerror("Error", "Unable to read image.")
            return

        h, w = self.img_cv.shape[:2]

        self.scale_y.config(to=h)
        self.current_y.set(h // 2)

        self.scale_x.config(to=w)
        self.current_x.set(w // 4)

        self.update_preview()

    def on_slider_update(self, event=None):
        self.update_preview()

    def on_entry_update(self, event=None):
        try:
            int(self.entry_y.get())
            int(self.entry_x.get())
            int(self.entry_blur.get())
            self.update_preview()
        except ValueError:
            pass

    def update_preview(self):
        if self.img_cv is None:
            return

        y_pos = self.current_y.get()
        x_pos = self.current_x.get()
        h, w = self.img_cv.shape[:2]

        y_pos = max(0, min(y_pos, h))
        x_pos = max(0, min(x_pos, w))

        preview_img = self.img_cv.copy()

        cv2.rectangle(preview_img, (0, 0), (w, y_pos), (0, 0, 0), -1)
        cv2.rectangle(preview_img, (0, y_pos), (x_pos, h), (0, 0, 0), -1)

        cv2.addWeighted(self.img_cv, 0.4, preview_img, 0.6, 0, preview_img)

        cv2.line(preview_img, (0, y_pos), (w, y_pos), (0, 0, 255), 2)
        cv2.line(preview_img, (x_pos, 0), (x_pos, h), (0, 0, 255), 2)

        preview_img = cv2.cvtColor(preview_img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(preview_img)

        display_h = 600
        aspect_ratio = w / h
        display_w = int(display_h * aspect_ratio)

        pil_img = pil_img.resize(
            (display_w, display_h),
            Image.Resampling.LANCZOS
        )

        self.img_display = ImageTk.PhotoImage(pil_img)
        self.canvas_area.config(image=self.img_display, text="")

    def save_result(self):
        if self.img_cv is None:
            return

        h, w = self.img_cv.shape[:2]

        y_pos = max(0, min(self.current_y.get(), h))
        x_pos = max(0, min(self.current_x.get(), w))
        blur_val = max(0, self.current_blur.get())

        mask = np.zeros((h, w), dtype=np.uint8)

        mask[:y_pos, :] = 255
        mask[:, :x_pos] = 255

        if blur_val > 0:
            kernel_size = blur_val * 2 + 1
            mask = cv2.GaussianBlur(mask, (kernel_size, kernel_size), 0)

        default_name = (
            os.path.splitext(os.path.basename(self.image_path))[0]
            + "_mask_L.png"
        )

        save_path = filedialog.asksaveasfilename(
            title="Save L-shaped mask",
            defaultextension=".png",
            initialfile=default_name,
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )

        if not save_path:
            return

        cv2.imencode(".png", mask)[1].tofile(save_path)
        messagebox.showinfo("Completed", f"Mask saved:\n{save_path}")


if __name__ == "__main__":
    root = tk.Tk()
    app = MaskEditorApp(root)
    root.mainloop()