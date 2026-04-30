# Automaton OS Architecture

## Goal

Build a local AI company / Jarvis-like system.

## Main components

```text
YOU
  -> Automaton Administrator
  -> Specialist Crews
  -> Model Router
  -> Tools
  -> Memory / Obsidian
```

## First MVP

The first MVP is a local research company:

```text
Administrator activates Research Crew
  -> Research topic
  -> Gather findings
  -> Analyze findings
  -> Write report
  -> Save report to Obsidian
```

## Model Router

Agents do not call Ollama or cloud models directly.
They call `ModelRouter`, which chooses a provider based on config.

Supported provider pattern:

```text
model profile -> provider -> model name
```

Examples:

```text
research -> ollama -> qwen2.5-coder:7b
research -> cloudflare -> @cf/meta/llama-3.1-8b-instruct
writer -> openai_compatible -> some-provider/model
```
