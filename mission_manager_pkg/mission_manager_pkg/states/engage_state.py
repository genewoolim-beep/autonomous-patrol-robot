"""
engage_state.py
==============
ENGAGE 상태: 조준이 맞은 상태에서 사격하고 결과를 판단한다.

진입(on_enter): 사격 트리거 발행(/fire_cmd). 피격 카운트는 Enemy State
               Evaluator 노드가 담당하고, 그 결과는 blackboard.opp_hp로 들어온다.
반복(execute):
  - 적 HP 0(opp_hp<=0)  -> RETURN (임무 완료, 복귀)
  - 타겟 놓침(is_gone)   -> TRACE (다시 추적)
  - 아직 살아있고 조준 유지 -> 계속 사격

주의: 여기서는 '한 번 진입 시 1발'이 아니라, 놓치지 않는 한 반복 사격하도록
      execute에서 재발사한다. 연사 간격이 필요하면 타이머/쿨다운을 두면 된다.
"""

from mission_manager_pkg.states.base_state import BaseState
from mission_manager_pkg.state_enum import State


class EngageState(BaseState):
    def on_enter(self):
        self.log.info('=== ENGAGE 진입: 사격 개시 ===')
        self.bb.fire()

    def execute(self) -> State | None:
        # 적 사살 -> 복귀
        if self.bb.opp_hp <= 0:
            self.log.info('적 처치! ENGAGE -> RETURN')
            return State.RETURN
        # 놓침 -> 재추적
        if self.bb.is_gone:
            self.log.info('타겟 놓침. ENGAGE -> TRACE')
            return State.TRACE
        # 아직 조준 유지 중이면 계속 사격
        if self.bb.enemy_locked:
            self.bb.fire()
        return None
