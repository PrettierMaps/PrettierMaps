ifeq ($(OS),Windows_NT)
    ACTIVATE=.venv\Scripts\activate
else
    ACTIVATE=. .venv/bin/activate
endif

.PHONY: venv
venv:
	pip install uv
	uv sync --all-groups
	$(ACTIVATE) && pre-commit install
.PHONY: clean
clean:
	rm -rf .venv
	rm -rf .pytest_cache
	rm -rf .hypothesis
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf build/
	rm -rf prettier_maps.egg-info/
	find . -type d -name "__pycache__" -exec rm -rf {} +

.PHONY: isort
isort:
	uv run isort .

.PHONY: ruff
ruff:
	uv run ruff check .
	uv run ruff format .

.PHONY: mypy
mypy:
	uv run mypy .

.PHONY: zip_plugin
zip_plugin:
	zip -r prettier_maps.zip prettier_maps

.PHONY: docs
docs:
	uv run mkdocs build