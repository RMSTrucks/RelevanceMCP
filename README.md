# Relevance AI Management MCP Server

A lightweight **FastAPI** micro-service that exposes your **Relevance AI workspace-management API** as standard **MCP (Model Context Protocol) tools**.  
With it, *any* LLM-powered agent can **create, update and orchestrate** agents, knowledge-bases, workflows, and even other MCP servers inside your Relevance workspace – the foundation for the **“agent that builds agents”** pattern.

---

## Table of Contents
1. [Why this project exists](#why-this-project-exists)  
2. [Features](#features)  
3. [Architecture](#architecture)  
4. [Quick-start](#quick-start)  
5. [Environment variables](#environment-variables)  
6. [Running locally](#running-locally)  
7. [Deployment](#deployment) – Railway & Render  
8. [Using inside Relevance AI](#using-inside-relevance-ai)  
9. [Troubleshooting](#troubleshooting)  
10. [Roadmap](#roadmap)  
11. [License](#license)

---

## Why this project exists
Clicking through dashboards to spin-up agents and KBs is slow and error-prone.  
By wrapping Relevance AI’s management REST API as MCP tools you can:

* Chat with a **Builder Agent** that designs and deploys new agents on-the-fly.  
* Automate workspace housekeeping (e.g. nightly KB sync).  
* Chain multiple MCP servers – your Builder Agent can register / deregister other servers programmatically.

---

## Features

| Category | Tools exposed |
|----------|---------------|
| **Agent Management** | `list_agents`, `get_agent`, `create_agent`, `update_agent`, `delete_agent` |
| **Knowledge-Base Management** | `list_knowledge_bases`, `get_knowledge_base`, `create_knowledge_base`, `add_document_to_kb`, `search_knowledge_base`, `delete_knowledge_base` |
| **Workflow Configuration** | `list_workflows`, `get_workflow`, `create_workflow`, `update_workflow`, `delete_workflow` |
| **MCP Server Registry** | `list_mcp_servers`, `register_mcp_server`, `get_mcp_server_tools`, `unregister_mcp_server` |
| **Passthrough** | `relevance_api_call` – raw access to any endpoint |

* **Zero-schema** – no Pydantic, ultra-fast cold-start.  
* **Stateless** – rate limits enforced by Relevance AI, nothing stored locally.  
* **CORS friendly** – enable browser clients with one env var.  
* **Health endpoint** – `/health` returns `{"status":"ok"}` for platform probes.

---

## Architecture

```
+------------------+   /mcp POST           +---------------------------+    HTTPS    +------------------+
| Relevance Agent  | ───────────────► | Relevance AI MCP Server | ─────────► | Relevance AI API |
|  (LLM)           |                   |  (FastAPI + Uvicorn)   |            |   Cloud Backend   |
+------------------+                   +---------------------------+            +------------------+
```

1. Agent sends JSON  
   `{ "name": "create_agent", "arguments": { "name": "FAQ-Bot" } }`
2. MCP server maps to Python function → calls Relevance REST endpoint.
3. Response relayed to the agent. 🚀

---

## Quick start

```bash
# 1. Clone
git clone https://github.com/YOUR-ORG/relevance-ai-mcp.git
cd relevance-ai-mcp

# 2. (optional) Virtual-env
python -m venv .venv && source .venv/bin/activate

# 3. Install minimal deps
pip install -r requirements.txt

# 4. Configure
cp .env.example .env
echo "RELEVANCE_API_KEY=ra_sk_********" >> .env   # workspace API key

# 5. Run
python main.py
# or (auto-reload)
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Health-check:  
`curl http://localhost:8000/health` → `{"status":"ok","version":"1.0.0"}`

---

## Environment variables

| Key | Required | Default | Notes |
|-----|----------|---------|-------|
| `RELEVANCE_API_KEY` | **Yes** | – | Workspace or personal API key. |
| `RELEVANCE_API_BASE_URL` | No | `https://api.relevanceai.com/v1` | Override for self-host / staging. |
| `PORT` | No | `8000` | Hosting platforms inject automatically. |
| `CORS_ORIGINS` | No | `*` | Comma-separated list of allowed origins. |
| `LOG_LEVEL` | No | `INFO` | `DEBUG`, `WARNING`, `ERROR`, … |

---

## Running locally

```bash
export RELEVANCE_API_KEY=ra_sk_...
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Example tool call:

```bash
curl -X POST http://localhost:8000/mcp \
     -H "Content-Type: application/json" \
     -d '{"name":"list_agents","arguments":{"limit":2}}'
```

---

## Deployment

### Railway (free tier)

1. Create new project → **Deploy from GitHub**.  
2. Railway detects `railway.json`; build & start automatically.  
3. Add **RELEVANCE_API_KEY** in *Variables*.  
4. Wait for `/health` to return 200.

### Render (free Web Service)

```yaml
# render.yaml snippet
services:
  - type: web
    name: relevance-ai-mcp
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host=0.0.0.0 --port=$PORT
```

Add the API key in Render dashboard → *Environment*.

Both platforms’ free plans handle light prototype traffic (< 100 K req/mo).

---

## Using inside Relevance AI

### Register the MCP server

1. In the Relevance dashboard → *Workspace settings* → **MCP Servers**  
2. Click **Add MCP Server**  
   * URL: `https://<your-domain>/mcp`  
   * Auth: **None** (server already has the key)  
3. Save – the server’s tools are now available.

### Build a **Builder Agent**

1. Create a new agent, system prompt e.g.:

   ```
   You are the Builder Agent.
   Your job is to design, create and maintain other agents, knowledge-bases and
   workflows in this workspace using the provided MCP tools.
   Confirm destructive actions. Optimise for cost and accuracy.
   ```

2. Attach tool **Call MCP Remote Server** pointing to your MCP URL.  
3. Chat examples:

| Intent | Example prompt |
|--------|----------------|
| List | “List all agents and show their model names.” |
| Create | “Create a DOT‐Compliance FAQ agent using GPT-4o and attach KB `dot_docs`.” |
| Update | “Add the `summarise` tool to the DOT agent.” |
| Chain | “Generate a workflow that 1) collects carrier info 2) calls DOT agent 3) emails summary.” |
| Clean up | “Delete prototype-chatbot-v1.” |

The Builder Agent will call `create_agent`, `update_agent`, etc., and return the results in conversation.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `401 Unauthorized` | Wrong / missing API key | Verify `RELEVANCE_API_KEY`. |
| 502 / health-check fails | App crashed | Check platform logs; common: wrong start command. |
| Browser CORS error | Origin blocked | Set `CORS_ORIGINS="https://studio.relevance.ai"` etc. |
| Time-outs on large uploads | Hitting Relevance limits | Chunk documents / async retry. |

---

## Roadmap

- [ ] Async bulk-import endpoint for large KB ingestion  
- [ ] Typed response models (Pydantic v2)  
- [ ] Docker image on GHCR  
- [ ] GitHub Action for auto-deploy to Railway  

---

## License
MIT – see `LICENSE` for full text.

---

*Built with ❤️ to accelerate autonomous agent development on Relevance AI.*
