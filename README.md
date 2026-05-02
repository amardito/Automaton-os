# Automaton-OS

Automaton-OS is a local AI company / Jarvis-like multi-agent system.

The goal is to build an AI system that can receive missions, route work to specialist crews, research autonomously, save knowledge into Obsidian, and later support coding agents, content agents, local models, voice, and richer interfaces.

## Current Version

```text
Automaton-OS v0.1
Local Research Company MVP
```

## Current Capabilities

- Model routing between local and cloud providers
- Cloudflare support through OpenAI-compatible API
- Ollama-ready local provider
- Administrator Agent
- Role-based Research Crew
- Research Agent
- Analyst Agent
- Report Writer Agent
- Mission logging with SQLite
- Mission queue
- Queue scheduler
- Obsidian research reports
- Obsidian Mission Index
- Obsidian Mission Queue
- Obsidian knowledge graph foundation
- Mission detail notes
- Auto-refresh Research Index

## Architecture

```text
User Mission
    ↓
Administrator Agent
    ↓
Research Crew
    ↓
Research Agent → Analyst Agent → Report Writer Agent
    ↓
Obsidian Research Report
    ↓
SQLite Mission Log
    ↓
Mission Index / Queue / Knowledge Graph
```

## Project Structure

```text
Automaton-OS/
├── configs/
│   ├── settings.yaml
│   ├── missions.yaml
│   └── agents.yaml
├── docs/
│   ├── ARCHITECTURE.md
│   └── COMMANDS.md
├── memory/
│   └── automaton_os.db
├── src/
│   └── automaton_os/
│       ├── core/
│       │   ├── administrator.py
│       │   ├── config.py
│       │   ├── model_router.py
│       │   └── scheduler.py
│       ├── crews/
│       │   └── research_crew.py
│       ├── memory/
│       │   ├── mission_log.py
│       │   └── obsidian.py
│       ├── providers/
│       │   ├── base.py
│       │   ├── ollama.py
│       │   └── openai_compatible.py
│       ├── tools/
│       │   └── web_search.py
│       └── main.py
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

## Setup

Create a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

Install the project:

```powershell
python -m pip install --upgrade pip
python -m pip install -e .
```

Copy the environment file:

```powershell
copy .env.example .env
```

Edit `.env`:

```env
OBSIDIAN_VAULT_PATH=C:/Users/your-user/Documents/Obsidian/MyVault

CLOUDFLARE_ACCOUNT_ID=your_cloudflare_account_id
CLOUDFLARE_API_TOKEN=your_cloudflare_api_token
```

## Model Providers

Automaton-OS supports model routing.

Current provider types:

```text
ollama
openai_compatible
```

Cloudflare Workers AI can be used through the `openai_compatible` provider.

Example `configs/settings.yaml`:

```yaml
models:
  default:
    provider: openai_compatible
    model: "@cf/meta/llama-3.1-8b-instruct"

  administrator:
    provider: openai_compatible
    model: "@cf/meta/llama-3.1-8b-instruct"

  researcher:
    provider: openai_compatible
    model: "@cf/meta/llama-3.1-8b-instruct"

  analyst:
    provider: openai_compatible
    model: "@cf/meta/llama-3.1-8b-instruct"

  writer:
    provider: openai_compatible
    model: "@cf/meta/llama-3.1-8b-instruct"

  local_test:
    provider: ollama
    model: "qwen2.5-coder:7b"

providers:
  openai_compatible:
    base_url: "https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_ACCOUNT_ID}/ai/v1"
    api_key: "${CLOUDFLARE_API_TOKEN}"

  ollama:
    base_url: "http://localhost:11434"
```

## Commands

Check a model profile:

```powershell
python -m automaton_os check-model --profile default
```

Run the Research Crew directly:

```powershell
python -m automaton_os run-research --topic "Best architecture for a local AI company"
```

Run a mission through the Administrator Agent:

```powershell
python -m automaton_os run-mission --mission "Research how Automaton-OS should organize research, coding, and content crews"
```

List mission logs:

```powershell
python -m automaton_os list-missions --limit 5
```

Queue a mission:

```powershell
python -m automaton_os queue-mission --mission "Research safe coding agent integration" --priority 1
```

List queued missions:

```powershell
python -m automaton_os list-queue
```

Run the queue scheduler:

```powershell
python -m automaton_os run-queue-scheduler --interval 900 --max-runs 5 --stop-when-empty
```

Refresh all Obsidian indexes:

```powershell
python -m automaton_os refresh-obsidian
```

Refresh the Research Index only:

```powershell
python -m automaton_os refresh-research-index
```

Refresh the Mission Queue Index only:

```powershell
python -m automaton_os refresh-queue-index
```

Refresh the knowledge graph foundation:

```powershell
python -m automaton_os refresh-knowledge-graph
```

## Obsidian Output

Automaton-OS creates notes inside:

```text
ObsidianVault/Automaton/
```

Generated notes include:

```text
Automaton-OS.md
Automaton Roadmap.md
Mission Index.md
Mission Queue.md
Research Index.md
Crew Index.md
Agent Registry.md
Model Provider Index.md
Research Crew.md
Missions/Mission <id>.md
Research/<research report>.md
```

## Recommended Safe Queue Run

For overnight research:

```powershell
python -m automaton_os run-queue-scheduler --interval 900 --max-runs 5 --stop-when-empty
```

Meaning:

```text
- check queue every 15 minutes
- run at most 5 missions
- stop if queue is empty
```

## Roadmap

### v0.1 — Local Research Company MVP

- [x] Project scaffold
- [x] Model router
- [x] Cloudflare/OpenAI-compatible provider
- [x] Ollama provider
- [x] Administrator Agent
- [x] Research Crew
- [x] Mission logs
- [x] Mission queue
- [x] Queue scheduler
- [x] Obsidian Mission Index
- [x] Obsidian Mission Queue
- [x] Obsidian knowledge graph foundation
- [x] Mission detail notes
- [x] Auto-refresh Research Index
- [x] Basic autonomous queue workflow
- [ ] Config validation / health check
- [ ] v0.1 release checkpoint

### v0.2 — Knowledge Memory

- Better research indexing
- Mission detail enrichment
- Research tagging
- Knowledge review loop

### v0.3 — Coding Crew

- Evaluate Aider / OpenCode / OpenHands
- Architect Agent
- Patch Writer Agent
- Reviewer Agent
- Approval-based code changes

### v0.4 — Content Crew

- Idea Agent
- Script Writer Agent
- Video Planner Agent
- Content calendar

### v1.0 — Local AI Company

- Administrator can create/manage specialist agents
- Scheduled autonomous work
- Voice/text gateway
- Local dashboard

## Status

Automaton-OS is currently experimental.

Do not give it unrestricted file, terminal, desktop, or credential access until stronger safety controls are implemented.
