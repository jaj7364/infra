import sys
import argparse
import time
from pathlib import Path

# 우리가 업그레이드한 부품들을 가져옵니다.
# (구조에 따라 from scanner.diff_scanner import DiffScanner 식으로 바뀔 수 있습니다)
from scanner import DiffScanner, FullScanner
from utils import get_git_diff_files, print_results

def main():
    parser = argparse.ArgumentParser(description="🚀 고성능 개인정보 스캔 도구 (Multiprocessing Edition)")

    parser.add_argument('--path', type=str, default='.', help='스캔할 디렉토리 경로')
    parser.add_argument('--diff-only', action='store_true', help='Git 변경 파일(Added/Modified)만 스캔')
    parser.add_argument('--summary-only', action='store_true', help='상세 내역 없이 요약만 출력')
    parser.add_argument('--fail-on-detection', action='store_true', help='탐지 건수가 있으면 Exit Code 1 반환 (CI용)')

    args = parser.parse_args()

    # 1. 경로 및 설정 초기화 (Pathlib 활용)
    base_path = Path(args.path).resolve()
    script_dir = Path(__file__).parent
    method_file_path = script_dir / 'pii_methods.txt'

    print(f"[*] 스캔 시작 (경로: {base_path})")
    print("=" * 50)

    # 2. 정밀 시간 측정 시작
    # time.time()보다 정밀한 측정이 가능한 perf_counter를 사용합니다.
    start_time = time.perf_counter()

    try:
        # 3. 모드에 따른 스캐너 선택 (다형성 활용)
        if args.diff_only:
            print("[*] 모드: Git 변경 파일 추적")
            target_files = get_git_diff_files()

            if not target_files:
                print("\n[+] 스캔할 변경된 파일이 없습니다. 종료합니다.")
                sys.exit(0)

            print(f"[*] 대상 파일 수: {len(target_files)}")
            scanner = DiffScanner(target_files, method_file_path)
        else:
            print("[*] 모드: 전체 디렉토리 스캔")
            if not base_path.exists():
                print(f"[-] 오류: 경로가 존재하지 않습니다: {base_path}")
                sys.exit(1)
            scanner = FullScanner(base_path, method_file_path)

        # 4. 스캔 실행 (우리가 만든 병렬 처리 로직이 여기서 작동합니다!)
        results = scanner.scan()

    except Exception as e:
        print(f"\n[❌ 오류 발생] 스캔 중 문제가 생겼습니다: {e}")
        sys.exit(1)

    # 5. 결과 출력 및 마무리
    elapsed_time = time.perf_counter() - start_time

    if not results:
        print(f"\n[✅] 탐지된 개인정보 의심 항목이 없습니다.")
        print(f"[*] 실행 시간: {elapsed_time:.2f}초")
        sys.exit(0)

    # formatter.py의 예쁜 출력을 호출합니다.
    total_count = print_results(results, args.summary_only)
    print(f"\n⏱️ 총 소요 시간: {elapsed_time:.2f}초")

    # 6. CI/CD 제어를 위한 종료 코드 설정
    if args.fail_on_detection and total_count > 0:
        print(f"\n[!] {total_count}건의 탐지 결과가 있어 프로세스를 실패(Exit 1) 처리합니다.")
        sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()