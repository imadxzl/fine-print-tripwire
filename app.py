"""Fine Print Tripwire: flags the risky clauses in Terms of Service and privacy policies.

Runs on Gemma 4 (open weights) through the Gemini API by default, or fully
locally through Ollama. Standard library only, so there's nothing to pip install.

    python app.py            -> http://localhost:8000

Environment (or a .env file next to this script):
    GEMINI_API_KEY   key from Google AI Studio (no key -> demo mode)
    GEMMA_MODEL      default gemma-4-26b-a4b-it
    BACKEND          gemini (default) | ollama | demo
    OLLAMA_MODEL     default gemma4
    OLLAMA_URL       default http://localhost:11434
    PORT             default 8000
"""

import json
import os
import re
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).parent
STATIC = ROOT / "static"
MAX_CHARS = 120_000
MAX_BODY = 20 * 1024 * 1024


def load_dotenv():
    env = ROOT / ".env"
    if not env.exists():
        return
    for line in env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


load_dotenv()
API_KEY = os.environ.get("GEMINI_API_KEY", "")
MODEL = os.environ.get("GEMMA_MODEL", "gemma-4-26b-a4b-it")
# Gemma 4 thinks by default, which is slow. "minimal" (~20 s for a full ToS) or "high" (slower,
# more careful); "low"/"medium" are rejected by gemma-4-26b-a4b-it.
THINKING_LEVEL = os.environ.get("THINKING_LEVEL", "minimal")
BACKEND = os.environ.get("BACKEND", "gemini" if API_KEY else "demo").lower()
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemma4")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")

CATEGORIES = [
    "data_sharing", "tracking", "auto_renewal", "arbitration", "liability",
    "content_rights", "termination", "unilateral_changes", "fees", "other",
]

PROMPT = """You are Fine Print Tripwire, a consumer-protection analyst. Read the legal text
(Terms of Service, privacy policy, EULA, subscription terms) and flag every clause
that an ordinary user would want to know about before agreeing.

Look especially for: selling/sharing personal data, tracking and profiling, auto-renewal
and cancellation traps, forced arbitration and class-action waivers, liability limits,
broad licenses over user content, termination without notice, changing terms without
notice, hidden fees, and anything unusual.

Return ONLY a JSON object, no markdown, no commentary, in exactly this shape:
{
  "document_type": "short label, e.g. Terms of Service",
  "overall_risk": <integer 0-100, 100 = extremely user-hostile>,
  "verdict": "one punchy sentence summarizing whether to worry",
  "flags": [
    {
      "quote": "EXACT verbatim excerpt copied character-for-character from the text, 1-2 sentences, max 300 characters",
      "category": one of %s,
      "severity": "high" | "medium" | "low",
      "title": "3-6 word headline",
      "plain_english": "what this actually means for the user, 1-2 sentences, no legalese",
      "what_you_can_do": "one concrete action (opt-out, setting, alternative), or 'Nothing - this is a dealbreaker or accept it'"
    }
  ]
}

Rules: quotes MUST be copied exactly from the text so they can be highlighted. Order flags
from most to least severe. Do not flag boilerplate that is harmless. If an image is given,
read the text in the image and quote from it.
""" % json.dumps(CATEGORIES)


# ---------------------------------------------------------------- model calls

def http_json(url, payload, headers=None, timeout=180):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", **(headers or {})},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:600]
        raise RuntimeError(f"Model API returned {e.code}: {detail}") from None
    except urllib.error.URLError as e:
        raise RuntimeError(f"Could not reach the model: {e.reason}") from None


def call_gemini(text, image):
    parts = [{"text": PROMPT}]
    if image:
        parts.append({"inline_data": {"mime_type": image["mime"], "data": image["data"]}})
    parts.append({"text": "LEGAL TEXT:\n\n" + (text or "(see image)")})
    data = http_json(
        f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent",
        {"contents": [{"role": "user", "parts": parts}],
         "generationConfig": {"temperature": 0.2,
                              "thinkingConfig": {"thinkingLevel": THINKING_LEVEL}}},
        headers={"x-goog-api-key": API_KEY},
    )
    try:
        out_parts = data["candidates"][0]["content"]["parts"]
    except (KeyError, IndexError):
        raise RuntimeError("Model returned no content: " + json.dumps(data)[:400]) from None
    # Skip "thought" parts if thinking is enabled; keep only the final answer.
    return "".join(p.get("text", "") for p in out_parts if not p.get("thought"))


def call_ollama(text, image):
    msg = {"role": "user", "content": PROMPT + "\n\nLEGAL TEXT:\n\n" + (text or "(see image)")}
    if image:
        msg["images"] = [image["data"]]
    data = http_json(
        f"{OLLAMA_URL}/api/chat",
        {"model": OLLAMA_MODEL, "messages": [msg], "stream": False,
         "format": "json", "options": {"temperature": 0.2}},
        timeout=600,
    )
    return data.get("message", {}).get("content", "")


