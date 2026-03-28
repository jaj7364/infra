# results는 full_scanner.py와 diff_scanner.py의 결과
def print_results(results, summary_only=False):
    total_methods = 0
    total_regex = 0

    for file_path, findings in results.items():
        if not summary_only:
            print(f"\n📄 {file_path}")

        for finding in findings:
            # summary_only 라면 조건문 통과
            if not summary_only:
                print(f"  -> [Line {finding['line']}] {finding['type']}: {finding['matches']}")

            if "사전탐지" in finding['type']:
                total_methods += 1
            else:
                total_regex += 1

    print("\n==================================================")
    print("[!] 개인정보 의심 항목 탐지 결과")
    print(f"    - 민감 메소드 의심: {total_methods}건")
    print(f"    - 하드코딩 개인정보 의심: {total_regex}건")
    print("==================================================")

    return total_methods + total_regex