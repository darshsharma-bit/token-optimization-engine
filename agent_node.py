import asyncio
import websockets
import json
import os
import requests
from dotenv import load_dotenv
import tiktoken

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Fetch an available free model dynamically
import time

import json
from datetime import datetime, timedelta

CACHE_FILE = ".models_cache.json"

def dynamic_free_models():
    # Try loading from cache first
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                cache = json.load(f)
                cached_time = datetime.fromisoformat(cache['timestamp'])
                if datetime.now() - cached_time < timedelta(hours=1):
                    return cache['models']
        except:
            pass

    url = "https://openrouter.ai/api/v1/models"
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}"}

    max_retries = 5

    for attempt in range(max_retries):
        try:
            r = requests.get(url, headers=headers)

            if r.status_code == 200:
                models = r.json().get("data", [])
                free_models = [m["id"] for m in models if ":free" in m["id"]]
                if not free_models:
                    free_models = ["openrouter/auto"]
                
                # Save to cache
                try:
                    with open(CACHE_FILE, 'w') as f:
                        json.dump({
                            'models': free_models,
                            'timestamp': datetime.now().isoformat()
                        }, f)
                except:
                    pass
                    
                return free_models

            elif r.status_code == 429:
                wait_time = 2 ** attempt
                print(f"[429] Rate limited (fetching models). Retrying in {wait_time}s...")
                time.sleep(wait_time)

            else:
                print("Error fetching models:", r.text)
                break

        except Exception as e:
            print("Exception fetching models:", e)
            time.sleep(2)

    return ["openrouter/auto"]

FREE_MODELS = dynamic_free_models()
CURRENT_MODEL = FREE_MODELS[0]
print(f"Initial Model Selected: {CURRENT_MODEL}")



# Token Counter (Professional Grade - GPT-4o / Gemini compatible)
def get_precise_metrics(input_text, compressed_text):
    try:
        # Use o200k_base which is optimized for newer flagship models
        encoding = tiktoken.get_encoding("o200k_base")
    except:
        # Fallback to cl100k_base if o200k is not available in local tiktoken version
        encoding = tiktoken.get_encoding("cl100k_base")
        
    orig_tokens = len(encoding.encode(input_text))
    comp_tokens = len(encoding.encode(compressed_text))
    
    reduction_pct = 0
    if orig_tokens > 0:
        reduction_pct = round(((orig_tokens - comp_tokens) / orig_tokens) * 100, 1)
        
    return {
        "original": orig_tokens,
        "compressed": comp_tokens,
        "reduction_pct": reduction_pct
    }

