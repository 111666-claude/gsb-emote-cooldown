"""入口：从标准输入读 JSONL 表情请求，逐行写判定结果。"""

import io
import json
import sys

from .guard import KNOWN, Guard

SAMPLES = ("duo", "burst", "offlist", "replay", "blocked", "work")


def run(instream, outstream, guard):
    """逐行判定，返回 {"allowed": n, "rejected": n}。"""
    allowed = 0
    rejected = 0
    for line in instream:
        line = line.strip()
        if not line:
            continue
        record = json.loads(line)
        ok, reason = guard.allow(
            record.get("id"),
            record.get("player"),
            record.get("emote"),
            record.get("at", 0),
        )
        if ok:
            allowed += 1
        else:
            rejected += 1
        outstream.write(json.dumps({"id": record.get("id"), "ok": ok, "reason": reason}) + "\n")
    return {"allowed": allowed, "rejected": rejected}


def feed(guard, records):
    """把一批记录喂给台账，返回逐行判定结果（去掉尾部换行）。"""
    out = io.StringIO()
    payload = "".join(json.dumps(item) + "\n" for item in records)
    run(io.StringIO(payload), out, guard)
    return out.getvalue().strip()


def scale_records(count=3000, players=500):
    """造一批确定性的规模样本：500 个玩家轮流发 4 种表情。"""
    return [
        {
            "id": "w%d" % index,
            "player": "p%d" % (index % players),
            "emote": KNOWN[index % len(KNOWN)],
            "at": index,
        }
        for index in range(count)
    ]


def scenario(name):
    """返回 (台账, 记录列表)。"""
    if name == "duo":
        return Guard(1000, 100), [
            {"id": "e1", "player": "p1", "emote": "wave", "at": 0},
            {"id": "e2", "player": "p2", "emote": "wave", "at": 100},
        ]
    if name == "burst":
        return Guard(0, 2), [
            {"id": "e1", "player": "p1", "emote": "wave", "at": 0},
            {"id": "e2", "player": "p1", "emote": "dance", "at": 10},
            {"id": "e3", "player": "p1", "emote": "taunt", "at": 20},
        ]
    if name == "offlist":
        return Guard(0, 100), [
            {"id": "e1", "player": "p1", "emote": "fly", "at": 0},
        ]
    if name == "replay":
        return Guard(1000, 100), [
            {"id": "e1", "player": "p1", "emote": "wave", "at": 0},
            {"id": "e1", "player": "p1", "emote": "wave", "at": 5000},
            {"id": "e9", "player": "p1", "emote": "fly", "at": 6000},
            {"id": "e9", "player": "p1", "emote": "fly", "at": 7000},
        ]
    if name == "blocked":
        return Guard(1000, 2), [
            {"id": "e1", "player": "p1", "emote": "wave", "at": 0},
            {"id": "e2", "player": "p1", "emote": "wave", "at": 200},
            {"id": "e3", "player": "p1", "emote": "dance", "at": 400},
            {"id": "e4", "player": "p1", "emote": "taunt", "at": 600},
            {"id": "e5", "player": "p1", "emote": "dance", "at": 800},
        ]
    raise SystemExit("未知场景：%s（可用：%s）" % (name, "|".join(SAMPLES)))


def main(argv=None):
    args = (argv or sys.argv[1:])[:1]
    raw = args[0] if args else "--sample=duo"
    name = raw.split("=", 1)[1] if raw.startswith("--sample=") else raw
    if name not in SAMPLES:
        raise SystemExit("需要 --sample=" + "|".join(SAMPLES))

    if name == "work":
        guard = Guard(0, 10 ** 6)
        records = scale_records()
        out = io.StringIO()
        payload = "".join(json.dumps(item) + "\n" for item in records)
        counts = run(io.StringIO(payload), out, guard)
        print(json.dumps({"scanned": guard.scanned, "ok": counts["allowed"], "rejected": counts["rejected"]}))
        return 0

    guard, records = scenario(name)
    print(feed(guard, records))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
