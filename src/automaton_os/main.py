import argparse
from rich import print

from automaton_os.core.model_router import ModelRouter
from automaton_os.crews.research_crew import ResearchCrew
from automaton_os.core.administrator import AdministratorAgent
from automaton_os.core.scheduler import run_scheduler, run_queue_scheduler
from automaton_os.memory.mission_log import (
    list_mission_logs,
    add_queued_mission,
    list_queued_missions,
    refresh_mission_queue_index,
)
from automaton_os.memory.obsidian import update_knowledge_graph_foundation


def check_model(profile: str) -> None:
    router = ModelRouter()

    response = router.chat(
        profile,
        [
            {
                "role": "user",
                "content": "Say hello as Automaton OS in one short sentence.",
            }
        ],
    )

    print("[bold green]Model response:[/bold green]")
    print(response)


def run_research(topic: str) -> None:
    crew = ResearchCrew()
    result = crew.run(topic)

    print("[bold green]Research completed.[/bold green]")
    print(
        {
            "topic": result["topic"],
            "saved": result["saved"],
        }
    )


def run_mission(mission: str) -> None:
    administrator = AdministratorAgent()
    result = administrator.run_mission(mission)

    print("[bold green]Mission completed.[/bold green]")
    print(
        {
            "mission": result["mission"],
            "administrator_decision": result["administrator_decision"],
            "saved": result.get("crew_result", {}).get("saved"),
            "mission_log": result.get("mission_log"),
        }
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="automaton_os",
        description="Automaton-OS local AI company command line interface.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    check_model_parser = subparsers.add_parser(
        "check-model",
        help="Check whether a model profile can respond.",
    )
    check_model_parser.add_argument(
        "--profile",
        default="default",
        help="Model profile name from configs/settings.yaml.",
    )

    research_parser = subparsers.add_parser(
        "run-research",
        help="Run the Research Crew directly on a topic.",
    )
    research_parser.add_argument(
        "--topic",
        required=True,
        help="Research topic.",
    )

    mission_parser = subparsers.add_parser(
        "run-mission",
        help="Give a mission to the Administrator Agent.",
    )
    mission_parser.add_argument(
        "--mission",
        required=True,
        help="Mission for the Administrator Agent.",
    )

    logs_parser = subparsers.add_parser(
        "list-missions",
        help="List recent mission logs.",
    )
    logs_parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Number of mission logs to show.",
    )

    scheduler_parser = subparsers.add_parser(
        "run-scheduler",
        help="Run scheduled autonomous missions.",
    )
    scheduler_parser.add_argument(
        "--config",
        default="configs/missions.yaml",
        help="Path to scheduled missions config.",
    )

    queue_add_parser = subparsers.add_parser(
        "queue-mission",
        help="Add a mission to the pending mission queue.",
    )
    queue_add_parser.add_argument(
        "--mission",
        required=True,
        help="Mission text to add to the queue.",
    )
    queue_add_parser.add_argument(
        "--priority",
        type=int,
        default=3,
        help="Mission priority. 1 is highest, 5 is lowest.",
    )

    queue_list_parser = subparsers.add_parser(
        "list-queue",
        help="List queued missions.",
    )
    queue_list_parser.add_argument(
        "--status",
        default=None,
        help="Optional status filter: pending, running, completed, failed.",
    )
    queue_list_parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Number of queued missions to show.",
    )

    queue_scheduler_parser = subparsers.add_parser(
        "run-queue-scheduler",
        help="Run pending queued missions on an interval.",
    )
    queue_scheduler_parser.add_argument(
        "--interval",
        type=int,
        default=300,
        help="Interval in seconds between queue checks.",
    )

    queue_index_parser = subparsers.add_parser(
        "refresh-queue-index",
        help="Refresh the Obsidian Mission Queue index.",
    )
    queue_index_parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Number of queued missions to include.",
    )

    graph_parser = subparsers.add_parser(
        "refresh-knowledge-graph",
        help="Create or update Obsidian knowledge graph foundation notes.",
    )

    args = parser.parse_args()

    if args.command == "check-model":
        check_model(args.profile)
    elif args.command == "run-research":
        run_research(args.topic)
    elif args.command == "run-mission":
        run_mission(args.mission)
    elif args.command == "list-missions":
        logs = list_mission_logs(limit=args.limit)
        print("[bold cyan]Recent mission logs:[/bold cyan]")
        print(logs)
    elif args.command == "run-scheduler":
        run_scheduler(config_path=args.config)
    elif args.command == "queue-mission":
        result = add_queued_mission(
            mission=args.mission,
            priority=args.priority,
        )
        print("[bold green]Queue result:[/bold green]")
        print(result)
    elif args.command == "list-queue":
        result = list_queued_missions(
            status=args.status,
            limit=args.limit,
        )
        print("[bold cyan]Mission queue:[/bold cyan]")
        print(result)
    elif args.command == "run-queue-scheduler":
        run_queue_scheduler(interval_seconds=args.interval)
    elif args.command == "refresh-queue-index":
        result = refresh_mission_queue_index(limit=args.limit)
        print("[bold green]Mission queue index refreshed:[/bold green]")
        print(result)
    elif args.command == "refresh-knowledge-graph":
        result = update_knowledge_graph_foundation()
        print("[bold green]Knowledge graph foundation refreshed:[/bold green]")
        print(result)


if __name__ == "__main__":
    main()