# emote-cooldown

表情冷却：从标准输入读 JSONL 请求，逐行写 JSONL 判定。只用 Python 标准库。

```
python3 -m emote --sample=duo
python3 -m emote --sample=burst
python3 -m emote --sample=offlist
python3 -m emote --sample=replay
python3 -m emote --sample=blocked
python3 -m emote --sample=work
python3 -m unittest discover -s tests
```

## 口径

- **冷却窗口**：同一玩家、同一表情，距该玩家上一次**成功**发送不足 `cooldown_ms` 判 `cooldown`。恰好等于 `cooldown_ms` 放行。不同玩家之间互不影响；冷却窗口以毫秒计，不随整秒边界重置。
- **整秒配额**：同一玩家在**同一整秒**内成功发送的表情总数不得超过 `rate_per_sec`，超出判 `rate`。整秒按 `at_ms // 1000` 划分。
- **白名单**：表情必须是 `KNOWN` 中登记的四种，否则判 `unknown`。
- **幂等**：同一个 `event_id` 只判定一次。重复出现一律判 `dup`，且不改变任何台账。

## 不变量

- 任何**被拒绝**的请求都不推进冷却，也不占用整秒配额；只有成功发送才记账。
- 无论首次判定是放行还是拒绝，该 `event_id` 都已入台账。
- 配额按整秒窗口记账，已过窗的记账不得继续参与判定，也不得随时间无限累积。
- 判定必须按台账索引进行，不得逐条翻查历史记录。

## 输出契约

每行输出一个 JSON 对象，键与顺序固定：

```
{"id": <原样>, "ok": <真假>, "reason": <拒绝原因或空串>}
```

拒绝原因为 `cooldown` / `rate` / `unknown` / `dup` 之一，放行时为空串。

`--sample=work` 不逐行输出，只打印一行诊断计数：

```
{"scanned": <判定过程中查看过的既有台账条目数>, "ok": <放行条数>, "rejected": <拒绝条数>}
```

规模口径：`--sample=work` 的三千次判定，`scanned` 不得超过 9000。

## 目录

```
emote/guard.py       判定台账
emote/__main__.py    stdin JSONL 入口与 --sample 场景
tests/test_guard.py  unittest 用例
```
