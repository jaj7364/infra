import os
from .base_scanner import BaseScanner

class FullScanner(BaseScanner):
    def __init__(self, target_dir, method_file_path):
        super().__init__(method_file_path)
        self.target_dir = target_dir

    def scan(self):
        results = {}

        for root, dirs, files in os.walk(self.target_dir):
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]

#             # 1. 통과시킬(검사할) 폴더 이름만 담을 '새로운 빈 바구니'를 하나 준비합니다.
#             filtered_dirs = []
#
#             # 2. 현재 방(root) 안에 있는 하위 폴더(dirs)들을 하나씩(d) 꺼내봅니다.
#             for d in dirs:
#
#                 # 3. 만약 그 폴더 이름(d)이 무시할 목록(self.ignore_dirs, 예: '.git')에 없다면?
#                 if d not in self.ignore_dirs:
#
#                     # 4. 검사해야 할 정상적인 폴더이므로 새 바구니에 담습니다(append).
#                     filtered_dirs.append(d)
#
#             # 5. 원래의 dirs 리스트 '내용물'을 방금 걸러낸 새 바구니의 내용물로 싹 갈아끼웁니다.
#             dirs[:] = filtered_dirs

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