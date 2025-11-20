# Telegram Account Manager (TAM)

A lightweight Telegram automation utility built with **Telethon**, allowing you to manage multiple accounts and perform bulk actions easily.

## Features

- **Multi-Account Management**  
  Securely add and store multiple Telegram sessions, including support for 2FA.

- **Mass Messaging**  
  Send messages from selected accounts to any **User**, **Group**, or **Channel**.

- **Mass Joining**  
  Join public groups or private invite links using multiple accounts at once.

- **Input Handling**  
  Accepts:
  - Chat IDs (e.g., `-100xxxx`)
  - Usernames (e.g., `@username`)
  - Invite Links (`https://t.me/...`)

- **Session Persistence**  
  Sessions are stored locally (`sessions.json` ), so each account only needs to log in once.

## Requirements

- Python **3.7+**
- Telethon (`pip install telethon`)
- Telegram **API ID** and **API Hash**  
  → Get yours at https://my.telegram.org

## Usage

 Edit **config.json** with your API ID and hash.  
 Run the tool:
 python main.py

## Disclaimer

This tool is for **educational purposes only***.
Automating actions on Telegram may cause account restrictions or bans if misused.
The developer is **not responsible** for any misuse or consequences resulting from this tool.
 
