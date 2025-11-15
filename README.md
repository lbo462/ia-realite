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

Install deps with `pip install -r requirements.txt`

## LM Studio && Langchain
- First of all, host your LLM model in LM Studio. The hugging face model url: `https://huggingface.co/matrixportalx/Llama-2-7b-chat-hf-Q4_K_M-GGUF/blob/main/llama-2-7b-chat-hf-q4_k_m.gguf`
- In LM Studio: Load your model -> Local Server -> Start Server -> Model is exposed through local port 1234 by default.
- Put this in your .env file:
```
OPENAI_API_KEY=lm-studio
OPENAI_API_BASE=http://localhost:1234/v1
```
- Run first test with:
```
python app.py
```


## LM Studio && Langchain
- First of all, host your LLM model in LM Studio. The hugging face model url: `https://huggingface.co/matrixportalx/Llama-2-7b-chat-hf-Q4_K_M-GGUF/blob/main/llama-2-7b-chat-hf-q4_k_m.gguf`
- In LM Studio: Load your model -> Local Server -> Start Server -> Model is exposed through local port 1234 by default.
- Put this in your .env file:
```
OPENAI_API_KEY=lm-studio
OPENAI_API_BASE=http://localhost:1234/v1
```
- Run first test with:
```
python app.py
```


## Contributing

Do not forget to lint the code with

```sh
python -m ruff format
python -m ruff check . --fix
```

before commit to the main branch.

