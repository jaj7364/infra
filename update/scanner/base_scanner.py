import os
from detectors import ALL_DETECTORS

class BaseScanner:
    def __init__(self, method_file_path):
        # 민감 메소드 사전
        self.method_dict = self._load_methods(method_file_path)
        # 정규식 기반 탐지기
        self.detectors = ALL_DETECTORS

        self.ignore_dirs = ('.git', '__pycache__', 'node_modules', 'venv', '.idea')
        self.ignore_exts = (
            '.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico',
            '.zip', '.tar', '.gz', '.pdf', '.pyc',
            '.woff', '.woff2', '.ttf', '.eot', '.otf',
            '.bin', '.exe', '.dll', '.class', '.jar',
            '.csl', '.dat', '.cfinfo', '.so', '.apk'
        )

    # 민감 메소드 파일(txt)을 열여서 method_dict 생성
    def _load_methods(self, file_path):
        method_dict = {}

        if not os.path.exists(file_path):
            print(f"[경고] 사전 파일({file_path}) 없음")
            return method_dict

        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()

                if not line or line.startswith('#'):
                    continue

                if '=' in line:
                    method, description = line.split('=', 1)
                    method_dict[method.strip()] = description.strip()
                else:
                    method_dict[line.strip()] = "사전 정의 메소드"

        return method_dict

    # 민감 메소드 기반 검사 & 정규식 기반 검사
    def _scan_file(self, file_path):
        findings = []
        encoding_to_try = ['utf-8', 'cp949', 'euc-kr']

        for encoding_type in encoding_to_try:
            try:
                with open(file_path, 'r', encoding=encoding_type) as f:
                    for line_num, line in enumerate(f, 1):
                        clean_line = line.strip()

                        if not clean_line:
                            continue

                        # 1️⃣ 사전 기반 탐지
                        for method, description in self.method_dict.items():
                            if method in clean_line:
                                findings.append({
                                    "type": f"[사전탐지] 민감 메소드 ({description})",
                                    "line": line_num,
                                    "matches": [method]
                                })

                        # 2️⃣ 정규식 탐지
                        for detector in self.detectors:
                            matches = detector.detect(clean_line)
                            if matches:
                                findings.append({
                                    "type": detector.name,
                                    "line": line_num,
                                    "matches": matches
                                })

                break  # encoding 성공 시 종료 (더이상 for문을 돌지 않고 retrun findings)

            except UnicodeDecodeError:
                continue
            except Exception as e:
                print(f"[경고] {file_path} 읽기 실패: {e}")
                break

        return findings