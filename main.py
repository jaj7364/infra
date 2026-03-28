import sys
import os
import argparse
import time
import subprocess #추가
from scanner import DirectoryScanner FileListScanner #추가

def get_git_diff_files():
    """GitLab MR 환경에서 타겟 브랜치와 비교하여 추가/수정된 파일만 추출"""
    # GitLab CI가 제공하는 타겟 브랜치 이름 (기본값 fallback 처리)
    target_branch = os.environ.get('CI_MERGE_REQUEST_TARGET_BRANCH_NAME', 'main')

    try:
        # GitLab Runner는 기본적으로 얕은 복사(shallow clone)를 할 수 있어 타겟 브랜치를 명시적으로 fetch
        subprocess.run(['git', 'fetch', 'origin', target_branch], check=False, capture_output=True)

        # A(Added), M(Modified) 상태인 파일만 추출 (D(Deleted)된 파일은 스캔할 수 없으므로 제외)
        cmd = ['git', 'diff', '--name-only', '--diff-filter=AM', f'origin/{target_branch}...HEAD']
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        # 줄바꿈 기준으로 리스트화 후, 빈 문자열 제거 및 실제 존재하는 파일인지 한 번 더 검증
        files = [f for f in result.stdout.strip().split('\n') if f and os.path.isfile(f)]
        return files
    except subprocess.CalledProcessError as e:
        print(f"[-] Git diff 추출 실패: {e}")
        return []

def main():
    parser = argparse.ArgumentParser(description="Privacy Scan for GitLab Runner")
    parser.add_argument('--path', type=str, default='.', help='스캔할 최상위 디렉토리 경로')
    parser.add_argument('--diff-only', action='store_true', help='Git Diff 변경된 파일만 스캔')
    args = parser.parse_args()

    print(f"[*] 개인정보 스캔을 시작합니다. (경로: {args.path})")
    print("==================================================")
    start_time = time.time()

#     #git diff 로직이 들어갈 자리
#     if args.diff_only:
#         print("[*] Git 변경 파일만 스캔합니다...")
#         target_files = get_git_diff_files()

    #1.전체 디렉터리 스캔 인스턴스 생성 및 실행
    script_dir = os.path.dirname(os.path.abspath(__file__))
    method_file_path = os.path.join(script_dir, 'pii_methods.txt')
    scanner = DirectoryScanner(args.path, method_file_path)
    results = scanner.scan()

    end_time = time.time()
    elapsed_time = end_time - start_time

    #2.결과 출력 및 CI/CD 제어
    if not results:
        print("\n[+] 탐지된 개인정보가 없습니다.")
        print(f"스캔 소요 시간: {elapsed_time:.1f}초")
        sys.exit(0)
    else:
        print("\n[-] 개인정보 노출이 의심되는 항목이 탐지되었습니다.")

        total_methods = 0
        total_regex = 0

        for file_path, findings in results.items():
            print(f"파일: {file_path}")
            for finding in findings:
                print(f"  -> [Line {finding['line']}] {finding['type']}: {finding['matches']}")

                if "사전탐지" in finding['type']:
                    total_methods += 1
                else:
                    total_regex += 1

        print("\n==================================================")
        print("[!] 소스코드 내에서 개인정보 의심 항목이 탐지되었습니다. 내용을 확인해주세요.")
        print(f"    - 민감 메소드 의심: {total_methods}건")
        print(f"    - 하드코딩 개인정보 의심: {total_regex}건")
        print(f"    - 스캔 소요 시간: {elapsed_time:.2f}초")
        print("==================================================")
        #나중에 파이프라인 차단하려면 sys.exit(1)로 변경
        sys.exit(0)

if __name__ == "__main__":
    main()