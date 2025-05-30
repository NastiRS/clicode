# Clicode

AI coding assistant with advanced reasoning, web search, and GitHub integration.

## Features

- 🧠 **Advanced Reasoning** - Deep analysis and step-by-step thinking
- 🔍 **Web Search** - Access to technical documentation via Exa API
- 🐙 **GitHub Integration** - Repository management and code search
- 📁 **File Management** - Read, write, delete, search files
- ⚡ **Command Execution** - Run system commands safely
- 💾 **Persistent Memory** - Remembers conversation context

## Quick Start

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run the assistant:**
   ```bash
   uv run clicode chat or clicode chat
   ```

## Configuration

Required environment variables in `.env`:

```bash
# Required
OPENROUTER_API_KEY=your_openrouter_api_key

# Optional
OPENROUTER_MODEL=your_openrouter_model # gpt-4.1-mini by default
GITHUB_ACCESS_TOKEN=your_github_token  # For GitHub features
EXA_API_KEY=your_exa_api_key          # For web search
```

## Key Capabilities

- **Smart Project Analysis** - Automatically detects project structure and tools
- **Package Management** - Respects project environments (uv, poetry, npm, etc.)
- **Technical Search** - Finds official documentation and code examples
- **GitHub Operations** - Create repos, manage branches, search code

## License

MIT
