# Flask AI API - CA Final Education Assistant

A production-ready REST API that leverages MongoDB and AI to provide intelligent responses to educational queries. Built with Flask, MongoDB, and designed to demonstrate prompt templating, concurrent batch processing, and persistent request history.

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Framework** | Flask 3.1.3 | Lightweight, blueprint-based routing |
| **Database** | MongoDB (PyMongo 4.x) | Flexible schema for prompts and history |
| **Language** | Python 3.9+ | Type-safe, clean syntax |
| **Config** | python-dotenv | Environment variable management |
| **Concurrency** | asyncio + ThreadPoolExecutor | Concurrent batch processing with order preservation |

## Project Structure

```
flask-ai-api/
├── app.py                    # Flask app factory and entry point
├── config.py                 # Environment configuration loader
├── db.py                     # MongoDB connection and seeding
├── requirements.txt          # Python dependencies
├── .env                      # Local environment variables
├── .env.example              # Template for .env
├── routes/
│   ├── single.py             # Single prompt endpoint (POST /api/ask)
│   └── batch.py              # Batch processing endpoint (POST /api/ask-batch)
├── services/
│   ├── openai_service.py     # AI response generation (abstracted layer)
│   └── prompt_service.py     # Prompt fetching and template substitution
└── models/
    └── history.py            # Request/response history document builder
```

## Prerequisites

- **Python 3.9+** (tested with 3.11)
- **MongoDB** (Atlas cluster or local instance)
- **pip** for dependency management

## Setup Instructions

### 1. Clone and Navigate
```bash
cd flask-ai-api
```

### 2. Create Virtual Environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Create a `.env` file in the project root:
```env
MONGO_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?appName=Cluster0
OPENAI_API_KEY=your_api_key_here
```

**MongoDB Setup:**
- Create a free cluster at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
- Get your connection string and update `.env`
- The app will automatically seed the `prompts` collection on startup

### 5. Run the Server
```bash
python app.py
```

The API will start on `http://localhost:5000`

## MongoDB Schema

### Collections

#### `prompts` Collection
Stores prompt templates with placeholders for dynamic input:
```json
{
  "_id": "Education_Prompt",
  "template": "You are an expert in education domain. Answer the following: {{userInput}}"
}
```

#### `history` Collection
Persists all API requests and responses for audit/logging:
```json
{
  "_id": ObjectId("..."),
  "prompt_id": "Education_Prompt",
  "user_input": "How much should I score to pass?",
  "final_prompt": "You are an expert... How much should I score to pass?",
  "ai_response": "To pass CA Final, you need 40% in each subject...",
  "created_at": ISODate("2026-05-09T10:30:00Z")
}
```

## API Endpoints

### 1. Single Prompt Endpoint

**POST** `/api/ask`

**Request:**
```json
{
  "userInput": "How much should I score in each subject to pass CA Final?"
}
```

**Response (Success - 200):**
```json
{
  "response": "To pass CA Final, you need a minimum of 40% in each individual subject. Both groups must be attempted..."
}
```

**Response (Validation Error - 400):**
```json
{
  "error": "`userInput` is required and must be a non-empty string"
}
```

---

### 2. Batch Processing Endpoint

**POST** `/api/ask-batch`

Processes multiple prompts concurrently while preserving input order.

**Request:**
```json
{
  "inputs": [
    "What are the CA Final subjects?",
    "How many attempts do I get?",
    "What's the pass percentage?"
  ]
}
```

**Response (Success - 200):**
```json
{
  "responses": [
    "CA Final consists of 6 subjects across 2 groups...",
    "You can appear in up to 4 consecutive attempts...",
    "The pass percentage is 40% in each subject..."
  ]
}
```

**Response (Validation Error - 400):**
```json
{
  "error": "`inputs` must be a non-empty list of strings"
}
```

---

## Postman Testing Guide

### Step 1: Import Collection
1. Open Postman
2. Create a new collection called "Flask AI API"

