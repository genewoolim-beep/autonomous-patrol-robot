"""
patrol_state.py
==============
PATROL 상태: Auto SLAM으로 자율 순찰하며 적을 기다린다. (시작 상태)

진입(on_enter): 순찰(탐사) 시작/재개. 추적이 켜져 있었다면 끈다.
반복(execute):  적이 탐지되면(is_enemy) 자동으로 TRACE로 전이.

★ 사람이 명령을 넣지 않아도, is_enemy 플래그만 True가 되면 알아서 넘어간다.
"""

from mission_manager_pkg.states.base_state import BaseState
from mission_manager_pkg.state_enum import State


class PatrolState(BaseState):
    def on_enter(self):
        self.log.info('=== PATROL 진입: 자율 순찰 시작 ===')
        self.bb.stop_tracking()      # 이전 추적 잔여 동작 정리
        self.bb.start_exploration()  # explore_lite 순찰 시작/재개

    def execute(self) -> State | None:
        # 적 탐지 -> 추적 상태로 자동 전이
        if self.bb.is_enemy:
            self.log.info('적 탐지! PATROL -> TRACE')
            return State.TRACE
        return None
