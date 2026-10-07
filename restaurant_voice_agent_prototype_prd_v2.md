# PRD --- Restaurant Bilingual Voice Call Assistant Prototype

**Document status:** Prototype implementation specification — Revised for live dashboard synchronization\
**Target user:** French restaurant owner / restaurant staff\
**Primary implementation target:** Coding agent\
**Prototype provider:** Retell AI\
**Frontend:** Next.js / React\
**Backend:** Python + FastAPI + LangChain\
**Database:** MongoDB\
**Deployment target:** Local first, then Render/Vercel if needed\
**Primary languages:** French and English\
**Design direction:** Light-theme version of the selected conversational
dashboard concept

------------------------------------------------------------------------

## 1. Executive Summary

Build a working prototype of a bilingual AI voice assistant for a French
restaurant.

The restaurant currently receives roughly 30--40 calls per day for:

1.  Product/food orders.
2.  Repeated restaurant questions such as opening hours, menu
    information, delivery area, location, payment methods, and similar
    FAQs.

The prototype should demonstrate that an AI agent can:

-   Receive an incoming phone call.
-   Speak naturally with the caller in French or English.
-   Understand whether the caller wants to place an order or ask a
    restaurant question.
-   Answer simple, predefined restaurant FAQs without inventing
    information.
-   Collect structured order information.
-   Capture customer name, phone number, and delivery address.
-   Store the call transcript.
-   Store call metadata.
-   Store the extracted order.
-   Display live call status, transcript, detected intent, customer details, and order state in the dashboard while the call is still in progress.
-   Synchronize live backend state to the dashboard without requiring a browser refresh.
-   Allow human escalation.
-   Support a demo "Make a Call" flow.
-   Support a post-call review/correction flow.
-   Store corrections/feedback so future agent configuration can be
    improved.

This is a **prototype**, not a production deployment.

The objective is to prove the complete product workflow with minimal
engineering and minimal cost before investing in production-grade
telephony, LLM orchestration, compliance, observability, security, and
learning systems.

------------------------------------------------------------------------

# 2. Product Goal

## Primary goal

Demonstrate this complete journey:

``` text
Customer
   |
   | Phone call
   v
Retell Voice Agent
   |
   | French / English conversation
   v
Intent detection
   |
   +---- Restaurant FAQ ----> Answer from approved knowledge
   |
   +---- Product Order ----> Collect order details
   |
   +---- Escalation --------> Human handoff
   |
   v
Transcript + structured result
   |
   v
Python/FastAPI Backend
   |
   +---- Live state events ----> Socket.IO ----> Light-theme Dashboard
   |
   v
MongoDB
   |
   v
Light-theme Dashboard
```

The client should be able to look at the dashboard and understand:

> "A customer called, the AI answered, spoke French, understood the
> request, captured the order/customer information, saved the
> transcript, and can escalate to a human."

------------------------------------------------------------------------

# 3. Prototype Success Criteria

The prototype is successful when all of the following work end-to-end.

### Scenario A --- Incoming order

A customer calls the configured restaurant number.

The AI:

1.  Answers in French.
2.  Understands the customer wants to order.
3.  Collects one or more menu items.
4.  Collects quantity.
5.  Collects customer name.
6.  Confirms/uses the caller phone number.
7.  Collects delivery address.
8.  Repeats the order back for confirmation.
9.  Ends the call naturally.

After the call:

-   Transcript exists.
-   Customer information exists.
-   Order exists.
-   Call is classified as `ORDER`.
-   Dashboard shows the call.
-   Dashboard shows extracted order information.

### Scenario B --- Restaurant FAQ

Customer asks something like:

> "À quelle heure êtes-vous ouverts ?"

The agent answers only from approved restaurant information.

The call is classified as:

`FAQ`

The answer appears in the transcript.

### Scenario C --- Human escalation

Customer says:

> "Je voudrais parler à quelqu'un."

The agent recognizes an escalation request and triggers the escalation
path.

Dashboard shows:

`ESCALATED`

### Scenario D --- English

Customer speaks English.

The agent responds in English and continues the conversation.

### Scenario E --- Post-call review

Staff can open a completed call and:

-   Read transcript.
-   Review extracted information.
-   Edit incorrect customer/order fields.
-   Mark extraction as correct/incorrect.
-   Add a correction note.

The correction is stored for future improvement.

------------------------------------------------------------------------

# 4. Important Prototype Principle

Do NOT build the production architecture now.

Do NOT start with:

-   Complex LangGraph orchestration.
-   Fine-tuning.
-   Custom STT infrastructure.
-   Custom TTS infrastructure.
-   Distributed queues.
-   Kubernetes.
-   Complex event buses.
-   Vector databases unless actually needed.
-   Autonomous self-modifying prompts.
-   Production payment/order integrations.
-   Restaurant POS integration.
-   Advanced analytics.

First prove the call workflow.

------------------------------------------------------------------------

# 5. Voice Provider Decision

## Primary provider: Retell AI

Retell is the initial provider for this prototype.

The current Retell pricing page states that the pay-as-you-go entry
point starts at \$0, includes \$10 in free credits, full platform
access, transcripts, simulation testing, webhooks/API access, and 20
concurrent calls. Retell's current product material also states that new
accounts can start without a credit card. Verify the current
account/signup terms before implementation because provider pricing and
trial conditions can change.

Retell is suitable because it handles most of the difficult voice
infrastructure:

-   Phone calls.
-   Voice agent.
-   Speech processing.
-   TTS.
-   Conversation handling.
-   Call analytics.
-   Transcripts.
-   Webhooks.
-   Simulation testing.
-   Agent configuration.

For the prototype, do not independently implement the entire voice
pipeline.

### Provider abstraction requirement

The backend must not deeply couple business logic to Retell.

Create a provider abstraction:

``` text
VoiceProvider
   |
   +-- RetellVoiceProvider
   |
   +-- FutureVapiProvider
   |
   +-- FutureTwilioProvider
```

The first implementation only needs:

``` text
RetellVoiceProvider
```

But the interface must make replacement possible later.

------------------------------------------------------------------------

# 6. Prototype Scope

## In scope

### Calling

-   Incoming call.
-   Outgoing/demo call.
-   Call status.
-   Call duration.
-   Caller number.
-   Agent number.
-   Call ID.

### Conversation

-   French.
-   English.
-   Restaurant FAQ.
-   Product order.
-   Human escalation.
-   Order confirmation.

### Data extraction

-   Customer name.
-   Customer phone.
-   Delivery address.
-   Ordered items.
-   Quantity.
-   Optional notes.
-   Intent.
-   Language.
-   Escalation status.
-   Call summary.

### Storage

-   Calls.
-   Transcripts.
-   Orders.
-   Customers.
-   FAQ knowledge.
-   Corrections/feedback.

### Dashboard

-   Dashboard.
-   Live Calls.
-   Live transcript and live order state.
-   Live call status and elapsed time.
-   Call History.
-   Orders.
-   FAQ/Knowledge.
-   Customers.
-   Call detail page.

### Prototype learning

Controlled feedback only.

Example:

``` text
Call
 ↓
Extraction
 ↓
Human review
 ↓
Correction
 ↓
Feedback record
 ↓
Future prompt/FAQ improvement
```

The system must NOT automatically rewrite its own system prompt.

------------------------------------------------------------------------

# 7. Out of Scope

Do not implement these in the first prototype:

-   Real restaurant POS integration.
-   Payment processing.
-   Credit-card collection.
-   Automated refunds.
-   Fully autonomous order submission to kitchen.
-   Production customer authentication.
-   Production-grade GDPR compliance implementation.
-   Multi-tenant architecture.
-   Role-based access control.
-   Fine-tuning.
-   Reinforcement learning.
-   Autonomous prompt mutation.
-   Complex vector retrieval.
-   Advanced sentiment analysis.
-   Voice cloning.
-   Production call recording retention policies.
-   Advanced billing.
-   Automated staff scheduling.
-   WhatsApp integration.
-   SMS ordering.
-   Complex CRM integration.

