import math
import time

import pytest

from docbuild.utils.contextmgr import make_timer


def test_timer_has_correct_attributes():
    timer_name = 'test-timer'
    sleep_duration = 0.1
    time_func = make_timer(timer_name)

    with time_func() as timer_data:
        time.sleep(sleep_duration)

    for key in ('name', 'start', 'end', 'elapsed'):
        assert hasattr(timer_data, key), f"Expected key '{key}' not found in timer_data"


def test_timer_as_context_manager_measures_time():
    timer_name = 'test-timer'
    sleep_duration = 0.1
    timer = make_timer(timer_name)

    with timer() as timer_data:
        time.sleep(sleep_duration)

    elapsed = timer_data.elapsed
    assert isinstance(elapsed, float)
    assert elapsed == pytest.approx(sleep_duration, abs=0.05)


def test_timer_factory_creates_independent_timers():
    timer_name1 = 'test-timer-1'
    timer_name2 = 'test-timer-2'
    sleep_duration = 0.1

    timer1 = make_timer(timer_name1)
    timer2 = make_timer(timer_name2)

    with timer1() as timer_data1:
        time.sleep(sleep_duration)

    with timer2() as timer_data2:
        time.sleep(sleep_duration*2)

    assert timer_data1.name == timer_name1
    assert timer_data2.name == timer_name2
    assert timer_data1.elapsed != timer_data2.elapsed
    assert isinstance(timer_data1.elapsed, float)
    assert isinstance(timer_data2.elapsed, float)
    assert timer_data1.elapsed == pytest.approx(sleep_duration, abs=0.01)
    assert timer_data2.elapsed == pytest.approx(sleep_duration*2, abs=0.01)


def test_timer_for_nan_as_default():
    timer_name = 'test-timer'
    timer = make_timer(timer_name)
    sleep_duration = 0.1

    with timer() as timer_data:
        time.sleep(sleep_duration)
        assert timer_data.start > 0
        assert math.isnan(timer_data.end)
        assert math.isnan(timer_data.elapsed)
