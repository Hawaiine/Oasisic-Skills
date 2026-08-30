# Firecrawl MCP Setup Reference

Session-specific setup details for Firecrawl CLI + MCP integration with Hermes Agent.

## Quick Install

```bash
npx -y firecrawl-cli@latest init --all --browser
```

If browser auth times out, set the API key manually in `.env`:

```bash
# .env (under $HERMES_HOME)
FIRECRAWL_API_KEY=fc-...
```

## API Key Management

| Source | Value | Status |
|--------|-------|--------|
| User-provided session key | `fc-a1dcd4606bcb43129f52805acc5ed976` | ❌ Invalid token |
| User-provided second key | `fc-eba1df752c0f44db9c19a4aab45265e3` | ✅ Valid (this session) |

Keyless free tier (Path F) also works for search, scrape, and interact — no API key needed, but rate-limited.

## MCP Server

```bash
# Add Firecrawl MCP (non-interactive via stdin piping)
hermes mcp add firecrawl --url https://mcp.firecrawl.dev/v2/mcp
# Then pipe: y\n{api_key}\ny\n  (auth yes / key / enable all tools yes)
```

### 26 Tools Available

- **Scraping**: `firecrawl_scrape`, `firecrawl_parse`
- **Search**: `firecrawl_search`, `firecrawl_search_feedback`
- **Crawl**: `firecrawl_crawl`, `firecrawl_check_crawl_status`, `firecrawl_map`
- **Extract**: `firecrawl_extract`
- **Agent**: `firecrawl_agent`, `firecrawl_agent_status`
- **Interact**: `firecrawl_interact`, `firecrawl_interact_stop`
- **Feedback**: `firecrawl_feedback`
- **Monitors** (8): `firecrawl_monitor_create/list/get/update/delete/run/checks/check`
- **Research** (5): `firecrawl_research_search_papers/inspect_paper/related_papers/read_paper/search_github`

## Verification

```bash
mkdir -p .firecrawl
firecrawl --status
firecrawl scrape "https://firecrawl.dev" -o .firecrawl/install-check.md
```

## Keyless Free Tier (Fallback)

When no API key is available, unset `FIRECRAWL_API_KEY` and use:

```bash
unset FIRECRAWL_API_KEY
npx -y firecrawl-cli@latest scrape "https://firecrawl.dev"
```

MCP endpoint: `https://mcp.firecrawl.dev/v2/mcp` (also works keyless)

## Config Shape (config.yaml)

```yaml
mcp_servers:
  firecrawl:
    url: https://mcp.firecrawl.dev/v2/mcp
    headers:
      Authorization: Bearer ${FIRECRAWL_API_KEY}
    enabled: true
```

## Docs

- API reference: https://docs.firecrawl.dev
- Skills repo: https://github.com/firecrawl/skills
- Workflows: https://github.com/firecrawl/firecrawl-workflows