------------------------------------------------------------------------

# 8. UX / UI Direction

Use the selected **light-theme conversational dashboard** direction.

The visual style should be:

-   Clean.
-   Modern.
-   Professional.
-   Light background.
-   Dark navy sidebar.
-   Blue/purple primary accents.
-   Green success states.
-   Red escalation/end-call states.
-   Rounded cards.
-   Clear typography.
-   Large live-call visualization.
-   Transcript in conversational bubbles.
-   Order details visible without opening another page.

The dashboard should feel like a real operations product, not a generic
admin panel.

------------------------------------------------------------------------

# 9. Main Dashboard Screens

## 9.1 Dashboard

Show:

-   Calls today.
-   Orders taken.
-   Questions answered.
-   Escalated calls.
-   Current active calls.
-   Recent calls.
-   Recent orders.

Example:

``` text
Calls Today        32
Orders Taken       18
Queries Answered   11
Escalated           3
```

Prototype values should be calculated from database data, not hardcoded.

------------------------------------------------------------------------

## 9.2 Live Call

This is the most important screen.

Layout:

``` text
------------------------------------------------------------
| Live Call                           | Live Transcript      |
|                                     |                      |
|       Voice waveform                | Customer             |
|                                     | Bonjour...           |
|       AI Agent                      |                      |
|       Speaking...                   | Agent                |
|                                     | Bonjour, comment...  |
|       Mute  End  Transfer           |                      |
------------------------------------------------------------
| Detected Information                                     |
|                                                          |
| Intent: Product Order                                    |
| Name: Pierre Dupont                                     |
| Phone: +33...                                           |
| Address: 12 Rue de Paris                                |
|                                                          |
| Ordered Items                                            |
| 2 × Pizza Margherita                                    |
| 1 × Coca Cola                                           |
|                                                          |
| [Save Order] [Escalate to Human]                        |
------------------------------------------------------------
```

------------------------------------------------------------------------

## 9.3 Call History

Columns:

-   Time.
-   Phone.
-   Language.
-   Intent.
-   Duration.
-   Status.
-   Summary.
-   Recording/transcript availability.

Filters:

-   All.
-   Orders.
-   FAQ.
-   Escalated.
-   French.
-   English.

------------------------------------------------------------------------

## 9.4 Call Detail

Show:

-   Call metadata.
-   Full transcript.
-   Audio playback if available.
-   Extracted information.
-   Order.
-   Summary.
-   Escalation reason.
-   Feedback/correction panel.

------------------------------------------------------------------------

## 9.5 Orders

Show:

-   Customer.
-   Phone.
-   Address.
-   Items.
-   Quantity.
-   Status.
-   Call ID.
-   Created time.

Statuses:

``` text
PENDING_CONFIRMATION
CONFIRMED
CANCELLED
REVIEW_REQUIRED
```

------------------------------------------------------------------------

## 9.6 FAQ / Knowledge

Prototype restaurant knowledge:

``` text
Restaurant name
Opening hours
Address
Phone
Delivery area
Menu
Payment methods
Typical preparation time
Reservation policy
Cancellation policy
Special requests policy
```

Staff should be able to edit FAQs.

------------------------------------------------------------------------

## 9.7 Customers

Show:

-   Name.
-   Phone.
-   Address.
-   Number of calls.
-   Last call.
-   Orders.

------------------------------------------------------------------------

# 10. Restaurant Demo Knowledge

Create seed data.

Example:

``` json
{
  "restaurantName": "Le Gourmet",
  "language": ["fr", "en"],
  "openingHours": {
    "monday": "11:00-22:00",
    "tuesday": "11:00-22:00",
    "wednesday": "11:00-22:00",
    "thursday": "11:00-22:00",
    "friday": "11:00-23:00",
    "saturday": "11:00-23:00",
    "sunday": "12:00-21:00"
  },
  "deliveryArea": "Within 5 km of the restaurant",
  "paymentMethods": [
    "Cash",
    "Card"
  ],
  "address": "12 Rue de Paris, 75001 Paris"
}
```

Use obviously fictional/demo restaurant data.

Do not pretend this data represents the real client's restaurant.

------------------------------------------------------------------------

# 11. Agent Behavior

## Agent identity

The AI should introduce itself as the restaurant's virtual assistant.

Example French opening:

``` text
Bonjour, vous êtes bien chez Le Gourmet.
Je suis l'assistant virtuel du restaurant.
Comment puis-je vous aider ?
```

Example English opening:

``` text
Hello, you've reached Le Gourmet.
I'm the restaurant's virtual assistant.
How can I help you today?
```

------------------------------------------------------------------------

# 12. Core Agent Rules

The agent must follow these rules.

### Rule 1 --- Never invent restaurant information

If the answer is not in the approved restaurant knowledge:

``` text
Je ne veux pas vous donner une information incorrecte.
Je peux vous mettre en relation avec quelqu'un du restaurant.
```

Then escalate when appropriate.

### Rule 2 --- Order confirmation

Before finalizing an order:

-   Repeat items.
-   Repeat quantities.
-   Repeat name.
-   Repeat delivery address.
-   Ask for confirmation.

### Rule 3 --- Missing information

Ask one missing field at a time.

Do not ask for five pieces of information in one sentence.

### Rule 4 --- Unclear item

Do not guess.

Ask:

``` text
Pouvez-vous répéter le nom du produit, s'il vous plaît ?
```

### Rule 5 --- Human request

Immediately trigger escalation flow.

### Rule 6 --- Complaint/refund

Escalate.

### Rule 7 --- Language

Continue in the caller's language unless the caller requests another
language.

------------------------------------------------------------------------

# 13. Intent Model

The prototype needs only four intents:

``` text
ORDER
FAQ
ESCALATION
UNKNOWN
```

Optional later:

``` text
CANCELLATION
COMPLAINT
RESERVATION
OTHER
```

Do not create a huge intent taxonomy in the first prototype.

------------------------------------------------------------------------

# 14. Order Data Model

Example:

``` json
{
  "items": [
    {
      "name": "Pizza Margherita",
      "quantity": 2,
      "notes": ""
    }
  ],
  "customerName": "Pierre Dupont",
  "phone": "+33612345678",
  "address": "12 Rue de Paris, 75001",
  "orderType": "DELIVERY",
  "status": "CONFIRMED"
}
```

------------------------------------------------------------------------

# 15. MongoDB Collections

Use these collections.

## calls

``` text
_id
providerCallId
direction
fromNumber
toNumber
language
intent
status
startedAt
endedAt
durationSeconds
transcript
summary
recordingUrl
escalated
escalationReason
createdAt
updatedAt
```

## orders

``` text
_id
callId
customerId
items[]
customerName
phone
address
orderType
status
notes
createdAt
updatedAt
```

## customers

``` text
_id
name
phone
address
callCount
lastCallAt
createdAt
updatedAt
```

## faqs

``` text
_id
question
answerFr
answerEn
category
active
updatedAt
```

## feedback

``` text
_id
callId
field
originalValue
correctedValue
reason
createdBy
createdAt
```

------------------------------------------------------------------------

# 16. Call Status Model

``` text
INITIATED
RINGING
IN_PROGRESS
COMPLETED
FAILED
ESCALATED
```

Realtime dashboard connection state is separate from call status. Use `CONNECTED`, `RECONNECTING`, and `DISCONNECTED` only for the dashboard socket connection.

------------------------------------------------------------------------

