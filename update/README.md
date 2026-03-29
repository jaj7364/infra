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

privacy-scan/
├── main.py              # 지휘본부 (CLI 실행)
├── pii_methods.txt      # 민감 단어 사전
├── scanner/             # 스캐너 패키지
│   ├── __init__.py      # 패키지 선언 (from .diff_scanner import DiffScanner 등)
│   ├── base_scanner.py  # 뼈대
│   ├── diff_scanner.py  # Git 변경분 병렬 스캐너
│   └── full_scanner.py  # 전체 디렉토리 병렬 스캐너
├── utils/
│    ├── git_utils.py   
│    ├── reporter.py    # 결과 출력 및 색상 처리 
└── Detectors         # 정규식 탐지 로직

python privacy_scan/main.py --diff-only
python privacy_scan/main.py --path .
python privacy_scan/main.py --diff-only --summary-only
python privacy_scan/main.py --diff-only --fail-on-detection