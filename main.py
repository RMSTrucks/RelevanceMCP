import os
import logging
import requests
import contextlib
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import base64
import uvicorn
from typing import AsyncGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("relevance_ai_mcp")

# Load environment variables
load_dotenv()

# Get Relevance AI API key from environment variables
RELEVANCE_API_KEY = os.getenv("RELEVANCE_API_KEY")
if not RELEVANCE_API_KEY:
    logger.warning("RELEVANCE_API_KEY environment variable is not set")
else:
    # Log only the first 4 chars for debugging, keep rest masked
    logger.info("Relevance AI API key detected (token starts with %s****)",
                RELEVANCE_API_KEY[:4])

# Relevance AI API base URL
RELEVANCE_API_BASE_URL = os.getenv("RELEVANCE_API_BASE_URL", "https://api.relevanceai.com/v1")
logger.info("Using Relevance AI base URL: %s", RELEVANCE_API_BASE_URL)

# Detect PORT once so we can log it and also use it in __main__
PORT = int(os.getenv("PORT", 8000))
logger.info("Server will listen on port: %s", PORT)

# Initialize FastAPI app with lifespan context manager
app = FastAPI(title="Relevance AI MCP Server")

# Define lifespan context manager for startup/shutdown events
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup event code
    logger.info("=========================================================")
    logger.info("🚀 Relevance AI MCP Server STARTUP")
    logger.info("Listening on: 0.0.0.0:%s", PORT)
    logger.info("Tools registered: %s", ", ".join(TOOLS.keys()))
    logger.info("API key present: %s", "yes" if RELEVANCE_API_KEY else "no")
    logger.info("Base URL: %s", RELEVANCE_API_BASE_URL)
    logger.info("CORS Origins: %s", origins)
    logger.info("=========================================================")
    
    yield  # Server is running
    
    # Shutdown event code
    logger.info("Relevance AI MCP Server shutting down")

# Attach lifespan to app
app.router.lifespan_context = lifespan