# 17. Backend API

Implement these endpoints.

## Health

``` http
GET /api/health
```

Expected:

``` json
{
  "status": "ok"
}
```

------------------------------------------------------------------------

## Calls

``` http
GET /api/calls
GET /api/calls/:id
```

Filters:

``` text
?intent=ORDER
?status=COMPLETED
?language=fr
```

------------------------------------------------------------------------

## Orders

``` http
GET /api/orders
GET /api/orders/:id
POST /api/orders
PATCH /api/orders/:id
```

------------------------------------------------------------------------

## Customers

``` http
GET /api/customers
GET /api/customers/:id
```

------------------------------------------------------------------------

## FAQ

``` http
GET /api/faqs
POST /api/faqs
PATCH /api/faqs/:id
DELETE /api/faqs/:id
```

------------------------------------------------------------------------

## Feedback

``` http
POST /api/feedback
GET /api/feedback
```

------------------------------------------------------------------------

## Voice Provider

``` http
POST /api/voice/outbound
POST /api/webhooks/retell
```

The exact Retell webhook payload must be mapped through a dedicated
adapter.

Do not let Retell-specific payload fields spread throughout controllers.

## Realtime connection

Socket.IO is not exposed as a normal REST endpoint. The frontend connects to the FastAPI Socket.IO server using the configured backend URL.

Required realtime concepts:

``` text
connect
join_call_room(callId)
leave_call_room(callId)
subscribe_live_calls()
unsubscribe_live_calls()
```

The backend must emit normalized events only. The frontend must never consume raw Retell webhook payloads.

------------------------------------------------------------------------

# 18. Provider Adapter

Create:

``` text
VoiceProvider
```

Interface concept:

``` ts
interface VoiceProvider {
  createOutboundCall(input: OutboundCallInput): Promise<CallResult>;
  getCall(callId: string): Promise<CallResult>;
  normalizeWebhook(payload: unknown): NormalizedCallEvent;
}
```

Retell implementation:

``` text
RetellVoiceProvider
```

The application should consume:

``` text
NormalizedCallEvent
```

instead of raw Retell payloads.

------------------------------------------------------------------------

# 19. Normalized Call Event

Create an internal event format:

``` ts
type NormalizedCallEvent = {
  provider: "retell";
  providerCallId: string;
  eventType:
    | "call_started"
    | "call_ended"
    | "transcript_updated"
    | "call_analyzed"
    | "call_failed";

  timestamp: string;

  call?: {
    direction?: "inbound" | "outbound";
    fromNumber?: string;
    toNumber?: string;
    durationSeconds?: number;
  };

  transcript?: TranscriptMessage[];

  analysis?: {
    language?: "fr" | "en" | "unknown";
    intent?: "ORDER" | "FAQ" | "ESCALATION" | "UNKNOWN";
    summary?: string;
  };
};
```

------------------------------------------------------------------------

# 20. Transcript Model

``` ts
type TranscriptMessage = {
  id?: string;
  speaker: "customer" | "agent";
  text: string;
  timestamp?: string;
  language?: "fr" | "en" | "unknown";
  sequence?: number;
};
```

------------------------------------------------------------------------

# 21. Order Extraction Strategy

For the prototype, prioritize reliability over cleverness.

Pipeline:

``` text
Transcript
   ↓
Normalization
   ↓
Intent classification
   ↓
Structured extraction
   ↓
Validation
   ↓
Save
```

Validation rules:

### Customer name

-   Must be non-empty for confirmed order.
-   Should not be a generic word such as "oui".

### Phone

-   Must be present.
-   Normalize whitespace.
-   Preserve country code.

### Address

-   Required for delivery.
-   Do not invent missing address.

### Items

-   At least one item.
-   Quantity must be \>= 1.
-   Product should match the demo menu where possible.

If extraction is incomplete:

``` text
REVIEW_REQUIRED
```

Do not mark the order confirmed.

------------------------------------------------------------------------

# 22. Hallucination Prevention

This is a core requirement.

The agent must not:

-   Invent menu items.
-   Invent prices.
-   Invent delivery areas.
-   Invent opening hours.
-   Invent policies.
-   Invent availability.
-   Guess unclear customer information.

Use a small approved knowledge source.

The prototype should prefer:

``` text
KNOWN ANSWER
```

over:

``` text
LLM GENERAL KNOWLEDGE
```

For unsupported questions:

``` text
UNKNOWN → HUMAN
```

------------------------------------------------------------------------

# 23. Human-in-the-Loop

Prototype escalation options:

### Automatic escalation

Triggered when:

-   Customer asks for human.
-   Complaint.
-   Refund/cancellation.
-   Unknown policy.
-   Repeated misunderstanding.
-   High-risk or unsupported request.

### Dashboard escalation

Staff can click:

``` text
Escalate to Human
```

The UI should show:

``` text
Escalation reason
Call ID
Customer
Transcript
Current order
```

------------------------------------------------------------------------

# 24. Learning / Feedback

Do not implement ML training.

Implement a feedback ledger.

Example:

``` json
{
  "callId": "call_123",
  "field": "items[0].name",
  "originalValue": "Pizza Margherita",
  "correctedValue": "Pizza Margherita Special",
  "reason": "Agent extracted wrong menu item"
}
```

Later this dataset can be used to improve:

-   System prompt.
-   FAQ examples.
-   Product aliases.
-   Extraction rules.
-   Agent flow.

------------------------------------------------------------------------

# 25. Product Aliases

A useful prototype feature.

Example:

``` json
{
  "canonical": "Pizza Margherita",
  "aliases": [
    "margherita",
    "pizza marguerita",
    "pizza margarita",
    "la margherita"
  ]
}
```

This reduces extraction failures without requiring model training.

------------------------------------------------------------------------

# 26. Real-Time Dashboard Synchronization Strategy

Live dashboard synchronization is a core prototype requirement because it is one of the strongest parts of the client demonstration. The dashboard must visibly react while the phone call is happening.

The realtime layer should remain small and deterministic. Do not introduce Kafka, Redis Streams, a distributed event bus, or a separate realtime database. Socket.IO is sufficient for the prototype.

## 26.1 Source of truth

MongoDB remains the persistent source of truth. LangGraph holds the live business/order state during the conversation. Socket.IO is only the delivery mechanism that pushes normalized state changes to connected dashboard clients.

``` text
Retell
  ↓
FastAPI webhook / custom function
  ↓
LangGraph live state
  ↓
Validate + persist
  ↓
MongoDB
  ↓
Realtime Event Publisher
  ↓
Socket.IO
  ↓
Next.js Dashboard
```

The frontend must never treat a Socket.IO event as permanent storage. After reconnecting or opening a call detail page, it must fetch the authoritative state through the REST API.

## 26.2 What updates live

During an active call, the dashboard should update when any meaningful state changes:

-   Call created/started.
-   Call status changes.
-   Call language detected/changed.
-   Intent detected/changed.
-   New transcript message becomes available.
-   Customer name is captured.
-   Phone number is captured or normalized.
-   Delivery address is captured.
-   Order item is added.
-   Order item quantity changes.
-   Order item is removed.
-   Order validation status changes.
-   Human escalation is triggered.
-   Call ends.
-   Final call analysis is available.

Do not stream every internal LangGraph transition. Only publish user-visible business events.

## 26.3 Event flow

Every realtime event follows this pattern:

``` text
1. Retell sends webhook or invokes a custom function
              ↓
2. FastAPI validates and normalizes the input
              ↓
3. LangGraph updates live call/order state
              ↓
4. Backend validates the new state
              ↓
5. MongoDB is updated when persistence is required
              ↓
6. Backend creates a normalized dashboard event
              ↓
7. Socket.IO emits event to the relevant dashboard room
              ↓
8. Next.js updates local UI state
```

