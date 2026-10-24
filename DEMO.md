# Fine Print Tripwire: Demo Kit

## 1. Two-minute pitch script

Written for two speakers: **A** talks and **B** drives the laptop. With one person, do both.
The script is timed so that Gemma's ~25-second analysis runs **while you're talking**, so there's no dead air.

**Before you start:** the app is open at `localhost:8000`, the sample is already loaded with **Load sample**, and the window is zoomed to 125% so the back row can read it.

| Time | Speaker | Say | On screen |
|---|---|---|---|
| 0:00–0:15 | A | "Quick show of hands: who has actually read a Terms of Service before clicking *I agree*? … Right. Nobody. They're written so that nobody does. Some of them hide things you'd really care about." | App title |
| 0:15–0:25 | A | "This is **Fine Print Tripwire**. You give it any Terms of Service or privacy policy, as text or even a screenshot, and it tells you what you're actually agreeing to." | B scrolls the SnackSnap sample |
| 0:25–0:30 | A | "Here's the terms for SnackSnap, a made-up food photo app. Let's trip the wire." | **B clicks *Trip the wire*** (timer starts) |
| 0:30–0:55 | A | *(while it runs)* "Under the hood this is **Gemma 4**, Google's open-weights model. We ask it for structured output: a risk score, every risky clause quoted word for word, a plain-English explanation, and something you can actually *do* about it. Because the weights are open, the same code can run entirely on your own laptop, so your documents never have to leave your machine. That matters when the thing you're checking is a company's own privacy policy." | Spinner and seconds counter |
| 0:55–1:20 | A | "Risk **95 out of 100**. It found 8 problems. The worst one: *cancellation must be made by mailing a written request*. You can't cancel in the app. It also caught that they **sell your inferred health data to data brokers**, and that they get a **perpetual, irrevocable license** to your photos." | B clicks the top cards; each jumps to its highlight in the text |
| 1:20–1:30 | A | "Every card is linked to the exact sentence in the original text, so you don't have to trust the AI. You can check it yourself." | B clicks a highlight and it jumps back to its card |
| 1:30–1:50 | A | "And it's multimodal: just screenshot a sign-up screen." *(Optional live moment: "Which app do you use? Let's check it.")* | B drops in a screenshot and clicks the button (or shows a pre-captured result) |
| 1:50–2:00 | A | "Fine Print Tripwire: open model, plain English, no legalese. Read the fine print without reading the fine print. Thank you!" | Results view |

**If a judge asks…**
- *"Is it accurate?"* Every flag quotes the source word for word and is highlighted in place, so a human can check it in one click. We use a low temperature, and the prompt forbids flagging harmless boilerplate.
- *"Why Gemma rather than a bigger model?"* It's open-weights and multimodal, and with thinking set to minimal it handles a full ToS in about 25 seconds. Open weights also make the fully local, private version possible.
- *"What was hard?"* Gemma 4 thinks by default, which used about 800 thinking tokens just to say "hi", and our first full request ran for over a minute. Switching `thinkingLevel` to `minimal` got a full ToS down to about 25 seconds. Getting highlights to land also needed exact verbatim quotes and fuzzy matching (curly quotes, whitespace) as a fallback.
- *"What's next?"* A browser extension that checks the terms on the page you're about to accept, change tracking ("SnackSnap updated its terms; here's what got worse"), and a hosted version.

---

## 2. Backup plan

Fest Wi-Fi is the main risk. Prepare all four layers **before** your slot, and drop down a layer if one fails:

1. **Live with Gemma 4** (best). Run one analysis about 5 minutes before you present to warm up and confirm the network.
2. **Pre-recorded video.** Record a 90-second screen capture of the full flow (see below) and keep it open in a second tab or window, ready to play.
3. **Demo mode.** Remove the key from `.env` (or set `BACKEND=demo`) and restart `python app.py`. The app works with no network using keyword rules. Say: "this is the offline fallback; the real one uses Gemma."
4. **Screenshots.** Save 3 PNGs (input, results, screenshot analysis) to the desktop and use them as slides if the laptop itself has problems.

**Phone hotspot:** if the venue Wi-Fi is slow, tether one teammate's phone. A full analysis uses only a few KB of data.

### Recording the backup video (about 10 minutes)
1. Restart the app, click **Load sample**, and zoom the browser to 125%.
2. Start recording:
   - **Windows 11:** Snipping Tool → *Record* (`Win + Shift + R`), then select the browser window, **or**
   - **Xbox Game Bar:** `Win + Alt + R` to start and stop. Recordings are saved to `Videos\Captures`.
   - **Mac:** `Cmd + Shift + 5` → *Record selected portion*.
