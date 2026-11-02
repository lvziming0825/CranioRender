import os
import argparse
import cv2
import numpy as np
from rembg import remove
from PIL import Image
import scipy.interpolate as si


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Input lateral profile image.")
    parser.add_argument("--output", required=True, help="Output profile tracing image.")
    parser.add_argument("--smoothness", type=int, default=200)
    parser.add_argument("--line_thickness", type=int, default=2)
    parser.add_argument("--row_step", type=int, default=1)
    parser.add_argument("--n_out", type=int, default=1200)
    return parser.parse_args()


def extract_right_profile_points(mask, row_step=1):
    xs, ys = [], []
    height, _ = mask.shape

    for y in range(0, height, max(1, row_step)):
        idx = np.where(mask[y, :] > 0)[0]
        if idx.size > 0:
            xs.append(int(idx.max()))
            ys.append(y)

    if len(xs) < 20:
        raise RuntimeError("Too few boundary points were detected.")

    points = np.column_stack([xs, ys]).astype(np.float32)

    keep = [0]
    for i in range(1, len(points)):
        if not np.array_equal(points[i], points[i - 1]):
            keep.append(i)

    return points[keep]


def smooth_open_spline(points, smoothness=200, n_out=1200):
    if points.shape[0] <= 3:
        return points.astype(np.int32)

    x = points[:, 0]
    y = points[:, 1]

    tck, u = si.splprep([x, y], s=smoothness, per=0, k=3)
    u_new = np.linspace(u.min(), u.max(), n_out)
    x_new, y_new = si.splev(u_new, tck)

    return np.column_stack([x_new, y_new]).astype(np.int32)


def create_profile_tracing(
    input_path,
    output_path,
    smoothness=200,
    line_thickness=2,
    row_step=1,
    n_out=1200
):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    image = Image.open(input_path).convert("RGBA")
    image_no_bg = remove(image)
    image_np = np.array(image_no_bg)

    if image_np.ndim != 3 or image_np.shape[2] < 4:
        raise RuntimeError("No alpha channel was found after background removal.")

    alpha = image_np[:, :, 3]
    _, mask = cv2.threshold(alpha, 127, 255, cv2.THRESH_BINARY)

    points = extract_right_profile_points(mask, row_step=row_step)
    smooth_points = smooth_open_spline(points, smoothness=smoothness, n_out=n_out)

    height, width = mask.shape
    canvas = np.ones((height, width, 3), dtype=np.uint8) * 255

    cv2.polylines(
        canvas,
        [smooth_points.reshape((-1, 1, 2))],
        isClosed=False,
        color=(0, 0, 255),
        thickness=line_thickness,
        lineType=cv2.LINE_AA
    )

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    if not cv2.imwrite(output_path, canvas):
        raise RuntimeError(f"Failed to save output image: {output_path}")

    print(f"Saved: {output_path}")


def main():
    args = parse_args()

    create_profile_tracing(
        input_path=args.input,
        output_path=args.output,
        smoothness=args.smoothness,
        line_thickness=args.line_thickness,
        row_step=args.row_step,
        n_out=args.n_out
    )


if __name__ == "__main__":
    main()