The backend should update its state before emitting the corresponding event. This prevents the dashboard from showing an event that the backend failed to persist.

## 26.4 Call rooms

Use call-specific Socket.IO rooms.

Example:

``` text
room: call:{callId}
```

The Live Call page joins the room when opened. The frontend should also subscribe to a general active-calls channel for the dashboard summary/list.

Recommended channels:

``` text
restaurant:live-calls
call:{callId}
```

For the prototype, a single restaurant does not require complex tenant/channel authorization. Still, keep room naming explicit so multi-tenant support can be added later.

## 26.5 Normalized realtime event

Create an internal event contract independent of Retell:

``` json
{
  "event": "transcript.updated",
  "callId": "call_123",
  "sequence": 17,
  "timestamp": "2026-10-07T10:30:15Z",
  "payload": {
    "message": {
      "speaker": "customer",
      "text": "Bonjour, je voudrais deux pizzas margherita.",
      "language": "fr",
      "timestamp": "2026-10-07T10:30:15Z"
    }
  }
}
```

Required common fields:

``` text
event
callId
sequence
timestamp
payload
```

The `sequence` number is important for ordering events and safely ignoring stale/duplicated realtime messages.

## 26.6 Recommended event types

``` text
call.started
call.status.updated
call.language.updated
call.intent.updated
transcript.updated
customer.updated
order.updated
order.validation.updated
call.escalated
call.ended
call.analysis.updated
```

## 26.7 Frontend update behavior

The frontend must use event payloads to update the current screen without a full-page refresh.

Example:

``` text
Customer says: "Deux margheritas."
          ↓
Backend validates order action
          ↓
order.updated
          ↓
Live Call UI immediately shows:
2 × Pizza Margherita
```

For transcript events, append only the new message when the event contains a new message. Do not repeatedly replace the entire transcript unless the provider sends a corrected transcript snapshot.

For order events, prefer sending the normalized current order state so the frontend does not need to reproduce business logic.

## 26.8 Reconnection behavior

The dashboard must handle temporary Socket.IO disconnections gracefully.

When disconnected:

-   Show a small `Reconnecting...` or `Live connection interrupted` indicator.
-   Do not clear the current call state.
-   Automatically reconnect.

After reconnect:

``` text
Socket reconnects
      ↓
Frontend requests GET /api/v1/calls/{id}
      ↓
Backend returns authoritative current state
      ↓
Frontend reconciles local state
      ↓
Live updates continue
```

The REST fetch is the recovery mechanism; do not build a complex event replay service for the prototype.

## 26.9 Duplicate and out-of-order events

Realtime delivery must be treated as at-least-once for application purposes.

The frontend should ignore an event when:

``` text
event.callId != currently displayed call
```
or when its `sequence` is older than the latest processed sequence for that call.

The backend must also make webhook processing idempotent.

## 26.10 Dashboard states

The Live Call UI must clearly distinguish:

``` text
CONNECTING
RINGING
IN_PROGRESS
ESCALATED
COMPLETED
FAILED
RECONNECTING
```

Do not use a misleading green `LIVE` state when the socket is disconnected.

## 26.11 Realtime failure must not break the call

Socket.IO is a dashboard delivery layer, not part of the voice conversation path. If Socket.IO fails:

``` text
Retell → FastAPI → LangGraph → MongoDB
```
continues normally.

The dashboard may temporarily become stale, but the phone conversation and backend persistence must continue.

## 26.12 Demo requirement

The client demo must visibly demonstrate the realtime behavior:

``` text
Customer speaks
      ↓
AI responds
      ↓
Dashboard transcript changes
      ↓
Order item appears
      ↓
Customer provides address
      ↓
Address appears
      ↓
Customer confirms
      ↓
Order becomes CONFIRMED
      ↓
Call ends
      ↓
Call becomes COMPLETED
```

This live synchronization is a primary demo feature, not a cosmetic enhancement.

------------------------------------------------------------------------

# 27. Folder Structure

Use this structure.

``` text
restaurant-voice-agent/
│
├── apps/
│   │
│   ├── web/
│   │   ├── app/
│   │   │   ├── dashboard/
│   │   │   ├── live-calls/
│   │   │   ├── calls/
│   │   │   ├── orders/
│   │   │   ├── customers/
│   │   │   ├── knowledge/
│   │   │   └── settings/
│   │   │
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   ├── calls/
│   │   │   ├── transcript/
│   │   │   ├── orders/
│   │   │   ├── customers/
│   │   │   └── ui/
│   │   │
│   │   ├── lib/
│   │   ├── hooks/
│   │   ├── types/
│   │   └── tests/
│   │
│   └── api/
│       ├── app/
│       │   ├── main.py
│       │   ├── config/
│       │   ├── api/
│       │   │   ├── routes/
│       │   │   └── dependencies.py
│       │   ├── models/
│       │   ├── schemas/
│       │   ├── services/
│       │   ├── agents/
│       │   │   ├── chains/
│       │   │   ├── prompts/
│       │   │   ├── tools/
│       │   │   └── state/
│       │   ├── providers/
│       │   │   └── retell/
│       │   ├── webhooks/
│       │   ├── websocket/
│       │   ├── repositories/
│       │   ├── utils/
│       │   └── logging/
│       │
│       ├── tests/
│       │   ├── unit/
│       │   ├── integration/
│       │   ├── e2e/
│       │   └── fixtures/
│       │
│       ├── requirements.txt
│       └── pyproject.toml
│
├── packages/
│   └── shared/
│       ├── types/
│       ├── constants/
│       └── validation/
│
├── scripts/
│   ├── seed.ts
│   └── test-provider.ts
│
├── .env.example
├── docker-compose.yml
├── package.json
├── README.md
└── PRD.md
```

------------------------------------------------------------------------

# 28. Environment Variables

Create:

``` text
# Backend
PORT=
MONGODB_URI=

# Retell
RETELL_API_KEY=
RETELL_AGENT_ID=
RETELL_PHONE_NUMBER=
RETELL_PUBLIC_KEY=

# Frontend
NEXT_PUBLIC_API_URL=
NEXT_PUBLIC_RETELL_PUBLIC_KEY=

# Optional
LOG_LEVEL=
NODE_ENV=
```

Never commit real secrets.

------------------------------------------------------------------------

# 29. Development Order

The coding agent MUST build the system in this order.

Do not jump directly to the dashboard.

------------------------------------------------------------------------

## Phase 0 --- Project bootstrap

### Build

-   Monorepo structure.
-   Python.
-   Next.js frontend.
-   FastAPI backend.
-   Environment configuration.
-   ESLint.
-   Prettier.
-   Basic logging.
-   Health endpoint.

### Sanity checks

``` bash
python -m venv .venv
pip install -r apps/api/requirements.txt
pytest
ruff check .
mypy apps/api
```

Expected:

``` text
No Python errors.
No lint errors.
Health endpoint returns 200.
```

### Test

``` http
GET /api/health
```

Expected:

``` json
{
  "status": "ok"
}
```

------------------------------------------------------------------------

# 30. Phase 1 --- MongoDB

### Build first

Create:

-   Call model.
-   Order model.
-   Customer model.
-   FAQ model.
-   Feedback model.

Add indexes:

``` text
calls.providerCallId
calls.createdAt
calls.intent
calls.status
orders.createdAt
customers.phone
```

### Seed data

Create demo:

-   Restaurant.
-   Menu.
-   FAQs.
-   5 example calls.
-   3 example customers.
-   3 example orders.

### Sanity checks

Start MongoDB.

Run:

``` bash
npm run seed
```

Expected:

