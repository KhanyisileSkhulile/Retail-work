# M14-05 — Integrate chatbot

## Scope

Connect the existing chatbot message-processing service to the application through an HTTP API and browser interface.

## Components

- application/backend/chatbot/service.py: application-facing adapter for the existing chatbot.
- application/backend/chatbot/api.py: HTTP server and JSON endpoints.
- application/frontend/index.html: browser-based chat interface.
- testing/ai/test_chatbot_api.py: API validation and integration tests.

## Run

From the repository root with the project virtual environment active, start the API:

    python -m application.backend.chatbot.api

Open http://127.0.0.1:8000 in a browser.

## Endpoints

- GET /: serves the chatbot interface.
- GET /api/health: reports service health.
- POST /api/chat: accepts a JSON object containing a non-empty message.

## Tests

Run the API tests:

    python -m unittest testing.ai.test_chatbot_api

Run the existing chatbot tests:

    python -m unittest testing.ai.test_chatbot_integration testing.ai.test_chatbot_assistant testing.ai.test_chatbot_intents testing.ai.test_chatbot_queries

Run the restocking integration tests:

    python -m unittest testing.ai.test_restocking_integration

## Limitations

The chatbot uses the available project datasets and existing assistant capabilities. It is not connected to live point-of-sale, store inventory, or supplier systems. This integration is intended for local development and is not a production deployment.
