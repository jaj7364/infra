import sys
import os
import argparse
import time
from scanner import DiffScanner, FullScanner
from utils import get_git_diff_files, print_results

def main():
    # 터미널에서 입력받을 옵션들을 설명해주는 설명서(parser) 객체
    parser = argparse.ArgumentParser(description="Privacy Scan Tool")

    parser.add_argument('--path', type=str, default='.', help='스캔할 디렉토리')
    parser.add_argument('--diff-only', action='store_true', help='Git 변경 파일만 스캔')
    parser.add_argument('--summary-only', action='store_true', help='요약만 출력')
    parser.add_argument('--fail-on-detection', action='store_true', help='탐지 시 exit code 1')

    # 위에서 설정한 옵션 규칙을 바탕으로, 사용자가 실제 입력한 명령어들을 분석해서 args 변수에 담습니다.
    args = parser.parse_args()

    print(f"[*] 개인정보 스캔 시작 (경로: {args.path})")
    print("==================================================")

    # 스캔 시간 측정
    start_time = time.time()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    method_file_path = os.path.join(script_dir, 'pii_methods.txt')

    # 스캐너 선택
    if args.diff_only:
        print("[*] Git 변경 파일만 스캔합니다...")
        # 방금 수정된 파일 목록
        target_files = get_git_diff_files()

        if not target_files:
            print("\n[+] 스캔할 변경 파일 없음")
            sys.exit(0)

        print(f"[*] 대상 파일 수: {len(target_files)}")
        # 변경된 파일 목록만 검사하는 특화된 스캐너
        scanner = FileListScanner(target_files, method_file_path)

    else:
        print("[*] 전체 디렉토리 스캔")
        # 지정된 폴더 전체를 검사하는 스캐너
        scanner = DirectoryScanner(args.path, method_file_path)

    # 스캔 실행
    results = scanner.scan()

    elapsed_time = time.time() - start_time

    # 결과 처리
    if not results:
        print("\n[+] 탐지된 개인정보 없음")
        print(f"스캔 시간: {elapsed_time:.2f}초")
        sys.exit(0)

    print("\n[-] 개인정보 의심 항목 발견")

    total_count = print_results(results, args.summary_only)

    print(f"\n⏱️ 총 스캔 시간: {elapsed_time:.2f}초")

    # CI 제어
    if args.fail_on_detection and total_count > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()