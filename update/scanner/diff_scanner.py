import os
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from .base_scanner import BaseScanner

class DiffScanner(BaseScanner):
    def __init__(self, target_files, method_file_path):
        super().__init__(method_file_path)
        # 문자열 리스트를 Path 객체 리스트로 변환
        self.target_files = [Path(f) for f in target_files]

    def scan(self):
        results = {}

        # 1. 스캔 대상 필터링 (불필요한 파일은 병렬 프로세스에 보내지도 않음)
        valid_files = []
        for file_path in self.target_files:
            if not file_path.exists() or file_path.is_dir():
                continue

            if file_path.suffix.lower() in self.ignore_exts:
                continue

            if file_path.name in ("pii_methods.txt", ".cfinfo"):
                continue

            valid_files.append(file_path)

        if not valid_files:
            return results

        # 2. 병렬 실행 (ProcessPoolExecutor)
        # max_workers를 지정하지 않으면 자동으로 CPU 코어 수에 맞게 설정됩니다.
        with ProcessPoolExecutor() as executor:
            # map 함수는 valid_files의 각 요소를 self._scan_file에 하나씩 던져줍니다.
            # 결과는 리스트의 리스트 형태([[결과1, 결과2], [], [결과3]])가 됩니다.
            all_findings = list(executor.map(self._scan_file, valid_files))

        # 3. 결과 합치기 (데이터 재구성)
        for file_path, file_results in zip(valid_files, all_findings):
            if file_results:
                results[str(file_path)] = file_results

        return results