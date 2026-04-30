import time
from pathlib import Path

import yaml
from apscheduler.schedulers.background import BackgroundScheduler
from rich import print

from automaton_os.core.administrator import AdministratorAgent
from automaton_os.memory.mission_log import (
    get_next_pending_mission,
    update_queued_mission_status,
)


def load_scheduled_missions(path: str = "configs/missions.yaml") -> list[dict]:
    config_path = Path(path)

    if not config_path.exists():
        raise FileNotFoundError(f"Mission config not found: {path}")

    with config_path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}

    return data.get("scheduled_missions", [])


def run_scheduled_mission(name: str, mission: str) -> None:
    print(f"\n[bold blue]Running scheduled mission:[/bold blue] {name}")
    print(f"[dim]{mission}[/dim]")

    administrator = AdministratorAgent()
    result = administrator.run_mission(mission)

    print("[bold green]Scheduled mission completed.[/bold green]")
    print(
        {
            "mission": result.get("mission"),
            "administrator_decision": result.get("administrator_decision"),
            "saved": result.get("crew_result", {}).get("saved"),
            "mission_log": result.get("mission_log"),
        }
    )


def run_scheduler(config_path: str = "configs/missions.yaml") -> None:
    scheduled_missions = load_scheduled_missions(config_path)

    enabled_missions = [
        mission_config
        for mission_config in scheduled_missions
        if mission_config.get("enabled", False)
    ]

    if not enabled_missions:
        print("[bold yellow]No enabled scheduled missions found.[/bold yellow]")
        return

    scheduler = BackgroundScheduler()

    for mission_config in enabled_missions:
        name = mission_config["name"]
        mission = mission_config["mission"]
        interval_seconds = int(mission_config.get("interval_seconds", 300))

        scheduler.add_job(
            run_scheduled_mission,
            trigger="interval",
            seconds=interval_seconds,
            args=[name, mission],
            id=name,
            replace_existing=True,
            max_instances=1,
        )

        print(
            f"[bold cyan]Scheduled:[/bold cyan] {name} "
            f"every {interval_seconds} seconds"
        )

    scheduler.start()

    print("\n[bold green]Automaton-OS scheduler started.[/bold green]")
    print("[dim]Press Ctrl+C to stop.[/dim]")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[bold yellow]Stopping scheduler...[/bold yellow]")
        scheduler.shutdown()
        print("[bold green]Scheduler stopped.[/bold green]")


def run_next_queued_mission() -> None:
    next_mission = get_next_pending_mission()

    if next_mission["status"] == "empty":
        print("[bold yellow]No pending queued missions.[/bold yellow]")
        return

    queued = next_mission["mission"]
    mission_id = queued["id"]
    mission_text = queued["mission"]

    print(f"\n[bold blue]Running queued mission #{mission_id}[/bold blue]")
    print(f"[dim]{mission_text}[/dim]")

    update_queued_mission_status(
        mission_id=mission_id,
        status="running",
    )

    administrator = AdministratorAgent()

    try:
        result = administrator.run_mission(mission_text)

        mission_log = result.get("mission_log", {})
        result_log_id = mission_log.get("id")

        update_queued_mission_status(
            mission_id=mission_id,
            status="completed",
            result_log_id=result_log_id,
        )

        print("[bold green]Queued mission completed.[/bold green]")
        print({
            "mission_id": mission_id,
            "mission_log": mission_log,
            "saved": result.get("crew_result", {}).get("saved"),
        })

    except Exception as error:
        update_queued_mission_status(
            mission_id=mission_id,
            status="failed",
        )

        print("[bold red]Queued mission failed.[/bold red]")
        print(str(error))


def run_queue_scheduler(interval_seconds: int = 300) -> None:
    scheduler = BackgroundScheduler()

    scheduler.add_job(
        run_next_queued_mission,
        trigger="interval",
        seconds=interval_seconds,
        id="mission_queue_runner",
        replace_existing=True,
        max_instances=1,
    )

    print(
        f"[bold cyan]Scheduled mission queue runner every {interval_seconds} seconds[/bold cyan]"
    )

    scheduler.start()

    print("\n[bold green]Automaton-OS queue scheduler started.[/bold green]")
    print("[dim]Press Ctrl+C to stop.[/dim]")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[bold yellow]Stopping queue scheduler...[/bold yellow]")
        scheduler.shutdown()
        print("[bold green]Queue scheduler stopped.[/bold green]")