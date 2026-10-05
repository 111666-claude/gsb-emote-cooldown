"""表情冷却台账：判定请求流里的每个表情请求是否放行。"""

KNOWN = ("wave", "dance", "taunt", "sit")

SECOND_MS = 1000


class Guard:
    """按玩家与表情计时，并按整秒窗口限制发送量。"""

    def __init__(self, cooldown_ms, rate_per_sec):
        self.cooldown_ms = cooldown_ms
        self.rate_per_sec = rate_per_sec
        self.last = {}
        self.log = []
        self.seen = set()
        self.scanned = 0

    def allow(self, event_id, player, emote, at_ms):
        """判定一次表情请求，返回 (是否允许, 拒绝原因)。"""
        previous = self.last.get(emote)
        if previous is not None:
            self.scanned += 1
            if at_ms - previous < self.cooldown_ms:
                return False, "cooldown"
        self.last[emote] = at_ms

        second = at_ms // SECOND_MS
        used = 0
        for entry in self.log:
            self.scanned += 1
            if entry == (player, second):
                used += 1
        if used > self.rate_per_sec:
            return False, "rate"

        self.log.append((player, second))
        self.seen.add(event_id)
        return True, ""
