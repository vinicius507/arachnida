# Arachnida

![Language](https://img.shields.io/badge/Language-Python-blue.svg)
![License](https://img.shields.io/badge/License-AGPL_3.0-blue.svg)
![Version](https://img.shields.io/badge/Version-0.1-blue.svg)
![Status](https://img.shields.io/badge/Status-Development-blue.svg)

Arachnida is an École 42 project from the CyberSecurity Piscine.

The goal of this project is to complete two exercises:

- **Spider**: A simple web crawler that will extract images from a website.
- **Scorpion**: A tool for handling image metadata.

## Installation

### From Source

Arachnida is not yet available on PyPI, but you can install it from source by
following the instructions below:

1. Clone the repository:

   ```bash
   git clone https://github.com/vinicius507/arachnida.git
   ```

2. `cd` into the project directory:

   ```bash
   cd arachnida
   ```

3. Install using `pip`:

   ```bash
   pip install .
   ```

## Usage

### Spider

The `spider` command is used to extract images from given URLs. The images are
saved to the `data` directory by default.

The following options are available:

```bash
usage: spider [-h] [-e EXTENSIONS] [-p PATH] [-r] [-l LIMIT] urls [urls ...]

Extracts images from a given URL.

positional arguments:
  urls                  The URL to extract images from

options:
  -h, --help            show this help message and exit
  -e EXTENSIONS, --extensions EXTENSIONS
                        Comma separated list of image extensions to download (default: None)
  -p PATH, --path PATH  The path to save the images (default: ./data)
  -r, --recursive       Recursively searches URLs for images (default: False)
  -l LIMIT, --limit LIMIT
                        The maximum depth level of the recursive image search (default: 5)
```

### Scorpion

Work in progress...
