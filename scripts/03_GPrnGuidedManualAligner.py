import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
import ctypes
import os


try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass


class AlignmentTool:
    def __init__(self):
        self.points = []
        self.img_original = None
        self.img_display = None
        self.window_name = ""

        self.view_zoom = 1.0
        self.view_center = None
        self.display_size = None

    def get_screen_size(self):
        root = tk.Tk()
        root.withdraw()
        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        root.destroy()
        return screen_w, screen_h

    def select_file(self, title):
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            title=title,
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tif *.tiff")]
        )
        root.destroy()
        return file_path

    def read_image(self, path):
        img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), -1)
        if img is None:
            raise RuntimeError(f"Unable to read image: {path}")
        return img

    def get_display_size(self, img, height_ratio=0.72, width_ratio=0.95):
        screen_w, screen_h = self.get_screen_size()
        h, w = img.shape[:2]

        target_h = int(screen_h * height_ratio)
        target_w = int(screen_w * width_ratio)

        scale = min(target_h / h, target_w / w)

        return int(w * scale), int(h * scale)

    def render_view(self, img):
        h, w = img.shape[:2]
        disp_w, disp_h = self.display_size

        if self.view_center is None:
            self.view_center = [w / 2, h / 2]

        if self.view_zoom <= 1.01:
            return cv2.resize(img, (disp_w, disp_h), interpolation=cv2.INTER_AREA)

        crop_w = max(10, int(w / self.view_zoom))
        crop_h = max(10, int(h / self.view_zoom))

        cx, cy = self.view_center

        x1 = int(np.clip(cx - crop_w / 2, 0, max(0, w - crop_w)))
        y1 = int(np.clip(cy - crop_h / 2, 0, max(0, h - crop_h)))

        crop = img[y1:y1 + crop_h, x1:x1 + crop_w]

        return cv2.resize(crop, (disp_w, disp_h), interpolation=cv2.INTER_LINEAR)

    def update_point_window(self):
        self.img_display = self.render_view(self.img_original.copy())

        h, w = self.img_original.shape[:2]
        disp_w, disp_h = self.display_size

        for i, p in enumerate(self.points):
            x_real, y_real = p

            if self.view_zoom <= 1.01:
                x_disp = int(x_real * disp_w / w)
                y_disp = int(y_real * disp_h / h)
            else:
                crop_w = int(w / self.view_zoom)
                crop_h = int(h / self.view_zoom)
                cx, cy = self.view_center

                x1 = int(np.clip(cx - crop_w / 2, 0, max(0, w - crop_w)))
                y1 = int(np.clip(cy - crop_h / 2, 0, max(0, h - crop_h)))

                x_disp = int((x_real - x1) * disp_w / crop_w)
                y_disp = int((y_real - y1) * disp_h / crop_h)

            if 0 <= x_disp < disp_w and 0 <= y_disp < disp_h:
                cv2.circle(self.img_display, (x_disp, y_disp), 5, (0, 0, 255), -1)
                cv2.putText(
                    self.img_display,
                    str(i + 1),
                    (x_disp + 8, y_disp - 8),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 255),
                    1,
                    cv2.LINE_AA
                )

        cv2.imshow(self.window_name, self.img_display)

    def point_window_mouse_event(self, event, x, y, flags, param):
        h, w = self.img_original.shape[:2]
        disp_w, disp_h = self.display_size

        if event == cv2.EVENT_MOUSEWHEEL:
            old_zoom = self.view_zoom

            if flags > 0:
                self.view_zoom *= 1.15
            else:
                self.view_zoom /= 1.15

            self.view_zoom = max(1.0, min(self.view_zoom, 8.0))

            if self.view_center is None:
                self.view_center = [w / 2, h / 2]

            if old_zoom != self.view_zoom:
                cx, cy = self.view_center
                dx = (x - disp_w / 2) / old_zoom
                dy = (y - disp_h / 2) / old_zoom

                cx += dx * 0.25
                cy += dy * 0.25

                self.view_center = [
                    float(np.clip(cx, 0, w - 1)),
                    float(np.clip(cy, 0, h - 1))
                ]

            self.update_point_window()

        elif event == cv2.EVENT_LBUTTONDOWN:
            if self.view_zoom <= 1.01:
                real_x = int(x * w / disp_w)
                real_y = int(y * h / disp_h)
            else:
                crop_w = int(w / self.view_zoom)
                crop_h = int(h / self.view_zoom)
                cx, cy = self.view_center

                x1 = int(np.clip(cx - crop_w / 2, 0, max(0, w - crop_w)))
                y1 = int(np.clip(cy - crop_h / 2, 0, max(0, h - crop_h)))

                real_x = int(x1 + x * crop_w / disp_w)
                real_y = int(y1 + y * crop_h / disp_h)

            self.points.append([real_x, real_y])
            self.update_point_window()

    def get_two_points(self, image_path, window_name):
        self.img_original = self.read_image(image_path)
        h, w = self.img_original.shape[:2]

        display_w, display_h = self.get_display_size(
            self.img_original,
            height_ratio=0.72,
            width_ratio=0.95
        )

        self.display_size = (display_w, display_h)
        self.view_zoom = 1.0
        self.view_center = [w / 2, h / 2]
        self.window_name = window_name
        self.points = []

        print(f"\n{window_name}")
        print("Click two points in order: 1. Glabella  2. Pronasale")
        print("Mouse wheel: zoom view. Press any key after selecting the two points.")

        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, display_w, display_h)
        cv2.setMouseCallback(window_name, self.point_window_mouse_event)
        self.update_point_window()

        cv2.waitKey(0)
        cv2.destroyAllWindows()

        if len(self.points) < 2:
            print("Point selection was not completed.")
            return None

        return np.array(self.points[:2], dtype=np.float32)

    def fine_tune_mouse_event(self, event, x, y, flags, param):
        if event == cv2.EVENT_MOUSEWHEEL:
            h, w = param["overlay_shape"][:2]
            disp_w, disp_h = self.display_size

            old_zoom = self.view_zoom

            if flags > 0:
                self.view_zoom *= 1.15
            else:
                self.view_zoom /= 1.15

            self.view_zoom = max(1.0, min(self.view_zoom, 8.0))

            if self.view_center is None:
                self.view_center = [w / 2, h / 2]

            if old_zoom != self.view_zoom:
                cx, cy = self.view_center
                dx = (x - disp_w / 2) / old_zoom
                dy = (y - disp_h / 2) / old_zoom

                cx += dx * 0.25
                cy += dy * 0.25

                self.view_center = [
                    float(np.clip(cx, 0, w - 1)),
                    float(np.clip(cy, 0, h - 1))
                ]

    def draw_info_panel(
        self,
        image,
        d_tx,
        d_ty,
        d_angle,
        d_scale,
        step_move,
        step_angle,
        step_scale
    ):
        lines = [
            "WASD move | -/+ move step | QE rotate | [] angle step",
            "ZC scale | ,/. scale step | wheel zoom | R reset | Enter save",
            f"Tx {d_tx:.1f} | Ty {d_ty:.1f} | Angle {d_angle:.2f} | Scale {d_scale:.4f}",
            f"Move {step_move}px | Angle {step_angle:.2f} | Scale step {step_scale:.4f} | View {self.view_zoom:.2f}x"
        ]

        overlay = image.copy()
        cv2.rectangle(overlay, (8, 8), (690, 76), (0, 0, 0), -1)
        image = cv2.addWeighted(overlay, 0.38, image, 0.62, 0)

        y = 24
        for text in lines:
            cv2.putText(
                image,
                text,
                (16, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.32,
                (255, 255, 255),
                1,
                cv2.LINE_AA
            )
            y += 15

        return image

    def manual_fine_tune(self, img_photo, img_tracing, initial_matrix):
        print("\nFine-tuning mode")
        print("[W/A/S/D] : move")
        print("[-/+]     : adjust move step")
        print("[Q/E]     : rotate")
        print("[[/]]     : adjust angle step")
        print("[Z/C]     : scale down / scale up")
        print("[,/.]     : adjust scale step")
        print("[Mouse wheel] : local view zoom")
        print("[R]       : reset")
        print("[Enter]   : save")

        h_dst, w_dst = img_tracing.shape[:2]
        center_dst = (w_dst // 2, h_dst // 2)

        d_tx, d_ty = 0.0, 0.0
        d_angle = 0.0
        d_scale = 1.0

        step_move = 2
        step_angle = 0.5
        step_scale = 0.005

        self.view_zoom = 1.0
        self.view_center = [w_dst / 2, h_dst / 2]

        window_name = "Fine-Tuning Mode"

        dummy = img_tracing.copy()
        if len(dummy.shape) == 2:
            dummy = cv2.cvtColor(dummy, cv2.COLOR_GRAY2BGR)

        display_w, display_h = self.get_display_size(
            dummy,
            height_ratio=0.72,
            width_ratio=0.95
        )
        self.display_size = (display_w, display_h)

        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, display_w, display_h)

        mouse_param = {"overlay_shape": img_tracing.shape}
        cv2.setMouseCallback(window_name, self.fine_tune_mouse_event, mouse_param)

        while True:
            m_adjust = cv2.getRotationMatrix2D(center_dst, d_angle, d_scale)
            m_adjust[0, 2] += d_tx
            m_adjust[1, 2] += d_ty

            mat_init = np.vstack([initial_matrix, [0, 0, 1]])
            mat_adjust = np.vstack([m_adjust, [0, 0, 1]])
            current_matrix = np.dot(mat_adjust, mat_init)[:2, :]

            warped = cv2.warpAffine(
                img_photo,
                current_matrix,
                (w_dst, h_dst),
                borderMode=cv2.BORDER_CONSTANT,
                borderValue=(255, 255, 255)
            )

            bg = img_tracing.copy()
            if len(bg.shape) == 2:
                bg = cv2.cvtColor(bg, cv2.COLOR_GRAY2BGR)

            overlay = cv2.addWeighted(warped, 0.6, bg, 0.4, 0)

            overlay = self.draw_info_panel(
                overlay,
                d_tx,
                d_ty,
                d_angle,
                d_scale,
                step_move,
                step_angle,
                step_scale
            )

            display_overlay = self.render_view(overlay)
            cv2.imshow(window_name, display_overlay)

            key = cv2.waitKey(20) & 0xFF

            if key == 13:
                cv2.destroyAllWindows()
                return current_matrix

            elif key == ord("r") or key == ord("R"):
                d_tx, d_ty = 0.0, 0.0
                d_angle = 0.0
                d_scale = 1.0
                self.view_zoom = 1.0
                self.view_center = [w_dst / 2, h_dst / 2]
                print("Reset.")

            elif key == ord("w"):
                d_ty -= step_move
            elif key == ord("s"):
                d_ty += step_move
            elif key == ord("a"):
                d_tx -= step_move
            elif key == ord("d"):
                d_tx += step_move

            elif key == ord("-"):
                step_move = max(1, step_move - 1)
                print(f"Move step: {step_move}px")
            elif key == ord("+") or key == ord("="):
                step_move += 1
                print(f"Move step: {step_move}px")

            elif key == ord("q"):
                d_angle += step_angle
            elif key == ord("e"):
                d_angle -= step_angle

            elif key == ord("["):
                step_angle = max(0.1, step_angle - 0.1)
                print(f"Angle step: {step_angle:.2f}")
            elif key == ord("]"):
                step_angle += 0.1
                print(f"Angle step: {step_angle:.2f}")

            elif key == ord("z"):
                d_scale -= step_scale
            elif key == ord("c"):
                d_scale += step_scale

            elif key == ord(","):
                step_scale = max(0.001, step_scale - 0.001)
                print(f"Scale step: {step_scale:.4f}")
            elif key == ord("."):
                step_scale += 0.001
                print(f"Scale step: {step_scale:.4f}")

            d_scale = max(d_scale, 0.1)

    def run(self):
        print("Starting manual rigid-alignment tool.")

        photo_path = self.select_file("Select original profile photograph")
        if not photo_path:
            return

        tracing_path = self.select_file("Select target profile tracing")
        if not tracing_path:
            return

        pts_src = self.get_two_points(
            photo_path,
            "Photo: Click Glabella and Pronasale points"
        )
        if pts_src is None:
            return

        pts_dst = self.get_two_points(
            tracing_path,
            "Tracing: Click Glabella and Pronasale points"
        )
        if pts_dst is None:
            return

        img_photo = self.read_image(photo_path)
        img_tracing = self.read_image(tracing_path)

        if len(img_tracing.shape) == 2:
            img_tracing = cv2.cvtColor(img_tracing, cv2.COLOR_GRAY2BGR)

        initial_matrix, _ = cv2.estimateAffinePartial2D(pts_src, pts_dst)

        if initial_matrix is None:
            print("Initial alignment failed.")
            return

        final_matrix = self.manual_fine_tune(
            img_photo,
            img_tracing,
            initial_matrix
        )

        h_dst, w_dst = img_tracing.shape[:2]

        warped_final = cv2.warpAffine(
            img_photo,
            final_matrix,
            (w_dst, h_dst),
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(255, 255, 255)
        )

        overlay_final = cv2.addWeighted(
            warped_final,
            0.7,
            img_tracing,
            0.3,
            0
        )

        save_dir = os.path.dirname(photo_path)

        save_path_aligned = os.path.join(save_dir, "aligned_profile_photo.jpg")
        save_path_check = os.path.join(save_dir, "alignment_overlay_check.jpg")

        cv2.imencode(".jpg", warped_final)[1].tofile(save_path_aligned)
        cv2.imencode(".jpg", overlay_final)[1].tofile(save_path_check)

        print("\nCompleted.")
        print(f"Saved: {save_path_aligned}")
        print(f"Saved: {save_path_check}")

        final_display_w, final_display_h = self.get_display_size(
            overlay_final,
            height_ratio=0.72,
            width_ratio=0.95
        )

        self.display_size = (final_display_w, final_display_h)
        self.view_zoom = 1.0
        self.view_center = [
            overlay_final.shape[1] / 2,
            overlay_final.shape[0] / 2
        ]

        final_display = self.render_view(overlay_final)

        cv2.namedWindow("Final Alignment Check", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Final Alignment Check", final_display_w, final_display_h)
        cv2.imshow("Final Alignment Check", final_display)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


if __name__ == "__main__":
    tool = AlignmentTool()
    tool.run()