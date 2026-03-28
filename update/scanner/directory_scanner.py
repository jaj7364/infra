import os
from .base_scanner import BaseScanner

class DirectoryScanner(BaseScanner):
    def __init__(self, target_dir, method_file_path):
        super().__init__(method_file_path)
        self.target_dir = target_dir

    def scan(self):
        results = {}

        for root, dirs, files in os.walk(self.target_dir):
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]

            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in self.ignore_exts:
                    continue

                if file in ("pii_methods.txt", ".cfinfo"):
                    continue

                file_path = os.path.join(root, file)
                file_results = self._scan_file(file_path)

                if file_results:
                    results[file_path] = file_results

        return results