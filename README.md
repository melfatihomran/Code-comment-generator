# Code Comment Generator

Fine-tunes **CodeT5** to generate natural-language comments/docstrings from
source code, trained on a filtered subset of **CodeSearchNet**. Served
through a small **FastAPI** app with an editor-styled demo UI.

> Why this project: sequence-to-sequence generation is a step up from
> classification-style portfolio projects (sentiment analysis, spam
> detection), it's directly relevant to how LLM coding assistants work, and
> the same pipeline extends naturally into code explanation, code
> summarization, or a GitHub-bot style assistant.

## Demo

```
┌─────────────────────────────────────────┐
│ snippet.py                               │
├───────────────────────────────────────────┤
│   # Adds two numbers and returns the sum  │   <- generated, shown as a
│ 1 def add(a, b):                          │      real inline comment
│ 2     return a + b                        │
├───────────────────────────────────────────┤
│ beams [4]                          [Run]  │
└─────────────────────────────────────────┘
```

Run it locally: see [Running the demo app](#running-the-demo-app) below.

## Results

## Results

| Model | BLEU | ROUGE-1 | ROUGE-2 | ROUGE-L | Exact Match |
| ----- | ---- | ------- | ------- | ------- | ----------- |

| `codet5-small` (pretrained, no FT) | 1.00 | 8.16 | 0.73 | 7.62 | 0.00 |
| `codet5-small` (fine-tuned, ours) | 19.65 | 41.11 | 23.41 | 38.83 | 5.60% |

## Dataset

[`sentence-transformers/codesearchnet`](https://huggingface.co/datasets/sentence-transformers/codesearchnet)
(config `"pair"`) — comment/code pairs scraped across multiple languages.

**Important, verified directly against the dataset before building this
pipeline:** this config ships **only a `train` split** (1,375,067 rows) with
**two columns**, `comment` (str) and `code` (str). There is no
validation/test split — the notebook builds its own via shuffle + slice
(see `notebooks/codet5_finetune_codesearchnet.ipynb`, section 3).

Preprocessing drops:

- code shorter than 20 or longer than 4000 characters
- comments shorter than 8 or longer than 400 characters
- boilerplate comments (`TODO`, `FIXME`, `XXX`, `deprecated`)
- comments that are mostly punctuation/markup noise

## Repo structure

```
code-comment-generator/
├── notebooks/
│   └── codet5_finetune_codesearchnet.ipynb   # Kaggle training notebook (run this first)
├── src/
│   ├── data_utils.py                          # filtering, splitting, tokenization (shared logic)
│   └── eval_utils.py                          # BLEU/ROUGE/exact-match + qualitative sample formatting
├── app/
│   ├── main.py                                # FastAPI app (POST /generate, GET /health, GET /)
│   ├── templates/index.html                   # demo UI
│   └── static/style.css
├── results/                                    # metrics + qualitative samples (populate after training)
├── requirements.txt
└── README.md
```

## Pipeline

1. **Load + inspect** the dataset, confirm schema (`notebooks/.../section 1`)
2. **Filter** low-quality pairs (`section 2`)
3. **Split** into train/val/test (`section 3`) — 8,000 / 1,000 / 1,000 by default
4. **Baseline**: run the pretrained model on the test set _before_ any fine-tuning (`section 5`)
5. **Tokenize** code → encoder input, comment → decoder target, with `-100` label masking on padding (`section 6`)
6. **Fine-tune** with `Seq2SeqTrainer` (`section 8`)
7. **Evaluate** the fine-tuned model on the same held-out test set (`section 9`)
8. **Compare** fine-tuned vs. baseline on identical examples (`section 10`)
9. **Save** qualitative samples + push the model to the Hugging Face Hub (`sections 11–12`)

## Running the training notebook

1. Upload `notebooks/codet5_finetune_codesearchnet.ipynb` to Kaggle, enable a GPU (T4 is enough).
2. Run all cells top to bottom.
3. Download `test_metrics_finetuned.json`, `test_metrics_baseline.json`, and
   `qualitative_samples.md` from the Kaggle output and place them in `results/`.
4. (Optional but recommended) uncomment the `push_to_hub` lines in the final
   cell to publish your fine-tuned model — this is the easiest way to wire it
   into the FastAPI app below.

To scale up later: raise `TRAIN_SIZE` in section 3. Nothing else in the
pipeline needs to change.

## Running the demo app

```bash
pip install -r requirements.txt

# Point at your fine-tuned model on the Hub, or a local saved checkpoint
export MODEL_NAME="melfatihomran/codet5-small-code-comment-gen"
# or: export MODEL_NAME="./codet5-comment-gen-final"

uvicorn app.main:app --reload --port 8000
```

Open `http://localhost:8000`, paste a function, click **Run**.

API directly:

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"code": "def add(a, b):\n    return a + b", "num_beams": 4}'
```

## Possible extensions

- **Code explanation**: same architecture, longer target sequences, prompt for paragraph-style explanations instead of one-line docstrings
- **Multi-document summarization**: summarize an entire file/module rather than a single function
- **GitHub bot**: wrap `app/main.py`'s `/generate` endpoint in a GitHub Action that comments on PRs missing docstrings
- **Language-conditioned generation**: the raw CodeSearchNet has per-language splits; tagging examples by language and adding a task-prefix could improve quality on a specific language
