# Business Process → Relevance AI Tool Framework
_A reusable prompt & worksheet for analysts, SMEs, and LLM agents_

---

## 0. How to Use This Prompt

1. Copy everything from **Phase 1** onward into your Relevance AI chat or any LLM playground.  
2. Answer the questions in each phase **before** moving to the next.  
3. When all phases are complete, you will have:
   - A fully decomposed workflow
   - A step-by-step Relevance AI tool spec
   - Implementation notes (LLM vs code vs API)
4. Hand the final spec to engineering or let an agent generate the code/steps automatically.

---

## Phase 1 – Discovery

**Objective:** Capture the business goal, context, and end-to-end human workflow.

### Questions for the SME
- What problem does this process solve?  
- Who are the primary users & stakeholders?  
- What is the success metric (time, cost, accuracy, compliance)?  
- Walk me through the process as you would teach a new hire.  
- Where do human decisions, look-ups, or approvals occur?

### Outputs
- 2–3 sentence **Purpose Statement**  
- Bullet-list **Current Workflow** (chronological)  
- Known documents, data sources, APIs, spreadsheets involved

---

## Phase 2 – Analysis

**Objective:** Break the workflow into discrete, automatable units.

### Activities
1. **Task Granularity** – Split each human action into the smallest meaningful step.  
2. **Decision Identification** – Mark steps that rely on judgment or domain knowledge.  
3. **Data Mapping** – Note required inputs/outputs for each step.

### Guiding Questions
- Does this step require natural-language understanding or generation?  
- Can the rule be expressed deterministically in code?  
- Is external data/API access needed?

### Outputs
| # | Step Name | Human / Auto | Inputs | Outputs | Notes |
|---|-----------|--------------|--------|---------|-------|
|   |           |              |        |         |       |

---

## Phase 3 – Tool Design (Relevance AI Steps)

**Objective:** Translate analysis into a Relevance AI tool specification.

### Step Types Reference
- **LLM Step** – reasoning, drafting, summarising  
- **Code Step** – calculations, transformations, complex logic  
- **API Step** – external service calls  
- **Conditional / Branch** – if/else logic  
- **Loop / Map** – iterate over collections

### Design Checklist
- For each table row from Phase 2, assign a Step Type.  
- Define parameter schema: `name`, `type`, `description`, `required?`, `example`.  
- Draft the prompt for LLM steps (include system/context + user vars).  
- Specify success criteria & error handling for every step.

### Output
A structured YAML/JSON or markdown block summarising the Relevance AI tool, e.g.:

```
tool_name: fmcsa_compliance_checker
description: Evaluate DOT registration requirements for new trucking companies
steps:
  - name: gather_company_info
    type: llm
    prompt: |
      You are ...
  - name: fetch_regulations
    type: api
    endpoint: https://...
  ...
```

---

## Phase 4 – Implementation Planning

**Objective:** Prepare for coding & configuration.

- Choose runtime: native Relevance AI tool vs. external MCP server  
- Dependencies (Python libs, credentials, environment variables)  
- Dev-ops: repo location, CI/CD, hosting (Render, Railway, etc.)  
- Access control & secrets management  
- Performance / cost considerations (token usage, API quotas)

---

## Phase 5 – Validation & Testing

1. Create test cases covering normal, edge, and failure scenarios.  
2. Define measurable pass/fail criteria.  
3. Run step-by-step dry runs using sample data.  
4. Iterate on prompts & code until tests pass.

---

## Phase 6 – Deployment & Iteration

- Deploy to staging; enable logging & tracing.  
- Gather real-world feedback (success metrics from Phase 1).  
- Schedule periodic prompt & code reviews.  
- Add enhancements or new steps as business needs evolve.

---

### Mini-Example (Skeleton)

> **Purpose:** Automate initial FMCSA registration eligibility check.  
> **Steps:**  
> 1. Collect company profile (LLM)  
> 2. Determine vehicle class rules (lookup table → code)  
> 3. Fetch latest fee amounts (API)  
> 4. Generate compliance summary (LLM)  
> 5. Return JSON + PDF report (code)

Copy this skeleton, expand each step using the phases above, and you have a production-ready Relevance AI tool blueprint.