# --------------------------------------------------------------------------- #
#                                CORS SETUP                                   #
# --------------------------------------------------------------------------- #
# Allow calls from browsers / other dashboards, etc.
origins_env = os.getenv("CORS_ORIGINS")  # comma-separated list or empty
origins = [o.strip() for o in origins_env.split(",")] if origins_env else ["*"]
logger.info("CORS allowed origins: %s", origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper function for making API requests to Relevance AI
def make_relevance_request(method, endpoint, data=None, params=None):
    """
    Make a request to the Relevance AI API
    
    Args:
        method: HTTP method (GET, POST, PUT, DELETE)
        endpoint: API endpoint (without base URL)
        data: Request body for POST/PUT requests
        params: Query parameters for GET requests
        
    Returns:
        API response as dictionary
    """
    if not RELEVANCE_API_KEY:
        logger.error("Attempted Relevance AI API call without RELEVANCE_API_KEY configured")
        return {"error": "RELEVANCE_API_KEY environment variable is not set"}
        
    url = f"{RELEVANCE_API_BASE_URL}/{endpoint.lstrip('/')}"
    headers = {
        "Authorization": f"Bearer {RELEVANCE_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    logger.info(f"Making {method} request to {endpoint}")
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            return {"error": f"Unsupported method: {method}"}
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        error_message = str(e)
        try:
            if hasattr(e, 'response') and e.response is not None:
                error_data = e.response.json()
                error_message = error_data.get('error', {}).get('message', str(e))
                logger.error(f"Relevance AI API error: {error_message}")
        except:
            logger.exception("Error parsing Relevance AI API error response")
        
        return {"error": error_message}

# ===== TOOL IMPLEMENTATIONS =====

# Agent Management Tools
def list_agents(limit=50, offset=0):
    """List all agents in your Relevance AI workspace"""
    params = {
        "limit": limit,
        "offset": offset
    }
    return make_relevance_request("GET", "agents", params=params)

def get_agent(agent_id):
    """Get details of a specific agent by ID"""
    return make_relevance_request("GET", f"agents/{agent_id}")

def create_agent(name, description=None, system_prompt=None, tools=None, knowledge_bases=None, model=None):
    """Create a new agent in Relevance AI"""
    data = {
        "name": name,
        "description": description or f"Agent created via MCP: {name}"
    }
    
    if system_prompt:
        data["system_prompt"] = system_prompt
        
    if tools:
        data["tools"] = tools
        
    if knowledge_bases:
        data["knowledge_bases"] = knowledge_bases
        
    if model:
        data["model"] = model
    
    return make_relevance_request("POST", "agents", data=data)

def update_agent(agent_id, name=None, description=None, system_prompt=None, tools=None, knowledge_bases=None, model=None):
    """Update an existing agent in Relevance AI"""
    data = {}
    
    if name:
        data["name"] = name
        
    if description:
        data["description"] = description
        
    if system_prompt:
        data["system_prompt"] = system_prompt
        
    if tools:
        data["tools"] = tools
        
    if knowledge_bases:
        data["knowledge_bases"] = knowledge_bases
        
    if model:
        data["model"] = model
    
    return make_relevance_request("PUT", f"agents/{agent_id}", data=data)

def delete_agent(agent_id):
    """Delete an agent from Relevance AI"""
    return make_relevance_request("DELETE", f"agents/{agent_id}")

# Knowledge Base Management Tools
def list_knowledge_bases(limit=50, offset=0):
    """List all knowledge bases in your Relevance AI workspace"""
    params = {
        "limit": limit,
        "offset": offset
    }
    return make_relevance_request("GET", "knowledge-bases", params=params)

def get_knowledge_base(kb_id):
    """Get details of a specific knowledge base by ID"""
    return make_relevance_request("GET", f"knowledge-bases/{kb_id}")

def create_knowledge_base(name, description=None, embedding_model=None):
    """Create a new knowledge base in Relevance AI"""
    data = {
        "name": name,
        "description": description or f"Knowledge base created via MCP: {name}"
    }
    
    if embedding_model:
        data["embedding_model"] = embedding_model
    
    return make_relevance_request("POST", "knowledge-bases", data=data)

def add_document_to_kb(kb_id, document, metadata=None):
    """Add a document to a knowledge base"""
    data = {
        "document": document,
        "metadata": metadata or {}
    }
    return make_relevance_request("POST", f"knowledge-bases/{kb_id}/documents", data=data)

def search_knowledge_base(kb_id, query, limit=10):
    """Search a knowledge base with a query"""
    data = {
        "query": query,
        "limit": limit
    }
    return make_relevance_request("POST", f"knowledge-bases/{kb_id}/search", data=data)

def delete_knowledge_base(kb_id):
    """Delete a knowledge base from Relevance AI"""
    return make_relevance_request("DELETE", f"knowledge-bases/{kb_id}")

# Workflow Configuration Tools
def list_workflows(limit=50, offset=0):
    """List all workflows in your Relevance AI workspace"""
    params = {
        "limit": limit,
        "offset": offset
    }
    return make_relevance_request("GET", "workflows", params=params)

def get_workflow(workflow_id):
    """Get details of a specific workflow by ID"""
    return make_relevance_request("GET", f"workflows/{workflow_id}")

def create_workflow(name, description=None, steps=None):
    """Create a new workflow in Relevance AI"""
    data = {
        "name": name,
        "description": description or f"Workflow created via MCP: {name}"
    }
    
    if steps:
        data["steps"] = steps
    
    return make_relevance_request("POST", "workflows", data=data)

def update_workflow(workflow_id, name=None, description=None, steps=None):
    """Update an existing workflow in Relevance AI"""
    data = {}
    
    if name:
        data["name"] = name
        
    if description:
        data["description"] = description
        
    if steps:
        data["steps"] = steps
    
    return make_relevance_request("PUT", f"workflows/{workflow_id}", data=data)

def delete_workflow(workflow_id):
    """Delete a workflow from Relevance AI"""
    return make_relevance_request("DELETE", f"workflows/{workflow_id}")

# Tool Management
def list_mcp_servers(limit=50, offset=0):
    """List all registered MCP servers in your Relevance AI workspace"""
    params = {
        "limit": limit,
        "offset": offset
    }
    return make_relevance_request("GET", "mcp-servers", params=params)

def register_mcp_server(name, url, description=None, auth_type=None, auth_token=None):
    """Register a new MCP server with Relevance AI"""
    data = {
        "name": name,
        "url": url,
        "description": description or f"MCP server registered via MCP: {name}"
    }
    
    if auth_type:
        data["auth_type"] = auth_type
        
    if auth_token:
        data["auth_token"] = auth_token
    
    return make_relevance_request("POST", "mcp-servers", data=data)

def get_mcp_server_tools(server_id):
    """Get all tools available on a registered MCP server"""
    return make_relevance_request("GET", f"mcp-servers/{server_id}/tools")

def unregister_mcp_server(server_id):
    """Unregister an MCP server from Relevance AI"""
    return make_relevance_request("DELETE", f"mcp-servers/{server_id}")

# Direct API Access
def relevance_api_call(method, endpoint, data=None, params=None):
    """Make a direct call to any Relevance AI API endpoint"""
    return make_relevance_request(method, endpoint, data=data, params=params)

# Tool registry - maps tool names to functions
TOOLS = {
    # Agent Management
    "list_agents": list_agents,
    "get_agent": get_agent,
    "create_agent": create_agent,
    "update_agent": update_agent,
    "delete_agent": delete_agent,
    
    # Knowledge Base Management
    "list_knowledge_bases": list_knowledge_bases,
    "get_knowledge_base": get_knowledge_base,
    "create_knowledge_base": create_knowledge_base,
    "add_document_to_kb": add_document_to_kb,
    "search_knowledge_base": search_knowledge_base,
    "delete_knowledge_base": delete_knowledge_base,
    
    # Workflow Configuration
    "list_workflows": list_workflows,
    "get_workflow": get_workflow,
    "create_workflow": create_workflow,
    "update_workflow": update_workflow,
    "delete_workflow": delete_workflow,
    
    # Tool Management
    "list_mcp_servers": list_mcp_servers,
    "register_mcp_server": register_mcp_server,
    "get_mcp_server_tools": get_mcp_server_tools,
    "unregister_mcp_server": unregister_mcp_server,
    
    # Direct API Access
    "relevance_api_call": relevance_api_call
}

# ===== API ENDPOINTS =====

@app.post("/mcp")
async def mcp_endpoint(request: Request):
    """
    MCP-compatible endpoint that handles tool calls
    Compatible with Relevance AI's "Call MCP Remote Server Tool"
    """
    try:
        # Parse JSON request
        body = await request.json()
        
        # Extract tool name and arguments
        tool_name = body.get("name")
        arguments = body.get("arguments", {})
        
        if not tool_name:
            return {"error": "Missing required field: name"}
        
        logger.info(f"Tool call: {tool_name} with args: {arguments}")
        
        if tool_name not in TOOLS:
            return {"error": f"Tool '{tool_name}' not found"}
        
        # Call the tool function with arguments
        result = TOOLS[tool_name](**arguments)
        return {"result": result}
    except Exception as e:
        logger.exception(f"Error processing request")
        return {"error": str(e)}

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "ok",
        "message": "Relevance AI MCP Server is running",
        "version": "1.0.0"
    }

# Root endpoint with documentation
@app.get("/")
async def root():
    """Root endpoint with API documentation"""
    return {
        "name": "Relevance AI MCP Server",
        "description": "API server for Relevance AI integration via MCP",
        "endpoints": {
            "/mcp": "MCP-compatible endpoint for tool calls",
            "/health": "Health check endpoint",
            "/tools": "List available tools"
        },
        "tools": list(TOOLS.keys()),
        "documentation": "See README.md for usage details"
    }

# List available tools
@app.get("/tools")
async def list_tools():
    """List all available tools"""
    tool_info = {}
    for name, func in TOOLS.items():
        tool_info[name] = {
            "description": func.__doc__
        }
    
    return {
        "tools": list(TOOLS.keys()),
        "tool_info": tool_info
    }

if __name__ == "__main__":
    # Local / manual run
    logger.info(
        "Running under __main__. Starting Uvicorn on 0.0.0.0:%s (development mode)",
        PORT,
    )
    uvicorn.run(app, host="0.0.0.0", port=PORT)
