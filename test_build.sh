uv sync --extra dev
rm -r ./dist
uv build
uv pip install dist/vrchatapi_extensions-0.1.0-py3-none-any.whl
uv run pylint ./src
rm -r ./src/vrchatapi_extensions.egg-info