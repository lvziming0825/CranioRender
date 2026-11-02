# CranioRender

### High-Fidelity Orthodontic Profile Synthesis via ControlNet-Guided Generative AI

**Research project | Journal of Dentistry (2026)**

[![Paper](https://img.shields.io/badge/Paper-Journal%20of%20Dentistry-blue)](https://doi.org/10.1016/j.jdent.2026.106916)
[![DOI](https://img.shields.io/badge/DOI-10.1016%2Fj.jdent.2026.106916-green)](https://doi.org/10.1016/j.jdent.2026.106916)
[![PubMed](https://img.shields.io/badge/PubMed-42457116-blue)](https://pubmed.ncbi.nlm.nih.gov/42457116/)
![Python](https://img.shields.io/badge/Python-Research%20Code-yellow)

## Overview

CranioRender is a research project for high-fidelity orthodontic profile synthesis using cephalometric contour guidance and diffusion-based generative artificial intelligence.

The framework integrates Stable Diffusion inpainting with ControlNet to produce photorealistic lower-facial visualizations guided by explicitly defined soft-tissue contours.

The project aims to support research into AI-assisted orthodontic visualization and communication.

## Publication

**Beyond geometric deformation: High-fidelity orthodontic profile synthesis via ControlNet-guided generative AI**

Fengcong Wang, Yang Lyu, Yilan Yang.

*Journal of Dentistry*, Volume 174, Article 106916, 2026.

- **Paper:** https://doi.org/10.1016/j.jdent.2026.106916
- **PubMed:** https://pubmed.ncbi.nlm.nih.gov/42457116/

## Methodology

The published framework includes:

1. Cephalometric soft-tissue contour extraction and registration.
2. Contour-guided image conditioning.
3. Stable Diffusion-based inpainting with ControlNet.
4. Quantitative evaluation of landmark adherence and image quality.
5. Subjective evaluation of image realism.

## Published Results

| Metric | Result |
|---|---|
| Mean landmark error | 1.38 ± 0.13 mm |
| Landmark deviations within 2.0 mm | 95.0% |
| LPIPS | 0.089 ± 0.024 |
| SSIM | 0.951 ± 0.009 |
| PSNR | 28.69 ± 2.47 dB |

These values are reported in the published study and are not independent repository benchmarks.

## Code Availability

**Status: Repository initialization / release preparation.**

The research code and documentation are being organized for public release.

Installation instructions, reproducibility details, and example workflows will be provided with the code release.

## Data Availability

The original clinical data are not included in this repository. Data requests are subject to the conditions described in the publication, applicable ethics requirements, and institutional approval where necessary.

## Citation

If you use this research, please cite:

Wang F, Lyu Y, Yang Y. Beyond geometric deformation: High-fidelity orthodontic profile synthesis via ControlNet-guided generative AI. *Journal of Dentistry*. 2026;174:106916. https://doi.org/10.1016/j.jdent.2026.106916

## Intended Use

This project is intended for research and methodological development. Generated images are not guaranteed predictions of individual clinical outcomes and should not be used as standalone clinical decision-making tools.

## Maintainers

Research team associated with the published study.

## License

A software license will be specified after verification of source-code ownership, institutional requirements, and third-party dependencies.
