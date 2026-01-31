# Surge to Shadowrocket Converter

This project converts fmz200's Surge modules to Shadowrocket format.

## Overview

This project automatically fetches Surge modules from [fmz200/wool_scripts](https://github.com/fmz200/wool_scripts) and converts them to be compatible with Shadowrocket format.

## Key Conversions

- **[Map Local]** → **[URL Rewrite]** sections
- **Map Local patterns** → **`- reject-dict`** format for URL rewrites
- **Script sections** → Adjusted spacing to Shadowrocket format (no spaces around `=`)
- **Rule sections** → Maintained compatibility

## Configuration

Modules to convert are specified in `config.yaml`. You can modify this file to add or remove modules as needed.

## Usage

### Manual Conversion

```bash
cd ~/Documents/surge-to-shadowrocket
python3 main.py
```

The converted modules will be in the `output/` directory and ready to use in Shadowrocket.

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