3. Click **Trip the wire**, wait for the results, click 2–3 cards to show the jump-to-highlight, then drop in a screenshot and show that result.
4. Stop. Trim the waiting time if your tool allows it. Otherwise, narrating over the wait is fine.
5. Upload it to YouTube as **Unlisted**. Most MLH submission forms want a video link, so you'll reuse this for submission too.
6. Keep the local file on the desktop as well, so you don't depend on the venue Wi-Fi to play it.

**Optional voice-over:** record a second take reading the pitch script above. That gives you a submission video that stands on its own for judges who weren't at your table.

---

## 3. Submission text

### Project name
Fine Print Tripwire

### Tagline (one line)
Paste any Terms of Service, or just screenshot it, and Gemma 4 tells you, in plain English, the clauses you'd regret agreeing to.

### Inspiration
Nobody reads Terms of Service, and companies know it. Clauses about selling your data, cancellation traps and forced arbitration hide in thousands of words of legalese. We wanted a tool that reads it for you, and one you don't have to trust blindly: every warning points to the exact sentence it came from.

### What it does
- Takes legal text **or a screenshot** (Gemma 4 reads the image directly).
- Returns a **0–100 risk score** and a one-line verdict.
- Flags every risky clause (data selling, tracking, auto-renewal, arbitration, content licenses, termination, unilateral changes, fees) with a **severity**, a **plain-English explanation**, and **one concrete thing you can do** about it (an opt-out, a setting, a deadline).
- **Highlights each flagged clause in the original text.** Clicking a warning jumps to its sentence, and clicking a highlight jumps back to its warning, so a human can verify every claim in one click.

### How we built it
- **Model:** Gemma 4 (`gemma-4-26b-a4b-it`) through the Gemini API, with text and image input in a single request.
- **Prompting:** a structured prompt that asks for strict JSON, including verbatim quotes, a fixed category list and severity levels. On the server we strip code fences, check the output against the schema and sort by severity.
- **Backend:** a small web server in Python using only the standard library, with no dependencies. It has three interchangeable backends: Gemini API, **Ollama (open weights running locally)**, and an offline keyword demo mode.
- **Frontend:** a single HTML page in plain JavaScript. It fuzzy-matches each quote back into the source text (ignoring case, whitespace, curly quotes and dashes) so the highlights land even when the formatting differs.

### Challenges we ran into
- **Latency from thinking.** Gemma 4 reasons by default, which spent about 800 thinking tokens on "say hi in 3 words", and our first full request ran for over a minute. Setting `thinkingLevel: minimal` got a full Terms of Service down to about 25 seconds without losing accuracy on our test document. We also found that this model accepts `minimal` and `high` but rejects `low`.
- **Separating thoughts from answers.** The API returns thinking as separate parts, so we filter on the `thought` flag and parse only the final answer.
- **Making highlights land.** Models paraphrase. We require verbatim quotes and back them with a fuzzy matcher. On our test document, 8 out of 8 quotes matched exactly.

### Accomplishments we're proud of
- On our deliberately hostile sample terms, it found all the major traps (cancellation by mailed letter only, sale of inferred health data, a perpetual license to your photos, forced arbitration) in a single pass.
- Screenshot input works end to end: it found all 4 planted clauses in an image with no text pasted.
- Zero dependencies: `python app.py` and you're running.

### What we learned
How to get reliable structured output from an open model, how much thinking settings affect latency, and that "show your source" UX matters as much as the model when people need to trust an AI's judgment.

### What's next
- A browser extension that checks the terms on the sign-up page you're on.
- Change tracking: "This app updated its terms; here's what got worse."
- Comparing two services' terms side by side.
- A packaged fully local mode for privacy-sensitive users.

### Built with
`gemma-4` · `gemini-api` · `python` · `javascript` · `html` · `css` · `ollama`

---

### Category-specific blurbs (paste into each category's field if the form asks "why does this fit?")

**Best Use of Gemma 4**
> Fine Print Tripwire is built around Gemma 4 and uses all three things the category asks for. **Multimodal:** users can screenshot a sign-up screen or policy instead of copying text, and Gemma reads the image and quotes from it. **A focused AI tool for the community:** it does one job, protecting ordinary users from hostile Terms of Service. **Rapid prototyping:** we went from idea to a working, structured-output app in one afternoon through the Gemini API, and tuned Gemma's thinking level to bring a full analysis down from over a minute to about 25 seconds.

**Best Open-Source AI Project (DigitalOcean)**
> Fine Print Tripwire is an open-source app (MIT) built on an open-weights model, Gemma 4, and open weights are central to why it matters. A tool that reads privacy policies shouldn't have to send your documents to someone else's cloud. Because Gemma's weights are open, the same code includes an **Ollama backend that runs fully on your own machine**. It also has an offline demo mode, has zero dependencies, and is designed to be easy for others to fork and extend: new clause categories are a single list in `app.py`.