def parse_json(raw):
    raw = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.M).strip()
    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end == -1:
        raise RuntimeError("Model did not return JSON. Raw output: " + raw[:400])
    return json.loads(raw[start:end + 1])


def normalize(result):
    flags = []
    for f in result.get("flags") or []:
        if not isinstance(f, dict) or not f.get("quote"):
            continue
        sev = str(f.get("severity", "medium")).lower()
        f["severity"] = sev if sev in ("high", "medium", "low") else "medium"
        if f.get("category") not in CATEGORIES:
            f["category"] = "other"
        flags.append(f)
    order = {"high": 0, "medium": 1, "low": 2}
    flags.sort(key=lambda f: order[f["severity"]])
    result["flags"] = flags
    if not isinstance(result.get("overall_risk"), (int, float)):
        weights = {"high": 25, "medium": 10, "low": 4}
        result["overall_risk"] = min(100, sum(weights[f["severity"]] for f in flags))
    result["overall_risk"] = max(0, min(100, int(result["overall_risk"])))
    return result


# ------------------------------------------------- demo mode (no model needed)

DEMO_RULES = [
    (r"sell|share .{0,40}(third part|partner|advertis)", "data_sharing", "high", "Your data gets sold or shared",
     "They can pass your personal information to other companies, including advertisers.",
     "Look for a 'Do Not Sell or Share' link or privacy settings to opt out."),
    (r"arbitration|class action", "arbitration", "high", "You can't sue them in court",
     "Disputes go to private arbitration and you give up joining class actions.",
     "Check for an opt-out window (often 30 days) and email them to opt out."),
    (r"automatically renew|auto-renew|renews automatically", "auto_renewal", "medium", "Subscription renews on its own",
     "You'll keep getting charged until you cancel.",
     "Set a calendar reminder before the renewal date."),
    (r"perpetual|irrevocable|royalty-free", "content_rights", "high", "They own a license to your content",
     "They can use, change, and profit from what you upload, forever.",
     "Don't upload anything you might want to keep exclusive."),
    (r"at any time.{0,60}(without notice|sole discretion)|without (prior )?notice", "unilateral_changes", "medium",
     "Rules can change without warning", "They can change terms or cut you off without telling you first.",
     "Export your data regularly."),
    (r"location|biometric|contacts|microphone", "tracking", "medium", "Sensitive tracking",
     "They collect sensitive data like location, contacts, or biometrics.",
     "Deny those permissions in your phone settings."),
    (r"not (be )?liable|limitation of liability|maximum extent", "liability", "low", "Limited responsibility if things go wrong",
     "If their service harms you, the most they owe you is tiny.",
     "Nothing - fairly standard, but worth knowing."),
]


def demo_analyze(text):
    sentences = re.split(r"(?<=[.!?])\s+", text or "")
    flags, used = [], set()
    for pattern, cat, sev, title, plain, todo in DEMO_RULES:
        for s in sentences:
            if cat not in used and re.search(pattern, s, re.I):
                flags.append({"quote": s.strip()[:300], "category": cat, "severity": sev, "title": title,
                              "plain_english": plain, "what_you_can_do": todo})
                used.add(cat)
                break
    return {"document_type": "Legal text", "verdict": "Demo mode (keyword rules, no AI). Add GEMINI_API_KEY to use Gemma 4.",
            "flags": flags}


def analyze(text, image):
    text = (text or "")[:MAX_CHARS]
    if BACKEND == "demo":
        return normalize(demo_analyze(text))
    raw = call_ollama(text, image) if BACKEND == "ollama" else call_gemini(text, image)
    return normalize(parse_json(raw))


# ---------------------------------------------------------------- HTTP server

class Handler(BaseHTTPRequestHandler):
    def send_json(self, code, obj):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/api/config":
            model = {"gemini": MODEL, "ollama": OLLAMA_MODEL}.get(BACKEND, "keyword rules")
            return self.send_json(200, {"backend": BACKEND, "model": model})
        files = {"/": ("index.html", "text/html"),
                 "/sample": ("../samples/snacksnap_terms.txt", "text/plain")}
        if path not in files:
            return self.send_error(404)
        name, ctype = files[path]
        body = (STATIC / name).read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path != "/api/analyze":
            return self.send_error(404)
        length = int(self.headers.get("Content-Length", 0))
        if length > MAX_BODY:
            return self.send_json(413, {"error": "Too large. Keep images under 15 MB."})
        try:
            req = json.loads(self.rfile.read(length) or b"{}")
            text, image = req.get("text", ""), req.get("image")
            if not text.strip() and not image:
                return self.send_json(400, {"error": "Paste some text or add a screenshot first."})
            self.send_json(200, analyze(text, image))
        except Exception as e:  # surface every failure to the UI during the demo
            self.send_json(500, {"error": str(e)})

    def log_message(self, fmt, *args):
        print("  " + fmt % args)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    model = {"gemini": MODEL, "ollama": OLLAMA_MODEL}.get(BACKEND, "keyword rules")
    print(f"Fine Print Tripwire on http://localhost:{port}  (backend: {BACKEND}, model: {model})")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
