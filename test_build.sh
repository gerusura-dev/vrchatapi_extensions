uv sync --dev
rm -r ./dist
uv run isort ./vrchatapi_extensions
uv build
uv pip install dist/vrchatapi_extensions-0.1.0-py3-none-any.whl
uv run pylint ./vrchatapi_extensions
rm -r ./vrchatapi_extensions.egg-info