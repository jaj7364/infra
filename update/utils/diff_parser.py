import os
import subprocess
from pathlib import Path

def get_git_diff_files():
    """GitLab MR 환경에서 변경된(Added, Modified, Renamed) 파일 리스트 추출"""
    
    # 1. 환경 변수 처리 (Pathlib 미적용 구간이지만 명확하게 관리)
    target_branch = os.environ.get('CI_MERGE_REQUEST_TARGET_BRANCH_NAME', 'main')
    
    try:
        # 2. Shallow Clone 대응 (fetch)
        # --depth=100은 안전장치지만, 대상 브랜치만 콕 집어 가져오는 게 더 효율적입니다.
        fetch_cmd = ['git', 'fetch', '--depth=100', 'origin', target_branch]
        subprocess.run(fetch_cmd, check=False, capture_output=True, text=True)

        # 3. 변경된 파일 추출 (A:추가, M:수정, R:이름변경 포함)
        # '...HEAD' (점 3개)는 공통 조상(Merge Base)부터 현재까지의 차이를 찾는 정석적인 방법입니다.
        diff_cmd = [
            'git', 'diff',
            '--name-only',
            '--diff-filter=AMR',  # R(Renamed)도 포함하는 것이 보안상 안전합니다.
            f'origin/{target_branch}...HEAD'
        ]

        result = subprocess.run(diff_cmd, capture_output=True, text=True, check=True)

        # 4. 결과 정제 (List Comprehension + Pathlib)
        # 텅 빈 줄을 제거하고, 실제로 존재하는 '파일'인지 검증합니다.
        files = [
            line.strip() 
            for line in result.stdout.splitlines() 
            if line.strip() and Path(line.strip()).is_file()
        ]

        return files

    except subprocess.CalledProcessError as e:
        print(f"[-] git 명령 실행 실패: {e.stderr}")
        return []
    except Exception as e:
        print(f"[-] Git diff 처리 중 예상치 못한 오류: {e}")
        return []