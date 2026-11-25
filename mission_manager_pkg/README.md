# mission_manager_pkg

Auto SLAM / Nav2 위에서 도는 **자동 전이 상태머신**. 사람이 명령을 넣지 않아도
조건이 맞으면 순찰 → 추적 → 교전 → 복귀로 알아서 넘어간다.

## 폴더 구조

```
mission_manager_pkg/                 # 패키지 루트 (빌드 메타데이터)
├── package.xml
├── setup.py
├── setup.cfg
├── resource/mission_manager_pkg
├── launch/mission.launch.py         # namespace 인자로 실행
├── config/mission_params.yaml       # tick_hz 등
├── test/test_states.py              # ROS 없이 전이 검증
└── mission_manager_pkg/             # ★ 실제 파이썬 코드 (이름 중복 폴더)
    ├── mission_manager_node.py      # ROS 노드 + 자동 전이 루프
    ├── state_enum.py                # 상태 이름표 (Enum)
    ├── blackboard.py                # 상태 공유 데이터 + ROS 발행 창구
    └── states/
        ├── base_state.py            # 공통 인터페이스 (on_enter/execute/on_exit)
        ├── patrol_state.py          # 순찰 (시작 상태)
        ├── trace_state.py           # 방위각 추적
        ├── engage_state.py          # 사격 + HP 카운트
        └── return_state.py          # 도킹 복귀
```

## 파일별 역할

| 파일 | 역할 |
|---|---|
| `state_enum.py` | 모든 상태를 Enum으로 정의. 오타 방지. |
| `blackboard.py` | 상태 간 공유 데이터(is_enemy, opp_hp 등) + "무엇을 발행한다"는 동작을 한 곳에. 상태는 ROS를 직접 안 만지고 blackboard만 본다. |
| `base_state.py` | 모든 상태가 같은 3메서드를 갖게 강제. 노드가 상태 종류를 몰라도 execute() 호출만 하면 됨. |
| `patrol_state.py` | 탐사 시작/재개. `is_enemy` True → TRACE. |
| `trace_state.py` | 탐사 정지 + 회전 추적. `enemy_locked` → ENGAGE, `is_gone` → PATROL. |
| `engage_state.py` | 사격. `opp_hp<=0` → RETURN, `is_gone` → TRACE. |
| `return_state.py` | 복귀 요청. 도킹 완료 → DONE. |
| `mission_manager_node.py` | 토픽 구독 → blackboard 갱신, 타이머로 execute() 반복 호출 → 자동 전이. |

## 상태 전이 (자동)

```
        /start_patrol
             │
             ▼
        ┌─────────┐  is_enemy   ┌────────┐  enemy_locked  ┌────────┐
        │ PATROL  │───────────▶│ TRACE  │──────────────▶│ ENGAGE │
        └─────────┘             └────────┘                └────────┘
             ▲                    │  ▲                     │   │
             └──── is_gone ───────┘  └──── is_gone ────────┘   │ opp_hp<=0
                                                                ▼
                                          ┌────────┐  dock   ┌──────┐
                                          │ RETURN │───────▶│ DONE │
                                          └────────┘         └──────┘
```

전이 '조건'은 각 상태 파일의 `execute()` 안에 있고, 노드는 그걸 실행만 한다.

## 입력/출력 토픽 (네임스페이스 자동 프리픽스)

**구독 (입력)**
- `start_patrol` (Bool) — 게임 시작 신호
- `is_enemy` (Bool) — YOLO 적 탐지
- `is_gone` (Bool) — 타겟 놓침
- `enemy_locked` (Bool) — 조준 정렬 완료
- `opp_hp` (Int32) — 남은 적 HP
- `dock_result` (Bool) — 도킹 완료

**발행 (출력)**
- `start_slam`, `explore/resume` (Bool) — 탐사 제어
- `start_tracking` (Bool) — azimuth_tracker 켜고 끄기
- `fire_cmd` (Bool) — 사격
- `return_request` (Bool) — dock_manager에 복귀 요청
- `cmd_vel` (Twist) — 안전 정지용

## 빌드 & 실행

```bash
cd ~/rokey_ws
colcon build --symlink-install --packages-select mission_manager_pkg
source install/setup.bash

ros2 launch mission_manager_pkg mission.launch.py namespace:=robot4
```

시작하려면 게임 시작 신호를 한 번 주면 된다:

```bash
ros2 topic pub -1 /robot4/start_patrol std_msgs/Bool "{data: true}"
```

## 테스트 (ROS 불필요)

```bash
cd ~/rokey_ws/src/mission_manager_pkg
PYTHONPATH=. python3 test/test_states.py
```

## 남은 연결 지점 (직접 채워야 하는 부분)

- **explore/resume**: explore_lite(m-explore-ros2)가 이 토픽을 구독하는지 확인.
  네임스페이스에 맞게 리매핑 필요할 수 있음.
- **azimuth_tracker / target_navigator / dock_manager**: 이 노드들은 별도 패키지에
  두거나 이 패키지에 추가. 미션 매니저는 토픽으로만 통신하므로 위치는 자유.
- **enemy_locked 판정**: "조준이 맞았다"를 누가 판단해 발행하는지 정해야 함
  (YOLO 방위각 오차가 임계값 이하일 때 등).
