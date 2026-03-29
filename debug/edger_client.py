import json

from fino_filing import EdgerClient, EdgerConfig

# submissions
client = EdgerClient(EdgerConfig(user_agent_email="odukaki@gmail.com"))
print(json.dumps(client.get_submissions("0000320193"), indent=4))
