import openai
import os
import json
from openai import OpenAI
client = OpenAI()

# TODO: Implement retry logic
def call_gpt(system_prompt, user_prompt):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0,
        max_tokens=1000,
        top_p=1,
    )
    try: 
        output = json.loads(response.choices[0].message.content)
        return output
    except Exception as e:
        return None