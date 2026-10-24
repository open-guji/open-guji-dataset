# status/ — 各字组做得怎么样

每轮重落后由 CV 仓 `guji groups status` 生成，一轮一对文件：`<日期>-<产物标签>.md`（总表）与同名 `.json`（每组 × 每册全量、与人裁不一致的格明细）。
口径见 CV 仓 `open_guji_cv/eval/group_status.py` 模块头；规范见 CV 仓 `doc/字组/README.md` 第四节。负责人：A24。

    guji groups status --prod <产物根>[,…] --labels char-groups/labels/unified.jsonl \
        --codepoints <工作区>/config/codepoints.yaml --out char-groups/status --tag <标签>

| 文件 | 产物 | 备注 |
|---|---|---|
| 2026-10-24-本机-vol04-20 | 本机 vol04–10（旧包）＋vol11–20（10-24 修复前的包） | 第一份；人裁只有 vol01–10，「不一致」只能在 vol04–10 上核，含格号漂移与码位差，要逐格看 |
