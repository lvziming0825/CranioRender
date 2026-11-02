import os
import sys
import argparse
import torch
import cv2
import numpy as np
from PIL import Image, ImageOps, ImageFilter
from diffusers import StableDiffusionControlNetInpaintPipeline, ControlNetModel

try:
    from rembg import remove

    REMBG_AVAILABLE = True
except ImportError:
    REMBG_AVAILABLE = False
    print("[INFO] rembg not installed. Using fallback threshold-based background matting.")

parser = argparse.ArgumentParser(description="Deterministic ControlNet Profile Synthesis Pipeline")
parser.add_argument(
    "--inpaint_path",
    type=str,
    default="./Weights/sd-inpaint",
    help="directory to local offline Stable Diffusion Inpainting repository checkpoint."
)
parser.add_argument(
    "--controlnet_path",
    type=str,
    default="./Weights/sd-controlnet-canny",
    help="directory to local offline ControlNet Canny model checkpoint."
)
parser.add_argument(
    "--data_dir",
    type=str,
    default="./demo/05_ControlNetVTOGenerator",
    help="Directory containing the target input profile photo, region mask, and tracing spline."
)

args = parser.parse_known_args()[0] if len(sys.argv) > 1 else parser.parse_args([])

if not os.path.exists(args.inpaint_path) or not os.path.exists(args.controlnet_path):
    raise FileNotFoundError(f"Missing localized checkpoints")

SEED_VALUE = 4  # The seed used in the pipeline of the demo.
CONTROLNET_WEIGHT = 0.88  # same as the weights reported in the manuscript.
DENOISING_STRENGTH = 0.84  # same the weights reported in the manuscript.
RESOLUTION = (512, 512)

POSITIVE_PROMPT = "RAW photo, medical photography, side profile, realistic skin texture, visible skin pores, detailed skin, subsurface scattering, (slight smile:0.8), soft lighting, 8k uhd, dslr, red lip"  # same as the prompts recorded in the main text
NEGATIVE_PROMPT = "smooth skin, plastic, wax figure, blur, cartoon, painting, bad anatomy, open mouth, teeth, beard, makeup, floating hair, distortion"  # same as the prompts recorded in the main text

print(f"\n[INFO] Initializing pipeline environments with locked Seed: {SEED_VALUE}")


def execute_inference():

    mode_tag = "OURS_PROPOSED"
    print(f"\n Running inference pipeline mode: {mode_tag}")

    photo_path = os.path.join(args.data_dir, "Result_Aligned_Photo.jpg")
    mask_path = os.path.join(args.data_dir, "Result_Aligned_Photo_mask_L.png")
    tracing_path = os.path.join(args.data_dir, "controlnet_lineart_512.png")

    init_img = Image.open(photo_path).convert("RGB").resize(RESOLUTION)
    control_img = Image.open(tracing_path).convert("RGB").resize(RESOLUTION)

    mask_raw = Image.open(mask_path).convert("L").resize(RESOLUTION)
    mask_for_ai = ImageOps.invert(mask_raw)

    torch.manual_seed(SEED_VALUE)
    torch.cuda.manual_seed_all(SEED_VALUE)
    generator = torch.Generator(device="cuda").manual_seed(SEED_VALUE)

    controlnet = ControlNetModel.from_pretrained(
        args.controlnet_path, torch_dtype=torch.float16, use_safetensors=True, local_files_only=True
    )
    pipe = StableDiffusionControlNetInpaintPipeline.from_pretrained(
        args.inpaint_path, controlnet=controlnet, torch_dtype=torch.float16, variant="fp16",
        use_safetensors=True, local_files_only=True, safety_checker=None, feature_extractor=None, image_processor=None
    )
    pipe.to("cuda")
    pipe.enable_model_cpu_offload()

    active_cn_weight = CONTROLNET_WEIGHT
    active_strength = DENOISING_STRENGTH

    generated_image = pipe(
        prompt=POSITIVE_PROMPT,
        negative_prompt=NEGATIVE_PROMPT,
        image=init_img,
        mask_image=mask_for_ai,
        control_image=control_img,
        num_inference_steps=30,
        guidance_scale=7.5,
        controlnet_conditioning_scale=active_cn_weight,
        strength=active_strength,
        generator=generator
    ).images[0]

    mask_blur = mask_for_ai.filter(ImageFilter.GaussianBlur(radius=5))
    result = Image.composite(generated_image, init_img, mask_blur)

    output_filename = f"{mode_tag}_Seed{SEED_VALUE}_Final.png"
    save_path = os.path.join(args.data_dir, output_filename)
    result.save(save_path)
    print(f"Synthesis was saved to directory:\n {save_path}")


if __name__ == "__main__":
    execute_inference()


    print("\n Inference completed.")