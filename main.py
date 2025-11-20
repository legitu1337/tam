#github.com/legitu1337
#please dont take this and sell it on telegram
import asyncio
import json
import os
import platform
import re
from telethon import TelegramClient, functions, types
from telethon.errors import (
    ApiIdInvalidError,
    PhoneNumberInvalidError,
    PhoneCodeInvalidError,
    FloodWaitError,
    ChatWriteForbiddenError,
    UsernameInvalidError,
    UsernameNotOccupiedError,
    InviteRequestSentError,
    UserAlreadyParticipantError,
    SessionPasswordNeededError
)
from telethon.sessions import StringSession

CONFIG_FILE = "config.json"
SESSION_FILE = "sessions.json"

def clear_screen():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def load_config():
    if not os.path.exists(CONFIG_FILE):
        dummy_config = {"api_id": 123456, "api_hash": "hash"}
        with open(CONFIG_FILE, "w") as f:
            json.dump(dummy_config, f, indent=4)
        print(f"Error: {CONFIG_FILE} not found, created blank, plase fill it.")
        exit(1)
    try:
        with open(CONFIG_FILE, "r") as file:
            config = json.load(file)
            if "api_id" not in config or "api_hash" not in config:
                print("Error: config.json must contain 'api_id' and 'api_hash'.")
                exit(1)
            return config
    except json.JSONDecodeError:
        print("Error: config.json is not a valid JSON file.")
        exit(1)

