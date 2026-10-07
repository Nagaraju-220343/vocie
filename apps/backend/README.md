# Restaurant Bilingual Voice Call Assistant API

## Phase 2 Setup

### 1. MongoDB Requirement & Local Setup
This project requires MongoDB. You can run MongoDB locally using Docker, or use MongoDB Atlas.
To run locally with Docker:
`docker run -d -p 27017:27017 --name mongodb mongo:latest`

### 2. Environment Variables
Copy `.env.example` to `.env` and fill in the values.
```env
APP_NAME=Restaurant Voice Agent API
APP_ENV=development
LOG_LEVEL=INFO
PORT=8000
CORS_ORIGINS=http://localhost:3000

MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=restaurant_voice_assistant
```

### 3. Start the Backend
Activate the virtual environment and run the server:
```bash
python -m uvicorn app.main:app --reload
```

### 4. Database Seed
To populate the fictional demo data:
```bash
set PYTHONPATH=.
python -m app.db.seed
```

### 5. Running Tests
Tests use a separate `restaurant_voice_assistant_test` database.
```bash
set PYTHONPATH=.
pytest
```

### 6. Code Quality (Ruff & Mypy)
```bash
ruff check .
mypy .
```

### 7. Retell Setup

1. **Retell Account**: Create an account and set up your agent in the Retell Dashboard (https://dashboard.retellai.com/).
2. **Existing Agent**: Obtain your Agent ID from the dashboard. This application connects to the *existing* agent you configured there.
3. **Phone Number**: Configure or import a phone number in Retell and ensure you note it down.
4. **Environment Configuration**: Add the credentials to `.env`:
   ```env
   RETELL_API_KEY=your_retell_api_key
   RETELL_AGENT_ID=your_existing_retell_agent_id
   RETELL_PHONE_NUMBER=+1234567890
   RETELL_WEBHOOK_SECRET=your_webhook_secret
   ```
5. **Testing**:
   Once configured, you can make a controlled outbound test call to your personal phone number via the development endpoint:
   ```bash
   curl -X POST http://localhost:8000/api/voice/outbound \
        -H "Content-Type: application/json" \
        -d '{"phone_number": "+1YOURNUMBER"}'
   ```
   **Note**: Ensure your phone number is in E.164 format. The prompt and agent configurations are fully managed in the Retell Dashboard; FastAPI does not replace or manage the prompt. Webhooks for handling transcript persistence will be added in a future phase.

### 8. Phase 6: Retell Voice Agent Configuration

**Important:** The conversational flow and behavior is configured directly within the Retell Dashboard Prompt, **not** in FastAPI. FastAPI handles data persistence and business logic, while Retell manages the conversation flow.

**1. Agent Configuration (Retell Dashboard):**
- **Language Supported:** English & French
- **Voice:** Choose a suitable bilingual or high-quality voice (e.g., standard conversational).

**2. Intended Conversation Flow / Prompt Instructions:**
You should configure the System Prompt of your Retell Agent in the dashboard with the following rules:
*   **Role & Greeting:** You are a bilingual (French/English) receptionist and order-taking assistant for the restaurant. Start with a natural greeting: "Hello! Welcome to [Restaurant Name]. How can I help you today?" / "Bonjour ! Bienvenue chez [Restaurant Name]. Comment puis-je vous aider ?"
*   **Language Behavior:** Detect the caller's language and continue in that language. Preserve context if the user switches languages mid-conversation.
*   **Intents & Actions:**
    *   **FAQ:** Answer questions only using known/approved restaurant information (e.g., from custom functions or base knowledge). Do NOT invent opening hours, prices, or policies. If unknown, say: "I'm sorry, I don't have that information. I can connect you with a member of our team if you'd like." (or French equivalent).
    *   **ORDER:** Collect required order information progressively: Customer Name, Phone Number, Delivery/Pickup preference, Address (if delivery), Items, Quantities. Before ending, summarize the order. Do NOT say the order has been successfully placed. Say "I've noted your order details" or "I'll make sure the restaurant team receives these details."
    *   **ESCALATION:** If the customer asks for a human, say "Of course. I'll connect you with a member of our team." (or French equivalent). Do not pretend the human has joined the call.
    *   **UNKNOWN:** If the request is unrelated to a restaurant, say "I can help with restaurant information, answer questions about the restaurant, or take an order."
*   **Conversation Guidelines:** Keep it short and natural. Ask only necessary questions. Allow interruptions and corrections.

**3. Manual Testing Procedure:**
Because voice behavior cannot be fully validated through unit tests, execute the following manual tests via the Retell phone number or dashboard:

| Scenario | Language | Input | Expected Result | Pass/Fail | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **A. FAQ** | English | "What time do you close?" | FAQ detected. Correct approved answer. No hallucination. | | |
| **B. FAQ** | French | "Quels sont vos horaires ?" | FAQ detected. Approved French answer. French conversation. | | |
| **C. Order** | English | "I want to place an order." | ORDER detected. Collects info, confirms details, doesn't claim placement. | | |
| **D. Order** | French | "Je voudrais passer une commande." | ORDER detected. Collects info in French, summarizes order. | | |
| **E. Language Switch** | Both | "Bonjour... actually, can we speak English?" | Switches to English. Conversation context preserved. | | |
| **F. Escalation** | English | "I want to speak to a person." | ESCALATION detected. Polite response. No false claim of joining. | | |
| **G. Unknown** | English | "Can you book me a hotel?" | UNKNOWN detected. Safe response. No hallucination. | | |
| **H. Order Correction** | English | "I want two pizzas. Actually, make that three." | Final quantity is correctly identified as 3. | | |
| **I. FAQ during Order** | English | "I want two pizzas. By the way, what time do you close?" | Answers FAQ, then returns to order context without losing info. | | |

*Note: Document the Pass/Fail results during your manual validation.*
