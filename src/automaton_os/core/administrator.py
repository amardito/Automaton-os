import json
import re

from automaton_os.core.model_router import ModelRouter
from automaton_os.crews.research_crew import ResearchCrew
from automaton_os.memory.mission_log import save_mission_log


def extract_json(raw: str) -> dict:
    raw = raw.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    code_block_match = re.search(
        r"```(?:json)?\s*(\{.*?\})\s*```",
        raw,
        re.DOTALL,
    )

    if code_block_match:
        return json.loads(code_block_match.group(1).strip())

    object_match = re.search(r"\{.*\}", raw, re.DOTALL)

    if object_match:
        return json.loads(object_match.group(0).strip())

    raise ValueError(f"No valid JSON found in model output: {raw}")


class AdministratorAgent:
    def __init__(self) -> None:
        self.router = ModelRouter()

    def decide(self, mission: str) -> dict:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are the Administrator Agent of Automaton-OS. "
                    "You decide which specialist crew should handle a mission. "
                    "Return only valid JSON."
                ),
            },
            {
                "role": "user",
                "content": f"""
Mission:
{mission}

Available crews:
- research_crew: use for research, investigation, comparison, strategy, architecture study, market study, technical study.
- coding_crew: not implemented yet.
- content_crew: not implemented yet.

Return only JSON in this exact format:
{{
  "crew": "research_crew",
  "task": "clear task for the crew",
  "reason": "short reason why this crew is selected"
}}

Rules:
- If the mission asks to research, compare, investigate, analyze, study, or find best architecture, use research_crew.
- If a needed crew is not implemented yet, route to research_crew to research how to do it.
- Do not use markdown.
- Do not explain outside JSON.
""",
            },
        ]

        raw = self.router.chat("administrator", messages)

        try:
            decision = extract_json(raw)
        except Exception:
            decision = {
                "crew": "research_crew",
                "task": mission,
                "reason": "Fallback: administrator output was invalid, so route to research crew.",
            }

        return self.normalize_decision(decision, mission)

    def normalize_decision(self, decision: dict, mission: str) -> dict:
        crew = decision.get("crew", "research_crew")

        allowed_crews = {
            "research_crew",
            "coding_crew",
            "content_crew",
        }

        if crew not in allowed_crews:
            crew = "research_crew"

        if crew in {"coding_crew", "content_crew"}:
            return {
                "crew": "research_crew",
                "task": f"Research how to handle this future mission safely: {mission}",
                "reason": f"{crew} is not implemented yet, so research_crew will research the approach first.",
            }

        return {
            "crew": crew,
            "task": decision.get("task", mission),
            "reason": decision.get("reason", "No reason provided."),
        }

    def run_mission(self, mission: str) -> dict:
        decision = self.decide(mission)

        if decision["crew"] == "research_crew":
            crew = ResearchCrew()
            result = crew.run(decision["task"])

            saved = result.get("saved", {})
            saved_path = saved.get("path")

            mission_log = save_mission_log(
                mission=mission,
                status="completed",
                administrator_decision=decision,
                crew_name="research_crew",
                saved_path=saved_path,
                result_summary=f"Research report saved to {saved_path}",
            )

            return {
                "mission": mission,
                "administrator_decision": decision,
                "crew_result": result,
                "mission_log": mission_log,
            }

        mission_log = save_mission_log(
            mission=mission,
            status="failed",
            administrator_decision=decision,
            crew_name=decision.get("crew"),
            saved_path=None,
            result_summary=f"Crew is not implemented yet: {decision['crew']}",
        )

        return {
            "mission": mission,
            "administrator_decision": decision,
            "mission_log": mission_log,
            "error": f"Crew is not implemented yet: {decision['crew']}",
        }