"""
blackboard.py
=============
모든 상태가 공유하는 '칠판(blackboard)'.

이 파일이 하는 일:
  - 상태끼리 주고받아야 하는 데이터(적 탐지 여부, 남은 HP, 마지막 타겟 좌표 등)를
    한 객체에 모아둔다.
  - ROS 퍼블리셔 핸들과 "무엇을 발행한다"는 동작(메서드)도 여기에 둔다.
  - 각 상태(state)는 ROS를 직접 몰라도 되고, 오직 blackboard만 보면 된다.

왜 이렇게 하나 (핵심 설계):
  - 상태 파일에서 rclpy/퍼블리셔를 직접 만지면, 상태 로직과 ROS 배선이 뒤엉켜
    디버깅이 어려워진다.
  - blackboard가 그 사이를 막아주는 '단일 창구' 역할을 하므로,
    상태는 "blackboard.fire()" 처럼 의도만 표현하면 된다.
  - 나중에 토픽 이름이 바뀌어도 이 파일 한 곳만 고치면 된다.

노드(mission_manager_node)가 이 객체를 생성해서 각 상태에 넘겨준다.
"""

from std_msgs.msg import Bool, Int32
from geometry_msgs.msg import Twist


class Blackboard:
    def __init__(self, node):
        # node = MissionManagerNode 인스턴스. 퍼블리셔 생성을 위해 참조를 들고 있는다.
        self.node = node
        self.log = node.get_logger()

        # ---- 상태 간 공유되는 '입력' 데이터 (구독 콜백이 갱신) ----
        self.is_enemy = False          # YOLO: 적 탐지 여부
        self.is_gone = False           # 타겟 놓침
        self.enemy_locked = False      # 조준 정렬 완료
        self.opp_hp = 3                # 남은 적 HP (Enemy State Evaluator가 갱신)
        self.game_started = False      # /start_patrol 수신 여부

        # ---- 출력 퍼블리셔 ----
        # 토픽은 상대경로로 선언 -> 네임스페이스(/robot4)가 자동으로 앞에 붙는다.
        self.pub_start_slam = node.create_publisher(Bool, 'start_slam', 10)
        self.pub_explore_resume = node.create_publisher(Bool, 'explore/resume', 10)
        self.pub_start_tracking = node.create_publisher(Bool, 'start_tracking', 10)
        self.pub_fire = node.create_publisher(Bool, 'fire_cmd', 10)
        self.pub_return = node.create_publisher(Bool, 'return_request', 10)
        self.pub_cmd_vel = node.create_publisher(Twist, 'cmd_vel', 10)

    # ===== 상태들이 호출하는 '동작' 메서드 =====
    # 각 상태는 아래 메서드만 부르면 되고, 토픽 이름/메시지 타입은 몰라도 된다.

    def start_exploration(self):
        """Auto SLAM 순찰 시작/재개."""
        self._pub(self.pub_start_slam, True)
        self._pub(self.pub_explore_resume, True)
        self.log.info('[BB] 순찰(탐사) 시작/재개')

    def pause_exploration(self):
        """Auto SLAM 순찰 일시정지."""
        self._pub(self.pub_explore_resume, False)
        self.log.info('[BB] 순찰(탐사) 일시정지')

    def start_tracking(self):
        """방위각 회전 추적 활성화."""
        self._pub(self.pub_start_tracking, True)
        self.log.info('[BB] 방위각 추적 시작')

    def stop_tracking(self):
        """방위각 회전 추적 비활성화 + 정지."""
        self._pub(self.pub_start_tracking, False)
        self._stop_robot()
        self.log.info('[BB] 방위각 추적 중지')

    def fire(self):
        """사격 트리거 발행."""
        self._pub(self.pub_fire, True)
        self.log.info('[BB] 사격!')

    def request_return(self):
        """도킹 복귀 요청 (dock_manager가 처리)."""
        self._pub(self.pub_return, True)
        self.log.info('[BB] 복귀 요청')

    def _stop_robot(self):
        """cmd_vel 0으로 안전 정지."""
        self.pub_cmd_vel.publish(Twist())

    def _pub(self, pub, value: bool):
        m = Bool()
        m.data = value
        pub.publish(m)
