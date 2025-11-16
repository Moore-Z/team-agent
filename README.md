# Team Knowledge Agent

A Retrieval-Augmented Generation (RAG) system designed to help software development teams access and query their knowledge base through Confluence integration and AI-powered question answering.

## Features

- **Confluence Integration**: Automatically sync and index team documentation from Confluence spaces
- **AI-Powered Q&A**: Ask questions about your team's knowledge base using natural language
- **Web Interface**: Clean, chat-like interface for interacting with the knowledge agent
- **Multiple LLM Support**: Works with Ollama (local) and Anthropic Claude models
- **Vector Search**: Efficient document retrieval using ChromaDB vector store
- **Quality Control**: Built-in mechanisms to prevent hallucination and ensure answer accuracy

## Architecture

```
team-agent/
├── backend/
│   ├── app/
│   │   ├── web_app.py          # FastAPI web server
│   │   ├── onboarding_routes.py # User onboarding endpoints
│   │   └── static/             # Frontend assets (CSS, JS)
│   ├── core/
│   │   ├── agents/
│   │   │   └── qa_agent.py     # Main Q&A agent implementation
│   │   ├── config/             # Configuration files
│   │   └── rag/                # Vector store and embeddings
│   └── connectors/
│       ├── confluence.py       # Confluence API integration
│       ├── confluenceToJason.py # Data extraction and persistence
│       └── test_specific_space.py # Space-specific testing
├── data/                       # Vector database storage
├── docs/                       # Documentation files
├── debug_confluence_permissions.py # Connection debugging tool
└── requirements.txt            # Python dependencies
```

## Quick Start

### Prerequisites

