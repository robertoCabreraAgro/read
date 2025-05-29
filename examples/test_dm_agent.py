"""Simple test script for DmAgent.
Run after executing populate_db.py to ensure the database has data."""

from agent.dm_agent import DmAgent

if __name__ == "__main__":
    agent = DmAgent()
    if agent.dm_guidelines:
        print(f"Guidelines loaded: {agent.dm_guidelines.name}")
    else:
        print("No DM guidelines found.")

    events = agent.get_recent_campaign_events(limit=2)
    if events:
        print("Recent events:")
        for ev in events:
            end = f"-{ev.day_range_end}" if ev.day_range_end and ev.day_range_end != ev.day_range_start else ""
            print(f"  - {ev.title} (Days {ev.day_range_start}{end})")
    else:
        print("No recent events found.")
