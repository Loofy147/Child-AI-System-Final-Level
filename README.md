# Child AI System

The Child AI System is a Python-based AI that uses a custom logic engine for reasoning and knowledge integration. Built with Flask, it provides a REST API for interaction, allowing users to query the AI, input new knowledge, and initiate learning cycles.

## Core Features

*   **Logic Engine**: A custom-built inference engine that supports first-order predicate logic, non-monotonic logic, and temporal logic.
*   **Knowledge Integration**: The system can integrate knowledge from unstructured text using NLP techniques, powered by spaCy.
*   **Learning Module**: The AI can learn from feedback, induce new rules, and evaluate its own performance over time.
*   **REST API**: A comprehensive API for interacting with the AI's core functionalities.

## Project Structure

```
.
├── child_ai
│   ├── __init__.py
│   ├── extensions.py
│   ├── knowledge_integration.py
│   ├── learning_module.py
│   ├── logic_engine.py
│   ├── main.py
│   └── routes
├── tests
├── .gitignore
├── config.py
├── manage.py
├── README.md
├── requirements.txt
└── run.py
```

## Setup

### Prerequisites

*   Python 3.8+
*   `venv` for virtual environments

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd child-ai-system
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Download the spaCy model:**
    This is required for the knowledge integration module.
    ```bash
    python -m spacy download en_core_web_sm
    ```

5.  **Initialize the database (optional):**
    You can seed the database with some initial data using the custom `seed_db` command.
    ```bash
    flask seed_db
    ```

6.  **Run the application:**
    ```bash
    python run.py
    ```
    The application will be running at `http://localhost:5000`.

## API Usage

The following are some of the main API endpoints:

*   **`GET /api/ai/query`**: Query the AI with a logical predicate.
    *   **Example**: `GET /api/ai/query?q=Mortal(Socrates)`
*   **`POST /api/ai/add_fact`**: Add a new fact to the knowledge base.
    *   **Example**: `POST /api/ai/add_fact` with JSON body `{"fact": "Human(Plato)"}`
*   **`POST /api/learning/feedback`**: Provide feedback to the AI.
    *   **Example**: `POST /api/learning/feedback` with JSON body `{"input_text": "Plato is a human", "output_str": "Human(Plato)", "feedback": true}`
*   **`POST /api/learning/run_cycle`**: Manually trigger a learning cycle.

## Testing

To run the test suite, use `pytest`:

```bash
python -m pytest
```

The tests will run against an in-memory SQLite database.
