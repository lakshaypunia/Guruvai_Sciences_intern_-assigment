import heapq
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)-8s | %(message)s")
log = logging.getLogger("MeetingScheduler")


# ─────────────────────────────────────────────────────────────────────────────

def can_attend_all(events: list[tuple[int, int]]) -> bool:
    
    if not events:
        log.info("can_attend_all: empty list → True")
        return True

    sorted_events = sorted(events, key=lambda e: e[0])
    log.info("can_attend_all | sorted events: %s", sorted_events)

    for i in range(1, len(sorted_events)):
        prev_end   = sorted_events[i - 1][1]
        curr_start = sorted_events[i][0]

        if curr_start < prev_end:
            log.info(
                "  Overlap detected: event %s starts at %d before event %s ends at %d → False",
                sorted_events[i], curr_start, sorted_events[i - 1], prev_end,
            )
            return False

        log.info(
            "  No overlap: event %s → event %s (gap=%d)",
            sorted_events[i - 1], sorted_events[i], curr_start - prev_end,
        )

    log.info("  No overlaps found → True")
    return True


# ─────────────────────────────────────────────────────────────────────────────

def min_rooms_required(events: list[tuple[int, int]]) -> int:

    if not events:
        log.info("min_rooms_required: empty list → 0")
        return 0

    sorted_events = sorted(events, key=lambda e: e[0])
    log.info("min_rooms_required | sorted events: %s", sorted_events)

    heap: list[int] = []   # min-heap of end-times

    for start, end in sorted_events:
        if heap and heap[0] <= start:
            freed_at = heap[0]
            heapq.heapreplace(heap, end)   # reuse the freed room
            log.info(
                "  Event (%d,%d): room freed at %d → reused  | active rooms=%d",
                start, end, freed_at, len(heap),
            )
        else:
            heapq.heappush(heap, end)      # open a new room
            log.info(
                "  Event (%d,%d): no free room          → new room | active rooms=%d",
                start, end, len(heap),
            )

    rooms = len(heap)
    log.info("  Minimum rooms required: %d", rooms)
    return rooms


# ─────────────────────────────────────────────────────────────────────────────

def assign_rooms(events: list[tuple[int, int]]) -> list[tuple[tuple[int, int], str]]:
    if not events:
        log.info("assign_rooms: empty list → []")
        return []

    LETTERS   = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    sorted_idx = sorted(range(len(events)), key=lambda i: events[i][0])
    log.info("assign_rooms | processing order: %s", [events[i] for i in sorted_idx])

    busy: list[tuple[int, str]] = []   # min-heap (end_time, room_name)
    free: list[str]             = []   # stack of available room names
    assignment: list[str]       = [""] * len(events)
    total_rooms                 = 0

    for i in sorted_idx:
        start, end = events[i]

        # Release rooms whose meeting has already ended
        while busy and busy[0][0] <= start:
            _, freed_room = heapq.heappop(busy)
            free.append(freed_room)

        if free:
            room = free.pop()
            log.info("  Event (%d,%d) → %-8s (reused)", start, end, room)
        else:
            room = f"Room {LETTERS[total_rooms % 26]}"
            total_rooms += 1
            log.info("  Event (%d,%d) → %-8s (new)", start, end, room)

        heapq.heappush(busy, (end, room))
        assignment[i] = room

    result = [(events[i], assignment[i]) for i in range(len(events))]
    log.info("  Assignment: %s", result)
    return result


# ─────────────────────────────────────────────────────────────────────────────

def run_demo() -> None:
    sep = "=" * 55

    # ── Test 1: adjacent events (no overlap, 1 room) ──────────────────────────
    log.info(sep)
    log.info("Test 1: Adjacent events  [(9,10), (10,11), (11,12)]")
    log.info(sep)
    events = [(9, 10), (10, 11), (11, 12)]
    result_attend = can_attend_all(events)
    result_rooms  = min_rooms_required(events)
    log.info("can_attend_all   → %s  (expected True)", result_attend)
    log.info("min_rooms        → %d  (expected 1)\n", result_rooms)
    assert result_attend is True
    assert result_rooms == 1

    # ── Test 2: overlapping events ────────────────────────────────────────────
    log.info(sep)
    log.info("Test 2: Overlapping      [(9,11), (10,12), (11,13)]")
    log.info(sep)
    events = [(9, 11), (10, 12), (11, 13)]
    result_attend = can_attend_all(events)
    result_rooms  = min_rooms_required(events)
    log.info("can_attend_all   → %s  (expected False)", result_attend)
    log.info("min_rooms        → %d  (expected 2)\n", result_rooms)
    assert result_attend is False
    assert result_rooms == 2

    # ── Test 3: all events at the same time ───────────────────────────────────
    log.info(sep)
    log.info("Test 3: All simultaneous [(1,5), (1,5), (1,5)]")
    log.info(sep)
    events = [(1, 5), (1, 5), (1, 5)]
    result_attend = can_attend_all(events)
    result_rooms  = min_rooms_required(events)
    log.info("can_attend_all   → %s  (expected False)", result_attend)
    log.info("min_rooms        → %d  (expected 3)\n", result_rooms)
    assert result_attend is False
    assert result_rooms == 3

    # ── Test 4: single event ──────────────────────────────────────────────────
    log.info(sep)
    log.info("Test 4: Single event     [(9, 10)]")
    log.info(sep)
    events = [(9, 10)]
    result_attend = can_attend_all(events)
    result_rooms  = min_rooms_required(events)
    log.info("can_attend_all   → %s  (expected True)", result_attend)
    log.info("min_rooms        → %d  (expected 1)\n", result_rooms)
    assert result_attend is True
    assert result_rooms == 1

    # ── Test 5: mixed case ────────────────────────────────────────────────────
    log.info(sep)
    log.info("Test 5: Mixed            [(1,4), (2,5), (7,8), (5,9)]")
    log.info(sep)
    events = [(1, 4), (2, 5), (7, 8), (5, 9)]
    result_attend = can_attend_all(events)
    result_rooms  = min_rooms_required(events)
    log.info("can_attend_all   → %s  (expected False)", result_attend)
    log.info("min_rooms        → %d  (expected 2)\n", result_rooms)
    assert result_attend is False
    assert result_rooms == 2

    log.info(sep)
    log.info("All assertions passed.")

    log.info(sep)
    log.info("Room Assignment Demo  [(9,11), (10,12), (11,13)]")
    log.info(sep)
    events = [(9, 11), (10, 12), (11, 13)]
    result = assign_rooms(events)
    for event, room in result:
        log.info("  %s → %s", event, room)

    log.info(sep)
    log.info("Room Assignment Demo  [(9,10), (10,11), (11,12)]")
    log.info(sep)
    events = [(9, 10), (10, 11), (11, 12)]
    result = assign_rooms(events)
    for event, room in result:
        log.info("  %s → %s", event, room)

    log.info(sep)
    log.info("COMPLEXITY SUMMARY")
    log.info(sep)
    log.info("Function            | Time       | Space")
    log.info("--------------------+------------+------")
    log.info("can_attend_all      | O(n log n) | O(n)")
    log.info("min_rooms_required  | O(n log n) | O(n)")
    log.info("assign_rooms        | O(n log n) | O(n)")
    log.info(sep)


if __name__ == "__main__":
    run_demo()
