
## Project Structure

```
honey_project/
├── src/
│   └── mas_api/
│       ├── __init__.py       # Package initialization
│       └── main.py           # FastAPI application and core algorithms
├── tests/
│   ├── __init__.py           # Test package initialization
│   └── test_unit.py          # Unit tests for core algorithms
├── data/
│   ├── sample_data.json      # Sample data for chronological endpoint
│   └── sample_data_with_states.json  # Sample data for streaming endpoint
├── docs/
│   └── interview_questions.md  # Original interview problem description
├── scripts/
│   └── run_server.py         # Server startup script
├── requirements.txt          # Python dependencies
├── pytest.ini              # Pytest configuration
├── Makefile                 # Development commands
└── README.md                # This file
```


### Installation

```bash
# Install dependencies
make install

# Or manually:
pip install -r requirements.txt
```

### Running the Server

```bash
# Using Make
make run

# Or directly
python scripts/run_server.py
```

The API will be available at:
- Main API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Health Check
- **GET** `/health` - Service health status

### Imaging Windows
- **POST** `/imaging-windows/chronological` - Simple chronological ordering of activities
- **POST** `/imaging-windows/streaming` - Streaming windows grouped by activity state

Example request body for chronological endpoint:
```json
{
  "imaging_activities": [
    {
      "activity_id": "ACT-001",
      "start_time": "2024-01-15T10:00:00Z",
      "end_time": "2024-01-15T10:30:00Z"
    }
  ]
}
```

## Testing

```bash
# Run all tests
make test

# Run unit tests only
make test-unit
```

## Core Algorithms

### 1. Chronological Window
Simple chronological ordering of all imaging activities by start time for basic satellite scheduling operations.

### 2. Streaming Windows by State  
Groups activities by state (scheduled/proposed) with temporal non-overlap constraints for advanced satellite operations scheduling.

### Available Make Commands

```bash
make help          # Show available commands
make install       # Install dependencies
make test          # Run all tests
make test-unit     # Run unit tests only
make run           # Start the server
make clean         # Clean build artifacts
``` 