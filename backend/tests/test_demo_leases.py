import pytest
from app.auth.demo import DemoLeaseManager, AllSeatsBusyError, IDLE_SECONDS, LEASE_SECONDS


class FakeClock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


@pytest.fixture
def clock():
    return FakeClock()


@pytest.fixture
def leases(clock):
    return DemoLeaseManager(["a", "b"], clock=clock)


def test_claims_free_seats_in_order(leases):
    assert leases.claim().username == "a"
    assert leases.claim().username == "b"


def test_all_seats_busy(leases, clock):
    leases.claim()
    clock.now += 60
    leases.claim()
    with pytest.raises(AllSeatsBusyError) as e:
        leases.claim()
    assert e.value.retry_after == IDLE_SECONDS - 60


def test_idle_lease_is_reclaimed(leases, clock):
    first = leases.claim()
    leases.claim()
    clock.now += IDLE_SECONDS
    second = leases.claim()
    assert second.username == first.username
    assert not leases.is_valid(first.username, first.lease_id)
    assert leases.is_valid(second.username, second.lease_id)


def test_touch_keeps_lease_alive(leases, clock):
    lease = leases.claim()
    clock.now += IDLE_SECONDS - 1
    leases.touch(lease.username)
    clock.now += IDLE_SECONDS - 1
    assert leases.is_valid(lease.username, lease.lease_id)


def test_hard_cap_despite_activity(leases, clock):
    lease = leases.claim()
    for _ in range(LEASE_SECONDS // 600):
        clock.now += 600
        leases.touch(lease.username)
    assert not leases.is_valid(lease.username, lease.lease_id)


def test_busy_user_not_reclaimed(leases, clock):
    leases.claim()
    leases.claim()
    clock.now += LEASE_SECONDS
    lease = leases.claim(is_busy=lambda name: name == "a")
    assert lease.username == "b"


def test_release_frees_seat(leases):
    lease = leases.claim()
    leases.release(lease.username, lease.lease_id)
    assert not leases.is_valid(lease.username, lease.lease_id)
    assert leases.claim().username == lease.username


def test_stale_release_does_nothing(leases, clock):
    old = leases.claim()
    leases.claim()
    clock.now += IDLE_SECONDS
    new = leases.claim()
    leases.release(old.username, old.lease_id)
    assert leases.is_valid(new.username, new.lease_id)
