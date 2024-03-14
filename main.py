import re
import os
import json
import subprocess

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

def get_script(prompt: str, sys_prompt: str):
    completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": sys_prompt
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        model="gpt-3.5-turbo",
        max_tokens=150,
        temperature=0.2
    )

    res = completion.choices[0].message.content

    return res, capture_code_blocks(res)[0]

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

while True:
    print('Select Bot:\n1: Bash script bot\n2: Python script bot')
    bot = input('Selection: ')
    try:
        if int(bot) != 1 and int(bot) !=2:
            continue
    except:
        continue
    if int(bot) == 1:
        run_bash_bot()
    if int(bot) == 2:
        run_python_bot()