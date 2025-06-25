# 📅 Cal.com Bookings with Context7 MCP and Cursor

Welcome to this hands-on mini-project where you'll use **Context7 MCP Server** to integrate with **Cal.com** — no coding required! By the end, you'll be able to schedule bookings in Cal.com directly from **Cursor**, using intelligent agent communication.

## ✅ Prerequisites

Before we begin, make sure you've completed the following setup:

1. **Create a Cal.com Account**  
   Sign up at [https://cal.com](https://cal.com) and complete your profile setup.

2. **Generate a Cal.com API Key**  
   Go to your Cal.com dashboard → *Settings* → *API* → *Create API Key*.  
   Save this key securely — you'll need it soon.

3. **Create Sample Bookings**  
   Add a few test bookings in your Cal.com account so you can later interact with them through the MCP agent.

## 🔌 What We're Building

You'll connect the **Context7 MCP Server** to Cursor, allowing intelligent agents to:

- Access your Cal.com bookings.
- Create new bookings via agent commands — **without writing code**.
- Seamlessly interact with your scheduling data in a conversational, interactive way.

To connect to the MCP server in Cursor, use the following line of code:

```bash
{
  "mcpServers": {
    "context7": {
      "url": "https://mcp.context7.com/mcp"
    }
  }
}
```

For troubleshooting you might install it also manually:

```bash
npx -y @upstash/context7-mcp@latest
```

and replace in Cursor Settings with:

```json
{
  "mcpServers": {
    "context7-cloud": {
      "url": "https://mcp.context7.com/mcp",
      "description": "Context7 cloud MCP server",
      "timeout": 30000,
      "retries": 3
    },
    "context7-local": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"],
      "description": "Local MCP server (runs Cal.com docs you ingested)"
    }
  }
}
```

## 🚀 Let's Get Started

Once your environment is ready, you'll connect the Cal.com tool to the Context7 MCP server, and try creating a booking from Cursor by simply asking your agent.

Have fun exploring the power of AI-enhanced automation — and remember: no lines of code, just context!

---
