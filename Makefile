PYTHON ?= python3
MODEL ?= google/gemma-3-4b-it
RESULTS ?= results

.PHONY: test bootstrap-external milu indicifeval indicgenbench-dev

test:
	$(PYTHON) -m pytest -q

bootstrap-external:
	$(PYTHON) scripts/bootstrap_external.py

milu:
	$(PYTHON) scripts/run_external.py milu --model $(MODEL) --output $(RESULTS)/milu

indicifeval:
	$(PYTHON) scripts/run_external.py indicifeval --model $(MODEL) --output $(RESULTS)/indicifeval

indicgenbench-dev:
	$(PYTHON) scripts/prepare_indicgenbench.py --task crosssum --split dev
	$(PYTHON) scripts/prepare_indicgenbench.py --task flores_en_kn --split dev
	$(PYTHON) scripts/prepare_indicgenbench.py --task flores_kn_en --split dev
	$(PYTHON) scripts/prepare_indicgenbench.py --task xquad --split dev
	$(PYTHON) scripts/prepare_indicgenbench.py --task xorqa --split dev
