# UTE ChatBot

# 📱 Vietnamese KG-RAG Chatbot Application

## Features

- 🗣 Natural interaction in Vietnamese.  
- 📊 Knowledge graph integration with Neo4j
- Chat history management with SQLite
- Real-time graph visualization
- Execution time tracking
- Clean and modern UI
- 🧠 Combines KG retrieval with LLM generation to deliver precise, meaningful, and context-aware answers.

## Tech Stack

- Python 3.8+
- Google Gemini API for LLM
- Neo4j for knowledge graph
- SQLite for chat history
- NetworkX and Matplotlib for graph visualization
- PhoBERT for Vietnamese text embedding
- CustomTkinter and ttkbootstrap for modern UI

## Project Structure

```
chat_bot/
├── config/
│   ├── __init__.py
│   └── config.py           # Configuration settings
├── models/
│   ├── __init__.py
│   ├── llm.py             # Gemini LLM integration
│   └── embedding_model.py  # PhoBERT embedding model
├── database/
│   ├── __init__.py
│   ├── neo4j_connect.py   # Neo4j connection handler
│   └── history.py         # SQLite history management
├── utils/
│   ├── __init__.py
│   └── LogHandler.py      # Logging functionality
├── visualization/
│   ├── __init__.py
│   └── graph_representation.py  # Knowledge graph visualization
├── gui/
│   ├── __init__.py
│   └── gui.py             # Main GUI implementation
├── tests/
│   ├── __init__.py
│   └── test.py            # Test utilities
├── requirements.txt
└── main.py                # Application entry point
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd chat_bot
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Configure Neo4j:
- Install Neo4j Desktop
- Create a new database
- Update connection details in config/config.py

4. Set up Gemini API:
- Get API key from Google Cloud Console
- Update GEMINI_API_KEY in config/config.py

## Usage

Run the application:
```bash
python main.py
```

### Features:
- Ask questions in Vietnamese about UTE
- View knowledge graph visualization
- Check chat history
- Track response time
- Clear history and logs

## Development

### Adding New Features
1. Update Neo4j database with new knowledge
2. Extend GUI functionality in gui.py
3. Add new visualization options in graph_representation.py
4. Update models for better language processing

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google Gemini API for LLM capabilities
- Neo4j for graph database
- VINAI's PhoBERT for Vietnamese language processing
- CustomTkinter for modern UI components