- Python 3.8+
- [Ollama](https://ollama.ai/) installed and running (for local LLM)
- Confluence access (URL, username, API token)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd team-agent
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file in the project root:
   ```
   CONFLUENCE_URL=https://your-company.atlassian.net
   CONFLUENCE_USERNAME=your-email@company.com
   CONFLUENCE_API_TOKEN=your-api-token
   CONFLUENCE_PERSONAL_SPACE_KEY=~your-space-key
   ANTHROPIC_API_KEY=your-anthropic-key  # Optional, for Claude models
   ```

4. **Start Ollama** (if using local LLM):
   ```bash
   ollama serve
   ollama pull qwen3:4b  # or your preferred model
   ```

### Usage

#### Web Interface

1. **Start the web server**:
   ```bash
   python backend/app/web_app.py
   ```

2. **Open your browser** and navigate to `http://localhost:8001`

3. **Ask questions** about your team's documentation through the chat interface

#### Command Line Interface

Run the standalone agent:
```bash
python agent.py
```

#### Confluence Data Ingestion

The system provides comprehensive Confluence integration with detailed debugging and data processing capabilities.

##### Environment Setup

1. **Configure Confluence credentials in `.env`**:
   ```bash
   CONFLUENCE_URL=https://your-company.atlassian.net
   CONFLUENCE_USERNAME=your-email@company.com
   CONFLUENCE_API_TOKEN=your-api-token
   CONFLUENCE_PERSONAL_SPACE_KEY=~your-space-key
   ```

2. **Generate API Token**:
   - Go to Atlassian Account Settings > Security > API Tokens
   - Create new token with appropriate permissions
   - Copy token to `.env` file

##### Available Scripts and Tools

**Main Data Ingestion**:
```bash
python backend/connectors/confluenceToJason.py
```

**Debug Connection Issues**:
```bash
python debug_confluence_permissions.py
```

**Test Specific Space Access**:
```bash
python backend/connectors/test_specific_space.py
```

##### Confluence API Integration Details

**ConfluenceConnector Class (`backend/connectors/confluence.py`)**

Core methods for Confluence interaction:

```python
class ConfluenceConnector:
    def __init__(self, url: str, username: str, api_token: str):
        """Initialize connection to Confluence with credentials"""

    def fetch_spaces(self) -> List[Dict]:
        """Fetch all accessible Confluence spaces"""

    def fetch_pages(self, space_key: str, limit: int = 100) -> List[Dict]:
        """Fetch all pages from a specific space with content"""

    def fetch_page_by_id(self, page_id: str) -> Dict:
        """Get specific page by ID with full content and metadata"""

    def fetch_space_by_key(self, space_key: str) -> Dict:
        """Get space information and metadata"""

    def process_page_content(self, page: Dict) -> Dict:
        """Clean HTML content and extract metadata for RAG processing"""
```

**Data Processing Flow**:

1. **Space Discovery**:
   ```python
   # Get all accessible spaces
   spaces = connector.fetch_spaces()
   # Returns: [{'key': 'SPACE_KEY', 'name': 'Space Name', ...}, ...]
   ```

2. **Page Retrieval**:
   ```python
   # Fetch pages with full content and metadata
   pages = connector.fetch_pages(space_key, expand='body.storage,version,ancestors')
   # Returns: List of page objects with content, metadata, and hierarchy
   ```

3. **Content Processing**:
   ```python
   processed = connector.process_page_content(page)
   # Returns: {
   #   'id': 'confluence_PAGE_ID',
   #   'content': 'cleaned_text_content',
   #   'metadata': {
   #     'source': 'confluence',
   #     'title': 'Page Title',
   #     'space': 'SPACE_KEY',
   #     'url': 'full_confluence_url',
   #     'last_modified': 'timestamp',
   #     'author': 'author_name'
   #   }
   # }
   ```

##### API Endpoints Used

The connector uses these Confluence REST API endpoints:

- **Spaces**: `GET /wiki/rest/api/space` - List all spaces
- **Space Details**: `GET /wiki/rest/api/space/{spaceKey}` - Get space info
- **Space Pages**: `GET /wiki/rest/api/space/{spaceKey}/content` - Get all pages in space
- **Page Content**: `GET /wiki/rest/api/content/{pageId}` - Get page with content

**Request Parameters**:
- `expand=body.storage,version,ancestors,space` - Include content and metadata
- `limit=100` - Pagination control
- `start=0` - Offset for pagination

##### FormConfluenceDataToPersist Class

Extended connector for data persistence (`backend/connectors/confluenceToJason.py`):

```python
# Usage example
connector = FormConfluenceDataToPersist()

# Process and save to JSON
result = connector.process_and_save_pages_to_json(
    space_key="YOUR_SPACE_KEY",
    output_file="data/confluence_data.json"
)
```

**Key Features**:
- Automatic credential loading from environment
- Error handling and debugging information
- JSON export functionality
- Personal space support

##### Troubleshooting Common Issues

**Connection Problems**:
```bash
# Run comprehensive debug check
python debug_confluence_permissions.py
```

This script checks:
- Environment variable configuration
- Network connectivity to Confluence
- API authentication
- Permission verification
- Proxy/firewall issues

**Space Access Issues**:
```bash
# Test access to specific space
python backend/connectors/test_specific_space.py
```

**Common Error Codes**:
- `401 Unauthorized`: Invalid credentials or expired token
- `403 Forbidden`: User lacks permission for space/content
- `404 Not Found`: Space key or page ID doesn't exist
- `429 Too Many Requests`: Rate limiting - add delays between requests

##### Data Flow to Vector Store

1. **Confluence → JSON**:
   ```bash
   python backend/connectors/confluenceToJason.py
   # Creates: data/confluence_data.json
   ```

2. **JSON → Vector Store**:
   ```python
   # In qa_agent.py initialization
   # ChromaDB automatically processes JSON data
   # Creates embeddings using OllamaEmbeddings or HuggingFace
   ```

3. **Query Processing**:
   ```python
   # User question → Vector search → Context retrieval → LLM response
   qa_chain.run("How do I deploy the service?")
   ```

## Configuration

### LLM Models

The system supports multiple LLM backends:

- **Ollama (Local)**: Configure in `backend/core/agents/qa_agent.py`
  ```python
  qa_agent = QAAgent(
      chroma_db_path="data/chroma_db",
      ollama_model="qwen3:4b"
  )
  ```

- **Anthropic Claude**: Configure in `agent.py`
  ```python
  llm = ChatAnthropic(model="claude-3-5-sonnet-20241022", temperature=0)
  ```

### Vector Store

ChromaDB is used for document storage and retrieval:
- Database path: `data/chroma_db`
- Collection name: `team_knowledge`
- Embeddings: Ollama or HuggingFace embeddings

## Quality Control

The system implements several mechanisms to ensure answer quality:

- **Similarity Thresholds**: Prevents responses when retrieved content isn't sufficiently relevant
- **Confidence Scoring**: Evaluates the reliability of generated answers
- **Source Attribution**: Always provides references to source documents
- **Graceful Degradation**: Returns "I don't know" rather than hallucinating

See `rag_quality_control_guide.md` for detailed quality control strategies.

## Development

### Project Structure

- `backend/app/web_app.py`: FastAPI web application with chat endpoints
- `backend/core/agents/qa_agent.py`: Core Q&A logic and RAG chain
- `backend/connectors/confluence.py`: Confluence API integration
- `agent.py`: Standalone CLI version
- `requirements.txt`: Python dependencies

### Adding New Data Sources

1. Create a new connector in `backend/connectors/`
2. Implement data fetching and processing methods
3. Update the vector store with new documents
4. Follow the pattern established in `confluence.py`

### Testing

Run basic tests:
```bash
python basic_test.py
```

## API Endpoints

### Web Interface
- `GET /`: Chat interface homepage
- `POST /chat`: Send message and receive AI response

### Onboarding
- `POST /onboard`: User onboarding endpoint (see `backend/app/onboarding_routes.py`)

## Troubleshooting

### Common Issues

1. **Ollama Connection Failed**:
   - Ensure Ollama is running: `ollama serve`
   - Check the model is installed: `ollama list`

2. **Empty Responses**:
   - Verify vector database has been populated
   - Check Confluence credentials and permissions

3. **Slow Performance**:
   - Consider using a smaller embedding model
   - Optimize chunk size and overlap parameters

## Contributing

1. Follow the existing code style and structure
2. Update documentation for new features
3. Ensure quality control mechanisms are maintained
4. Test with both local and cloud LLM configurations

## License

[Add your license information here]