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
            f'origin/{target_branch}..HEAD'
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"[-] git diff 실패: {result.stderr}")
            return []

        files = [
            f for f in result.stdout.strip().split('\n')
            if f and os.path.isfile(f)
        ]

        return files

    except Exception as e:
        print(f"[-] Git diff 처리 중 오류: {e}")
        return []