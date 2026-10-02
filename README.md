# Agentic AI

A local command-line AI assistant powered by Ollama and Qwen (`qwen3:4b`). The assistant runs an autonomous multi-step tool-calling loop capable of inspecting host system information, safely managing files within a designated workspace, and executing Python code in an isolated Docker container.

## Features

- **Autonomous Tool-Calling Loop**: Uses Ollama's chat API to iteratively plan and execute tools (up to 8 steps per turn) before returning a final response.
- **System Diagnostics**:
  - `get_system_info`: Retrieves OS platform, release, version, CPU architecture, processor details, hostname, and Python runtime version.
  - `get_current_time`: Returns the current local system time in 12-hour AM/PM format.
- **Workspace File Management**:
  - Confined strictly to the `workspace/` directory with path traversal protection.
  - `list_files`: Lists directory contents formatted as a Markdown table with filename, file type, human-readable size, and creation timestamp.
  - `read_file`: Reads text files (up to 5,000 characters) while rejecting binary formats.
  - `write_file`: Writes text or code files, automatically creating missing parent directories and blocking binary formats.
- **Containerized Python Sandbox**:
  - `run_python`: Executes arbitrary Python code inside an isolated, disposable Docker container (`python:3.12-slim`) with disabled network access, 256MB memory cap, 0.5 CPU cap, dropped capabilities, read-only root filesystem, non-root user permissions, and a 15-second execution timeout.
- **Interactive CLI**: Multi-turn command-line conversation loop with session persistence.

## Tech Stack

- **Python**: Core runtime
- **Ollama Python SDK (`ollama`)**: Interface for local LLM chat and tool-calling
- **Qwen 3 (`qwen3:4b`)**: Default local LLM
- **Docker**: Container sandbox environment for isolated Python execution

## Installation & Setup

1. **Clone repository**:
   ```bash
   git clone https://github.com/DE-IGNIS/agentic-ai.git
   cd agentic-ai
   ```

2. **Install dependencies**:
   ```bash
   pip install ollama
   ```

3. **Pull Ollama model**:
   Ensure your local Ollama daemon is running, then pull the model:
   ```bash
   ollama pull qwen3:4b
   ```

4. **Pull Docker sandbox image**:
   Ensure Docker is installed and running, then pull the sandbox image:
   ```bash
   docker pull python:3.12-slim
   ```

5. **Run application**:
   ```bash
   python main.py
   ```

## Requirements

- **Python**: 3.10+
- **Ollama**: Installed and running with `qwen3:4b` available
- **Docker**: Running daemon (required for the `run_python` sandbox tool)

## Architecture

- **`main.py`**: Entry point providing the interactive CLI prompt loop and holding conversation state (`messages`).
- **`agent.py`**: Orchestrates the multi-turn agent execution loop (`MAX_STEPS = 8`), dispatching tool calls returned by Ollama and appending tool responses back into the message history.
- **`tools/execute.py`**: Central registry (`TOOL_REGISTRY`, `ALL_TOOLS`) managing registered tool functions and error-handled dispatching (`execute_tool`).
- **`tools/system.py`**: Implements system diagnostic and timestamp tools (`get_system_info`, `get_current_time`).
- **`tools/filesystem.py`**: Implements safe, bounded file operations (`list_files`, `read_file`, `write_file`) restricted to `workspace/`.
- **`tools/sandbox.py`**: Implements ephemeral containerized code execution (`run_python`) via Docker subprocess.
- **`workspace/`**: Isolated local directory where all agent file read and write operations take place.
