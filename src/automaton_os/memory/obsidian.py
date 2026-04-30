from datetime import datetime
from pathlib import Path
import re

from automaton_os.core.config import load_settings


def _safe_filename(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text[:100] or "untitled"


def _get_automaton_base_path() -> Path:
    settings = load_settings()

    obsidian = settings.get("obsidian", {})
    vault_path = obsidian.get("vault_path")
    automaton_folder = obsidian.get("automaton_folder", "Automaton")

    if not vault_path:
        raise RuntimeError(
            "Obsidian vault_path is not configured. "
            "Set OBSIDIAN_VAULT_PATH in .env or configs/settings.yaml."
        )

    base_path = Path(vault_path).expanduser().resolve() / automaton_folder
    base_path.mkdir(parents=True, exist_ok=True)

    return base_path


def save_markdown_note(folder: str, title: str, content: str) -> dict:
    base_path = _get_automaton_base_path()
    target_folder = (base_path / folder).resolve()
    target_folder.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{_safe_filename(title)}.md"
    path = target_folder / filename

    markdown = f"""# {title}

Created: {datetime.now().isoformat(timespec="seconds")}
Source: Automaton-OS

---

{content}
"""

    path.write_text(markdown, encoding="utf-8")

    return {
        "status": "saved",
        "path": str(path),
    }


def save_research_report(topic: str, content: str) -> dict:
    return save_markdown_note(
        folder="Research",
        title=f"Research - {topic}",
        content=content,
    )

def update_mission_index(logs: list[dict]) -> dict:
    base_path = _get_automaton_base_path()
    path = base_path / "Mission Index.md"

    lines = [
        "# Automaton Mission Index",
        "",
        "This file is automatically updated by Automaton-OS.",
        "",
        "## Recent Missions",
        "",
        "| ID | Created At | Status | Crew | Mission | Report |",
        "|---:|------------|--------|------|---------|--------|",
    ]

    for log in logs:
        log_id = log.get("id", "")
        created_at = log.get("created_at", "")
        status = log.get("status", "")
        crew_name = log.get("crew_name", "")
        mission = str(log.get("mission", "")).replace("|", "\\|")
        saved_path = log.get("saved_path") or ""

        if saved_path:
            report_link = f"[Open Report]({saved_path})"
        else:
            report_link = ""

        lines.append(
            f"| {log_id} | {created_at} | {status} | {crew_name} | {mission} | {report_link} |"
        )

    lines.extend([
        "",
        "## Notes",
        "",
        "- Newest missions appear first.",
        "- Reports are saved in the `Automaton/Research` folder.",
        "- This index is generated from the SQLite mission log.",
        "",
    ])

    path.write_text("\n".join(lines), encoding="utf-8")

    return {
        "status": "saved",
        "path": str(path),
    }


def update_mission_queue_index(queue_items: list[dict]) -> dict:
    base_path = _get_automaton_base_path()
    path = base_path / "Mission Queue.md"

    lines = [
        "# Automaton Mission Queue",
        "",
        "This file is automatically updated by Automaton-OS.",
        "",
        "## Linked Context",
        "",
        "- [[Mission Index]]",
        "- [[Automaton Project Status]]",
        "- [[Automaton Roadmap]]",
        "- [[Research Index]]",
        "",
        "## Queue Overview",
        "",
        "| ID | Priority | Status | Mission | Result Log ID |",
        "|---:|---------:|--------|---------|--------------:|",
    ]

    for item in queue_items:
        mission_id = item.get("id", "")
        priority = item.get("priority", "")
        status = item.get("status", "")
        mission = str(item.get("mission", "")).replace("|", "\\|")
        result_log_id = item.get("result_log_id") or ""

        mission_link = f"[[Missions/Mission {mission_id}|{mission}]]"

        lines.append(
            f"| {mission_id} | {priority} | {status} | {mission_link} | {result_log_id} |"
        )

    lines.extend([
        "",
        "## Status Meaning",
        "",
        "- `pending`: waiting to be processed",
        "- `running`: currently being processed",
        "- `completed`: finished successfully",
        "- `failed`: failed during execution",
        "",
        "## Notes",
        "",
        "- New missions are stored in SQLite.",
        "- This index is generated from the mission queue.",
        "- Mission detail notes can be expanded later.",
        "- Related reports are listed in [[Mission Index]].",
        "",
    ])

    path.write_text("\n".join(lines), encoding="utf-8")

    return {
        "status": "saved",
        "path": str(path),
    }


def write_automaton_note(filename: str, content: str) -> dict:
    base_path = _get_automaton_base_path()
    path = base_path / filename

    path.write_text(content, encoding="utf-8")

    return {
        "status": "saved",
        "path": str(path),
    }


def update_knowledge_graph_foundation() -> dict:
    saved_files = {}

    roadmap = """# Automaton Roadmap

This is the living roadmap for [[Automaton-OS]].

## Linked Context

- [[Mission Index]]
- [[Mission Queue]]
- [[Research Index]]
- [[Crew Index]]
- [[Agent Registry]]
- [[Model Provider Index]]

## Current Phase

**v0.1 — Local AI Company Foundation**

Current focus:
- Administrator Agent
- Research Crew
- Mission logging
- Mission queue
- Obsidian knowledge graph
- Cloud/local model routing

## Roadmap

### v0.1 — Research Company
- [x] Model router
- [x] Cloudflare provider through OpenAI-compatible adapter
- [x] Research Crew
- [x] Administrator Agent
- [x] Mission logs
- [x] Mission queue
- [x] Mission Index
- [x] Mission Queue Index
- [ ] Knowledge graph foundation
- [ ] Scheduled queue runner stabilization

### v0.2 — Knowledge Memory
- [ ] Better research index
- [ ] Mission detail notes
- [ ] Research tagging
- [ ] Obsidian graph links
- [ ] Knowledge review loop

### v0.3 — Coding Crew
- [ ] Evaluate Aider / OpenCode / OpenHands
- [ ] Architect Agent
- [ ] Patch Writer Agent
- [ ] Reviewer Agent
- [ ] Approval-based code changes

### v0.4 — Content Crew
- [ ] Idea Agent
- [ ] Script Writer Agent
- [ ] Video Planner Agent
- [ ] Content calendar

### v1.0 — Local AI Company
- [ ] Administrator can create/manage specialist agents
- [ ] Scheduled autonomous work
- [ ] Voice/text gateway
- [ ] Local dashboard
"""

    research_index = """# Research Index

This is the research hub for [[Automaton-OS]].

## Linked Context

- [[Automaton Roadmap]]
- [[Mission Index]]
- [[Mission Queue]]
- [[Research Crew]]
- [[Model Provider Index]]

## Research Areas

### Local AI Company Architecture
Related topics:
- local AI company
- multi-agent orchestration
- CrewAI
- LangGraph
- autonomous research

### Coding Agents
Related topics:
- Aider
- OpenCode
- OpenHands
- patch-based editing
- code review
- sandboxing

### Content Agents
Related topics:
- video scripts
- content planning
- YouTube research
- script generation
- creative workflows

### Memory and Knowledge
Related topics:
- Obsidian
- SQLite logs
- mission index
- mission queue
- knowledge graph

## Notes

Research reports are saved in the `Research/` folder.
"""

    crew_index = """# Crew Index

This note tracks the specialist crews in [[Automaton-OS]].

## Linked Context

- [[Automaton Roadmap]]
- [[Agent Registry]]
- [[Research Index]]
- [[Mission Queue]]

## Crews

### [[Research Crew]]

Status: implemented

Purpose:
- research topics
- analyze findings
- write final Markdown reports
- save reports to Obsidian

Agents:
- [[Research Agent]]
- [[Analyst Agent]]
- [[Report Writer Agent]]

### [[Coding Crew]]

Status: planned

Purpose:
- inspect codebases
- propose safe patches
- review implementation plans
- integrate with tools like Aider, OpenCode, or OpenHands

Agents:
- [[Architect Agent]]
- [[Coder Agent]]
- [[Reviewer Agent]]

### [[Content Crew]]

Status: planned

Purpose:
- generate content ideas
- write video scripts
- plan video structures
- create content calendars

Agents:
- [[Idea Agent]]
- [[Script Writer Agent]]
- [[Video Planner Agent]]
"""

    agent_registry = """# Agent Registry

This note tracks agents used by [[Automaton-OS]].

## Linked Context

- [[Automaton Roadmap]]
- [[Crew Index]]
- [[Research Crew]]
- [[Coding Crew]]
- [[Content Crew]]
- [[Model Provider Index]]

## Administrator

### [[Administrator Agent]]

Status: implemented

Responsibilities:
- receive missions
- decide which crew should handle the mission
- route unsupported crew missions to research first

## Research Crew Agents

### [[Research Agent]]

Status: implemented

Responsibilities:
- collect search results
- summarize findings
- avoid inventing unsupported facts

### [[Analyst Agent]]

Status: implemented

Responsibilities:
- compare research notes
- identify tradeoffs
- identify risks
- recommend direction

### [[Report Writer Agent]]

Status: implemented

Responsibilities:
- write final Markdown report
- prepare content for Obsidian

## Coding Crew Agents

### [[Architect Agent]]

Status: planned

### [[Coder Agent]]

Status: planned

### [[Reviewer Agent]]

Status: planned

## Content Crew Agents

### [[Idea Agent]]

Status: planned

### [[Script Writer Agent]]

Status: planned

### [[Video Planner Agent]]

Status: planned
"""

    model_provider_index = """# Model Provider Index

This note tracks model providers used by [[Automaton-OS]].

## Linked Context

- [[Automaton Roadmap]]
- [[Agent Registry]]
- [[Research Crew]]

## Model Router

Status: implemented

Purpose:
- let agents use different model profiles
- switch between local and cloud models by config
- avoid hardcoding Ollama or Cloudflare in agent logic

## Providers

### [[Ollama Provider]]

Status: implemented adapter, used later on high-end PC

Use case:
- local model execution
- privacy-first workflows
- local coding/research tasks

### [[Cloudflare Provider]]

Status: working through OpenAI-compatible adapter

Use case:
- cloud model access from lower-end devices
- fast testing without local GPU
- Cloudflare Workers AI / AI Gateway style routing

### [[OpenAI-Compatible Provider]]

Status: implemented

Use case:
- generic cloud API adapter
- Cloudflare
- OpenRouter
- other compatible endpoints

## Current Model Roles

Configured roles:
- default
- administrator
- researcher
- analyst
- writer
- local_test
"""

    research_crew = """# Research Crew

Part of [[Crew Index]] and [[Automaton-OS]].

## Status

Implemented.

## Purpose

The Research Crew handles research-style missions.

## Agents

- [[Research Agent]]
- [[Analyst Agent]]
- [[Report Writer Agent]]

## Flow

Mission
→ Administrator Agent
→ Research Crew
→ Research Agent
→ Analyst Agent
→ Report Writer Agent
→ Obsidian Research Report

## Related

- [[Research Index]]
- [[Mission Index]]
- [[Mission Queue]]
- [[Model Provider Index]]
"""

    automaton_os = """# Automaton-OS

Automaton-OS is a local AI company / Jarvis-like system.

## Linked Context

- [[Automaton Roadmap]]
- [[Mission Index]]
- [[Mission Queue]]
- [[Research Index]]
- [[Crew Index]]
- [[Agent Registry]]
- [[Model Provider Index]]

## Goal

Build an AI system that can:
- receive missions
- route work to specialist crews
- research autonomously
- save knowledge to Obsidian
- later integrate coding, content, voice, and local models

## Current MVP

v0.1 focuses on:
- Administrator Agent
- Research Crew
- Model Router
- Mission logs
- Mission queue
- Obsidian knowledge graph
"""

    files = {
        "Automaton-OS.md": automaton_os,
        "Automaton Roadmap.md": roadmap,
        "Research Index.md": research_index,
        "Crew Index.md": crew_index,
        "Agent Registry.md": agent_registry,
        "Model Provider Index.md": model_provider_index,
        "Research Crew.md": research_crew,
    }

    for filename, content in files.items():
        saved_files[filename] = write_automaton_note(filename, content)

    return {
        "status": "saved",
        "files": saved_files,
    }


def update_mission_detail_notes(queue_items: list[dict]) -> dict:
    base_path = _get_automaton_base_path()
    missions_folder = base_path / "Missions"
    missions_folder.mkdir(parents=True, exist_ok=True)

    saved_files = {}

    for item in queue_items:
        mission_id = item.get("id", "")
        mission = item.get("mission", "")
        status = item.get("status", "")
        priority = item.get("priority", "")
        result_log_id = item.get("result_log_id") or ""

        filename = f"Mission {mission_id}.md"
        path = missions_folder / filename

        content = f"""# Mission {mission_id}

## Linked Context

- [[Mission Queue]]
- [[Mission Index]]
- [[Automaton Roadmap]]
- [[Research Index]]
- [[Crew Index]]

## Mission Metadata

| Field | Value |
|---|---|
| Mission ID | {mission_id} |
| Status | {status} |
| Priority | {priority} |
| Result Log ID | {result_log_id} |

## Mission

{mission}

## Related Work

- Queue: [[Mission Queue]]
- Completed mission index: [[Mission Index]]
- Roadmap: [[Automaton Roadmap]]

## Notes

This mission detail note is automatically generated by Automaton-OS.
"""

        path.write_text(content, encoding="utf-8")

        saved_files[filename] = {
            "status": "saved",
            "path": str(path),
        }

    return {
        "status": "saved",
        "files": saved_files,
    }