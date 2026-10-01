import json
import os
import threading
import time
import uuid
from dataclasses import dataclass
from typing import Callable
from urllib import parse, request

DEMO_USERNAMES = ["Demo Dan", "Demo Daniela", "Demo Darius", "Demo Diane", "Demo Donatello"]
DEMO_CHIPS = 5000
LEASE_SECONDS = 60 * 60
IDLE_SECONDS = 15 * 60

TURNSTILE_VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
TURNSTILE_TEST_SECRET = "1x0000000000000000000000000000000AA"  # cloudflare's always-pass secret


def is_demo_username(username: str) -> bool:
    return username in DEMO_USERNAMES


class AllSeatsBusyError(Exception):
    def __init__(self, retry_after: int):
        self.retry_after = retry_after
        super().__init__(f"All demo seats busy, retry in {retry_after}s")


@dataclass
class Lease:
    lease_id: str
    username: str
    claimed_at: float
    last_active: float

    def expires_at(self) -> float:
        return min(self.claimed_at + LEASE_SECONDS, self.last_active + IDLE_SECONDS)

    def is_expired(self, now: float) -> bool:
        return now >= self.expires_at()


class DemoLeaseManager:
    def __init__(self, usernames: list[str], clock: Callable[[], float] = time.time):
        self.usernames = usernames
        self.clock = clock
        self.leases: dict[str, Lease] = {}  # username -> Lease
        self.lock = threading.Lock()

    def claim(self, is_busy: Callable[[str], bool] = lambda _: False) -> Lease:
        """Hand out a free seat. A seat is free if it has no live lease and its user isn't mid-hand."""
        with self.lock:
            now = self.clock()
            for username in self.usernames:
                lease = self.leases.get(username)
                if (lease is None or lease.is_expired(now)) and not is_busy(username):
                    new_lease = Lease(uuid.uuid4().hex, username, now, now)
                    self.leases[username] = new_lease
                    return new_lease
            soonest = min((l.expires_at() for l in self.leases.values()), default=now)
            raise AllSeatsBusyError(max(int(soonest - now), 60))

    def is_valid(self, username: str, lease_id: str) -> bool:
        with self.lock:
            lease = self.leases.get(username)
            return bool(lease and lease.lease_id == lease_id and not lease.is_expired(self.clock()))

    def touch(self, username: str) -> None:
        with self.lock:
            lease = self.leases.get(username)
            if lease and not lease.is_expired(self.clock()):
                lease.last_active = self.clock()

    def release(self, username: str, lease_id: str) -> None:
        with self.lock:
            lease = self.leases.get(username)
            if lease and lease.lease_id == lease_id:
                del self.leases[username]


demo_leases = DemoLeaseManager(DEMO_USERNAMES)


def verify_turnstile(token: str | None, remote_ip: str | None) -> bool:
    secret = os.getenv("TURNSTILE_SECRET")
    if not secret:
        if os.getenv("FLASK_ENV") == "production":
            print("TURNSTILE_SECRET not set - refusing demo login")
            return False
        secret = TURNSTILE_TEST_SECRET
    if not token:
        print("turnstile: no token in demo request")
        return False
    data = parse.urlencode({"secret": secret, "response": token, "remoteip": remote_ip or ""}).encode()
    try:
        with request.urlopen(TURNSTILE_VERIFY_URL, data=data, timeout=5) as resp:
            result = json.load(resp)
        if not result.get("success"):
            print(f"turnstile rejected token: {result.get('error-codes')}")
        return bool(result.get("success"))
    except Exception as e:
        print(f"turnstile verification failed: {e}")
        return False
