import os
import socket
import subprocess
from datetime import datetime
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# API Keys
API_KEYS = [
    os.getenv("API_KEY_GEN_1"),
    os.getenv("API_KEY_GEN_2"),
    os.getenv("API_KEY_GEN_3"),
]

# Base directories
BASE_DIR = os.getcwd()
USER_INPUT_FILE = os.path.join(BASE_DIR, "user_input.txt")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

# Supported tools
SUPPORTED_TOOLS = ["nmap", "masscan", "nikto", "unicorn", "hping"]


def resolve_to_ip(target):
    try:
        return socket.gethostbyname(target)
    except socket.gaierror:
        return None


def call_groq(prompt):
    for key in API_KEYS:
        try:
            response = requests.post(
                url="https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "llama3-70b-8192",
                    "messages": [
                        {"role": "system", "content": "You are PenTestGPT, an AI that selects only from these tools: nmap, masscan, nikto, unicorn, hping."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.2
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content'].strip()
        except Exception as e:
            print(f"❌ Failed with key {key[:12]}... Trying next key.")
            continue
    raise Exception("❌ All API keys failed!")


def run_command(command):
    try:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout + result.stderr
    except Exception as e:
        return f"Command execution failed: {e}"


def save_to_file(path, content):
    with open(path, "w") as f:
        f.write(content)


def parse_tool_from_command(command):
    for tool in SUPPORTED_TOOLS:
        if tool in command:
            return tool
    return "unknown"


def main():
    print("=== AI Offensive Security Automation ===")
    target_input = input("Enter the target IP or domain: ").strip()
    task_description = input("Describe what you want to do (e.g., scan open ports, find subdomains): ").strip()

    if not target_input:
        print("❌ Target input is empty.")
        return

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    target_dir = os.path.join(REPORTS_DIR, f"{target_input.replace('.', '_')}__{timestamp}")
    os.makedirs(target_dir, exist_ok=True)

    save_to_file(USER_INPUT_FILE, f"Target: {target_input}\nTask: {task_description}\n")

    prompt = f"""
Your task is to perform: '{task_description}' on host '{target_input}'.
Only use tools from this list: {', '.join(SUPPORTED_TOOLS)}
Only return the exact Linux command(s) needed to achieve the task.
No explanation. No markdown. One or more commands if needed.
"""

    print("\n🧠 Asking AI for command(s)...")
    try:
        commands_text = call_groq(prompt)
        print(f"\n🔧 AI-Generated Command(s):\n{commands_text}\n")
    except Exception as e:
        print(str(e))
        return

    command_lines = [line.strip() for line in commands_text.split('\n') if line.strip()]
    combined_log = f"Target: {target_input}\nTask: {task_description}\n\nAI Commands:\n{commands_text}\n\nExecution Logs:\n"

    for idx, cmd in enumerate(command_lines, 1):
        print(f"🚀 Running Command {idx}: {cmd}")
        output = run_command(cmd)

        tool = parse_tool_from_command(cmd)
        tool_file = os.path.join(target_dir, f"{tool}_output.txt")
        save_to_file(tool_file, output)

        combined_log += f"\n[Command {idx}]: {cmd}\n{'-'*40}\n{output}\n"

    log_file = os.path.join(target_dir, "logs.txt")
    save_to_file(log_file, combined_log)

    print(f"✅ Scan complete. All logs and tool outputs are saved in: {target_dir}")


if __name__ == "__main__":
    main()