def load_sessions():
    if not os.path.exists(SESSION_FILE):
        return {}
    try:
        with open(SESSION_FILE, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        print("Error: sessions.json is not a valid JSON file.")
        return {}

def save_sessions(sessions):
    try:
        with open(SESSION_FILE, "w") as file:
            json.dump(sessions, file, indent=4)
    except Exception as e:
        print(f"Error saving sessions: {e}")

config = load_config()
sessions = load_sessions()

async def getentity(client, target_str):

    target_str = target_str.strip()

    if re.match(r'^-?\d+$', target_str):
        try:
            return await client.get_entity(int(target_str))
        except ValueError:
            pass

    try:
        return await client.get_entity(target_str)
    except ValueError:
        print(f"   [INFO] Target not found in cache. Refreshing chat list...")
        await client.get_dialogs()
        try:
            # try one more time after refresh
            if re.match(r'^-?\d+$', target_str):
                return await client.get_entity(int(target_str))
            else:
                return await client.get_entity(target_str)
        except Exception:
            raise ValueError(f"Could not find chat: {target_str}")

#ACCOUNT MANAGEMENT

async def add_account():
    phone_number = input("Enter your phone number (with country code, '+1234567890'): ").strip()

    if phone_number in sessions:
        print("This account is already added.")
        input("\nPress Enter to continue...")
        return

    client = TelegramClient(StringSession(), config["api_id"], config["api_hash"])
    
    try:
        await client.connect()
        
        if not await client.is_user_authorized():
            await client.send_code_request(phone_number)
            try:
                code = input("Enter the code you received: ")
                await client.sign_in(phone_number, code)
            except SessionPasswordNeededError:
                password = input("Two-step verification is enabled. Enter your password: ")
                await client.sign_in(password=password)

        session_string = client.session.save()
        sessions[phone_number] = session_string
        save_sessions(sessions)
        print(f"Account {phone_number} added successfully!")
    except ApiIdInvalidError:
        print("Error: Invalid API ID or API hash.")
    except PhoneNumberInvalidError:
        print("Error: Invalid phone number.")
    except PhoneCodeInvalidError:
        print("Error: Invalid verification code.")
    except FloodWaitError as e:
        print(f"Error: You must wait {e.seconds} seconds before trying again.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        await client.disconnect()
        input("\nPress Enter to continue...")
        clear_screen()

def delete_account():
    if not sessions:
        print("No accounts to delete!")
        input("\nPress Enter to continue...")
        clear_screen()
        return

    print("Select account to delete:")
    account_list = list(sessions.keys())
    for i, phone_number in enumerate(account_list):
        print(f"{i + 1}. {phone_number}")

    try:
        choice = int(input("Enter the number of the account to delete: "))
        if 1 <= choice <= len(account_list):
            phone_to_remove = account_list[choice - 1]
            del sessions[phone_to_remove]
            save_sessions(sessions)
            print(f"Account {phone_to_remove} deleted successfully.")
        else:
            print("Invalid selection.")
    except ValueError:
        print("Please enter a valid number.")
    except Exception as e:
        print(f"Error: {e}")
    
    input("\nPress Enter to continue...")
    clear_screen()

#ACTIONS

async def send_single(phone_number, target_input, message):
    client = None
    try:
        session_string = sessions[phone_number]
        client = TelegramClient(StringSession(session_string), config["api_id"], config["api_hash"])
        await client.connect()

        entity = await getentity(client, target_input)
        
        await client.send_message(entity, message)
        print(f"[SUCCESS] Message sent from {phone_number} to {target_input}!")

    except ValueError as ve:
        print(f"[ERROR] {phone_number}: {ve}")
    except ChatWriteForbiddenError:
        print(f"[ERROR] {phone_number}: You are not allowed to write in this chat.")
    except Exception as e:
        print(f"[ERROR] Failed to send from {phone_number}: {e}")
    finally:
        if client:
            await client.disconnect()

async def send_message_multi():
    if not sessions:
        print("No accounts added yet!")
        input("\nPress Enter to continue...")
        clear_screen()
        return

    print("Available accounts:")
    account_list = list(sessions.keys())
    for i, phone_number in enumerate(account_list):
        print(f"{i + 1}. {phone_number}")

    try:
        selected_indices = input("Select accounts (comma-separated '1,2'): ")
        selected_indices = [int(idx.strip()) - 1 for idx in selected_indices.split(",")]
        selected_accounts = [account_list[idx] for idx in selected_indices if 0 <= idx < len(account_list)]

        if not selected_accounts:
            print("No valid accounts selected.")
            return

        target_input = input("Enter ID, @username, or link: ")
        message = input("Enter the message to send: ")

        # meow
        tasks = [send_single(acc, target_input, message) for acc in selected_accounts]
        await asyncio.gather(*tasks)
        
    except (IndexError, ValueError):
        print("Error: Invalid account selection.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        input("\nPress Enter to continue...")
        clear_screen()

async def join_group(phone_number, group_link):
    client = None
    try:
        session_string = sessions[phone_number]
        client = TelegramClient(StringSession(session_string), config["api_id"], config["api_hash"])
        await client.connect()

        # some logic
        if "joinchat" in group_link or "+" in group_link:
            try:
                hash_arg = group_link.split("/")[-1].replace("+", "").strip()
                await client(functions.messages.ImportChatInviteRequest(hash=hash_arg))
                print(f"[SUCCESS] Account {phone_number} joined via Invite Link!")
            except UserAlreadyParticipantError:
                print(f"[INFO] Account {phone_number} is already in the group.")
            except InviteRequestSentError:
                 print(f"[INFO] Account {phone_number} sent a request to join (Admin approval needed).")
        else:
            try:
                username = group_link.split("/")[-1].strip()
                await client(functions.channels.JoinChannelRequest(channel=username))
                print(f"[SUCCESS] Account {phone_number} joined Public Group!")
            except UserAlreadyParticipantError:
                print(f"[INFO] Account {phone_number} is already in the group.")

    except Exception as e:
        print(f"[ERROR] {phone_number} failed to join: {e}")
    finally:
        if client:
            await client.disconnect()

async def join_group_multi():
    if not sessions:
        print("No accounts added yet!")
        input("\nPress Enter to continue...")
        clear_screen()
        return

    print("Available accounts:")
    account_list = list(sessions.keys())
    for i, phone_number in enumerate(account_list):
        print(f"{i + 1}. {phone_number}")

    try:
        selected_indices = input("Select accounts ('1,2'): ")
        selected_indices = [int(idx.strip()) - 1 for idx in selected_indices.split(",")]
        selected_accounts = [account_list[idx] for idx in selected_indices if 0 <= idx < len(account_list)] #yes

        if not selected_accounts:
             print("No valid accounts selected.")
             return

        group_link = input("Enter the group invite link or username: ")

        tasks = [join_group(acc, group_link) for acc in selected_accounts]
        await asyncio.gather(*tasks)
    except (IndexError, ValueError):
        print("Error: Invalid account selection.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        input("\nPress Enter to continue...")
        clear_screen()

async def main_menu():
    while True:
        print("\n--- Telegram Account Manager ---")
        print("--- Made by github.com/legitu1337 ---")
        print("1. Add a new Telegram account")
        print("2. Send a message from multiple accounts")
        print("3. Join a group with multiple accounts")
        print("4. Delete an account")
        print("5. Exit")
        choice = input("Choose an option (1-5): ")

        if choice == "1":
            clear_screen()
            await add_account()
        elif choice == "2":
            clear_screen()
            await send_message_multi()
        elif choice == "3":
            clear_screen()
            await join_group_multi()
        elif choice == "4":
            clear_screen()
            delete_account()
        elif choice == "5":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")
            input("\nPress Enter to continue...")
            clear_screen()

if __name__ == "__main__":
    clear_screen()
    asyncio.run(main_menu())
