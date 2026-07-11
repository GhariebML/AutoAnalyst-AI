import json

log_file = r"C:\Users\Admin\.gemini\antigravity\brain\95274fa0-5c4e-4585-b36c-d2fd0a2cf7ef\.system_generated\logs\transcript.jsonl"
found = False

with open(log_file, "r", encoding="utf-8") as f:
    for line in f:
        try:
            data = json.loads(line)
            content = data.get("content", "")
            if "Phase 2 (" in content or "Phase 2:" in content or "Phase 1-12" in content or "12-phase" in content:
                print("FOUND A MATCHING MESSAGE:")
                # print up to 5000 chars of the content
                print(content[:5000])
                print("-" * 80)
        except json.JSONDecodeError:
            pass
