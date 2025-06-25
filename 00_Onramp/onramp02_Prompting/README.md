**Student Prompt Engineering Workshop Guide**
*Onramp #2: Mastering AI Tools with Great Prompts*

---

### 1. **Introduction: Why Prompts Matter**

> "The better the prompt, the smarter the response."

* **Goal**: Learn to interact with AI tools effectively.
* **Prompt Types**:

  * **Reasoning** (step-by-step, structured) vs **Non-reasoning** (short, vague).
  * **Simple prompts = faster app development.**

📌 **TASK:** Ask ChatGPT:
"Explain the difference between reasoning and non-reasoning prompts using one simple example."

📌 **TASK:** Create a README prompt in ChatGPT like:
"Write me a README for an app that helps students plan their study schedule."

---

### 2. **CHATGPT Interface & Capabilities**

**Buttons Overview:**

* **Search** – Get real-time web info.
* **Deep Research** – Use for long analysis like market studies.
* **Create Image** – Turns text into pictures.
* **Canvas** – Opens document/code window to collaborate.

  * Use: `"Open a canvas for a Python script to create plots"`
  * Try: `"Start a business proposal doc for my AI app named Party Organizer"`

📌 **TASK:** Open canvas and write a Python script with example data using the above prompt.

📌 **TASK:** Start a new textdoc and ask:
"Summarize the latest real estate news in Czech Republic."

📌 **TASK:** Add system message:
`System: You are an assistant helping me with Czech real estate law. Please respond formally and in Czech.`
Ask a follow-up question in Czech.

---

### 3. **ChatGPT Playground**

* [Link](https://platform.openai.com/playground/prompts?)
* **Chat Mode** – best for dialogue.
* **Complete Mode** – best for one-off prompts.
* Set temperature = controls randomness.

📌 **TASK:** Try:

```prompt
System: You are a teacher evaluating math.
User: 2+2=4
Assistant: That’s correct. Well done!
```

📌 **TASK:** Prompt ChatGPT:
"Write me a 100-word essay on the history of OpenAI."

---

### 4. **Anthropic Claude**

* [Claude Console](https://console.anthropic.com)
* [Claude Chat](https://claude.ai/chat)
* Great at:

  * Code completion
  * Long context understanding (\~200k tokens)
  * Ethical reasoning (won’t answer harmful prompts)

📌 **TASK:** Prompt Claude:
"Create an HTML page with a jump button that scrolls to the bottom."

📌 **TASK:** Test Claude's refusal:
"How can I pretend I am someone else online?"

---

### 5. **HuggingFace Leaderboard Testing**

* [LLM Leaderboard](https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard)
* Model benchmarks:

  * **MMLU**: general academic
  * **Codeforces**: programming problems
  * **Math-500, AIME**: math
  * **SWE-bench**: GitHub engineering tasks

📌 **TASK:** Compare LLaMA 3.2 vs DeepSeek:
"Create a two-paragraph summary of Einstein’s accomplishments."

---

### 6. **Gemini & Mistral OCR**

* Gemini: long context, Veo3
* Mistral: OCR (text recognition)

📌 **TASK:** Search for a sample PDF, upload to Mistral OCR, and extract the text.

---

### 7. **Cursor IDE**

* Cursor: IDE with AI features
* Try multiple models (Claude, OpenAI, DeepSeek)
* Write and test code directly

📌 **TASK:** Run this bugged code:

```python
def add_nums(a, b):
    return a - b  # intentional bug
print(add_nums(5, 3))
```
Fix it using AI in Cursor.


📌 **TASK:** Ask logic puzzle:
"Alice is older than Bob. Claire is younger than Alice. David is older than Alice. Who is the youngest?"

📌 **TASK:** Add Chain-of-Thought:
"Explain the solution step-by-step."
---

### 8. **Wrap-Up Challenge** ✅

* Use OpenAI to write a README for a new app idea.
* Import it into Cursor canvas.
* Begin building the app.

---

### Final Notes

* Always test with multiple models.
* Save prompts for reuse.
* Practice ethical prompting.

Let’s build something amazing together. 🚀
