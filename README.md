# Automaton OS

Automaton OS is a local AI company / Jarvis-like system prototype.

The goal is to run an Administrator Agent with specialist crews that can research, analyze, write reports, save knowledge into Obsidian, and later integrate coding agents, content agents, voice, and always-on scheduling.

## Current MVP

**v0.1: Local Research Company**

Flow:

```text
You give a research topic
  -> Research Agent gathers findings
  -> Analyst Agent evaluates findings
  -> Report Writer Agent creates Markdown report
  -> Report is saved into Obsidian
```

## Key requirements

- Supports local models through Ollama.
- Supports cloud/OpenAI-compatible providers.
- Supports Cloudflare Workers AI / AI Gateway style configuration.
- Saves knowledge into Obsidian.
- Keeps project ready for future multi-agent crews.

## Project structure

```text
Automaton-OS/
├── configs/
│   ├── settings.yaml
│   ├── agents.yaml
│   └── missions.yaml
├── src/automaton_os/
│   ├── core/
│   │   ├── config.py
│   │   └── model_router.py
│   ├── providers/
│   │   ├── base.py
│   │   ├── ollama.py
│   │   └── openai_compatible.py
│   ├── crews/
│   │   └── research_crew.py
│   ├── tools/
│   │   └── web_search.py
│   ├── memory/
│   │   └── obsidian.py
│   └── main.py
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

## Setup

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

Copy environment file:

```powershell
copy .env.example .env
```

Edit `.env` and set your Obsidian vault path:

```env
OBSIDIAN_VAULT_PATH=C:/Users/Amar/Documents/Obsidian/MyVault
```

## Ollama setup

Make sure Ollama is running and the configured model exists:

```powershell
ollama pull qwen2.5-coder:7b
ollama run qwen2.5-coder:7b
```

Then test model routing:

```powershell
python -m automaton_os check-model --profile default
```

Or with the installed command:

```powershell
automaton check-model --profile default
```

## Run research crew

```powershell
python -m automaton_os run-research --topic "How to build a local Claude Code-like agent using Ollama"
```

Output will be saved to:

```text
<Your Obsidian Vault>/Automaton/Research/
```

## Model routing

Model profiles are configured in `configs/settings.yaml`.

Example local model:

```yaml
models:
  research:
    provider: "ollama"
    model: "qwen2.5-coder:7b"
```

Example Cloudflare-style model:

```yaml
models:
  research:
    provider: "cloudflare"
    model: "@cf/meta/llama-3.1-8b-instruct"
```

Then set this in `.env`:

```env
CLOUDFLARE_ACCOUNT_ID=your_account_id
CLOUDFLARE_API_TOKEN=your_token
```

## Roadmap

```text
v0.1  Local research crew
v0.2  Scheduler for autonomous research while you sleep
v0.3  Obsidian memory indexing
v0.4  Coding agent integration: Aider / OpenCode / OpenHands
v0.5  Content crew: scripts, video ideas, articles
v0.6  Voice/text interface
v0.7  Local dashboard
v1.0  Administrator Agent that creates/manages specialist agents
```
