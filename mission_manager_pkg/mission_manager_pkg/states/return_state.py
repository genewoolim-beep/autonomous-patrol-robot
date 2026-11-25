"""
return_state.py
==============
RETURN 상태: 임무를 마치고 충전 독으로 복귀한다.

진입(on_enter): 추적/순찰 정지 후 복귀 요청 발행(/return_request).
               실제 도킹 액션은 dock_manager 노드가 수행한다.
반복(execute):  도킹 완료 신호를 받으면 DONE으로 전이.
               (도킹 완료는 dock_manager -> blackboard.dock_done 로 들어온다고 가정)
"""

from mission_manager_pkg.states.base_state import BaseState
from mission_manager_pkg.state_enum import State


class ReturnState(BaseState):
    def on_enter(self):
        self.log.info('=== RETURN 진입: 도킹 복귀 요청 ===')
        self.bb.stop_tracking()
        self.bb.pause_exploration()
        self.bb.request_return()

    def execute(self) -> State | None:
        if getattr(self.bb, 'dock_done', False):
            self.log.info('도킹 완료. RETURN -> DONE')
            return State.DONE
        return None
