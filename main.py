import re
import os
import json
import subprocess
from typing import List

from openai import OpenAI

BASH_SYSTEM_PROMPT = """
Your task is turn the users prompt into a usable linux script.
Surround the script in triple backticks (```) like a code block.
Be sure to use command arguments instead of telling the user to replace an example name with something appropriate.
"""

PYTHON_SYSTEM_PROMPT = """
Your task is to turn the users prompt into a python script.
Surround your code with triple backticks (```) like a code block.
"""

ASSISTANT_SYSTEM_PROMPT = """
You are a helpful assistant
"""

config = { }
if os.path.exists("config.json"):
    with open('config.json', 'r') as f:
        config = json.load(f)
else:
    raise BaseException("config.json not found")

base_url = None
if "openai_url" in config:
    base_url = config["openai_url"]

if not base_url is None:
    client = OpenAI(
        base_url=base_url,
        api_key="NULL",
    )
else:
    if not "openai_key" in config:
        raise BaseException("openai_key not found in config")
    client = OpenAI(
        api_key=config["openai_key"],
    )

def capture_code_blocks(text):
    pattern = r"```(.*?)```"
    return re.findall(pattern, text, re.DOTALL)

def get_response(messages: List[object]):
    completion = client.chat.completions.create(
        messages=messages,
        model="gpt-4-1106-preview",
        max_tokens=1000,
        temperature=0.5
    )

    res = completion.choices[0].message.content

    blocks = capture_code_blocks(res)
    if len(blocks) > 0:
        return res, blocks[0]
    else:
        return res, None

def get_script(prompt: str, sys_prompt: str):
    return get_response([
        {
            "role": "system",
            "content": sys_prompt
        },
        {
            "role": "user",
            "content": prompt
        }
    ])

def run_bash_bot():
    prompt = input("Bash Prompt:> ")
    response, cmd = get_script(prompt, BASH_SYSTEM_PROMPT)
    print(response)
    print(f"Command: {cmd}")
    should_use = input("Write Script (Y/N)")
    if should_use.lower() == "y":
        with open('exec.sh', 'w') as f:
            f.write(cmd)
        should_exec = input("Execute script (Y/N)")
        if should_exec.lower() == "y":
            subprocess.call(['sh', 'exec.sh'])

def run_python_bot():
    prompt = input("Python Prompt:> ")
    res, _ = get_script(prompt, PYTHON_SYSTEM_PROMPT)
    print(res)

def run_assistant():
    messages = [{
        "role": "system",
        "content": ASSISTANT_SYSTEM_PROMPT
    }]
    while True:
        print("########################\n\n")
        messages.append({
            "role": "user",
            "content": input("User: ")
        })
        res, _ = get_response(messages)
        print(f"########################\n\nASSISTANT: {res}")
        messages.append({
            "role": "assistant",
            "content": res
        })


while True:
    print("""
Select Bot:
1: Bash script bot
2: Python script bot
3: General Help
""")
    bot = input('Selection: ')
    try:
        if int(bot) > 3:
            continue
    except:
        continue
    if int(bot) == 1:
        run_bash_bot()
    if int(bot) == 2:
        run_python_bot()
    if int(bot) == 3:
        run_assistant()