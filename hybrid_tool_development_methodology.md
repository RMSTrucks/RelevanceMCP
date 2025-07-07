# Hybrid Tool Development Methodology  
_Combining deliberate system design with Relevance AI’s “Build-from-Prompt” generator_

## Why This Method?

Building automation in Relevance AI can be time-consuming if every step is wired manually, yet relying 100 % on the “tool-builder AI” often leaves critical gaps (prompts, business logic, code).  
The hybrid method delivers the best of both worlds:

| Design Phase | Generator Phase | Manual Polish |
|--------------|-----------------|---------------|
| • Capture business goals and edge-cases<br>• Draft a detailed spec (steps, data schema, rules)<br>• Craft a **master prompt** describing the entire tool | • Paste the prompt into Relevance AI’s Tool Builder<br>• Let it auto-create inputs, steps, and wiring | • Insert domain prompts<br>• Write/verify Python or browser-automation code<br>• Configure secrets, error handling, tests |

Result: 70-90 % of scaffolding is produced automatically; humans focus on high-value logic and QA.

---

## Step-by-Step Playbook

### 1. Discovery & Specification  
1. Interview SMEs to map **current workflow** and pain points.  
2. Decompose into discrete, automatable steps.  
3. Define:  
   - Inputs / outputs  
   - Business rules & heuristics  
   - External systems (APIs, websites, email)  
4. Record everything in a markdown spec (e.g., `rms_quote_automation_tool_spec.md`).

### 2. Craft the Master Prompt  
Include:  
* Purpose & business context  
* Detailed pipeline table (step id, type, description)  
* Input/output schemas  
* Required secrets or env vars  
* Libraries / post-install commands  
* Error-handling rules  
* Success criteria  

> Tip: Use headings and bullet lists—Relevance’s generator parses structure surprisingly well.

### 3. Generate the Skeleton  
1. Open Relevance AI → **Tools → New Tool → “Build from prompt”**.  
2. Paste the master prompt, click **Generate**.  
3. Inspect resulting structure: confirm step count, types, and input fields.

### 4. Manual Completion  
* **LLM Steps** – Paste refined prompts, set models.  
* **Code Steps** – Insert Python (Playwright, PDF libs, etc.).  
* **Email / HTTP Steps** – Configure accounts & templates.  
* **Secrets** – Move credential placeholders to workspace secrets.  
* **Tests** – Run with sample inputs, iterate.

### 5. Deploy & Iterate  
Publish internally, gather feedback, update spec & prompt; regenerate or tweak as scope evolves.

---

## Roles & Collaboration Model

| Role | Responsibility |
|------|----------------|
| Business Owner | Supplies domain workflow & acceptance criteria |
| Architect (Jake) | Writes spec & master prompt, validates step design |
| Tool Builder AI | Generates initial scaffolding |
| Developer | Codes complex steps, sets up infra |
| QA / Users | Test real transcripts, report issues |

---

## Reusable Prompt Skeleton

```
# PURPOSE
<one-paragraph business goal>

# INPUTS
| name | type | required | description |
| ...  | ...  | ...      | ... |

# PIPELINE
| # | id | type | description |
| 1 | extract_data | LLM | ... |
| … | … | … | … |

# SECRETS
PROG_USER, PROG_PASS, ...

# PYPI
playwright==1.44.0
pdfrw==0.4
...

# ERROR HANDLING
...

# SUCCESS CRITERIA
...
```

Copy, fill, paste → generate.

---

## Advantages

* **Speed** – Minutes to scaffold multi-step tools.  
* **Consistency** – Every tool follows the same structural standard.  
* **Flexibility** – Regenerate when requirements change.  
* **Focus** – Human time spent on prompts & business logic, not wiring.

## Limitations

* Generator can’t write complex code or detailed prompts.  
* Browser automation steps still demand developer skill.  
* Overly long prompts may exceed builder limits—keep under ~5 k tokens.

---

## When to Use It

✅ Repetitive workflows with clear steps  
✅ Projects needing quick proof-of-concept  
✅ Teams comfortable editing Python & prompts

🚫 Highly novel algorithms or heavy integrations that exceed code-step limits.

---

### Recap

1. **Think deeply** → write spec  
2. **Prompt boldly** → auto-build skeleton  
3. **Code & polish** → deliver production-ready tool  

Adopt this rhythm for every new automation and compound your development velocity.
