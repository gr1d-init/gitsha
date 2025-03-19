# GitSHA
## The Git Commit Hash Extraction Tool

GitSHA is a lightweight script for scraping and extracting commit hashes, even some deleted commits from Git repositories. It do a simple work which run a bruteforce extraction from 0000 to ffff.

## Installation

GitSHA requires Python 3.8.0 or later.

```bash
git clone https://github.com/gr1d-init/gitsha.git
```

### Install dependencies
---
### Linux
```bash
cd gitsha
python -m venv gitshaenv && source ./gitshaenv/bin/activate
pip install requests
```
### Windows
```powershell
cd gitsha
python -m venv gitshaenv
gitshaenv\Scripts\activate.bat
pip install requests
```

## Usage

```bash
usage: python gitsha.py [-h HELP] -r REPO

GitSHA: Find leaked GitHub commit hashes using SHA1 prefixes.

options:
  -h, --help       show this help message and exit
  -r, --repo REPO  GitHub repository (format: 'user/repo')
```

### Example
```bash
python gitsha.py -r 'gr1d-init/gitsha'
```
Outputs: 
`progress_checkpoint.txt` saves your progress
`comit_entries` indicates the extracted commit entries


## Licensing and Copyright

GitSHA is licensed under the MIT License

Copyright (C) 2025 gr1d