``` text
Seed completed successfully.
5 calls inserted.
3 customers inserted.
3 orders inserted.
FAQ data inserted.
```

### Test cases

#### DB-001

Create a call.

Expected:

``` text
Call exists with unique _id.
```

#### DB-002

Create customer with phone.

Expected:

``` text
Customer stored.
```

#### DB-003

Create duplicate providerCallId.

Expected:

``` text
Duplicate is rejected or safely upserted.
No duplicate call records.
```

------------------------------------------------------------------------

# 31. Phase 2 --- Restaurant Knowledge

Build a simple FAQ service.

``` text
FaqService
```

Methods:

``` text
getActiveFaqs()
findFaq()
createFaq()
updateFaq()
deleteFaq()
```

### Sanity checks

Ask:

``` text
What are the opening hours?
```

Expected:

``` text
Approved restaurant answer.
```

Ask:

``` text
What is your restaurant's policy on an unsupported issue?
```

Expected:

``` text
No invented answer.
```

------------------------------------------------------------------------

# 32. Phase 3 --- Retell Agent

Configure the first voice agent.

Start with a **simple single-prompt voice agent**.

Do not build a complicated conversation graph yet.

Agent responsibilities:

``` text
Greeting
 ↓
Identify language
 ↓
Identify intent
 ↓
Answer FAQ
 OR
Take order
 OR
Escalate
```

Use the restaurant demo knowledge.

### Important

The prompt must explicitly state:

``` text
Never invent information.
Only answer from approved restaurant information.
Ask for clarification when uncertain.
Escalate unsupported requests.
```

### Retell test

Use Retell's simulation/testing capability before consuming phone
credits.

Test:

1.  French greeting.
2.  English greeting.
3.  FAQ.
4.  Order.
5.  Human request.
6.  Unknown question.

------------------------------------------------------------------------

# 33. Phase 4 --- Voice Call Prototype

Connect the phone number/provider.

Implement:

``` text
Incoming call
    ↓
Retell agent
    ↓
Conversation
```

Then outbound:

``` text
Dashboard
    ↓
Make Call
    ↓
Backend
    ↓
Retell
    ↓
Customer phone
```

### Sanity checks

Call number.

Expected:

``` text
Call connects.
Agent answers.
Agent speaks French.
```

Change to English.

Expected:

``` text
Agent continues in English.
```

End call.

Expected:

``` text
Call ends normally.
```

------------------------------------------------------------------------

# 34. Phase 5 --- Retell Webhooks

Implement:

``` http
POST /api/webhooks/retell
```

The webhook handler must:

1.  Validate the request/signature according to the current Retell documentation.
2.  Determine event type.
3.  Normalize the provider payload.
4.  Upsert the call using `providerCallId`.
5.  For `transcript_updated`, replace/update the latest transcript snapshot for that call and publish a normalized `transcript.updated` event.
6.  For call lifecycle events, update the call status and publish the corresponding normalized realtime event.
7.  Save final call analysis on `call_analyzed` when available.
8.  Publish the event through Socket.IO after the backend state has been updated.
9.  Never let a Socket.IO failure cause the webhook request to fail after the database update has succeeded.

### Live transcript implementation note

The realtime dashboard must use the provider's supported `transcript_updated` webhook/event mechanism for mid-call transcript updates. Do not poll the call REST endpoint for live transcript data. The exact Retell payload and event availability must be verified against the current provider documentation during implementation.

For each transcript update, the provider may send the transcript accumulated so far rather than a single new sentence. The backend must normalize this into the application's transcript model and avoid duplicating messages.

### Important

Webhook processing must be idempotent.

Receiving the same webhook twice must not create duplicate calls/orders.

------------------------------------------------------------------------

# 35. Phase 6 --- Transcript Storage

Build:

``` text
TranscriptService
```

Store:

``` text
speaker
text
timestamp
language
```

### Test

Send a mock webhook fixture.

Expected:

``` text
Call record created.
Transcript saved.
No duplicate transcript if webhook repeated.
```

------------------------------------------------------------------------

# 36. Phase 7 --- Structured Extraction

Implement:

``` text
OrderExtractionService
```

Input:

``` text
Final transcript
```

Output:

``` json
{
  "intent": "ORDER",
  "customerName": "Pierre Dupont",
  "phone": "+33612345678",
  "address": "12 Rue de Paris, 75001",
  "items": [
    {
      "name": "Pizza Margherita",
      "quantity": 2
    }
  ]
}
```

### Validation

Reject:

``` text
Missing item.
Missing quantity.
Missing name.
Missing delivery address.
```

Set:

``` text
REVIEW_REQUIRED
```

rather than inventing data.

------------------------------------------------------------------------

# 37. Phase 8 --- Order Persistence

After final call:

``` text
Transcript
 ↓
Extraction
 ↓
Validation
 ↓
Customer upsert
 ↓
Order creation/update
 ↓
Call updated
```

### Important

Customer matching should initially use phone number.

If phone already exists:

``` text
Update customer.
Increment callCount.
```

Otherwise:

``` text
Create customer.
```

------------------------------------------------------------------------

# 38. Phase 9 --- Socket.IO / Live Dashboard Synchronization

Implement the realtime dashboard layer as a first-class prototype feature.

### Build

-   Add Socket.IO server integration to FastAPI.
-   Add a realtime event publisher service.
-   Add call-specific rooms using `call:{callId}`.
-   Add a general `restaurant:live-calls` channel for active-call summaries.
-   Add frontend Socket.IO client integration.
-   Add a connection-status indicator.
-   Add automatic reconnect.
-   Add REST reconciliation after reconnect.
-   Add event sequence handling.

### Events

``` text
call.started
call.status.updated
call.language.updated
call.intent.updated
transcript.updated
customer.updated
order.updated
order.validation.updated
call.escalated
call.ended
call.analysis.updated
```

### Event processing rule

``` text
Retell event
    ↓
Validate
    ↓
Normalize
    ↓
Update LangGraph/application state
    ↓
Persist required state to MongoDB
    ↓
Publish Socket.IO event
    ↓
Frontend updates immediately
```

Never emit a business-state event before the backend has successfully applied the corresponding state change.

### Live transcript

During a call, `transcript_updated` events must update the Live Call screen without a browser refresh. If the provider sends a full transcript snapshot, the backend must replace/reconcile the transcript rather than blindly append the entire snapshot on every event.

### Live order state

When an order custom function changes the current order, the backend must publish the normalized current order state. The frontend should render that state directly and should not perform its own menu validation or order inference.

### Reconnect test

1. Open Live Call.
2. Start a call.
3. Confirm transcript is updating.
4. Temporarily disconnect the browser socket.
5. Confirm the UI shows `Reconnecting...` but does not lose the call.
6. Restore connectivity.
7. Confirm the client reconnects.
8. Confirm the frontend fetches the current call from REST and reconciles state.
9. Confirm new realtime events continue normally.

### Sanity check

Open dashboard.

Make a call.

Expected:

``` text
Call appears without browser refresh.
Status changes live.
Transcript changes during the conversation.
Customer information appears as it is captured.
Order items appear/change as the order is built.
Escalation appears immediately.
Call changes to COMPLETED when the call ends.
```

### Failure isolation

Stop Socket.IO while a test call is active.

Expected:

``` text
Voice call continues.
Backend continues processing.
MongoDB continues receiving state.
Dashboard becomes temporarily stale/reconnecting.
After reconnect, dashboard catches up through REST reconciliation.
```

------------------------------------------------------------------------

# 39. Phase 10 --- Dashboard UI

Build UI in this order:

### 10.1 App shell

-   Sidebar.
-   Header.
-   Language selector.
-   Restaurant branding.

### 10.2 Dashboard cards

-   Calls.
-   Orders.
-   Queries.
-   Escalations.

