import time
import httpx

SERVICES = ["http://127.0.0.1:8001", "http://127.0.0.1:8002", "http://127.0.0.1:8003"]
TIMEOUT = 1.0        # seconds to wait for an answer
SLOW_MS = 500        # slower than this is SLOW
INTERVAL = 2         # seconds between rounds
FAIL_LIMIT = 3       # failed checks in a row before we say DOWN


def check(client, url):
    """Return the response time in ms, or None if the service did not answer."""
    start = time.perf_counter()
    try:
        client.get(f"{url}/health").raise_for_status()
    except httpx.HTTPError:
        return None
    return (time.perf_counter() - start) * 1000


failures = {url: 0 for url in SERVICES}      # failed checks in a row, per service

with httpx.Client(timeout=TIMEOUT) as client:
    round_no = 0
    while True:
        round_no += 1
        now = time.strftime("%H:%M:%S")
        states = []
        for url in SERVICES:
            port = url.split(":")[-1]
            elapsed_ms = check(client, url)

            if elapsed_ms is None:                   # no answer
                failures[url] += 1
                if failures[url] >= FAIL_LIMIT:
                    state = "DOWN"
                else:
                    state = f"SUSPECT ({failures[url]}/{FAIL_LIMIT})"
            else:                                    # it answered
                failures[url] = 0
                if elapsed_ms > SLOW_MS:
                    state = f"SLOW ({elapsed_ms:.0f} ms)"
                else:
                    state = f"UP ({elapsed_ms:.0f} ms)"

            states.append(f"{port}: {state}")
        print(f"[{now}] round {round_no:>2} | " + " | ".join(states))
        time.sleep(INTERVAL)
