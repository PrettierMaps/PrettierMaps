ifeq ($(OS),Windows_NT)
    ACTIVATE=.venv\Scripts\activate
else
    ACTIVATE=. .venv/bin/activate
endif

.PHONY: venv
venv:
	pip install uv
	uv venv
	$(ACTIVATE) && uv pip install -r requirements.txt -r requirements-test.txt -r requirements-dev.txt

.PHONY: clean
clean:
	rm -rf .venv
	rm -rf .pytest_cache
	rm -rf .hypothesis
	rm -rf .mypy_cache
	rm -rf .ruff_cache