def call_openrouter(messages):
    global CURRENT_MODEL, FREE_MODELS
    max_retries = 8
    model_idx = 0
    
    for attempt in range(max_retries):
        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                },
                data=json.dumps({
                    "model": CURRENT_MODEL,
                    "messages": messages,
                })
            )
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            
            elif response.status_code == 429:
                # Rotate model if we have more than one
                if len(FREE_MODELS) > 1:
                    model_idx = (model_idx + 1) % len(FREE_MODELS)
                    CURRENT_MODEL = FREE_MODELS[model_idx]
                    print(f"[429] Rate limited. Rotating to model: {CURRENT_MODEL}")
                
                wait_time = (1.5 ** attempt) + (time.time() % 2) # Slower backoff but with rotation
                print(f"[429] Retrying in {wait_time:.1f}s...")
                time.sleep(wait_time)
            
            else:
                print(f"OpenRouter Error {response.status_code}: {response.text}")
                if response.status_code >= 500:
                    time.sleep(2)
                    continue
                raise Exception(f"OpenRouter API Error: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"Request Exception: {e}")
            time.sleep(2)
            
    raise Exception("OpenRouter API Error: Max retries exceeded after model rotation")



# System prompt to COMPRESS English into ATP shorthand
COMPRESSOR_PROMPT = """SYSTEM ROLE: You are an AI Prompt Compressor. Your ONLY job is to convert long natural language instructions into a highly compressed, structured, low-token protocol format.

GOAL:
Minimize token usage while preserving complete intent.

STRICT RULES:

1. Output MUST be a single-line compressed protocol.
2. NO explanations, NO extra text.
3. Use short keys and abbreviations.
4. Use "|" as separator.
5. Use ":" for key-value pairs.
6. Remove ALL unnecessary words.
7. Preserve core intent ONLY.
8. Output must be as short as possible without losing meaning.

COMPRESSION STYLE:

* TASK → T
* LANGUAGE → L
* TARGET → G
* METHOD → M
* CONSTRAINTS → C
* MEMORY → MEM
* OPTIMIZATION → O

EXAMPLES:

Input:
"Write a Rust program to compute Fibonacci numbers in O(N) time"

Output:
T:CG|L:RUST|G:FIB|M:DP|MEM:ON

---

Input:
"Reverse a string in Python"

Output:
T:STR|L:PY|G:REV

---

Input:
"Approximate zeta(3) using Monte Carlo in Rust with bitwise operations, no standard math libraries, no floating division, AVX512 optimization, O(1) memory"

Output:
T:CG|L:RUST|G:ZETA3|M:MC|C:BIT,NO_STD,NO_DIV|O:AVX512|MEM:O1

---

IMPORTANT:

* Aggressively compress
* Prefer abbreviations
* Do not repeat information
* Do not add explanation

FINAL INSTRUCTION:
Convert input → ultra-compressed protocol ONLY."""

# System prompt to DECOMPRESS ATP shorthand back into actions
DECOMPRESSOR_PROMPT = """SYSTEM ROLE: You are an AI Execution Engine. You DO NOT generate natural language explanations. Your job is to RECEIVE a structured protocol string, PARSE it deterministically, EXECUTE the requested task using native Python logic, and RETURN the result.

CRITICAL RULES:

1. DO NOT call any LLM.
2. DO NOT re-interpret the task using natural language.
3. ONLY use the protocol fields.
4. Execution must be deterministic and local.
5. If a required field is missing → return ERROR.
6. If task is unknown → return ERROR:UNKNOWN_TASK.

---

INPUT FORMAT:
You will receive a single-line protocol string like:

TASK:STRING_OP|LANG:PYTHON|TARGET:REV_STR|INPUT:hello

---

STEP 1: PARSE PROTOCOL

Split by "|" → then split each part by ":" into key-value pairs.

Example result:
{
"TASK": "STRING_OP",
"LANG": "PYTHON",
"TARGET": "REV_STR",
"INPUT": "hello"
}

---

STEP 2: VALIDATE

* TASK must exist
* TARGET must exist
* If missing → return:
  ERROR:MISSING_FIELD

---

STEP 3: EXECUTE TASKS

Implement the following:

### TASK: STRING_OP

TARGET: REV_STR
→ Reverse INPUT string

Example:
INPUT: hello → OUTPUT: olleh

---

### TASK: MATH

TARGET: FIB
→ Return first N Fibonacci numbers

Fields:
N: integer

---

### TASK: CODE_GEN

→ Simulate code generation (no LLM)

Return:
"CODE_GEN::<LANG>::<TARGET>"

Example:
CODE_GEN::RUST::ZETA3

---

### TASK: JSON_PARSE

INPUT: JSON string
→ parse using Python json.loads

---

STEP 4: OUTPUT FORMAT

Return ONLY:

SUCCESS:<result>

OR

ERROR:<reason>

---

EXAMPLES:

Input:
TASK:STRING_OP|TARGET:REV_STR|INPUT:hello

Output:
SUCCESS:olleh

---

Input:
TASK:MATH|TARGET:FIB|N:5

Output:
SUCCESS:[0,1,1,2,3]

---

Input:
TASK:UNKNOWN

Output:
ERROR:UNKNOWN_TASK

---

FINAL INSTRUCTION:
Parse → Validate → Execute → Return result
NO explanations. ONLY output result."""

async def run_agent(agent_id: str, target_id: str = None, initial_task: str = None):
    uri = f"ws://127.0.0.1:8000/ws/{agent_id}"
    
    async with websockets.connect(uri) as websocket:
        print(f"\n[{agent_id.upper()}] Connected to ATP Router.")
        
        # If this agent is a Sender, it compresses and sends the task
        if initial_task and target_id:
            print(f"[{agent_id.upper()}] Original Human Task: {initial_task}")
            print(f"[{agent_id.upper()}] Compressing using OpenRouter...")
            
            # 1. Compress the task
            response_text = call_openrouter([
                {'role': 'system', 'content': COMPRESSOR_PROMPT},
                {'role': 'user', 'content': initial_task}
            ])
            compressed_payload = response_text.strip()
            # 2. Calculate Precise Metrics
            metrics = get_precise_metrics(initial_task, compressed_payload)
            print(f"[{agent_id.upper()}] Metrics -> {metrics['original']} orig | {metrics['compressed']} comp | {metrics['reduction_pct']}% reduction")
            
            # 3. Build and send the packet (including metrics in header)
            packet = {
                "h": {
                    "s": agent_id, 
                    "r": target_id, 
                    "i": 1,
                    "m": metrics # Added professional-grade metrics
                }, 
                "p": compressed_payload
            }
            await websocket.send(json.dumps(packet))
            print(f"[{agent_id.upper()}] Packet fired into the network -> {target_id}\n")

        # Listen for incoming packets continuously
        while True:
            try:
                message = await websocket.recv()
                packet = json.loads(message)
                sender = packet['h']['s']
                payload = packet['p']
                
                print(f"\n[{agent_id.upper()}] Received ATP Packet from {sender}: {payload}")
                print(f"[{agent_id.upper()}] Decompressing and executing task using OpenRouter...")
                
                # Decompress and execute
                result = call_openrouter([
                    {'role': 'system', 'content': DECOMPRESSOR_PROMPT},
                    {'role': 'user', 'content': payload}
                ])
                print(f"[{agent_id.upper()}] Execution Result:\n{result}\n")
                print(f"[{agent_id.upper()}] Waiting for next packet...")
                # Small delay to reduce API pressure and avoid bursts
                await asyncio.sleep(1)
                
            except websockets.exceptions.ConnectionClosed:
                print(f"[{agent_id.upper()}] Disconnected from router.")
                break

if __name__ == "__main__":
    import sys
    print("--- ATP Agent Node Initialization ---")
    
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        print("1: Start as RECEIVER Agent (Listens for tasks)")
        print("2: Start as SENDER Agent (Compresses and sends a task)")
        choice = input("Select role (1 or 2): ")
    
    if choice == "1":
        # Start the listener (we'll call him agent_coder)
        asyncio.run(run_agent(agent_id="agent_coder"))
    elif choice == "2":
        # Start the sender (we'll call him agent_manager)
        task = input("\nEnter a task in normal English for the coder to do: ")
        asyncio.run(run_agent(agent_id="agent_manager", target_id="agent_coder", initial_task=task))
    else:
        print("Invalid choice.")