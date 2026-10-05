"""表情冷却台账：判定请求流里的每个表情请求是否放行。"""

KNOWN = ("wave", "dance", "taunt", "sit")

SECOND_MS = 1000


class Guard:
    """按玩家与表情计时，并按整秒窗口限制发送量。"""

    def __init__(self, cooldown_ms, rate_per_sec):
        self.cooldown_ms = cooldown_ms
        self.rate_per_sec = rate_per_sec
        self.last = {}
        self.rate = {}
        self.seen = set()
        self.scanned = 0

    def allow(self, event_id, player, emote, at_ms):
        """判定一次表情请求，返回 (是否允许, 拒绝原因)。"""
        self.scanned += 1
        if event_id in self.seen:
            return False, "dup"

        if emote not in KNOWN:
            self.seen.add(event_id)
            return False, "unknown"

        key = (player, emote)
        self.scanned += 1
        previous = self.last.get(key)
        if previous is not None and at_ms - previous < self.cooldown_ms:
            self.seen.add(event_id)
            return False, "cooldown"

        second = at_ms // SECOND_MS
        buckets = self.rate.setdefault(player, {})
        for stale in [slot for slot in buckets if slot < second]:
            del buckets[stale]
        self.scanned += 1
        used = buckets.get(second, 0)
        if used >= self.rate_per_sec:
            self.seen.add(event_id)
            return False, "rate"

        self.last[key] = at_ms
        buckets[second] = used + 1
        self.seen.add(event_id)
        return True, ""
