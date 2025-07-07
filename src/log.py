import json
import os
from datetime import datetime

# GHi lại thông tin người dùng, câu hỏi, phản hồi vào file activity_log.json
def log_activity(user, question, response):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "user": str(user),
        "question": question,
        "response": response
    }
    log_file = "activity_log.json"
    if os.path.exists(log_file):
        with open(log_file, "r", encoding = "utf-8") as f:
            logs = json.load(f)
    else:
        logs = []
    logs.append(log_entry)
    with open(log_file, 'w', encoding = 'utf-8') as f:
        json.dump(logs, f, ensure_ascii = False, indent = 2)