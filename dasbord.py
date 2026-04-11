import streamlit as st
import asyncio
import websockets
import json
from agent_node import call_openrouter, COMPRESSOR_PROMPT
import tiktoken

# Must be called first
st.set_page_config(page_title="AI Prompt Compressor", layout="wide", initial_sidebar_state="collapsed")

# Inject Custom CSS for Modern Dark Theme & Centering
st.markdown("""
<style>
    .stTextArea textarea {
        background-color: #1E1E1E !important;
        color: #00FF00 !important;
        border-radius: 8px !important;
        border: 1px solid #333 !important;
        font-family: monospace;
    }
    .metric-container {
        display: flex;
        justify-content: space-around;
        background-color: #111;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #222;
        margin-top: 10px;
        margin-bottom: 20px;
    }
    .metric-box {
        text-align: center;
        font-family: monospace;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #00FF00;
    }
    /* Antigravity High Performance Glow */
    .glow-metric-value {
        font-size: 28px;
        font-weight: bold;
        color: #00FF00;
        text-shadow: 0 0 10px #00FF00, 0 0 20px #00FF00;
        animation: pulse 2s infinite alternate;
    }
    @keyframes pulse {
        from { text-shadow: 0 0 5px #00FF00; }
        to { text-shadow: 0 0 25px #00FF00, 0 0 40px #00FF00; }
    }
    .metric-label {
        font-size: 12px;
        color: #888;
    }
</style>
""", unsafe_allow_html=True)

# Helper function for token approximation
# Professional Token Counter
def get_tokens(text: str) -> int:
    if not text: return 0
    try:
        encoding = tiktoken.get_encoding("o200k_base")
    except:
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))

if "history" not in st.session_state:
    st.session_state.history = []

if "current_stats" not in st.session_state:
    st.session_state.current_stats = None

# Layout
col1, col2 = st.columns([1.2, 1])

with col1:
    st.title("⚡ AI Prompt Compressor")
    
    human_task = st.text_area("Input Prompt", placeholder="Enter natural language instructions here...", height=150, label_visibility="collapsed")
    
    # Action Button
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    with col_btn2:
        fire_button = st.button("Compress 🚀", use_container_width=True, disabled=not human_task.strip())

    if fire_button and human_task:
        with st.spinner("Compressing..."):
            try:
                # Execution
                alien_version = call_openrouter([
                    {'role': 'system', 'content': COMPRESSOR_PROMPT},
                    {'role': 'user', 'content': human_task}
                ]).strip()
                
                # Precise Token Metrics
                orig_tokens = get_tokens(human_task)
                comp_tokens = get_tokens(alien_version)
                reduction = round(((orig_tokens - comp_tokens) / orig_tokens) * 100, 1) if orig_tokens > 0 else 0
                
                st.session_state.current_stats = {
                    "orig": orig_tokens,
                    "comp": comp_tokens,
                    "red": reduction
                }
                
                # History Update
                st.session_state.history.insert(0, {
                    "input": human_task,
                    "output": alien_version,
                    "saved": f"{reduction}%"
                })
                # Keep only last 5
                st.session_state.history = st.session_state.history[:5]
                
                # Network Injection (with metrics payload for receiver agents)
                packet = {
                    "h": {
                        "s": "ui_manager", 
                        "r": "agent_coder", 
                        "i": 1, 
                        "m": {"orig": orig_tokens, "comp": comp_tokens, "red": reduction}
                    }, 
                    "p": alien_version
                }
                async def send_packet():
                    async with websockets.connect("ws://127.0.0.1:8000/ws/ui_manager") as ws:
                        await ws.send(json.dumps(packet))
                try:
                    asyncio.run(send_packet())
                    st.toast("Compression Successful & Injected! ✅", icon="🚀")
                except Exception:
                    st.toast("Compression Successful ✅", icon="🚀")
                
                # Visual Output
                st.code(alien_version, language="text")
                
            except Exception as e:
                st.error(f"Compression Fault: {e}")

with col2:
    if st.session_state.current_stats:
        st.subheader("📊 Compression Stats")
        stats = st.session_state.current_stats
        # Determine if we should apply the "Glow" effect (>80% reduction)
        red_class = "glow-metric-value" if stats['red'] >= 80 else "metric-value"
        
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-box">
                <div class="metric-value">{stats['orig']}</div>
                <div class="metric-label">ORIG TOKENS</div>
            </div>
            <div class="metric-box">
                <div class="metric-value">{stats['comp']}</div>
                <div class="metric-label">COMP TOKENS</div>
            </div>
            <div class="metric-box">
                <div class="{red_class}">{stats['red']}%</div>
                <div class="metric-label">REDUCTION</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.divider()

    st.subheader("🕘 Recent Compressions")
    if not st.session_state.history:
        st.info("No history yet")
    else:
        for item in st.session_state.history:
            with st.container(border=True):
                short_input = item['input'][:50] + "..." if len(item['input']) > 50 else item['input']
                st.markdown(f"**Input:** `{short_input}`")
                st.code(item['output'], language="text")
                st.markdown(f"**Saved:** <span style='color:#00FF00;font-weight:bold;'>{item['saved']}</span>", unsafe_allow_html=True)