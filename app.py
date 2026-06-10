import os
import random  # New import for picking random choices
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

load_dotenv()

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

TARGET_USER_ID = os.environ.get("TARGET_USER_ID")
KEYWORDS = [k.strip().lower() for k in os.environ.get("KEYWORDS", "").split(",")]

# 1. Read our new toggle from the .env file (defaults to True if missing)
REQUIRE_KEYWORDS = os.environ.get("REQUIRE_KEYWORDS", "true").lower() == "true"

# 2. Load the random responses from our text file
try:
    with open("responses.txt", "r") as f:
        # Read lines, strip whitespace, and ignore empty lines
        RESPONSES = [line.strip() for line in f.readlines() if line.strip()]
except FileNotFoundError:
    # A fallback just in case the file goes missing
    RESPONSES = ["Hello there!"]

@app.message()
def handle_message_events(message, say, logger):
    user_id = message.get("user")
    text = message.get("text", "").lower()

    # Check if the message is from our target user
    if user_id == TARGET_USER_ID:

        # 3. Check if it's a main-channel message.
        # Threaded replies contain a 'thread_ts' key, main messages do not.
        is_main_channel = message.get("thread_ts") is None

        # We only want to trigger on new, main-channel messages
        if is_main_channel:
            should_respond = False

            # 4. Decide whether we should respond based on our toggle mode
            if REQUIRE_KEYWORDS:
                if any(keyword in text for keyword in KEYWORDS):
                    should_respond = True
            else:
                # "No keyword" mode is active, so we always respond
                should_respond = True

            if should_respond:
                thread_ts = message.get("ts")

                # 5. Pick a random line from our list of responses
                random_reply = random.choice(RESPONSES)

                # Reply using the randomly chosen text
                say(
                    text=f"<@{user_id}> {random_reply}",
                    thread_ts=thread_ts
                )

                logger.info(f"Responded to {user_id} in thread {thread_ts} with a random message.")

if __name__ == "__main__":
    print("⚡️ Bolt app is running in Socket Mode!")
    SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN")).start()
