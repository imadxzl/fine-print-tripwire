# Fine Print Tripwire 🪤

**Find the clauses you'd regret agreeing to.**

🔗 **Live demo: https://fine-print-tripwire.vercel.app/**. Click **Load sample**, then **Trip the wire**.

Paste any Terms of Service, privacy policy or subscription agreement, or drop in a **screenshot** of one. Fine Print Tripwire uses **Gemma 4**, Google's open-weights multimodal model, to flag the risky clauses: data selling, auto-renewal traps, forced arbitration, broad content licenses and more. For each one it gives you:

- a **0–100 risk score** and a one-line verdict
- every flagged clause **highlighted in the original text**, colored by severity
- a **plain-English explanation** with no legalese
- **what you can actually do about it** (opt-outs, settings, deadlines)

Built at Hacktoberfest 2026 for the *Best Use of Gemma 4* and *Best Open-Source AI Project* categories.

## Why an open model?
You shouldn't have to trust a company's cloud to tell you what that company's fine print means. Gemma 4 is open-weights, so the same code can run **entirely on your own machine** with Ollama, and your documents never leave your laptop.

## Run it

Requires Python 3.9+. There are no dependencies to install.

```bash
cd fine-print-tripwire
cp .env.example .env      # then put your Gemini API key in .env
python app.py
```

Open <http://localhost:8000>, click **Load sample**, then **Trip the wire**.

| Setting (`.env`) | Default | Meaning |
|---|---|---|
| `GEMINI_API_KEY` | | Key from [Google AI Studio](https://aistudio.google.com/apikey). Without one, the app runs in keyword-only demo mode. |
| `GEMMA_MODEL` | `gemma-4-26b-a4b-it` | Gemma 4 model served through the Gemini API |
| `THINKING_LEVEL` | `minimal` | Gemma 4 reasoning: `minimal` (~20–30 s for a full ToS) or `high` (slower, more careful) |
| `BACKEND` | `gemini` | `gemini`, `ollama` (fully local), or `demo` |
| `OLLAMA_MODEL` | `gemma4` | Local model tag when `BACKEND=ollama` |

### Fully local (open weights)
```bash
ollama pull gemma4
BACKEND=ollama python app.py
```

### Deploy your own
The live demo runs on **Vercel**, imported straight from this repo. To host your own copy:
1. Import the repo on Vercel (or DigitalOcean App Platform, Render, etc.). `requirements.txt` is empty on purpose so hosts detect a Python app, and the `Procfile` runs `python app.py` on platforms that use one.
2. Add `GEMINI_API_KEY` as an environment variable (marked **Sensitive** or **Encrypted**), then redeploy so it takes effect.
3. When the host sets `PORT`, the app listens on `0.0.0.0`. Each visitor gets `RATE_LIMIT` analyses per 10 minutes (default 5), and at most `MAX_CONCURRENT` run at once (default 3), which protects the API quota. These limits are tracked in memory per server instance.

## How it works
1. `app.py` is a small standard-library web server. It sends the text, and any image as inline data, to Gemma 4 with a structured prompt asking for JSON: risk score, verdict, and flags, each with a **verbatim quote**, category, severity, explanation and action.
2. The response is cleaned (fence stripping, schema normalization, severity sorting).
3. The page fuzzy-matches each quote back into the original text (ignoring case, whitespace and curly quotes) to highlight it. Clicking a highlight jumps to its explanation, and clicking an explanation jumps back to the highlight.

## License
MIT
