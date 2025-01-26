import streamlit as st
import json
import time
from pathlib import Path

# Path to the JSON file used for shared messages
MESSAGES_FILE = Path("messages.json")

# Streamlit app
def main():
    st.title("Real-time Chat Messages")

    # Placeholder for dynamically updating chat messages
    placeholder = st.empty()

    while True:
        # Check if the JSON file exists
        if MESSAGES_FILE.exists():
            # Read messages from the JSON file
            with open(MESSAGES_FILE, "r") as file:
                messages = json.load(file)

            with placeholder.container():
                st.subheader("Messages:")
                for message in messages:
                        with st.chat_message(message["role"]):
                            st.markdown(message["contents"])
        else:
            with placeholder.container():
                st.subheader("Messages:")
                st.write("No messages yet.")

        time.sleep(1)  # Refresh every second

if __name__ == "__main__":
    main()
