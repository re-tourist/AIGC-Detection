# M3 Run Order

# 这次先确认容器里的 Python 版本，Community-Forensics baseline 建议使用 Python 3.10 或 3.11，不要继续在旧的 3.8 环境里硬跑。
python -c "import sys; print(sys.version)"

# 这次先在容器内仓库根目录安装根级依赖，requirements.txt 已包含 Community-Forensics baseline 所需依赖。
pip install -r requirements.txt

# 下面所有命令都假定你已经进入容器内仓库根目录 /home/workspace/AIGC，并且宿主机 BRGen 已挂载到容器内 data/BRGen。
pwd && ls data/BRGen && ls data/BRGen/BR-Gen && ls data/BRGen/BR-Gen/RealImage/COCO

# 这次先在容器内仓库根目录跑测试，确认 restricted pilot 代码状态正常。
python -m unittest discover -s tests -p 'test_*.py' -v

# 这次先 dry-run 解析 COCO image list，只验证路径、文件名和 audit schema，不下载文件。
python scripts/materialize_br_gen_real_subset.py --source-root data/BRGen/BR-Gen --source-dataset COCO --output-root data/BRGen/BR-Gen/RealImage --dry-run

# 这次正式 materialize BR-Gen 实际引用的 COCO real 子集，只下载 image_list 里列出的文件，不下载整套 COCO，并打开进度输出和单请求超时。
python scripts/materialize_br_gen_real_subset.py --source-root data/BRGen/BR-Gen --source-dataset COCO --output-root data/BRGen/BR-Gen/RealImage --timeout-seconds 20 --progress-every 10

# 这次生成 expanded COCO-only restricted pilot manifest，不再使用 64 fake 样本 cap，只保留 source_id=COCO，并保持 evaluation_scope=restricted_pilot。
python scripts/prepare_br_gen_m3_formal.py --source-root data/BRGen/BR-Gen --output-root data/mirrored/br_gen/subsets/restricted_pilot --allowed-sources COCO

# 这次对 expanded restricted pilot manifest 跑 Community Forensics baseline，导出 repo-compatible prediction JSONL。
python scripts/export_community_forensics_predictions.py --manifest data/mirrored/br_gen/subsets/restricted_pilot/manifest/formal_manifest.jsonl --output outputs/m3/restricted_pilot/predictions.jsonl --device cuda --batch-size 16

# 这次对 expanded restricted pilot predictions 跑 minimal runner 和增强后的 localized sidecar，结果只用于 coverage audit 与 failure discovery，不作为 formal benchmark。
python scripts/run_m3_formal_eval.py --manifest data/mirrored/br_gen/subsets/restricted_pilot/manifest/formal_manifest.jsonl --predictions outputs/m3/restricted_pilot/predictions.jsonl --output-dir outputs/m3/restricted_pilot/eval

# 这次最后检查 expanded restricted pilot 关键产物是否齐全，包括 summary、localized summary、coverage audit、failure evidence map 和 localized coverage summary。
ls data/mirrored/br_gen/subsets/restricted_pilot/manifest && ls outputs/m3/restricted_pilot/eval
