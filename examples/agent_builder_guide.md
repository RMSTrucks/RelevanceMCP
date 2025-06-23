# Builder Agent Guide  
_Create an agent that builds and manages other agents in Relevance AI_

---

## 1. What is a **Builder Agent**?

A **Builder Agent** is a “meta-agent” whose sole purpose is to design, create, update and retire other agents, knowledge-bases (KBs) and workflows inside your Relevance AI workspace.  
Instead of clicking around the dashboard, you simply _chat_ with the Builder Agent:

> “Spin-up a DOT-Compliance FAQ bot that uses GPT-4o and the `dot_docs` KB.”

Behind the scenes the Builder Agent calls the **Relevance AI MCP Server** you just deployed.  
That server wraps Relevance AI’s management REST API as MCP tools (`create_agent`, `update_agent`, `list_knowledge_bases`, …).  
Result: a fully-configured agent appears in your workspace—no manual UI work required.

---

## 2. Prerequisites

| Item | Why it’s needed |
|------|-----------------|
| Relevance AI account & API key | Authenticates MCP Server calls |
| **Relevance AI MCP Server** running | Exposes management tools over `/mcp` |
| Public HTTPS URL for the server | Relevance must reach it |
| Basic familiarity with Relevance AI dashboard | To verify results |

### 2.1 Run the MCP Server

```bash
git clone https://github.com/YOUR-ORG/relevance-ai-mcp.git
cd relevance-ai-mcp
cp .env.example .env
echo "RELEVANCE_API_KEY=ra_sk_********" >> .env
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

Health-check:  
`curl http://localhost:8000/health` → `{"status":"ok"}`  

Deploy to Railway / Render for a public URL (see project README).

---

## 3. Register the MCP Server in Relevance AI

1. **Workspace Settings → MCP Servers → Add Server**  
2. Name: `relevance-management`  
3. URL: `https://your-domain.com/mcp`  
4. Authentication: **None** — server already holds the API key  
5. Save – tools become discoverable.

*(Optional) Verify: open _Tools → MCP Servers → relevance-management → Tools_ and ensure you see `create_agent`, `list_agents`, …*

---

## 4. Create the Builder Agent

1. **Agents → New Agent → Custom (Advanced)**  
2. **System Prompt** (example):

   ```
   You are the Builder Agent.
   Your mission: design, create and maintain other agents, knowledge-bases and
   workflows in this workspace using the provided MCP tools.
   Confirm destructive actions. Optimise for cost, accuracy and maintainability.
   ```

3. **Tools**  
   - Add **Call MCP Remote Server**  
   - URL → `https://your-domain.com/mcp`  
   - Body template (leave defaults):  

     ```json
     {
       "name": "{{tool_name}}",
       "arguments": {{arguments}}
     }
     ```

4. **Memory / KB (optional)**  
   Attach a KB with your design patterns, pricing guidelines, company branding, etc.

5. **Save** – the Builder Agent is ready.

---

## 5. First Conversation (Smoke Test)

Open the agent chat and type:

```
list all agents (return id & model)
```

Expected flow  

1. Builder Agent calls `list_agents` via MCP  
2. MCP server hits Relevance API  
3. Agent displays a table of agents

If you see the table → success!

---

## 6. Example Prompts

| Goal | Sample user prompt | Expected tool cascade |
|------|-------------------|-----------------------|
| Create an agent | “Create a _DOT Compliance FAQ_ agent using GPT-4o and KB `dot_docs`.” | `create_agent`, `update_agent` |
| Attach tool | “Add the `summarise` tool to DOT Compliance FAQ agent.” | `get_agent`, `update_agent` |
| Bulk list | “Show me all KBs larger than 100 MB.” | `list_knowledge_bases` |
| Workflow | “Generate a workflow: 1) collect carrier info 2) query DOT bot 3) email summary.” | `create_workflow` |
| Clean-up | “Delete prototype-chatbot-v1.” | `delete_agent` (with confirmation) |

---

## 7. Best Practices

* **Iterate incrementally** – ask the Builder Agent to _draft_ the JSON config, review, then approve creation.  
* **Use confirmations** – require `yes`/`no` before `delete_*` operations.  
* **Chunk large uploads** – KB document ingestion >10 MB may timeout.  
* **Version prompts** – store system-prompt snippets in a KB so the Builder Agent can re-use them.  
* **Log everything** – tail MCP server logs (`docker logs -f`, `railway logs -f`) during early testing.  
* **Cost awareness** – specify model (e.g., `gpt-4o-mini`) and maximum tokens when creating agents.

---

## 8. Troubleshooting

| Symptom | Probable cause | Fix |
|---------|----------------|-----|
| `401 Unauthorized` in MCP logs | Wrong / missing API key | Check `RELEVANCE_API_KEY`. |
| Builder Agent “tool not found” | MCP server not registered / wrong URL | Verify MCP server settings & health. |
| Browser CORS error | Domain not allowed | Set `CORS_ORIGINS="https://studio.relevance.ai"` in `.env`. |
| Long document upload fails | Relevance size limit | Split file, retry with `add_document_to_kb`. |

---

## 9. Next Steps

* **Automated nightly jobs** – schedule the Builder Agent (via Relevance Workflows or external cron) to sync docs, archive stale agents, etc.  
* **Multi-workspace management** – spin up one MCP server per workspace and let a _Global Builder Agent_ orchestrate them.  
* **Self-healing** – add monitoring; if `/health` fails, notify you in Slack.  

---

Happy building! Your Builder Agent now eliminates dashboard drudgery and accelerates agent innovation 🚀
