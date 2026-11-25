"""
test_states.py
=============
ROS 없이 상태 전이 로직만 검증하는 테스트.
blackboard를 가짜(fake)로 대체해서, 로봇/ROS 없이도 전이 규칙을 확인한다.

실행:
    cd ~/rokey_ws/src/mission_manager_pkg
    PYTHONPATH=. python3 -m pytest test/test_states.py -v
    # pytest 없으면: PYTHONPATH=. python3 test/test_states.py
"""

from mission_manager_pkg.state_enum import State
from mission_manager_pkg.states.patrol_state import PatrolState
from mission_manager_pkg.states.trace_state import TraceState
from mission_manager_pkg.states.engage_state import EngageState
from mission_manager_pkg.states.return_state import ReturnState


class _FakeLog:
    def info(self, *a): pass
    def warn(self, *a): pass


class _FakeBB:
    """blackboard 대역. 동작 메서드는 아무것도 안 하는 스텁."""
    def __init__(self):
        self.log = _FakeLog()
        self.is_enemy = False
        self.is_gone = False
        self.enemy_locked = False
        self.opp_hp = 3
        self.dock_done = False

    def stop_tracking(self): pass
    def start_exploration(self): pass
    def pause_exploration(self): pass
    def start_tracking(self): pass
    def fire(self): pass
    def request_return(self): pass


def test_patrol_holds_without_enemy():
    bb = _FakeBB()
    assert PatrolState(bb).execute() is None


def test_patrol_to_trace_on_enemy():
    bb = _FakeBB(); bb.is_enemy = True
    assert PatrolState(bb).execute() == State.TRACE


def test_trace_to_engage_on_lock():
    bb = _FakeBB(); bb.enemy_locked = True
    assert TraceState(bb).execute() == State.ENGAGE


def test_trace_to_patrol_on_gone():
    bb = _FakeBB(); bb.is_gone = True
    assert TraceState(bb).execute() == State.PATROL


def test_engage_to_return_on_kill():
    bb = _FakeBB(); bb.opp_hp = 0
    assert EngageState(bb).execute() == State.RETURN


def test_engage_to_trace_on_gone():
    bb = _FakeBB(); bb.is_gone = True
    assert EngageState(bb).execute() == State.TRACE


def test_return_to_done_on_dock():
    bb = _FakeBB(); bb.dock_done = True
    assert ReturnState(bb).execute() == State.DONE


if __name__ == '__main__':
    # pytest 없이도 돌아가도록
    for name, fn in list(globals().items()):
        if name.startswith('test_') and callable(fn):
            fn()
            print(f'PASS: {name}')
    print('ALL PASSED')
