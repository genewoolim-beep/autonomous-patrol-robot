"""
mission_manager_node.py
======================
미션 매니저 ROS2 노드 (시스템의 두뇌).

이 파일이 하는 일:
  1. blackboard 생성 + 모든 상태 객체 생성
  2. ROS 입력 토픽을 구독해서 blackboard의 플래그를 갱신
     (예: /is_enemy -> bb.is_enemy = True)
  3. 타이머로 주기적으로 현재 상태의 execute()를 호출하고,
     반환된 다음 상태로 자동 전이 (사람 개입 불필요)

자동 전이 루프 (tick):
    nxt = current.execute()      # 조건 검사
    if nxt: 상태 교체 + on_exit/on_enter 실행

핵심: 전이 '조건'은 각 상태 파일 안에 있고, 이 노드는 그 조건을 '실행'만 한다.
      노드는 어떤 상태가 있는지 세부를 몰라도 되게 최대한 얇게 유지.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, Int32

from mission_manager_pkg.state_enum import State
from mission_manager_pkg.blackboard import Blackboard
from mission_manager_pkg.states.patrol_state import PatrolState
from mission_manager_pkg.states.trace_state import TraceState
from mission_manager_pkg.states.engage_state import EngageState
from mission_manager_pkg.states.return_state import ReturnState


class MissionManagerNode(Node):
    def __init__(self):
        super().__init__('mission_manager')

        # 네임스페이스는 launch/run에서 리매핑으로 처리하므로 코드에선 상대 토픽만 쓴다.
        self.declare_parameter('tick_hz', 10.0)
        tick_hz = self.get_parameter('tick_hz').value

        # ---- 칠판 + 상태 객체 생성 ----
        self.bb = Blackboard(self)
        self.states = {
            State.PATROL: PatrolState(self.bb),
            State.TRACE:  TraceState(self.bb),
            State.ENGAGE: EngageState(self.bb),
            State.RETURN: ReturnState(self.bb),
        }

        # ---- 입력 구독: 토픽 -> blackboard 플래그 갱신 ----
        self.create_subscription(Bool, 'start_patrol', self._on_start_patrol, 10)
        self.create_subscription(Bool, 'is_enemy', self._on_is_enemy, 10)
        self.create_subscription(Bool, 'is_gone', self._on_is_gone, 10)
        self.create_subscription(Bool, 'enemy_locked', self._on_enemy_locked, 10)
        self.create_subscription(Int32, 'opp_hp', self._on_opp_hp, 10)
        self.create_subscription(Bool, 'dock_result', self._on_dock_result, 10)

        # ---- 상태 초기화: 게임 시작 신호를 받기 전엔 대기 ----
        self.current_state_key = None   # 아직 시작 안 함
        self.current = None

        # ---- 자동 전이 타이머 ----
        self.create_timer(1.0 / tick_hz, self._tick)

        self.get_logger().info('Mission Manager 준비 완료. /start_patrol 대기 중...')

    # ==========================================================
    # 입력 콜백
    # ==========================================================
    def _on_start_patrol(self, msg: Bool):
        if msg.data and self.current is None:
            # 게임 시작! PATROL로 진입
            self.bb.game_started = True
            self._enter(State.PATROL)

    def _on_is_enemy(self, msg: Bool):
        self.bb.is_enemy = msg.data

    def _on_is_gone(self, msg: Bool):
        self.bb.is_gone = msg.data

    def _on_enemy_locked(self, msg: Bool):
        self.bb.enemy_locked = msg.data

    def _on_opp_hp(self, msg: Int32):
        self.bb.opp_hp = msg.data

    def _on_dock_result(self, msg: Bool):
        self.bb.dock_done = msg.data

    # ==========================================================
    # 상태 실행 루프 (자동 전이의 심장)
    # ==========================================================
    def _tick(self):
        if self.current is None:
            return  # 아직 시작 신호 안 받음

        nxt = self.current.execute()
        if nxt is not None and nxt != self.current_state_key:
            self._transition(nxt)

    def _enter(self, state_key: State):
        self.current_state_key = state_key
        self.current = self.states[state_key]
        self.current.on_enter()

    def _transition(self, nxt: State):
        self.current.on_exit()
        if nxt == State.DONE:
            self.get_logger().info('=== 미션 종료 (DONE) ===')
            self.current = None
            self.current_state_key = State.DONE
            return
        self._enter(nxt)


def main():
    rclpy.init()
    node = MissionManagerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
