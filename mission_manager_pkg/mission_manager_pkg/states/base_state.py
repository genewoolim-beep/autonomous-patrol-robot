"""
base_state.py
=============
모든 상태(state)가 상속하는 공통 뼈대.

이 파일이 하는 일:
  - 모든 상태가 똑같은 3개 메서드(on_enter / execute / on_exit)를 갖도록 강제한다.
  - 덕분에 노드의 실행 루프는 "지금 상태가 뭔지" 몰라도
    self.current.execute() 만 호출하면 된다. (다형성)

각 메서드의 의미:
  - on_enter(): 이 상태에 '처음 들어올 때' 딱 1번 실행. (예: TRACE 진입 시 순찰 정지)
  - execute():  타이머마다 '반복' 실행. 다음 상태(State)를 반환하면 전이,
                None을 반환하면 현재 상태 유지. ★자동 전이의 핵심★
  - on_exit():  이 상태를 '떠날 때' 딱 1번 실행. (정리 작업)
"""

from mission_manager_pkg.state_enum import State


class BaseState:
    def __init__(self, blackboard):
        self.bb = blackboard          # 공유 칠판
        self.log = blackboard.log

    def on_enter(self):
        """상태 진입 시 1회. 필요 없으면 오버라이드 안 해도 됨."""
        pass

    def execute(self) -> State | None:
        """
        주기적 실행. 다음 상태를 반환하면 전이, None이면 현재 유지.
        각 상태가 반드시 오버라이드한다.
        """
        return None

    def on_exit(self):
        """상태 이탈 시 1회. 필요 없으면 오버라이드 안 해도 됨."""
        pass
