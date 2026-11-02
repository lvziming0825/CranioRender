# ControlNet-Guided Orthodontic Profile Synthesis



## Step 1. Soft-Tissue Profile Tracing Extraction

Script:

scripts/01\_DolphinTraceRedifier.py

Input:

demo/01\_DolphinTraceRedifier/profile\_trace.jpg

Output:

demo/01\_DolphinTraceRedifier/red\_tracing\_spline.jpg

Command:

python scripts/01\_DolphinTraceRedifier.py --input "demo/01\_DolphinTraceRedifier/profile\_trace.jpg" --output "demo/01\_DolphinTraceRedifier/red\_tracing\_spline.jpg"

Description:

Extracts the right-side soft-tissue profile contour from a lateral profile tracing and generates a smoothed red contour for subsequent processing.





## Step 2. ControlNet Line-Art Generation

Script:

scripts/02\_SDLineArt512Binarizer.py

Input:

demo/02\_SDLineArt512Binarizer/red\_tracing\_spline.jpg

Output:

demo/02\_SDLineArt512Binarizer/controlnet\_lineart\_512.png

Command:

python scripts\\02\_SDLineArt512Binarizer.py --input "demo\\02\_SDLineArt512Binarizer\\red\_tracing\_spline.jpg" --white\_output "demo\\02\_SDLineArt512Binarizer\\standardized\_black\_line\_512.png" --output "demo\\02\_SDLineArt512Binarizer\\controlnet\_lineart\_512.png"
Description:

Converts the red profile tracing into a 512×512 binary line-art image with a black background and white contour for subsequent ControlNet conditioning.



## Step 3. Manual Profile Registration

Script:

scripts/03\_GPrnGuidedManualAligner.py

Input:

demo/03\_GPrnGuidedManualAligner/Original patient profile.jpg

demo/03\_GPrnGuidedManualAligner/controlnet\_lineart\_512.png

Output:

demo/03\_GPrnGuidedManualAligner/Result\_Aligned\_Photo.jpg

demo/03\_GPrnGuidedManualAligner/Result\_Overlay\_Check.jpg

Command:

python scripts/03\_GPrnGuidedManualAligner.py

Description:

Performs an initial rigid registration between the original patient profile photograph and the ControlNet line-art reference using manually selected Glabella and Pronasale landmarks. A graphical fine-tuning interface is subsequently provided for adjustment of translation, rotation, and scale while preserving facial proportions. This human-in-the-loop registration step was intentionally retained to ensure accurate alignment prior to profile synthesis.



## Step 4. L-Shaped Inpainting Mask Generation

Script:
scripts/04\_LShapeInpaintingMaskDesigner.py

Input:
demo/04\_LShapeInpaintingMaskDesigner/Result\_Aligned\_Photo.jpg

Output:
demo/04\_LShapeInpaintingMaskDesigner/Result\_Aligned\_Photo\_mask\_L.png

Command:

python scripts/04\_LShapeInpaintingMaskDesigner.py

Description:

This step generates an L-shaped inpainting mask used to define spatial constraints for diffusion-based profile synthesis. The mask is interactively defined using a graphical interface, allowing the user to specify horizontal and vertical boundaries that separate preserved anatomical regions from editable regions.

Specifically, the upper facial region and posterior cervical region are preserved (white regions), while the lower facial region is assigned as the inpainting area (black regions). A Gaussian smoothing operation is applied along mask boundaries to reduce discontinuities and improve blending stability during diffusion inpainting.

This manual mask design step is included to ensure anatomically meaningful region control and to allow subject-specific adjustment prior to the final synthesis stage.



## Step 5. High-Fidelity Profile Synthesis via Constrained Latent Diffusion

Script:
scripts/05\_ControlNetVTOGenerator.py

Input:
demo/05\_ControlNetVTOGenerator/Result\_Aligned\_Photo.jpg
demo/05\_ControlNetVTOGenerator/Result\_Aligned\_Photo\_mask\_L.png
demo/05\_ControlNetVTOGenerator/controlnet\_lineart\_512.png

Command:

python scripts/05\_ControlNetVTOGenerator.py --inpaint\_path "./Weights/sd-inpaint" --controlnet\_path "./Weights/sd-controlnet-canny"

Description:

1. This step performs high-fidelity facial profile synthesis using a ControlNet-guided latent diffusion inpainting framework. The pipeline takes a pre-aligned patient profile image, an inpainting mask defining editable facial regions, and a structural conditioning map derived from the traced soft-tissue profile. These inputs jointly constrain the diffusion process, enabling anatomically consistent image synthesis while preserving global facial structure.
2. The generation process is implemented on a fully local Stable Diffusion inpainting model with ControlNet conditioning. Key hyperparameters, including the ControlNet guidance scale, denoising strength, and random seed, are explicitly controlled to ensure reproducibility. The system supports deterministic inference under fixed configurations and allows controlled variation for qualitative evaluation.
3. This step serves as the final synthesis stage of the pipeline, integrating structural constraints and photorealistic rendering for orthodontic facial profile simulation.
4. Weights should be downloaded manually



## Environment Setup

pip install -r requirements.txt

Description:

Step 3 and Step 4 include interactive GUI tools implemented in Tkinter for manual annotation. These are standard Python library components and require no additional installation.