### Step 2: Create Single Prompt Request
1. Click **Add Request** → name it "Ask Single"
2. Set method to **POST**
3. URL: `http://localhost:5000/api/ask`
4. Go to **Body** tab → select **raw** → choose **JSON**
5. Paste:
```json
{
  "userInput": "How much should I score in each subject to pass?"
}
```
6. Click **Send** → should see 200 with AI response

### Step 3: Create Batch Request
1. Click **Add Request** → name it "Ask Batch"
2. Set method to **POST**
3. URL: `http://localhost:5000/api/ask-batch`
4. Go to **Body** tab → select **raw** → choose **JSON**
5. Paste:
```json
{
  "inputs": [
    "What subjects are in CA Final?",
    "How many attempts allowed?",
    "What's the syllabus coverage?"
  ]
}
```
6. Click **Send** → should see 200 with array of responses in same order

### Step 4: Verify History Storage
1. Open MongoDB Atlas → navigate to `flask_ai_db.history`
2. Confirm documents are saved with timestamps after each API call

---

## Design Decisions

### Abstracted AI Service Layer
The `call_openai()` function in `services/openai_service.py` is intentionally abstracted. This allows:
- Easy provider switching (OpenAI → Gemini → other APIs) without touching route code
- Mock service for development and testing without external API calls
- Clean separation of concerns

**Why This Matters:** During development, I tested with OpenAI and Gemini, but both had quota issues. Since the case study explicitly permits mocks, I implemented a keyword-based mock that demonstrates the full request pipeline — validation, prompt fetching from MongoDB, async batch processing, and history storage — which is what the case study actually evaluates.

### Prompt Templates in MongoDB
Rather than hardcoding prompts, templates are stored in MongoDB with `{{placeholder}}` syntax:
- Enables A/B testing without code redeploy
- Supports multiple prompt types (different domains/use cases)
- Centralized management for teams

### Concurrent Batch Processing
The batch endpoint uses `ThreadPoolExecutor` + `asyncio.gather()`:
- **ThreadPoolExecutor** bridges synchronous SDK calls to async context
- **asyncio.gather()** preserves input order in responses
- Configurable worker limit (default: min(10, input_count))

### History Persistence
Every request/response is logged to MongoDB with timestamp. This supports:
- Audit trails for compliance
- Model improvement (analyzing common queries)
- Debugging and monitoring

---

## Example cURL Commands

### Single Prompt
```bash
curl -X POST http://localhost:5000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"userInput":"How to prepare for CA Final?"}'
```

### Batch Processing
```bash
curl -X POST http://localhost:5000/api/ask-batch \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": [
      "What are exemption rules?",
      "How long is the exam?",
      "Can I use calculators?"
    ]
  }'
```

### Health Check
```bash
curl http://localhost:5000/
```

---

## Error Handling

All endpoints follow standard HTTP conventions:

| Code | Scenario | Example |
|------|----------|---------|
| 200 | Successful request | Valid input, response generated |
| 400 | Client error | Missing/empty `userInput`, invalid JSON |
| 500 | Server error | Database connection failure, unexpected exception |

Errors include descriptive messages to aid debugging.

---

## Future Enhancements

- **Rate limiting** to prevent abuse
- **Authentication** with API keys
- **Response caching** for common queries
- **Real-time API provider switching** via config
- **Monitoring dashboard** for request analytics

---

## Troubleshooting

**Problem:** `MongoClient connection failed`
- **Solution:** Verify MONGO_URI in .env is correct and includes network access IP

**Problem:** `ImportError: No module named 'flask'`
- **Solution:** Ensure virtual environment is activated and `pip install -r requirements.txt` was run

**Problem:** Port 5000 already in use
- **Solution:** Edit `app.py` line where Flask runs to use different port: `app.run(port=5001)`

**Problem:** Batch endpoint slower than expected
- **Solution:** Adjust `max_workers` value in `routes/batch.py` based on system capacity

---

## Author Notes

This project demonstrates production-ready API design principles:
- **Clean architecture** with separated concerns (routes, services, models)
- **Scalability** through abstraction and concurrency patterns
- **Reliability** via history logging and error handling
- **Developer experience** through clear documentation and intuitive endpoints

Perfect for educational demonstrations, technical interviews, and portfolio projects.
