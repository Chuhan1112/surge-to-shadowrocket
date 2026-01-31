# Surge to Shadowrocket Converter

This project converts fmz200's Surge modules to Shadowrocket format.

## Overview

This project automatically fetches Surge modules from [fmz200/wool_scripts](https://github.com/fmz200/wool_scripts) and converts them to be compatible with Shadowrocket format.

## Key Conversions

- **[Map Local]** → **[URL Rewrite]** sections
- **Map Local patterns** → **`- reject-dict`** format for URL rewrites
- **Script sections** → Adjusted spacing to Shadowrocket format (no spaces around `=`)
- **Rule sections** → Maintained compatibility

## Features

- **Configurable module selection** via `config.yaml`
- **Robust error handling** with retry logic
- **Detailed logging** for monitoring conversions
- **Rate limiting considerations** for API requests
- **File validation** to ensure integrity

## Configuration

Modules to convert are specified in `config.yaml`. You can modify this file to add or remove modules as needed.

### Enhanced Configuration Options

The `config.yaml` supports additional options for advanced usage:

```yaml
# GitHub repo info
github:
  owner: "fmz200"
  repo: "wool_scripts"
  branch: "main"

# Advanced options
options:
  # Rate limiting (requests per minute) - not yet implemented
  rate_limit: 30
  # Number of concurrent requests (not implemented in basic version)
  max_concurrent: 1
  # Retry settings
  max_retries: 3
  retry_delay: 1.0  # Base delay in seconds for exponential backoff

# Modules to convert
modules:
  - source: "Surge/module/split/partX/Xiaohongshu.sgmodule"
    output: "Xiaohongshu.module"
  # ... more modules
```

## Usage

### Manual Conversion

```bash
cd ~/Documents/surge-to-shadowrocket
python3 main.py
```

The converted modules will be in the `output/` directory and ready to use in Shadowrocket.

### Enhanced Version

For improved error handling and logging, use the enhanced version:

```bash
cd ~/Documents/surge-to-shadowrocket
python3 enhanced_main.py
```

### GitHub Actions Workflow

The following workflow can be used to automate the conversion process:

```yaml
name: Convert Surge to Shadowrocket Modules

on:
  schedule:
    - cron: '0 2 * * *'  # Run daily at 2 AM UTC
  workflow_dispatch:  # Allow manual trigger

jobs:
  convert:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install requests pyyaml
        
    - name: Run conversion script
      run: |
        python main.py
        
    - name: Commit and push if there are changes
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add -A
        if [ -z "$(git status --porcelain)" ]; then
          echo "No changes to commit"
        else
          git commit -m "feat: Update converted Shadowrocket modules $(date)"
          git push
        fi
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Adding New Modules

To add new modules, edit `config.yaml` and add entries in the format:

```yaml
  - source: "Surge/module/split/partX/ModuleName.sgmodule"
    output: "ModuleName.module"
```

## Project Structure

```
surge-to-shadowrocket/
├── main.py                 # Main conversion script
├── enhanced_main.py        # Enhanced version with better error handling
├── config.yaml             # Configuration file for modules to convert
├── README.md               # This file
├── requirements.txt        # Python dependencies
└── output/                 # Directory for converted modules
    └── *.module            # Converted Shadowrocket modules
```

## Future Improvements

Potential enhancements identified during code review:

1. **Progress bar** for large conversions
2. **Concurrency support** for faster processing
3. **Cache mechanism** to avoid re-downloading unchanged files
4. **More detailed logging** with timestamps
5. **Configuration validation**
6. **Better error reporting**