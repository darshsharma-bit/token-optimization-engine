# 🚀 Token Optimization Engine (TOE)

**Compress prompts into ultra-efficient representations without losing meaning.**

---

## 📖 Overview

**Token Optimization Engine (TOE)** is a high-performance agentic AI system designed to solve the growing cost and latency issues in LLM applications. TOE dynamically compresses natural language prompts into a structured, minimal-token representation (Agentic Token Protocol / CAL-style). 

This compressed payload remains fully understood by AI models while stripping away linguistic redundancy, saving up to **80% in token costs** and significantly improving inference speed without sacrificing intent or accuracy.

---

## ✨ Features

- 💎 **CAL-based Compression**: Converts wordy instructions into ultra-dense semantic packets.
- 🤖 **Multi-Agent Architecture**: A coordinated team of Manager, Compressor, Coder, and Reviewer agents.
- 📊 **Analytics Dashboard**: Real-time visualization of token reduction and compression efficiency.
- 🔄 **Iterative Feedback**: Automatic self-correction loop to ensure original intent is preserved.
- ⚡ **Dynamic Model Selection**: Automatically fetches and utilizes the best available free/paid models via OpenRouter.
- 🛡️ **Fault Tolerance**: Robust error handling with exponential backoff and model rotation to bypass rate limits (429s).

---

## 🧠 Architecture

TOE operates as a decentralized network of specialized agents communicating over a central **ATP Router**:

1.  **UI/Manager Agent**: Captures human instructions and initiates the optimization sequence.
2.  **Compressor Agent**: Analyzes the prompt and translates it into the dense ATP/CAL protocol.
3.  **Coder/Executor Agent**: Receives compressed packets, deconstructs the logic, and generates the requested output.
4.  **Reviewer Agent (Loop)**: Validates the output against the original intent, triggering re-compression if semantic drift is detected.

---

## 🛠️ Tech Stack

- **Language**: Python 3.9+
- **Frontend**: Streamlit (Modern Dark UI)
- **API**: OpenRouter (Unified LLM access)
- **Communication**: WebSockets / FastAPI (Real-time routing)
- **Utilities**: `tiktoken` (Professional token counting), `python-dotenv`

---

## ⚙️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/toe.git
   cd toe
   ```

2. **Set up Virtual Environment**:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   source venv/bin/activate # Linux/Mac
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## ▶️ Usage

1. **Start the Router**:
   ```bash
   python router.py
   ```

2. **Launch a Receiver Agent** (in a new terminal):
   ```bash
   python agent_node.py 1
   ```

3. **Launch the Dashboard**:
   ```bash
   streamlit run dasbord.py
   ```

4. **Run Compression**: Paste your long prompt into the Dashboard and click **Compress 🚀**. Watch your tokens disappear!

---

## 🔐 Environment Variables

Create a `.env` file in the root directory:

```env
OPENROUTER_API_KEY=your_api_key_here
```

---

## 📁 Project Structure

```text
├── agent_node.py     # Core agent logic and API handlers
├── router.py         # WebSocket-based packet routing system
├── dasbord.py        # Streamlit visualization and UI
├── protocool.py      # Pydantic models for ATP packets
├── fetch_models.py   # Utility to verify API connectivity
├── .env.example      # Template for environment variables
└── README.md         # Documentation
```

---

## 📸 Screenshots

![Dashboard Overview](https://placehold.co/800x450/111111/00FF00?text=TOE+Dashboard+Preview)
*Placeholder: Visualizing 85% token reduction in real-time.*

---

## 🧭 Roadmap

- [ ] **Cross-Model Benchmarking**: Compare compression quality across GPT-4, Claude, and Llama.
- [ ] **Custom Protocols**: Allow users to define their own shorthand dictionaries.
- [ ] **Persistent Memory**: Agents remember past compression patterns for faster processing.
- [ ] **CLI Tool**: A lightweight command-line interface for batch processing.

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:
1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

