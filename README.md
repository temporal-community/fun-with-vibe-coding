# CFP Tracker

A system to track and notify about upcoming Call for Papers (CFPs) from various sources.

## Features

- Ingests CFPs from multiple sources
- Stores structured CFP data
- Provides query and filtering capabilities
- Sends monthly Slack notifications about upcoming CFPs

## Project Structure

```
cfp_tracker/
├── src/
│   ├── ingestion/         # CFP data ingestion modules
│   ├── models/           # Data models and schemas
│   ├── storage/          # Database and storage operations
│   ├── api/              # API endpoints
│   ├── notifications/    # Slack notification system
│   └── utils/            # Utility functions
├── tests/                # Test suite
├── config/               # Configuration files
└── scripts/              # Utility scripts
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Initialize the database:
```bash
python scripts/init_db.py
```

## Development

- Run tests: `pytest`
- Run linting: `flake8`
- Format code: `black .`

## License

MIT
