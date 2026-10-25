# status/ — 各字组做得怎么样

每轮重落后由 CV 仓 `guji groups status` 生成，一轮一对文件：`<日期>-<产物标签>.md`（总表）与同名 `.json`（每组 × 每册全量、与人裁不一致的格明细）。
口径见 CV 仓 `open_guji_cv/eval/group_status.py` 模块头；规范见 CV 仓 `doc/字组/README.md` 第四节。负责人：A24。

    guji groups status --prod <产物根>[,…] --labels char-groups/labels/unified.jsonl \
        --codepoints <工作区>/config/codepoints.yaml --out char-groups/status --tag <标签> \
        [--prev char-groups/status/<上一份>.json]

一条命令出两张表（2026-10-25 起）：字组状态总表，和送审格分类（G 字组／V 组外异体对／N 形近护栏／O 无关，按册、按字对，
口径见 CV 仓 `open_guji_cv/eval/review_breakdown.py`）。给了 `--prev` 就在送审数后面写比上一份的增减。
跑之前：各册最新包 `guji products pack fetch <册> -w <工作区> --label <★ 那个标签> --to <产物根>/<册>`；
人工数据先重建 `python char-groups/labels/build_unified.py --cv <CV 仓>`（要 `guji db pull`）。本机 17 册约 10 秒。

| 文件 | 产物 | 备注 |
|---|---|---|
| 2026-10-24-本机-vol04-20 | 本机 vol04–10（旧包）＋vol11–20（10-24 修复前的包） | 第一份；人裁只有 vol01–10，「不一致」只能在 vol04–10 上核，含格号漂移与码位差，要逐格看 |
| 2026-10-25-最新重跑-vol04-20 | vol06、09、11–20 cv 0.5.12 重跑；vol07、08、10 0.5.16.dev 人裁修补；vol04 0.5.7；vol05 冻结 | 第一份带送审分类；增减比的是本机上一轮（vol11–20 v0.5.9、vol04–10 v0.5.7）。送审 2,937→2,169 |
