import os
from .base_scanner import BaseScanner

class FileListScanner(BaseScanner):
    def __init__(self, target_files, method_file_path):
        super().__init__(method_file_path)
        self.target_files = target_files

    def scan(self):
        results = {}

        for file_path in self.target_files:
            if not os.path.exists(file_path):
                continue

            ext = os.path.splitext(file_path)[1].lower()
            if ext in self.ignore_exts:
                continue

            file_name = os.path.basename(file_path)
            if file_name in ("pii_methods.txt", ".cfinfo"):
                continue

            file_results = self._scan_file(file_path)

            if file_results:
                results[file_path] = file_results

        return results