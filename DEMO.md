# Fine Print Tripwire: Demo Kit

**Live:** https://fine-print-tripwire.vercel.app/ · **Code:** https://github.com/imadxzl/fine-print-tripwire

## 1. Two-minute pitch script (solo)

You present and drive the laptop yourself. The script is timed so that Gemma's ~25-second analysis runs **while you're talking**, so there's no dead air. Keep the mouse work small: one click, then talk.

**Before you start:** open the app (the live URL or `localhost:8000`), click **Load sample**, and zoom the browser to 125% so the back row can read it.

| Time | Say | Do |
|---|---|---|
| 0:00–0:15 | "Quick show of hands: who has actually read a Terms of Service before clicking *I agree*? … Right. Nobody. They're written so that nobody does. Some of them hide things you'd really care about." | Point at the screen |
| 0:15–0:25 | "This is **Fine Print Tripwire**. You give it any Terms of Service or privacy policy, as text or even a screenshot, and it tells you what you're actually agreeing to." | Scroll the SnackSnap sample |
| 0:25–0:30 | "Here's the terms for SnackSnap, a made-up food photo app. Let's trip the wire." | **Click *Trip the wire*** (timer starts) |
| 0:30–0:55 | *(while it runs)* "Under the hood this is **Gemma 4**, Google's open-weights model. I ask it for structured output: a risk score, every risky clause quoted word for word, a plain-English explanation, and something you can actually *do* about it. Because the weights are open, the same code can run entirely on your own laptop, so your documents never have to leave your machine. That matters when the thing you're checking is a company's own privacy policy." | Spinner and seconds counter |
| 0:55–1:20 | "Risk **95 out of 100**. It found 8 problems. The worst one: *cancellation must be made by mailing a written request*. You can't cancel in the app. It also caught that they **sell your inferred health data to data brokers**, and that they get a **perpetual, irrevocable license** to your photos." | Click the top cards; each jumps to its highlight |
| 1:20–1:30 | "Every card is linked to the exact sentence in the original text, so you don't have to trust the AI. You can check it yourself." | Click a highlight and it jumps back to its card |
| 1:30–1:50 | "And it's multimodal: just screenshot a sign-up screen." *(Optional live moment: "Which app do you use? Let's check it.")* | Drop in a screenshot and click the button (or show a pre-captured result) |
| 1:50–2:00 | "It's live right now at fine-print-tripwire.vercel.app. Open model, plain English, no legalese. Read the fine print without reading the fine print. Thank you!" | Results view |

**If a judge asks…**
- *"Is it accurate?"* Every flag quotes the source word for word and is highlighted in place, so a human can check it in one click. It uses a low temperature, and the prompt forbids flagging harmless boilerplate.
- *"Why Gemma rather than a bigger model?"* It's open-weights and multimodal, and with thinking set to minimal it handles a full ToS in about 25 seconds. Open weights also make the fully local, private version possible.
- *"What was hard?"* Gemma 4 thinks by default, which used about 800 thinking tokens just to say "hi", and my first full request ran for over a minute. Switching `thinkingLevel` to `minimal` got a full ToS down to about 25 seconds. Getting highlights to land also needed exact verbatim quotes and fuzzy matching (curly quotes, whitespace) as a fallback.
- *"Can people abuse the public site?"* Each visitor is rate-limited and only a few analyses run at once, which protects the API quota.
- *"What's next?"* A browser extension that checks the terms on the page you're about to accept, change tracking ("SnackSnap updated its terms; here's what got worse"), and a side-by-side comparison of two services' terms.

---

## 2. Backup plan

Fest Wi-Fi is the main risk. Prepare all of these **before** your slot, and drop down a layer if one fails:

1. **Live with Gemma 4** (best). Use the Vercel URL or `localhost:8000`, whichever responds faster. Run one analysis about 5 minutes before you present to warm up and confirm the network.
2. **The other copy.** If the live site has problems, run it locally (`python app.py`), and if local has problems, use the live site. They're the same code.
3. **Pre-recorded video.** Record a 90-second screen capture of the full flow (see below) and keep it open in a second tab or window, ready to play.
4. **Demo mode.** Run locally with `BACKEND=demo`. It works with no network using keyword rules. Say: "this is the offline fallback; the real one uses Gemma."
5. **Screenshots.** Save 3 PNGs (input, results, screenshot analysis) to the desktop and use them as slides if the laptop itself has problems.

**Phone hotspot:** if the venue Wi-Fi is slow, tether your phone. A full analysis uses only a few KB of data.

### Recording the backup video (about 10 minutes)
1. Open the app, click **Load sample**, and zoom the browser to 125%.
2. Start recording:
   - **Windows 11:** Snipping Tool → *Record* (`Win + Shift + R`), then select the browser window, **or**
   - **Xbox Game Bar:** `Win + Alt + R` to start and stop. Recordings are saved to `Videos\Captures`.
3. Click **Trip the wire**, wait for the results, click 2–3 cards to show the jump-to-highlight, then drop in a screenshot and show that result.
4. Stop. Trim the waiting time if your tool allows it. Otherwise, narrating over the wait is fine.
5. Upload it to YouTube as **Unlisted**. Most MLH submission forms want a video link, so you'll reuse this for submission too.
6. Keep the local file on the desktop as well, so you don't depend on the venue Wi-Fi to play it.

