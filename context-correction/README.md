# context-correction

上下文 + LM 概率纠正测试集（候选冻结）。**用 `samples_v2/`，`samples/`（v1）已弃用。**

## v1 为什么弃用（2026-10-01，D1）

v1 的候选池本身没有被人为塞字：`build_context_correction_dataset.py --from-seed`
里是 `fuse_priors(字形库候选, OCR top1+s2t)`，无 `extra`（整理本字只在线上 seed 上下文
通道里作 extra 注入，且该通道的字位已被 `ORIGIN["context"]=None` 剔出集）。问题在**选格**：

- 金标只存在于被进库协议收下的格：align 通道要「OCR = 整理本字」双信号一致才收；human 通道多半是人对 OCR 提议点确认。
  OCR 读错且库也没有的格没人收，不在集里。
- 后果：align 层 1152 格 **0 个金标在池外**，金标非首选时 277/277 是 OCR 源候选（source 标成 rapidocr、概率低）；
  human 层 529 格才有 167 格金标不在池里。「候选源 / 概率形状 / 名次」整套特征都带着选择规则，
  学出来的模型 +17%（去掉 `is_rapid` 仍 +8~17%）是假的；连现行规则的头条增益（+1.3%）也主要来自这一层（见 v2 分层）。

## v2

`samples_v2/*/expected.json`：池与 v1 逐字相同，只做标注（`scripts/build_context_correction_v2.py`，在 open-guji-cv）：

- `source`：`glyph`（字形库 top-k）/ `ocr`（RapidOCR top1+s2t）。
- `gold_reach`：`glyph` 1101 / `ocr_only` 413（`selection_biased=true`）/ `unreachable` 167（金标不在池，**保留不删**）。
- `top1_correct`；可救格 = 金标在池且非首选 = 379，其中 glyph 层 **25**、ocr_only 层 354（有偏）。

**头条只报 glyph 层**；ocr_only 与 unreachable 只作分层计数，不进头条。已知局限：glyph 层仍由进库协议选出（OCR 同意的格 OCR 概率会抬高金标），
彻底去偏需要「未被收下的格」的独立金标（phase9_seed 队列 / ocr_carrier 在本机，云端无）。

评测：`eval_context_correction.py <dataset>/context-correction --samples-dir samples_v2 ...`（输出含 `by_reach`）。
