# ORMIR-XCT

[Michael T. Kuczynski](https://www.linkedin.com/in/mkuczyns/), [Nathan J. Neeteson](https://www.linkedin.com/in/nathan-neeteson/), [Kathryn S. Stok](https://www.linkedin.com/in/kstok/), [Andrew J. Burghardt](https://www.linkedin.com/in/aburghardt/), [Michelle A. Espinosa Hernandez](https://www.linkedin.com/in/michelleaespinosah/), [Jared Vicory](https://www.kitware.com/jared-vicory/), [Justin J. Tse](https://www.linkedin.com/in/justin-j-tse/), [Pholpat Durongbhan](https://www.linkedin.com/in/pholpatd/), [Serena Bonaretti](https://sbonaretti.github.io/), [Andy Kin On Wong](https://www.linkedin.com/in/andy-kin-on-wong-76408859/), [Steven K. Boyd](https://mccaig.ucalgary.ca/boyd), [Sarah L. Manske](https://www.linkedin.com/in/sarah-manske-b5402b41/). *ORMIR_XCT: A Python package for high resolution peripheral quantitative computed tomography image processing*. Journal of Open Source Software, 9(97), 6084, https://doi.org/10.21105/joss.06084, 2024.

**Version:** 1.1.0

- ORMIR-XCT is a Python package for processing high resolution peripheral computed tomography (HR-pQCT) scans. 
- Development of this project began during the 2022 “Building the Jupyter Community in Musculoskeletal Imaging Research” workshop hosted by the Open and Reproducible Musculoskeletal Imaging Research (ORMIR) group.

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://github.com/ORMIR-XCT/ORMIR-XCT/blob/main/LICENSE)
![PyPI - Version](https://img.shields.io/pypi/v/ormir-xct?link=https%3A%2F%2Fpypi.org%2Fproject%2Formir-xct%2F)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/ORMIR-XCT/ORMIR-XCT/build-test-env.yml)

---

## Installation
### Option A: Install into a new Anaconda environment:
***For Windows, Linux, and Intel-based Mac:***
#### Step 1: Install the ormir-xct Anaconda environment from the YAML file:
`conda env create -f environment.yml`

#### Step 2: Activate and use the ormir-xct environment:
`conda activate ormir-xct`  

***For Apple Silicon Mac (M-chips):***
#### Step 1: Install the ormir-xct Anaconda environment, specifying macOS architecture:

`CONDA_SUBDIR=osx-64 conda create -n ormir-xct python=3.11 pip`

#### Step 2: Activate the ormir-xct environment:
`conda activate ormir-xct`

#### Step 3: Tell conda to always use the macOS architecture:
`conda env config vars set CONDA_SUBDIR=osx-64`

#### Step 4: Deactivate and reactivate the environment:
`conda deactivate`  
`conda activate ormir-xct`

#### Step 5: Install the required dependencies using pip:
`pip install -r requirements.txt`  

### Option B: Install into an existing Anaconda environment: 
#### Step 1: Activate your environment:
`conda activate my_env`

#### Step 2: Install ormir-xct from PyPi
`pip install ormir-xct`
 
---

## Example Usage
Example Jupyter Notebooks demonstrating the major functionality of the ORMIR-XCT package are provided in the *[examples](https://github.com/ORMIR-XCT/ORMIR-XCT/tree/main/examples)* directory.

---

## Command Line Applications
The ORMIR-XCT package now provides a command line interface for some workflows. To install the command line applications, activate your `ormir-xct` Anaconda environment and run:
`pip install -e .`
For detailed usage instructions, type the command followed by `-h` into the terminal.

| Command                    | Description                                                                              |
| ---------------------------|----------------------------------------------------------------------------------------- |
| `adaptive-local-threshold` | Perform adaptive local thresholding on an image to segment bone.                         |
| `autocontour`              | Generate proximal, distal, and combined periosteal masks using the autocontour workflow. |
| `bmd`                      | Compute bone mineral density for an input image.                                         |
| `bmd-masked`               | Compute masked bone mineral density for an input image, within the provided mask         |
| `fft-laplace-hamming`      | Binarize an input image using a Laplace-Hamming filter and fixed threshold.              |
| `jsw-analysis`             | Reimplementation of the IPL joint space width analysis worflow.                          |
| `seg-gauss`                | Binarize an input image using Gaussian smoothing followed by a fixed threshold.          |
| `trab-bvtv`                | Compute trabecular bone volume fraction (Tb.BV/TV).                                      |
| `trab-th`                  | Compute trabecular thickness (Tb.Th).                                                    |
| `trab-sp`                  | Compute trabecular separation (Tb.Sp).                                                   |
| `trab-microarch`           | Compute trabecular microarchitecture parameters (Tb.Th, Tb.Sp, and Tb.BV/TV).            |

---

## Ways to Contribute
### Reporting Bugs
- Bugs can be reported by creating a new GitHub issue in this repository. For each bug, please provide details on how to reproduce the bug and the specific error message (if possible).

### Contributing Guidelines
- Install `ormir-xct` with development tools (e.g. black, ruff, pytest, hypothesis):
    1. Clone the repository
    2. Create an Anaconda environment as above
    3. Install development tools: `pip install -e .[dev]`
- To add a new feature, expand existing functionality, add documentation, or other contributions, please submit a new GitHub issue outlining your contribution in detail. 
- When submitting a new pull request, ensure you outline what you have changed and why it is necessary to make this change.

---

## Citation
When using the ORMIR-XCT package, please use the following citation:
- *Kuczynski et al., (2024). ORMIR-XCT: A Python package for high resolution peripheral quantitative computed tomography image processing. Journal of Open Source Software, 9(97), 6084, https://doi.org/10.21105/joss.06084*
