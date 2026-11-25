"""
trace_state.py
=============
TRACE 상태: 적을 발견해 순찰을 멈추고 방위각 회전 추적으로 조준을 맞춘다.

진입(on_enter): 순찰 정지 + 방위각 추적(azimuth_tracker) 활성화.
반복(execute):
  - 조준 정렬 완료(enemy_locked) -> ENGAGE로 자동 전이
  - 타겟 놓침(is_gone)           -> PATROL로 복귀 (다시 탐색)
이탈(on_exit): 추적 종료 정리.
"""

from mission_manager_pkg.states.base_state import BaseState
from mission_manager_pkg.state_enum import State


class TraceState(BaseState):
    def on_enter(self):
        self.log.info('=== TRACE 진입: 순찰 정지, 방위각 추적 ===')
        self.bb.pause_exploration()  # 순찰 정지 (cmd_vel 제어권 회수)
        self.bb.start_tracking()     # 회전 추적 시작

    def execute(self) -> State | None:
        # 조준 완료 -> 교전
        if self.bb.enemy_locked:
            self.log.info('조준 완료! TRACE -> ENGAGE')
            return State.ENGAGE
        # 놓침 -> 순찰 복귀
        if self.bb.is_gone:
            self.log.info('타겟 놓침. TRACE -> PATROL')
            return State.PATROL
        return None

    def on_exit(self):
        self.bb.stop_tracking()