### 10.3 Live call

Most important.

### 10.4 Transcript

Conversation bubbles.

### 10.5 Detected information

Customer/order information.

### 10.6 Call history

### 10.7 Call detail

### 10.8 Orders

### 10.9 FAQ

### 10.10 Customers

------------------------------------------------------------------------

# 40. Phase 11 --- Make Call

Build:

``` text
[Make a Call]
```

Modal:

``` text
Phone number
Language
Scenario
```

Example scenarios:

``` text
Order
FAQ
Escalation
```

Click:

``` text
Start Call
```

Backend creates outbound call.

UI shows:

``` text
Calling...
```

Then:

``` text
In Progress
```

Then:

``` text
Completed
```

------------------------------------------------------------------------

# 41. Phase 12 --- Human Escalation

Build:

``` text
Transfer to Human
```

UI.

When triggered:

``` text
call.status = ESCALATED
```

Store:

``` text
escalationReason
```

Display:

``` text
Customer requested human
```

For prototype, if true telephony transfer is not available in the free
setup, simulate the handoff while preserving the correct architecture.

Do not block the prototype on real human transfer.

------------------------------------------------------------------------

# 42. Phase 13 --- Feedback

Call detail page:

``` text
Was the extracted order correct?

[Correct] [Needs Correction]
```

If incorrect:

``` text
Field
Original
Correct value
Reason
```

Save feedback.

Example:

``` json
{
  "field": "customerName",
  "originalValue": "Pierre Dupont",
  "correctedValue": "Pierre Dupont-Durand",
  "reason": "Transcript interpretation"
}
```

------------------------------------------------------------------------

# 43. Phase 14 --- Analytics

Only basic analytics.

Calculate:

``` text
Total calls
Orders
FAQs
Escalations
Average call duration
Order extraction corrections
```

Do not build advanced BI.

------------------------------------------------------------------------

# 44. Testing Strategy

Use:

``` text
Vitest/Jest
Supertest
React Testing Library
Playwright
```

The exact testing framework can be selected by the coding agent based on
the existing project setup.

------------------------------------------------------------------------

# 45. Unit Test Cases

## UT-001 --- Intent classification

Input:

``` text
"Bonjour, je voudrais commander deux pizzas."
```

Expected:

``` text
ORDER
```

------------------------------------------------------------------------

## UT-002 --- FAQ classification

Input:

``` text
"À quelle heure ouvrez-vous ?"
```

Expected:

``` text
FAQ
```

------------------------------------------------------------------------

## UT-003 --- Escalation classification

Input:

``` text
"Je voudrais parler à une personne."
```

Expected:

``` text
ESCALATION
```

------------------------------------------------------------------------

## UT-004 --- Order extraction

Input:

``` text
"Je voudrais deux pizzas margherita et une coca."
```

Expected:

``` json
{
  "items": [
    {
      "name": "Pizza Margherita",
      "quantity": 2
    },
    {
      "name": "Coca Cola",
      "quantity": 1
    }
  ]
}
```

------------------------------------------------------------------------

## UT-005 --- Missing address

Input:

``` text
Customer orders delivery but gives no address.
```

Expected:

``` text
status = REVIEW_REQUIRED
```

------------------------------------------------------------------------

## UT-006 --- Invalid quantity

Input:

``` text
"Je voudrais zéro pizza."
```

Expected:

``` text
Validation failure.
```

------------------------------------------------------------------------

## UT-007 --- Unknown FAQ

Input:

``` text
"Do you have a private event room?"
```

If not present in knowledge:

Expected:

``` text
UNKNOWN / ESCALATION
```

Never invent an answer.

------------------------------------------------------------------------

## UT-008 --- Phone normalization

Input:

``` text
"06 12 34 56 78"
```

Expected normalized representation:

``` text
+33612345678
```

Use a proper phone parsing library where appropriate; do not build
country-specific parsing from scratch.

------------------------------------------------------------------------

# 46. Webhook Tests

## WH-001

Send:

``` text
call_started
```

Expected:

``` text
Call created.
Status = IN_PROGRESS.
```

## WH-002

Send transcript update.

Expected:

``` text
Transcript appended/updated.
```

## WH-003A --- Live transcript webhook

Send a `transcript_updated` event while the call is in progress.

Expected:

``` text
Call remains IN_PROGRESS.
Latest transcript snapshot is stored/reconciled.
Socket.IO transcript.updated event is emitted.
Connected Live Call UI updates without refresh.
```

Send a second transcript snapshot containing the first and second turns.

Expected:

``` text
No duplicate transcript messages.
Latest transcript is represented correctly.
```

------------------------------------------------------------------------

## WH-003

Send call ended.

Expected:

``` text
Status = COMPLETED.
EndedAt populated.
Duration populated if available.
```

## WH-004

Send same webhook twice.

Expected:

``` text
No duplicate call.
```

## WH-005

Send malformed webhook.

Expected:

``` text
400 or safe rejection.
No database mutation.
```

------------------------------------------------------------------------

# 47. API Integration Tests

## API-001

``` http
GET /api/calls
```

Expected:

``` text
200
Array of calls
```

## API-002

``` http
GET /api/orders
```

Expected:

``` text
200
Array of orders
```

## API-003

``` http
POST /api/feedback
```

Expected:

``` text
201
Feedback stored.
```

## API-004

Invalid order.

Expected:

``` text
400
Validation error.
```

------------------------------------------------------------------------

# 48. Frontend Tests

## UI-001

Dashboard loads.

Expected:

``` text
KPI cards visible.
Recent calls visible.
```

## UI-002

Live call state.

Expected:

``` text
In Progress badge visible.
Call timer visible.
Transcript visible.
```

## UI-003

Order extraction.

Expected:

``` text
Customer details visible.
Items visible.
Save Order button visible.
```

## UI-004

Escalation.

Expected:

``` text
Escalate button changes call state.
Escalation indicator visible.
```

## UI-004A --- Realtime connection recovery

Expected:

``` text
Connection indicator changes to Reconnecting.
Current call data remains visible.
Socket reconnects automatically.
REST reconciliation restores authoritative state.
```

## UI-004B --- Stale event protection

Send an older realtime event after a newer event.

Expected:

``` text
Older event does not roll the UI back.
```

## UI-005

Call history.

Expected:

``` text
Completed calls visible.
```

------------------------------------------------------------------------

# 49. End-to-End Tests

## E2E-001 --- Complete order

Scenario:

``` text
Customer calls
 ↓
French greeting
 ↓
Orders two pizzas
 ↓
Gives name
 ↓
Gives phone
 ↓
Gives address
 ↓
Confirms
 ↓
Ends call
```

Expected:

``` text
Call = COMPLETED
Intent = ORDER
Language = FR
Customer saved
Order saved
Transcript saved
Dashboard updated
```

------------------------------------------------------------------------

## E2E-002 --- FAQ

Scenario:

``` text
Customer calls
 ↓
Asks opening hours
 ↓
Agent answers from FAQ
 ↓
Call ends
```

Expected:

``` text
Intent = FAQ
No order created
Transcript stored
```

------------------------------------------------------------------------

## E2E-003 --- Escalation

Scenario:

``` text
Customer calls
 ↓
Requests human
```

Expected:

``` text
Call = ESCALATED
Escalation reason stored
Dashboard displays escalation
```

------------------------------------------------------------------------

## E2E-004 --- Unknown question

Scenario:

``` text
Customer asks unsupported question
```

Expected:

``` text
Agent does not invent answer.
Escalation or safe fallback occurs.
```

------------------------------------------------------------------------

## E2E-005 --- English

Scenario:

``` text
Customer starts in English.
```

Expected:

``` text
Agent responds in English.
Language = EN.
```

