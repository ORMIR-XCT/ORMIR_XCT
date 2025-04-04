# ORMIR_XCT

[Michael T. Kuczynski](https://www.linkedin.com/in/mkuczyns/), [Nathan J. Neeteson](https://www.linkedin.com/in/nathan-neeteson/), [Kathryn S. Stok](https://www.linkedin.com/in/kstok/), [Andrew J. Burghardt](https://www.linkedin.com/in/aburghardt/), [Michelle A. Espinosa Hernandez](https://www.linkedin.com/in/michelleaespinosah/), [Jared Vicory](https://www.kitware.com/jared-vicory/), [Justin J. Tse](https://www.linkedin.com/in/justin-j-tse/), [Pholpat Durongbhan](https://www.linkedin.com/in/pholpatd/), [Serena Bonaretti](https://sbonaretti.github.io/), [Andy Kin On Wong](https://www.linkedin.com/in/andy-kin-on-wong-76408859/), [Steven K. Boyd](https://mccaig.ucalgary.ca/boyd), [Sarah L. Manske](https://www.linkedin.com/in/sarah-manske-b5402b41/). *ORMIR_XCT: A Python package for high resolution peripheral quantitative computed tomography image processing*. Journal of Open Source Software, 9(97), 6084, https://doi.org/10.21105/joss.06084, 2024.

**Version:** 1.0.2

- ORMIR_XCT is a Python package for processing high resolution peripheral computed tomography (HR-pQCT) scans. 
- Development of this project began during the 2022 “Building the Jupyter Community in Musculoskeletal Imaging Research” workshop hosted by the Open and Reproducible Musculoskeletal Imaging Research (ORMIR) group.

---

## Installation
### Option A: Install into a new Anaconda environment:
<ins>***For Windows, Linux, and Intel-based Mac:***</ins>
#### Step 1: Install the ormir_xct Anaconda environment from the YAML file:
`conda env create -f environment.yml`

#### Step 2: Activate and use the ormir_xct environment:
`conda activate ormir_xct`<br><br>

<ins>***For Apple Silicon Mac (M-chips):***</ins>
#### Step 1: Install the ormir_xct Anaconda environment, specifying macOS architecture:
`CONDA_SUBDIR=osx-64 conda create -n ormir_xct python=3.11.11 pip`

#### Step 2: Activate the ormir_xct environment:
`conda activate ormir_xct`

#### Step 3: Tell conda to always use the macOS architecture:
`conda env config vars set CONDA_SUBDIR=osx-64`

#### Step 4: Deactivate and reactivate the environment:
`conda deactivate`
`conda activate bl`

#### Step 5: Install the required dependencies using pip:
`pip install -r requirements.txt`
<br><br>

### Option B: Install into an existing Anaconda environment: 
#### Step 1: Activate your environment:
`conda activate my_env`

#### Step 2: Install ormir-xct from PyPi
`pip install ormir-xct`

---

## Example Usage
Example Jupyter Notebooks demonstrating the major functionality of the ORMIR_XCT package are provided in the *[examples](https://github.com/ORMIR-XCT/ORMIR_XCT/tree/main/examples)* directory.

---

## Ways to Contribute
### Reporting Bugs
- Bugs can be reported by creating a new GitHub issue in this repository. For each bug, please provide details on how to reproduce the bug and the specific error message (if possible).

### Contributing New Features
- To add a new feature, expand existing functionality, add documentation, or other contributions, please submit a new GitHub issue outlining your contribution in detail. 
- When submitting a new pull request, ensure you outline what you have changed and why it is necessary to make this change.

---

## Citation
When using the ORMIR_XCT package, please use the following citation:
- *Kuczynski et al., (2024). ORMIR_XCT: A Python package for high resolution peripheral quantitative computed tomography image processing. Journal of Open Source Software, 9(97), 6084, https://doi.org/10.21105/joss.06084*