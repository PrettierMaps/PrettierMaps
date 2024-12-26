.PHONY: venv
venv:
	pip install uv
	uv sync --all-groups
	uv run pre-commit install

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
	uv run ruff check . --fix
	uv run ruff format .

.PHONY: mypy
mypy:
	uv run mypy .

.PHONY: test
test:
	uv run pytest

.PHONY: test-in-docker
test-in-docker:
	docker build -t my-qgis-app -f .devcontainer/Dockerfile.test .
	docker run --rm -it my-qgis-app

.PHONY: zip_plugin
zip_plugin:
	rm -f prettier_maps.zip
	zip -r prettier_maps.zip prettier_maps

.PHONY: docs
docs:
	uv run mkdocs build