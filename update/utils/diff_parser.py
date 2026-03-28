import os
import subprocess

def get_git_diff_files():
    """GitLab MR 환경에서 변경된 파일 리스트 추출"""
    target_branch = os.environ.get('CI_MERGE_REQUEST_TARGET_BRANCH_NAME', 'main')

    try:
        # shallow clone 대응
        subprocess.run(
            ['git', 'fetch', '--depth=100', 'origin', target_branch],
            check=False,
            capture_output=True
        )

        # 변경된 파일 추출 (Added, Modified)
        cmd = [
            'git', 'diff',
            '--name-only',
            '--diff-filter=AM',
            f'origin/{target_branch}...HEAD'
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"[-] git diff 실패: {result.stderr}")
            return []

        files = [
            f for f in result.stdout.strip().split('\n')
            if f and os.path.isfile(f)
        ]
#     # 1. 스캔할 파일 이름들을 담을 빈 바구니를 준비합니다.
#         files = []
#
#         # 2. 터미널 출력 결과(stdout)를 다듬습니다.
#         # .strip(): 맨 앞이나 맨 뒤에 붙은 쓸데없는 공백이나 줄바꿈을 깔끔하게 지웁니다.
#         # .split('\n'): 엔터키(줄바꿈 기호 '\n')를 기준으로 글자를 칼질해서 조각조각 냅니다.
#         chopped_texts = result.stdout.strip().split('\n')
#
#         # 3. 조각난 글자(파일 경로)들을 하나씩 꺼내서 f 라고 부릅니다.
#         for f in chopped_texts:
#
#             # 4. 검증 1단계 (if f): 이름이 텅 비어있지 않은지 확인합니다. ("" 이면 False 취급)
#             # 5. 검증 2단계 (os.path.isfile): 이 경로에 진짜로 '파일'이 존재하는지 디스크를 뒤져서 확인합니다. (삭제된 파일이면 스캔할 수 없으니까요!)
#             if f and os.path.isfile(f):
#
#                 # 두 검증을 모두 통과한 진짜 파일만 바구니에 담습니다.
#                 files.append(f)

        return files

    except Exception as e:
        print(f"[-] Git diff 처리 중 오류: {e}")
        return []