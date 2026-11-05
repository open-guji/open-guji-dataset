set -u
export PATH=/home/user/open-guji-cv/.venv/bin:$PATH
cd /home/user/ws
for v in "$@"; do
  [ -d cache/$v/char_patch_on ] && continue
  guji products pack fetch $v --to /home/user/prod_main -w . 2>&1 | tail -1
  GUJI_WORKSPACE=. guji source pull $v 2>&1 | tail -1
  for m in off on; do
    rm -rf /home/user/sb_$m/$v; cp -r /home/user/prod_main/$v /home/user/sb_$m/
    ov='{}'; [ $m = on ] && ov='{"params":{"cell_shrink":{"inner_frame_cut":true}}}'
    GUJI_PRODUCTS_DIR=/home/user/sb_$m GUJI_RAW_ROOT=/home/user/ws guji step cell_shrink $v --pages all --force --allow-cv-mismatch --why "A22 列端评测集 $m" --override "$ov" -w . 2>&1 | grep 完成：
    rm -rf cache/$v/char_patch_$m; mv cache/$v/char_patch cache/$v/char_patch_$m
  done
done
echo ALLDONE