------------------------------------------------------------------------

# 50. Voice Quality Sanity Checklist

Before demoing to the client:

### French

-   [ ] Agent pronunciation understandable.
-   [ ] Agent does not speak too fast.
-   [ ] Agent waits for customer to finish.
-   [ ] Agent handles common French ordering phrases.
-   [ ] Agent handles numbers.
-   [ ] Agent handles addresses.
-   [ ] Agent confirms important details.

### English

-   [ ] Agent switches correctly.
-   [ ] No accidental French response.
-   [ ] Order extraction works.

### Latency

Measure:

``` text
Customer stops speaking
        ↓
Agent starts responding
```

Track approximate response latency.

Do not promise a production SLA in the prototype.

------------------------------------------------------------------------

# 51. Accuracy Sanity Checklist

Create a fixed test script containing at least:

### Order variations

``` text
"Deux margheritas."

"Je voudrais deux pizzas margherita."

"Can I have two Margherita pizzas?"

"Deux pizzas marguerita."

"Une pizza margherita et deux cocas."
```

Expected:

Correct canonical product + quantity.

### FAQ variations

``` text
"Quand vous ouvrez ?"
"Vous êtes ouverts ce soir ?"
"What time do you close?"
"What are your opening hours?"
```

Expected:

Same approved FAQ answer.

------------------------------------------------------------------------

# 52. No-Hallucination Test Set

Ask questions intentionally absent from knowledge:

``` text
"Do you offer wedding catering?"
"How many employees work here?"
"Can you guarantee delivery in exactly 15 minutes?"
"Do you have a loyalty program?"
```

Expected:

The agent does not fabricate information.

Acceptable behavior:

``` text
"I don't have that information."
```

or:

``` text
"I can connect you with someone from the restaurant."
```

------------------------------------------------------------------------

# 53. Performance Requirements

Prototype targets:

### API

``` text
Health endpoint < 300ms locally.
Normal CRUD endpoint < 500ms locally.
```

### Dashboard

``` text
Initial page usable < 2 seconds locally.
```

### Realtime

``` text
Provider event → backend processing → dashboard update should feel near real-time.
Target: normally visible within ~1–2 seconds under local/demo conditions.
```

This is a prototype UX target, not a production SLA. If provider webhook delivery is slower, do not introduce unnecessary polling or middleware solely to force a number.

### Voice

Prioritize natural turn-taking and low perceived latency.

Do not add expensive middleware between the caller and the voice
provider.

------------------------------------------------------------------------

# 54. Error Handling

Every external operation must have graceful failure handling.

### Retell unavailable

Dashboard:

``` text
Voice service unavailable.
```

### MongoDB unavailable

Backend:

``` text
503
```

### Webhook duplicate

Do not create duplicate records.

### Extraction failure

Set:

``` text
REVIEW_REQUIRED
```

### Unknown intent

Set:

``` text
UNKNOWN
```

and escalate/fallback.

### Socket.IO unavailable

The dashboard must show:

``` text
Live connection interrupted — reconnecting...
```

Do not fail the phone call or backend persistence because the dashboard socket is unavailable.

### Realtime event out of order

Ignore stale events using the per-call sequence number.

### Dashboard reconnect

After reconnect, fetch authoritative call state through REST before resuming incremental realtime updates.

------------------------------------------------------------------------

# 55. Logging

Use structured logs.

Every call-related log should include:

``` text
requestId
callId
providerCallId
eventType
timestamp
```

Example:

``` text
INFO call.started
callId=abc123
provider=retell
```

Never log:

-   API keys.
-   Full payment information.
-   Secrets.

For prototype, be careful with personal information in logs.

------------------------------------------------------------------------

# 56. Security Basics

Even though this is a prototype:

-   `.env` must be gitignored.
-   Retell API key only on backend.
-   Webhook endpoint must validate authenticity according to provider
    documentation when available.
-   Do not expose provider secret keys to frontend.
-   Validate all API input.
-   Escape/render transcript safely.
-   Do not allow arbitrary HTML from transcript.
-   Use HTTPS in deployed environments.
-   Do not collect payment-card data.

------------------------------------------------------------------------

# 57. Demo Mode

Add a demo mode so the client demo does not depend entirely on a real
phone call.

Demo mode should be able to load:

``` text
Scenario 1: French Order
Scenario 2: French FAQ
Scenario 3: English Order
Scenario 4: Escalation
```

This allows:

``` text
Client demo
   ↓
Select scenario
   ↓
See realistic live-call UI
   ↓
Transcript updates
   ↓
Order extracted
```

Real phone calling remains the primary technical demonstration.

------------------------------------------------------------------------

# 58. Demo Seed Scenario

Use:

### Customer

``` text
Pierre Dupont
+33 6 12 34 56 78
12 Rue de Paris, 75001
```

### Conversation

Customer:

``` text
Bonjour, je voudrais deux pizzas margherita et une salade.
```

Agent:

``` text
Bien sûr. Pour la livraison, pouvez-vous me donner votre adresse ?
```

Customer:

``` text
12 Rue de Paris, 75001.
```

Agent:

``` text
Merci. Puis-je avoir votre nom et confirmer votre numéro de téléphone ?
```

Customer:

``` text
Pierre Dupont. Mon numéro est 06 12 34 56 78.
```

Agent:

``` text
Parfait. Je confirme : deux pizzas margherita et une salade, à livrer au 12 Rue de Paris, 75001, pour Pierre Dupont. Est-ce correct ?
```

Customer:

``` text
Oui.
```

Expected extracted order:

``` json
{
  "intent": "ORDER",
  "language": "fr",
  "customerName": "Pierre Dupont",
  "phone": "+33612345678",
  "address": "12 Rue de Paris, 75001",
  "items": [
    {
      "name": "Pizza Margherita",
      "quantity": 2
    },
    {
      "name": "Salade",
      "quantity": 1
    }
  ],
  "status": "CONFIRMED"
}
```

------------------------------------------------------------------------

# 59. Build Sequence --- Exact Order

The coding agent should follow this sequence.

``` text
1. Project bootstrap
       ↓
2. Environment/config
       ↓
3. MongoDB connection
       ↓
4. Database schemas
       ↓
5. Seed data
       ↓
6. Basic REST API
       ↓
7. FAQ service
       ↓
8. Retell account/agent configuration
       ↓
9. Retell provider adapter
       ↓
10. Incoming call
       ↓
11. Webhook receiver
       ↓
12. Transcript persistence
       ↓
13. Order extraction
       ↓
14. Customer persistence
       ↓
15. Order persistence
       ↓
16. WebSocket events
       ↓
17. Dashboard shell
       ↓
18. Live Call screen
       ↓
19. Transcript UI
       ↓
20. Order information UI
       ↓
21. Call history
       ↓
22. Orders page
       ↓
23. FAQ page
       ↓
24. Customer page
       ↓
25. Make Call
       ↓
26. Human escalation
       ↓
27. Feedback
       ↓
28. Demo mode
       ↓
29. E2E tests
       ↓
30. Deployment
```

Do not reverse this order unless a dependency requires it.

------------------------------------------------------------------------

# 60. Definition of Done

The prototype is done when:

-   [ ] Backend starts.
-   [ ] Frontend starts.
-   [ ] MongoDB connects.
-   [ ] Seed script works.
-   [ ] Retell agent is configured.
-   [ ] Incoming call works.
-   [ ] French conversation works.
-   [ ] English conversation works.
-   [ ] FAQ scenario works.
-   [ ] Order scenario works.
-   [ ] Escalation scenario works.
-   [ ] Transcript is stored.
-   [ ] Customer is stored.
-   [ ] Order is stored.
-   [ ] Call history works.
-   [ ] Live call screen works.
-   [ ] Dashboard updates in near real time.
-   [ ] Make Call works if provider/account setup permits.
-   [ ] Feedback can be stored.
-   [ ] No-hallucination tests pass.
-   [ ] Duplicate webhook test passes.
-   [ ] Invalid data tests pass.
-   [ ] E2E order test passes.
-   [ ] Demo mode works.
-   [ ] README explains setup.
-   [ ] `.env.example` exists.
-   [ ] No secrets committed.

