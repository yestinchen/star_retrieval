# STAR Retrieval

This repository contains the research code for:

```bibtex
@article{chen2022spatial,
  title={Spatial and temporal constrained ranked retrieval over videos},
  author={Chen, Yueting and Koudas, Nick and Yu, Xiaohui and Yu, Ziqiang},
  journal={Proceedings of the VLDB Endowment},
  volume={15},
  number={11},
  pages={3226--3239},
  year={2022},
  publisher={VLDB Endowment}
}
```

The codebase builds spatial-temporal indexes over tracked object detections, extracts query patterns from frame ranges, and runs top-k retrieval experiments using the baseline and proposed methods from the paper.

## Repository overview

- `vsimsearch/`: core library code for preprocessing, graph construction, indexing, ranking, metrics, and CLI apps.
- `vsimsearch/apps/index_app.py`: build and serialize an index from detection results.
- `vsimsearch/apps/pattern_app.py`: extract and serialize a query pattern from object ids and a frame interval.
- `vsimsearch/apps/query_app.py`: execute ranked retrieval over a serialized index and pattern.
- `scripts/`: experiment helpers for sampling frames, building batches of indexes and patterns, plotting figures, and reproducing paper workflows.
- `test/`: unit and exploratory tests.

## Requirements

- Python 3
- Packages listed in `requirements.txt`

Install dependencies with:

```bash
pip install -r requirements.txt
```

The current pinned dependencies include `numpy`, `pandas`, `networkx`, `matplotlib`, and `bitarray`.

## Input data format

The apps expect MOT-style detection or tracking results stored as CSV without a header.

Single-class input is parsed as:

```text
frame,id,left,top,width,height,conf,x,y,z
```

Multi-class input is parsed as:

```text
frame,id,left,top,width,height,conf,class,x,y,z
```

The loaders cache parsed node tables beside the source file using `*.cache.pkl` for faster repeated runs.

## Main workflow

The project is organized around three steps.

### 1. Build an index

```bash
python vsimsearch/apps/index_app.py \
  --file_path /path/to/detections.txt \
  --frame_height 1080 \
  --frame_width 1920 \
  --output_path /tmp/index.pkl \
  --index_type 1 \
  --discretize_func 4 \
  --df_param1 4 \
  --df_param2 5
```

Important arguments:

- `--index_type`: `1` proposed index, `2` per-frame proposed index, `3` vertex-only index, `4` edge-only index.
- `--single_type`: use the single-class loader instead of the multi-class loader.
- `--percent`: build the index on only the first fraction of frames.
- `--discretize_func` with `--df_param1` and `--df_param2`: choose how edge attributes are discretized before indexing.

### 2. Build a query pattern

```bash
python vsimsearch/apps/pattern_app.py \
  --file_path /path/to/detections.txt \
  --frame_height 1080 \
  --frame_width 1920 \
  --output_path /tmp/pattern.pkl \
  --ids 1,2,3 \
  --frames 10,20 \
  --discretize_func 4 \
  --df_param1 4 \
  --df_param2 5
```

This extracts the temporal pattern formed by the selected object ids over the inclusive frame interval.

### 3. Run retrieval

```bash
python vsimsearch/apps/query_app.py \
  --index_path /tmp/index.pkl \
  --pattern_path /tmp/pattern.pkl \
  --k 10 \
  --method proposed \
  --index_type 1
```

Available query methods:

- `baseline`
- `proposed`
- `proposed_seq`
- `noimd`

The query app prints ranked results, runtime, and collected metrics.

## Reproducing experiments

The repository includes utilities to reproduce experiments:

- `scripts/build_indexes.py`
- `scripts/build_patterns.py`
- `scripts/run_queries.py`
- `scripts/plot_figures.py`
- `scripts/paper/produce_figures.py`
