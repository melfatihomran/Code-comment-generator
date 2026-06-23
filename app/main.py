"""
FastAPI demo app for the Code Comment Generator.

Loads a fine-tuned CodeT5 model (from the Hugging Face Hub, or a local
path) and exposes:
  - POST /generate     -> generate a comment for a code snippet
  - GET  /health        -> liveness check
  - GET  /              -> simple HTML UI (templates/index.html)

Configure the model source with the MODEL_NAME environment variable:
  export MODEL_NAME="your-username/codet5-small-comment-generator"   # HF Hub
  export MODEL_NAME="./codet5-comment-gen-final"                     # local path
If unset, defaults to the base (non-fine-tuned) Salesforce/codet5-small
so the app is runnable out of the box for testing the API surface.
"""

import os
from functools import lru_cache

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

MODEL_NAME = os.environ.get("MODEL_NAME", "melfatihomran/codet5-small-code-comment-gen")
MAX_INPUT_LEN = 256
MAX_OUTPUT_LEN = 64

app = FastAPI(
    title="Code Comment Generator",
    description="Generates natural-language comments/docstrings for source code using a fine-tuned CodeT5 model.",
    version="1.0.0",
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

with open(os.path.join(BASE_DIR, "templates", "index.html"), encoding="utf-8") as f:
    INDEX_HTML = f.read()


class GenerateRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=20000, description="Source code to comment.")
    num_beams: int = Field(4, ge=1, le=8, description="Beam search width.")
    max_output_len: int = Field(MAX_OUTPUT_LEN, ge=8, le=128)


class GenerateResponse(BaseModel):
    comment: str
    model_name: str


@lru_cache(maxsize=1)
def get_pipeline():
    """
    Lazily load tokenizer + model on first request, then cache.
    Using lru_cache instead of a global so this is easy to unit-test by
    monkeypatching this function.
    """
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    import torch

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    model.eval()
    return tokenizer, model, device


def generate_comment(code: str, num_beams: int = 4, max_output_len: int = MAX_OUTPUT_LEN) -> str:
    import torch

    tokenizer, model, device = get_pipeline()
    inputs = tokenizer(
        code,
        return_tensors="pt",
        max_length=MAX_INPUT_LEN,
        truncation=True,
    ).to(device)
    with torch.no_grad():
        outputs = model.generate(**inputs, max_length=max_output_len, num_beams=num_beams)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)


@app.get("/health")
def health():
    return {"status": "ok", "model_name": MODEL_NAME}


@app.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest):
    if not req.code.strip():
        raise HTTPException(status_code=400, detail="`code` must not be empty.")
    try:
        comment = generate_comment(req.code, num_beams=req.num_beams, max_output_len=req.max_output_len)
    except Exception as e:  # surfaces model-loading / OOM / generation errors clearly
        raise HTTPException(status_code=500, detail=f"Generation failed: {e}")
    return GenerateResponse(comment=comment, model_name=MODEL_NAME)


@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(content=INDEX_HTML)
