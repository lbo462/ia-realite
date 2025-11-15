# IA Réalité

Like Reality TV, but with AIs.

## Used technologies

- Python
  - pip as a package manager
  - ruff for linting
  - httpx for HTTP requests
  - FastAPI to expose our application (is necessary)

- LM Studio to run the main AI model
- LangChain for its integration

## How to run

Create a python virtual env with `python -m venv .venv` and enter it with `source .venv/bin/activate`.

Instal deps with `pip install -r requirements.txt`

## Contributing

Do not forget to lint the code with

```sh
python -m ruff format
python -m ruff check . --fix
```

before commit to the main branch.

