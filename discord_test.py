import os
import requests

DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK")

print("=" * 70)
print("DISCORD CONNECTION TEST")
print("=" * 70)

if not DISCORD_WEBHOOK:
    print()
    print("ERROR: DISCORD_WEBHOOK is missing.")
    exit(1)

message = (
    "🚨 **GOLD NEWS AI TEST** 🚨\n\n"
    "✅ Discord connection is working!\n\n"
    "This is a test notification from my Gold News AI Agent."
)

payload = {
    "content": message
}

try:
    response = requests.post(
        DISCORD_WEBHOOK,
        json=payload,
        timeout=30
    )

    print()
    print("Discord HTTP status:", response.status_code)

    if response.status_code in (200, 204):
        print()
        print("SUCCESS!")
        print("Discord notification sent successfully.")
    else:
        print()
        print("FAILED!")
        print("Discord response:")
        print(response.text)
        exit(1)

except Exception as error:
    print()
    print("ERROR:")
    print(error)
    exit(1)
