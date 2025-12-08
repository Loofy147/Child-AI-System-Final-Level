# Child AI System

This project is a Python-based AI system that uses a custom-built logic engine to perform reasoning and knowledge integration. The system is built with Flask and includes a REST API for interacting with the AI.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd child-ai-system
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Download the spaCy model:**
    ```bash
    python -m spacy download en_core_web_sm
    ```

4.  **Run the application:**
    ```bash
    python run.py
    ```

The application will be available at `http://localhost:5000`.

## Testing

To run the test suite, use the following command:

```bash
python -m pytest
```