------------------------------------------------------------------------

# 61. Final Demo Flow

The final client demonstration should follow this sequence.

### Step 1

Open dashboard.

Show:

``` text
Calls Today
Orders
Queries
Escalations
```

### Step 2

Click:

``` text
Live Calls
```

### Step 3

Call the restaurant number.

### Step 4

Speak French.

### Step 5

Place an order.

### Step 6

While the customer is still on the phone, the dashboard shows:

``` text
Live call status
Live transcript
Customer information as captured
Order items as they are added/changed
```

No browser refresh should be used. This is the visual "wow" moment of the demo.

### Step 7

Customer confirms.

### Step 8

Call ends.

### Step 9

Open Call History.

### Step 10

Open the call.

Show:

``` text
Recording
Transcript
Summary
Customer
Order
```

### Step 11

Edit one extracted field.

### Step 12

Save feedback.

### Step 13

Show FAQ scenario.

### Step 14

Show escalation scenario.

This should take approximately 5--10 minutes.

------------------------------------------------------------------------

# 62. Future Production Architecture

Only after the prototype is validated:

``` text
Telephony
    ↓
Voice Agent
    ↓
Real-time conversation
    ↓
Intent Router
    ├── FAQ Agent
    ├── Order Agent
    ├── Reservation Agent
    └── Escalation Agent
            ↓
       Human Operator
            ↓
     Post-call Processor
            ↓
      Structured Data
            ↓
       Event Queue
            ↓
     Database / CRM / POS
            ↓
       Feedback System
            ↓
     Evaluation Pipeline
```

Future additions:

-   LangGraph orchestration.
-   Better retrieval.
-   Product catalog integration.
-   POS integration.
-   Restaurant-specific aliases.
-   Human transfer.
-   Call quality scoring.
-   Evaluation datasets.
-   Automated regression tests from real calls.
-   Controlled prompt improvement.
-   GDPR/data-retention implementation.
-   Production observability.
-   Rate limiting.
-   Multi-tenant support.
-   Authentication and authorization.

------------------------------------------------------------------------

# 63. Important Architectural Rule for Future Learning

Do not allow:

``` text
Past call
   ↓
LLM
   ↓
Automatically change system prompt
```

Instead:

``` text
Past call
   ↓
Evaluation
   ↓
Correction
   ↓
Feedback dataset
   ↓
Human approval
   ↓
Prompt/FAQ/version update
   ↓
Regression tests
   ↓
Deploy
```

Every agent improvement must be measurable and reversible.

------------------------------------------------------------------------

# 64. Prototype Quality Bar

The prototype should feel like a real product, but it does not need
production infrastructure.

Prioritize in this order:

``` text
1. Voice actually works
2. Conversation feels natural
3. No hallucinated restaurant information
4. Orders extracted correctly
5. Transcript stored correctly
6. Dashboard updates live
7. Human escalation works/simulates correctly
8. Feedback is stored
9. UI polish
10. Analytics
```

If time is limited, stop after item 7 and make the demo reliable.

Do not sacrifice voice reliability to add more dashboard features.

------------------------------------------------------------------------

# 65. Coding Agent Instructions

The coding agent should:

1.  Read this PRD completely before coding.
2.  Build one phase at a time.
3.  Run tests after every phase.
4.  Do not silently skip failed tests.
5.  Do not hardcode production secrets.
6.  Do not invent Retell API payload fields.
7.  Check the current Retell documentation when implementing
    provider-specific functionality.
8.  Keep Retell-specific code inside `providers/retell`.
9.  Keep business logic independent of Retell.
10. Use Python types for API and database boundaries.
11. Validate external data before persistence.
12. Make webhooks idempotent.
13. Prefer safe fallback over hallucination.
14. Build the smallest working implementation first.
15. Avoid unnecessary dependencies.
16. Treat Socket.IO as a delivery layer, not as a source of truth.
17. Implement reconnect + REST reconciliation before calling realtime complete.
18. Never stream raw Retell payloads directly to the frontend.
19. Use normalized event contracts and per-call sequence numbers.
20. Test realtime failure without interrupting the voice call.
21. Keep live transcript handling aligned with the current Retell webhook/event capabilities.
22. Keep the application runnable after every phase.
23. Add tests before or alongside complex logic.
24. Use mock provider fixtures for tests so tests do not consume paid
    voice credits.
25. Never make automated real phone calls during CI.
26. Keep demo data clearly separated from real restaurant data.

------------------------------------------------------------------------

# 66. Provider Documentation Note

Retell's current public material indicates a pay-as-you-go entry point
with free credits and API/webhook/simulation capabilities. Provider
pricing, phone-number availability, trial restrictions, and country
support can change.

Before connecting a real French restaurant number, verify:

-   French number availability.
-   Inbound calling.
-   Outbound calling.
-   Number provisioning requirements.
-   Trial/free-credit restrictions.
-   Recording/transcription behavior.
-   Current pricing.
-   Data retention.
-   Transfer capability.
-   Webhook authentication.
-   Supported French voices.

The provider integration must be implemented against the current
official documentation rather than assumptions from this PRD.

------------------------------------------------------------------------

# 67. Final Architecture Summary

``` text
                         ┌───────────────────────┐
                         │      Customer         │
                         │    French / English   │
                         └───────────┬───────────┘
                                     │
                              Phone Call
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │       Retell          │
                         │     Voice Agent       │
                         │                       │
                         │ STT / TTS / Voice     │
                         │ Conversation          │
                         └───────────┬───────────┘
                                     │
                         Webhooks / Custom Functions
                                     │
                                     ▼
                         ┌────────────────────────┐
                         │    Python / FastAPI    │
                         │                        │
                         │ Provider Adapter       │
                         │ Transcript Service     │
                         │ Order / Customer Logic │
                         │ LangGraph Live State   │
                         │ Realtime Event Pub.    │
                         └───────────┬────────────┘
                                     │
                     ┌───────────────┼────────────────┐
                     │               │                │
                     ▼               ▼                ▼
                ┌────────┐     ┌────────────┐   ┌──────────┐
                │ MongoDB│     │ Socket.IO  │   │ Retell   │
                │ Source │     │ Realtime   │   │ Provider │
                │ of Truth│    │ Delivery   │   │ Adapter  │
                └────────┘     └─────┬──────┘   └──────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │   Next.js Dashboard   │
                         │                       │
                         │ KPI Dashboard         │
                         │ Live Calls            │
                         │ Live Transcript       │
                         │ Live Order State      │
                         │ Customers             │
                         │ FAQ                   │
                         │ Call History          │
                         └───────────────────────┘
```

### Architectural rule

``` text
Retell = voice/conversation provider
FastAPI = application boundary + orchestration
LangGraph = live business/order state
MongoDB = persistent source of truth
Socket.IO = realtime delivery only
Next.js = presentation/UI
```

Socket.IO must never become the database. If the dashboard disconnects, the system must continue processing the call and persist state. When the dashboard reconnects, it reconciles against REST/MongoDB state and resumes realtime updates.

**The prototype's core promise is simple:**

> **A restaurant customer can call, speak naturally in French or English, place an order or ask a common question, while the system captures the conversation and converts it into useful structured information for the restaurant — and the restaurant staff can watch the important call state update live in the dashboard without refreshing the page.**
