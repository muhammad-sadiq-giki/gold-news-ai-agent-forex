import os
import requests

webhook_url = os.environ["DISCORD_WEBHOOK_URL"]

message = {
    "content": "🚨 Hello! Your Gold AI News Agent is connected to Discord."
}

response = requests.post(webhook_url, json=message)

if response.status_code == 204:
    print("Discord message sent successfully!")
else:
    print("Something went wrong:", response.status_code, response.text)
