project/
├── main.py
├── core/
│    ├── git_utils.py
│    ├── reporter.py
├── scanner/
│    ├── __init__.py
│    ├── directory_scanner.py
│    ├── filelist_scanner.py
├── pii_methods.txt

python privacy_scan/main.py --diff-only
python privacy_scan/main.py --path .
python privacy_scan/main.py --diff-only --summary-only
python privacy_scan/main.py --diff-only --fail-on-detection