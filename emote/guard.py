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
        if event_id in self.seen:
            self.scanned += 1
            return False, "dup"
        self.seen.add(event_id)

        key = (player, emote)
        previous = self.last.get(key)
        if previous is not None:
            self.scanned += 1
            if at_ms - previous < self.cooldown_ms:
                return False, "cooldown"

        second = at_ms // SECOND_MS
        buckets = self.rate.get(player)
        if buckets is not None:
            self.scanned += 1
            while buckets:
                oldest = next(iter(buckets))
                if oldest >= second:
                    break
                del buckets[oldest]
            used = buckets.get(second, 0)
            if used >= self.rate_per_sec:
                return False, "rate"
            buckets[second] = used + 1
        else:
            self.rate[player] = {second: 1}

        if emote not in KNOWN:
            return False, "unknown"

        self.last[key] = at_ms
        return True, ""