**Optional voice-over:** record a second take reading the pitch script above. That gives you a submission video that stands on its own for judges who weren't at your table.

---

## 3. Submission text

### Project name
Fine Print Tripwire

### Links
- **Try it:** https://fine-print-tripwire.vercel.app/
- **Code:** https://github.com/imadxzl/fine-print-tripwire

### Tagline (one line)
Paste any Terms of Service, or just screenshot it, and Gemma 4 tells you, in plain English, the clauses you'd regret agreeing to.

### Inspiration
Nobody reads Terms of Service, and companies know it. Clauses about selling your data, cancellation traps and forced arbitration hide in thousands of words of legalese. I wanted a tool that reads it for you, and one you don't have to trust blindly: every warning points to the exact sentence it came from.

### What it does
- Takes legal text **or a screenshot** (Gemma 4 reads the image directly).
- Returns a **0–100 risk score** and a one-line verdict.
- Flags every risky clause (data selling, tracking, auto-renewal, arbitration, content licenses, termination, unilateral changes, fees) with a **severity**, a **plain-English explanation**, and **one concrete thing you can do** about it (an opt-out, a setting, a deadline).
- **Highlights each flagged clause in the original text.** Clicking a warning jumps to its sentence, and clicking a highlight jumps back to its warning, so a human can verify every claim in one click.

### How I built it
- **Model:** Gemma 4 (`gemma-4-26b-a4b-it`) through the Gemini API, with text and image input in a single request.
- **Prompting:** a structured prompt that asks for strict JSON, including verbatim quotes, a fixed category list and severity levels. On the server, I strip code fences, check the output against the schema and sort by severity.
- **Backend:** a small web server in Python using only the standard library, with no dependencies. It has three interchangeable backends: Gemini API, **Ollama (open weights running locally)**, and an offline keyword demo mode. The public deployment has per-visitor rate limiting and a concurrency cap to protect the API quota.
- **Frontend:** a single HTML page in plain JavaScript. It fuzzy-matches each quote back into the source text (ignoring case, whitespace, curly quotes and dashes) so the highlights land even when the formatting differs.
- **Hosting:** deployed on Vercel directly from the GitHub repo.

### Challenges I ran into
- **Latency from thinking.** Gemma 4 reasons by default, which spent about 800 thinking tokens on "say hi in 3 words", and my first full request ran for over a minute. Setting `thinkingLevel: minimal` got a full Terms of Service down to about 25 seconds without losing accuracy on my test document. I also found that this model accepts `minimal` and `high` but rejects `low`.
- **Separating thoughts from answers.** The API returns thinking as separate parts, so I filter on the `thought` flag and parse only the final answer.
- **Making highlights land.** Models paraphrase. I require verbatim quotes and back them with a fuzzy matcher. On my test document, 8 out of 8 quotes matched exactly.

### Accomplishments I'm proud of
- On my deliberately hostile sample terms, it found all the major traps (cancellation by mailed letter only, sale of inferred health data, a perpetual license to your photos, forced arbitration) in a single pass.
- Screenshot input works end to end: it found all 4 planted clauses in an image with no text pasted.
- Zero dependencies, live on the web, and `python app.py` runs it locally.

### What I learned
How to get reliable structured output from an open model, how much thinking settings affect latency, and that "show your source" UX matters as much as the model when people need to trust an AI's judgment.

### What's next
- A browser extension that checks the terms on the sign-up page you're on.
- Change tracking: "This app updated its terms; here's what got worse."
- Comparing two services' terms side by side.
- A packaged fully local mode for privacy-sensitive users.

### Built with
`gemma-4` · `gemini-api` · `python` · `javascript` · `html` · `css` · `ollama` · `vercel`

---

### Category-specific blurbs (paste into each category's field if the form asks "why does this fit?")

**Best Use of Gemma 4**
> Fine Print Tripwire is built around Gemma 4 and uses all three things the category asks for. **Multimodal:** users can screenshot a sign-up screen or policy instead of copying text, and Gemma reads the image and quotes from it. **A focused AI tool for the community:** it does one job, protecting ordinary users from hostile Terms of Service. **Rapid prototyping:** I went from idea to a working, deployed, structured-output app in one afternoon through the Gemini API, and tuned Gemma's thinking level to bring a full analysis down from over a minute to about 25 seconds. Try it: https://fine-print-tripwire.vercel.app/

**Best Open-Source AI Project (DigitalOcean)**
> Fine Print Tripwire is an open-source app (MIT) built on an open-weights model, Gemma 4, and open weights are central to why it matters. A tool that reads privacy policies shouldn't have to send your documents to someone else's cloud. Because Gemma's weights are open, the same code includes an **Ollama backend that runs fully on your own machine**. It also has an offline demo mode, has zero dependencies, and is designed to be easy for others to fork and extend: new clause categories are a single list in `app.py`. Code: https://github.com/imadxzl/fine-print-tripwire
