# -*- coding: utf-8 -*-
"""把 review/<tag>_verdicts.jsonl 的人裁并进 jys|ry|rr/items.jsonl 的真值（A 档，src user_review_<tag>，排最前、后到覆盖）。
与 cv research/char_groups/jys/merge_jys2.py 同口径；幂等（已并过的 tag 跳过）。
用法：python merge_into_items.py <tag> [<tag>...]（按给的顺序，后面的覆盖前面的；每个 tag 的格按其 group 字段落到对应组，
文件里没有 group 的（10-06 老批）由 TAG_GROUP 给）。不碰快照，不重算 baseline.json。
没有 items 的字组（如 ext_wmt 的 未末/土士/戊戌戍）只留在 review/ 里。"""
import json, sys
from pathlib import Path
D = Path(__file__).resolve().parent.parent
FAM = {g['id']: set(g['members']) for g in json.load(open(D / 'groups.json', encoding='utf-8'))['groups']}
STRONG = {'A_human', 'B_vision'}
TAG_GROUP = {'ry_flag': 'ry'}
NOTE = {'ry_flag': '日曰放行格人裁（10-06 flag 批）', 'ctx_r1': '上下文路复审第一轮（10-17，sheldon）', 'ctx_r2': '上下文路复审第二轮（10-17，sheldon）',
        'pop1': '日曰入人八全书抽样复审（10-20，sheldon）'}
def main(tags):
    items = {g: [json.loads(l) for l in open(D / g / 'items.jsonl', encoding='utf-8') if l.strip()] for g in ('jys', 'ry', 'rr')}
    for tag in tags:
        V = [json.loads(l) for l in open(D / 'review' / f'{tag}_verdicts.jsonl', encoding='utf-8')]
        V.sort(key=lambda v: v.get('t', 0))
        src = f'user_review_{tag}'; hit = miss = 0
        for v in V:
            g = v.get('group') or TAG_GROUP[tag]
            rows = [r for r in items.get(g, []) if r['id'] == v['id'] and r.get('core')]
            if not rows: miss += 1; continue
            for r in rows:
                if any(x['src'] == src for x in r['golds']): continue
                val = v['verdict']
                if val in FAM[g]:
                    old = r['gold'] if r['gold_tier'] in STRONG else None
                    note = NOTE.get(tag, tag) + (f'；覆盖旧真值 {old}' if old and old != val else '') + (f'；{v["note"]}' if v.get('note') else '')
                    r['golds'] = [{'char': val, 'tier': 'A_human', 'src': src, 'note': note}] + r['golds']
                    r['gold'], r['gold_tier'], r['label_origin'], r['gold_src'] = val, 'A_human', 'human', src
                    r['gold_conflict'] = len({x['char'] for x in r['golds'] if x['tier'] in STRONG}) > 1
                else:
                    r['golds'] = [{'char': None, 'tier': 'X_unclear', 'src': src, 'note': val}] + r['golds']
                hit += 1
        print(tag, '并入', hit, '格；不在 items（非 core 或该组无 items）', miss)
    for g, rows in items.items():
        (D / g / 'items.jsonl').write_text('\n'.join(json.dumps(r, ensure_ascii=False) for r in rows) + '\n', encoding='utf-8')
if __name__ == '__main__': main(sys.argv[1:])
