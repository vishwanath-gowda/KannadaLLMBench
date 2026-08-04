BASE_PYTHON ?= python3
VENV ?= .venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
MODEL ?= google/gemma-3-4b-it
RESULTS ?= results
DATA_SOURCE ?= indiccorp_v2_kannada
DATA_OUTPUT ?= data/samples/$(DATA_SOURCE).jsonl
RECORDS ?= 1000
MB ?= 5
FAMILIES ?= 2000
ROMAN_OUTPUT ?= data/interim/romanbench/candidates.jsonl
ROMAN_REVIEW ?= data/interim/romanbench/review.csv

.PHONY: help all venv install install-dev install-all build test lint format format-check check clean \
	bootstrap-external milu indicifeval indicgenbench-dev external-all \
	data-sources registry-validate data-build-records data-build-mb data-slice \
	transform contamination-check schemas romanbench-candidates romanbench-sample \
	romanbench-review-export romanbench-review-validate

help:
	@echo "KannadaLLMBench targets"
	@echo "  make venv                   Create .venv using active Python 3.12+"
	@echo "  make install-dev            Install package + dev/metrics/data/RomanBench dependencies"
	@echo "  make check                  Registry validation + lint + tests + schemas"
	@echo "  make build                  Build wheel and source distribution"
	@echo "  make all                    Run checks and build the package"
	@echo "  make bootstrap-external     Clone pinned external benchmark repositories"
	@echo "  make external-all           Prepare/run external benchmark commands"
	@echo "  make data-sources           List data sources and approval status"
	@echo "  make data-build-records     Build approved source, bounded by RECORDS"
	@echo "  make data-build-mb          Build approved source, bounded by MB MiB"
	@echo "  make data-slice             Generic HF slice (set DATASET/SPLIT/OUTPUT)"
	@echo "  make romanbench-candidates  Build controlled RomanBench candidate families"
	@echo "  make romanbench-sample      Build 100-family RomanBench development sample"
	@echo "  make romanbench-review-export Export family-level CSV for Kannada-speaker review"
	@echo "  make romanbench-review-validate Validate completed review CSV"
	@echo "  make clean                  Remove caches/build artifacts (not source)"

all: check build

venv:
	$(BASE_PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip

install: venv
	$(PIP) install -e .

install-dev: venv
	$(PIP) install -e '.[dev,metrics,data,romanbench]'

install-all: install-dev

build:
	$(PY) -m build

registry-validate:
	$(PY) scripts/validate_registry.py

data-sources:
	$(PY) scripts/list_data_sources.py

test:
	$(PY) -m pytest -q

lint:
	$(PY) -m ruff check src scripts tests

format:
	$(PY) -m ruff format src scripts tests

format-check:
	$(PY) -m ruff format --check src scripts tests

check: registry-validate lint test schemas

bootstrap-external:
	$(PY) scripts/bootstrap_external.py

milu:
	$(PY) scripts/run_external.py milu --model $(MODEL) --output $(RESULTS)/$(MODEL)/milu

indicifeval:
	$(PY) scripts/run_external.py indicifeval --model $(MODEL) --output $(RESULTS)/$(MODEL)/indicifeval

indicgenbench-dev:
	$(PY) scripts/prepare_indicgenbench.py --task crosssum --split dev
	$(PY) scripts/prepare_indicgenbench.py --task flores_en_kn --split dev
	$(PY) scripts/prepare_indicgenbench.py --task flores_kn_en --split dev
	$(PY) scripts/prepare_indicgenbench.py --task xquad --split dev
	$(PY) scripts/prepare_indicgenbench.py --task xorqa --split dev

external-all: milu indicifeval indicgenbench-dev

data-build-records:
	$(PY) scripts/build_dataset.py $(DATA_SOURCE) --output $(DATA_OUTPUT) --text-field text --dedup-field text --records $(RECORDS)

data-build-mb:
	$(PY) scripts/build_dataset.py $(DATA_SOURCE) --output $(DATA_OUTPUT) --text-field text --dedup-field text --mb $(MB)

DATASET ?=
SPLIT ?= train
OUTPUT ?= data/samples/slice.jsonl
data-slice:
	@test -n "$(DATASET)" || (echo "DATASET is required" && exit 2)
	$(PY) scripts/slice_dataset.py $(DATASET) --split $(SPLIT) --records $(RECORDS) --output $(OUTPUT)

romanbench-candidates:
	$(PY) scripts/build_romanbench_candidates.py --source-key $(DATA_SOURCE) --families $(FAMILIES) --output $(ROMAN_OUTPUT)

romanbench-sample:
	$(PY) scripts/build_romanbench_candidates.py --source-key $(DATA_SOURCE) --families 100 \
		--output data/interim/romanbench/sample.jsonl

romanbench-review-export:
	$(PY) scripts/export_romanbench_review.py --input $(ROMAN_OUTPUT) --output $(ROMAN_REVIEW)

romanbench-review-validate:
	$(PY) scripts/validate_romanbench_review.py $(ROMAN_REVIEW)

transform:
	@test -n "$(INPUT)" || (echo "INPUT is required" && exit 2)
	$(PY) scripts/transform_dataset.py $(INPUT) $(OUTPUT) --text-field text --dedup-field text

contamination-check:
	@test -n "$(TRAINING)" || (echo "TRAINING is required" && exit 2)
	@test -n "$(BENCHMARK)" || (echo "BENCHMARK is required" && exit 2)
	$(PY) scripts/check_contamination.py --training $(TRAINING) --benchmark $(BENCHMARK) \
		--training-field $(TRAINING_FIELD) --benchmark-field $(BENCHMARK_FIELD) --fail-on-overlap

schemas:
	$(PY) -m json.tool schemas/benchmark-item.schema.json >/dev/null
	$(PY) -m json.tool schemas/dataset-manifest.schema.json >/dev/null
	$(PY) -m json.tool schemas/romanbench-candidate.schema.json >/dev/null

clean:
	rm -rf .pytest_cache .ruff_cache build dist *.egg-info src/*.egg-info
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
