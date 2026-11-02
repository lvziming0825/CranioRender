import os
import argparse
import cv2
import numpy as np


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True, help="Input tracing image.")
    parser.add_argument("--output", required=True, help="Output ControlNet line-art image.")
    parser.add_argument("--white_output", default=None, help="Optional white-background output image.")
    parser.add_argument("--target_size", type=int, default=512)
    parser.add_argument("--threshold", type=int, default=30)
    parser.add_argument("--alpha", type=float, default=2.0)

    return parser.parse_args()


def resize_and_pad(img, target_size=512, pad_color=255):
    h, w = img.shape[:2]
    scale = target_size / max(h, w)

    new_w = int(w * scale)
    new_h = int(h * scale)

    resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

    if len(img.shape) == 3:
        canvas = np.ones((target_size, target_size, 3), dtype=np.uint8) * pad_color
    else:
        canvas = np.ones((target_size, target_size), dtype=np.uint8) * pad_color

    x_offset = (target_size - new_w) // 2
    y_offset = (target_size - new_h) // 2

    canvas[y_offset:y_offset + new_h, x_offset:x_offset + new_w] = resized

    return canvas


def save_image(path, img):
    output_dir = os.path.dirname(path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    ext = os.path.splitext(path)[1]
    if ext == "":
        ext = ".png"

    success, encoded = cv2.imencode(ext, img)
    if not success:
        raise RuntimeError(f"Unable to save image: {path}")

    encoded.tofile(path)


def generate_sd_lineart(
    input_path,
    output_path,
    white_output=None,
    target_size=512,
    threshold=30,
    alpha=2.0
):
    img = cv2.imdecode(np.fromfile(input_path, dtype=np.uint8), -1)

    if img is None:
        raise RuntimeError(f"Unable to read image: {input_path}")

    if len(img.shape) == 3 and img.shape[2] == 4:
        background = np.ones_like(img[:, :, :3]) * 255
        alpha_channel = img[:, :, 3] / 255.0

        for c in range(3):
            background[:, :, c] = (
                alpha_channel * img[:, :, c]
                + (1 - alpha_channel) * 255
            )

        img = background.astype(np.uint8)

    resized = resize_and_pad(img, target_size=target_size, pad_color=255)

    if len(resized.shape) == 3:
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    else:
        gray = resized

    # White background with dark tracing for visual checking
    _, black_line = cv2.threshold(gray, 230, 255, cv2.THRESH_BINARY)
    white_background_output = cv2.cvtColor(black_line, cv2.COLOR_GRAY2BGR)

    if white_output is not None:
        save_image(white_output, white_background_output)

    # Black background with bright tracing for ControlNet
    inverted = cv2.bitwise_not(gray)

    _, cleaned = cv2.threshold(
        inverted,
        threshold,
        255,
        cv2.THRESH_TOZERO
    )

    smoothed = cv2.GaussianBlur(cleaned, (3, 3), 0)

    enhanced = cv2.convertScaleAbs(
        smoothed,
        alpha=alpha,
        beta=0
    )

    final_output = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)

    save_image(output_path, final_output)

    if white_output is not None:
        print(f"Saved: {white_output}")

    print(f"Saved: {output_path}")


def main():
    args = parse_args()

    generate_sd_lineart(
        input_path=args.input,
        output_path=args.output,
        white_output=args.white_output,
        target_size=args.target_size,
        threshold=args.threshold,
        alpha=args.alpha
    )


if __name__ == "__main__":
    main()