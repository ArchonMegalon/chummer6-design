# Developer Guide — Black Ledger Tick Email

Goal:

When a Black Ledger turn generates player-safe news, Chummer must resolve recipients under a bounded policy, hand the message to the EA delivery bridge, and persist a delivery receipt without blocking world-tick generation.

Required runtime policy:

```yaml
CHUMMER_BLACK_LEDGER_NEWS_EMAIL_POLICY:
  allowed:
    - disabled
    - subscribed_only
    - subscribed_or_only_user_preview_fallback
    - operator_only
```

Current preview target:

```yaml
CHUMMER_BLACK_LEDGER_NEWS_EMAIL_POLICY: subscribed_or_only_user_preview_fallback
```

Required send loop:

```text
World tick generated
-> player-safe news generated
-> privacy gate passes
-> recipient resolver runs
-> delivery candidate created
-> EA sends or emits bounded suppression
-> delivery receipt stored
```

Required catch-up command:

```bash
python3 scripts/black_ledger_send_tick_news.py \
  --world emerald-sprawl-prelude \
  --turn 1 \
  --policy subscribed_or_only_user_preview_fallback \
  --dry-run
```
