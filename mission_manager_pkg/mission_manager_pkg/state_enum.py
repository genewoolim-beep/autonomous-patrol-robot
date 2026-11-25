"""
state_enum.py
=============
미션 상태의 '이름표'를 정의하는 파일.

이 파일이 하는 일:
  - 시스템에 존재하는 모든 상태를 하나의 Enum으로 모아둔다.
  - 각 상태 파일과 노드가 이 Enum을 공유해서, 문자열 오타로 인한
    "왜 전이가 안 되지?" 버그를 원천 차단한다.

왜 문자열("PATROL") 대신 Enum을 쓰나:
  - "PATROL"과 "Patrol"을 오타로 섞어 써도 파이썬은 에러를 안 낸다.
  - Enum(State.PATROL)을 쓰면 오타 시 즉시 AttributeError로 잡힌다.
"""

from enum import Enum, auto


class State(Enum):
    PATROL = auto()   # Auto SLAM 자율 순찰 (기본/시작 상태)
    TRACE = auto()    # 적 탐지 -> 순찰 정지 -> 방위각 회전 추적
    ENGAGE = auto()   # 조준 완료 -> 사격 -> 피격 카운트
    RETURN = auto()   # 임무 종료 -> 도킹 복귀
    DONE = auto()     # 종료
