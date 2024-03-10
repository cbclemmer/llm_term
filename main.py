import re
import os
import json
import subprocess

from openai import OpenAI

SYSTEM_PROMPT = """
Your task is turn the users prompt into a usable linux command.
Surround the command in triple backticks (```) like a code block.
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

def get_command(prompt: str):
    completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
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

while True:
    prompt = input("Prompt:> ")
    response, cmd = get_command(prompt)
    if cmd[0] == '\n':
        cmd = cmd[1:]
    print(response)
    print(f"Command: {cmd}")
    should_use = input("Use command (Y/N)")
    if should_use.lower() == "y":
        with open('exec.sh', 'w') as f:
            f.write(f'#!/bin/bash\n{cmd}')
        subprocess.call(['sh', 'exec.sh'])