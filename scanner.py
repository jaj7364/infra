import os
from detectors import ALL_DETECTORS

class DirectoryScanner:
    def __init__(self, target_dir, method_file_path):
        self.target_dir = target_dir
        self.method_dict = self._load_methods(method_file_path)
        self.detectors = ALL_DETECTORS

        self.ignore_dirs = ('.git', '__pycache__', 'node_modules', 'venv', '.idea')
        self.ignore_exts = ('.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico', '.zip', '.tar', '.gz', '.pdf', '.pyc', '.woff', '.woff2', '.ttf', '.eot', '.otf', '.bin', '.exe', '.dll', '.class', '.jar', '.csl', '.dat', '.cfinfo', '.so', '.apk', '.jar')

    def _load_methods(self, file_path):
        method_dict = {}
        if not os.path.exists(file_path):
            print(f"[경고] 사전 파일({file_path})을 찾을 수 없습니다. 메소드 스캔을 건너뜁니다.")
            return method_dict

        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                # '-'이 있으면 쪼개고, 없으면 기본 설명 부여
                if '-' in line:
                    method, description = line.split('-', 1)
                    method_dict[method.strip()] = description.strip()
                else:
                    method_dict[line.strip()] = "사전 정의 메소드"

        return method_dict

    def scan(self):
        results = {}
        for root, dirs, files in os.walk(self.target_dir):
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]

            # for file in files:
            #     print(f" ->파일 검사 시작: {file}")

            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in self.ignore_exts:
                    continue
                if file == "pii_methods.txt" or file.lower() == ".cfinfo":
                    continue

                file_path = os.path.join(root, file)
                # print(f" [디버그] 스캔 진입: {file_path}")
                file_results = self._scan_file(file_path)

                if file_results:
                    results[file_path] = file_results

        return results

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

                        #1단계: 사내 표준 메소드 사전 검사
                        for method, description in self.method_dict.items():
                            if method in clean_line:
                                findings.append({
                                    "type": f"[사전탐지] 민감 메소드 ({description})",
                                    "line": line_num,
                                    "matches": [method]
                                })

                        #2단계: 기존 정규식 탐지기 검사
                        for detector in self.detectors:
                            matches = detector.detect(clean_line)
                            if matches:
                                findings.append({
                                    'type': detector.name,
                                    'line': line_num,
                                    'matches': matches
                                })

                return findings

            except UnicodeDecodeError:
                pass
            except Exception as e:
                print(f"[경고] {file_path} 읽기 실패: {e}")
                break

        return findings