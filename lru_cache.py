import logging
import threading
import concurrent.futures

logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)-8s | %(message)s"
)
log = logging.getLogger("LRUCache")


# ── Doubly Linked List Node ────────────────────────────────────────────────────

class Node:
    """A single node in the doubly linked list."""

    __slots__ = ("key", "value", "prev", "next")

    def __init__(self, key: int = 0, value: int = 0):
        self.key   = key
        self.value = value
        self.prev: "Node | None" = None
        self.next: "Node | None" = None


# ── LRU Cache ─────────────────────────────────────────────────────────────────

class LRUCache:
    """
    LRU Cache backed by a HashMap + Doubly Linked List.

    Parameters
    ----------
    capacity : int
        Maximum number of key-value pairs the cache holds.
    """

    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("Capacity must be a positive integer.")

        self.capacity = capacity
        self.cache: dict[int, Node] = {}   # key → Node  (the HashMap)

        # Sentinel nodes — never hold real data, simplify edge cases
        self._head = Node()   # left boundary  (LRU side)
        self._tail = Node()   # right boundary (MRU side)
        self._head.next = self._tail
        self._tail.prev = self._head

        self._lock = threading.Lock()
        log.info("LRUCache initialised (thread-safe) | capacity=%d", capacity)

    # ── Private DLL helpers ────────────────────────────────────────────────────

    def _remove(self, node: Node) -> None:
        """Detach a node from the DLL in O(1)."""
        node.prev.next = node.next
        node.next.prev = node.prev

    def _insert_mru(self, node: Node) -> None:
        """Insert a node just before the tail (MRU position) in O(1)."""
        node.prev = self._tail.prev
        node.next = self._tail
        self._tail.prev.next = node
        self._tail.prev = node

    # ── Public API ─────────────────────────────────────────────────────────────

    def get(self, key: int) -> int:
        """
        Return value for key, or -1 if absent.
        Marks the key as most recently used.

        Time  : O(1)
        Space : O(1)  (no extra allocation)
        """
        with self._lock:
            if key not in self.cache:
                log.debug("get(%d) → -1  [miss]", key)
                return -1

            node = self.cache[key]
            self._remove(node)
            self._insert_mru(node)

            log.debug("get(%d) → %d  [hit, promoted to MRU]", key, node.value)
            return node.value

    def put(self, key: int, value: int) -> None:
        """
        Insert or update key-value pair.
        Evicts the LRU item when cache is at capacity.

        Time  : O(1)
        Space : O(1)  per call (one node allocation at most)
        """
        with self._lock:
            if key in self.cache:
                node = self.cache[key]
                node.value = value
                self._remove(node)
                self._insert_mru(node)
                log.debug("put(%d, %d) → updated existing key, promoted to MRU", key, value)
                return

            if len(self.cache) == self.capacity:
                lru_node = self._head.next
                self._remove(lru_node)
                del self.cache[lru_node.key]
                log.debug("put(%d, %d) → evicted LRU key=%d", key, value, lru_node.key)

            new_node = Node(key, value)
            self.cache[key] = new_node
            self._insert_mru(new_node)
            log.debug("put(%d, %d) → inserted as MRU", key, value)

    # ── Utility ────────────────────────────────────────────────────────────────

    def _state(self) -> str:
        """Return a human-readable snapshot of the DLL order (LRU → MRU)."""
        items = []
        cur = self._head.next
        while cur is not self._tail:
            items.append(f"{cur.key}:{cur.value}")
            cur = cur.next
        return "[LRU] " + " → ".join(items) + " [MRU]"


# ── Demo / Test ────────────────────────────────────────────────────────────────

def run_demo() -> None:
    log.info("=" * 55)
    log.info("DEMO — capacity = 3")
    log.info("=" * 55)

    cache = LRUCache(capacity=3)

    # Fill the cache
    cache.put(1, 10)
    log.info("State: %s", cache._state())

    cache.put(2, 20)
    log.info("State: %s", cache._state())

    cache.put(3, 30)
    log.info("State: %s", cache._state())

    # Access key=1 → promotes it to MRU
    result = cache.get(1)
    log.info("get(1) = %d | State: %s", result, cache._state())

    # put(4) → evicts LRU which is now key=2
    cache.put(4, 40)
    log.info("After put(4,40) | State: %s", cache._state())

    # key=2 was evicted
    result = cache.get(2)
    log.info("get(2) = %d  (expected -1, was evicted)", result)

    # key=3 still present
    result = cache.get(3)
    log.info("get(3) = %d  (expected 30)", result)

    # Update an existing key
    cache.put(3, 99)
    log.info("After put(3,99) update | State: %s", cache._state())

    log.info("=" * 55)
    log.info("THREAD-SAFETY DEMO — 8 threads, 200 total operations")
    log.info("=" * 55)
    import random
    ts_cache = LRUCache(capacity=4)
    errors: list[Exception] = []

    def _worker(tid: int) -> None:
        try:
            for _ in range(25):
                k = random.randint(1, 6)
                if random.random() < 0.5:
                    ts_cache.put(k, tid * 10 + k)
                else:
                    ts_cache.get(k)
        except Exception as e:
            errors.append(e)

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        futs = [pool.submit(_worker, i) for i in range(8)]
        concurrent.futures.wait(futs)

    if errors:
        log.error("Race condition detected! %s", errors)
    else:
        log.info("200 concurrent ops completed — no race conditions.")

    log.info("=" * 55)
    log.info("COMPLEXITY SUMMARY")
    log.info("=" * 55)
    log.info("Operation | Time | Space")
    log.info("----------+------+------")
    log.info("get(key)  | O(1) | O(1)")
    log.info("put(k,v)  | O(1) | O(1)  amortised (eviction is O(1))")
    log.info("Overall cache space: O(capacity)")
    log.info("=" * 55)


if __name__ == "__main__":
    run_demo()
