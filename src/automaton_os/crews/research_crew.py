from automaton_os.core.model_router import ModelRouter
from automaton_os.tools.web_search import web_search
from automaton_os.memory.obsidian import save_research_report


class ResearchCrew:
    def __init__(self) -> None:
        self.router = ModelRouter()

    def run(self, topic: str) -> dict:
        research_results = web_search(topic, max_results=5)

        research_notes = self._research(topic, research_results)
        analysis = self._analyze(topic, research_notes)
        report = self._write_report(topic, research_notes, analysis)

        saved = save_research_report(topic=topic, content=report)

        return {
            "topic": topic,
            "research_notes": research_notes,
            "analysis": analysis,
            "report": report,
            "saved": saved,
        }

    def _research(self, topic: str, research_results: list[dict]) -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are the Research Agent in Automaton-OS. "
                    "Your job is to collect and summarize useful findings from search results. "
                    "Do not invent facts. Use only the provided results."
                ),
            },
            {
                "role": "user",
                "content": f"""
Research topic:
{topic}

Search results:
{research_results}

Create concise research notes.

Format:
## Raw Research Notes
- Key finding
- Key finding

## Useful Sources
- Title: URL
""",
            },
        ]

        return self.router.chat("researcher", messages)

    def _analyze(self, topic: str, research_notes: str) -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are the Analyst Agent in Automaton-OS. "
                    "Your job is to evaluate research notes, compare options, identify risks, "
                    "and recommend a practical direction."
                ),
            },
            {
                "role": "user",
                "content": f"""
Topic:
{topic}

Research notes:
{research_notes}

Analyze the findings.

Format:
## Analysis
- ...

## Tradeoffs
- ...

## Risks
- ...

## Best Direction
- ...
""",
            },
        ]

        return self.router.chat("analyst", messages)

    def _write_report(self, topic: str, research_notes: str, analysis: str) -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are the Report Writer Agent in Automaton-OS. "
                    "Your job is to write clear Markdown reports for the Obsidian knowledge vault."
                ),
            },
            {
                "role": "user",
                "content": f"""
Topic:
{topic}

Research notes:
{research_notes}

Analysis:
{analysis}

Write the final Markdown report.

Format:
# Research Report: {topic}

## Summary

## Key Findings

## Analysis

## Recommended Direction

## Next Actions

## Sources
""",
            },
        ]

        return self.router.chat("writer", messages)