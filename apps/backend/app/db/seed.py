import logging
from datetime import datetime

from app.db.indexes import ensure_indexes
from app.db.mongodb import MongoDBManager
from app.models.call import CallModel
from app.models.customer import CustomerModel
from app.models.faq import FaqModel
from app.models.order import OrderModel
from app.repositories.call_repository import CallRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.faq_repository import FaqRepository
from app.repositories.order_repository import OrderRepository

logger = logging.getLogger(__name__)

def seed_database() -> None:
    logger.info("Connecting to database for seeding...")
    MongoDBManager.connect()
    ensure_indexes()
    
    logger.info("Starting database seed with fictional demo data...")

    customer_repo = CustomerRepository()
    call_repo = CallRepository()
    order_repo = OrderRepository()
    faq_repo = FaqRepository()
    
    # --- 1. Seed FAQs ---
    faqs_data = [
        {"question": "What time do you open?", "answerFr": "Nous ouvrons à 11h00.", "answerEn": "We open at 11:00 AM.", "category": "HOURS"},
        {"question": "Do you deliver?", "answerFr": "Oui, nous livrons dans un rayon de 5 km.", "answerEn": "Yes, we deliver within a 5 km radius.", "category": "DELIVERY"},
        {"question": "Do you have vegetarian options?", "answerFr": "Oui, nous proposons plusieurs plats végétariens comme la Quiche aux légumes.", "answerEn": "Yes, we offer several vegetarian dishes like Vegetable Quiche.", "category": "MENU"},
        {"question": "Where are you located?", "answerFr": "Nous sommes situés au 123 Rue de la Paix, Paris.", "answerEn": "We are located at 123 Rue de la Paix, Paris.", "category": "LOCATION"}
    ]
    for faq_data in faqs_data:
        # Check if exists by question to prevent duplicate on repeated seed
        if faq_repo.collection.find_one({"question": faq_data["question"]}) is None:
            faq_repo.create(FaqModel(**faq_data))  # type: ignore

    # --- 2. Seed Customers ---
    customers_data = [
        {"phone": "+33612345678", "name": "Jean Martin", "address": "10 Avenue des Champs", "callCount": 2, "lastCallAt": datetime.utcnow()},
        {"phone": "+33698765432", "name": "Sophie Laurent", "address": "5 Rue de Rivoli", "callCount": 1, "lastCallAt": datetime.utcnow()},
        {"phone": "+447911123456", "name": "Michael Brown", "address": "Hotel Le Meurice, Room 204", "callCount": 3, "lastCallAt": datetime.utcnow()}
    ]
    customer_ids = []
    for c_data in customers_data:
        existing = customer_repo.get_by_phone(str(c_data["phone"]))
        if existing:
            customer_ids.append(str(existing.id))
        else:
            c = CustomerModel(**c_data)  # type: ignore
            customer_ids.append(customer_repo.create(c))

    # --- 3. Seed Calls ---
    calls_data = [
        {"providerCallId": "demo-call-001", "direction": "INBOUND", "fromNumber": "+33612345678", "toNumber": "+33123456789", "language": "FR", "intent": "ORDER", "status": "COMPLETED", "durationSeconds": 120, "transcript": "Bonjour, je voudrais commander...", "summary": "Customer ordered a meal.", "escalated": False},
        {"providerCallId": "demo-call-002", "direction": "INBOUND", "fromNumber": "+447911123456", "toNumber": "+33123456789", "language": "EN", "intent": "ORDER", "status": "COMPLETED", "durationSeconds": 95, "transcript": "Hello, I'd like to place an order.", "summary": "Customer ordered some items for pickup.", "escalated": False},
        {"providerCallId": "demo-call-003", "direction": "INBOUND", "fromNumber": "+33698765432", "toNumber": "+33123456789", "language": "FR", "intent": "FAQ", "status": "COMPLETED", "durationSeconds": 45, "transcript": "A quelle heure fermez-vous ?", "summary": "Customer asked about closing hours.", "escalated": False},
        {"providerCallId": "demo-call-004", "direction": "INBOUND", "fromNumber": "+447911123456", "toNumber": "+33123456789", "language": "EN", "intent": "FAQ", "status": "COMPLETED", "durationSeconds": 30, "transcript": "Do you deliver to the local hotels?", "summary": "Customer asked about delivery.", "escalated": False},
        {"providerCallId": "demo-call-005", "direction": "INBOUND", "fromNumber": "+33612345678", "toNumber": "+33123456789", "language": "FR", "intent": "ESCALATION", "status": "ESCALATED", "durationSeconds": 60, "transcript": "Je veux parler à un humain.", "summary": "Customer requested human escalation.", "escalated": True, "escalationReason": "Human requested"}
    ]
    call_ids = []
    for call_data in calls_data:
        call = CallModel(**call_data)  # type: ignore
        call_ids.append(call_repo.upsert_by_provider_call_id(call.providerCallId, call))

    # --- 4. Seed Orders ---
    # Only seed if orders collection is empty for demo purposes, or matching call IDs
    if order_repo.collection.count_documents({}) < 3:
        orders_data = [
            {"callId": call_ids[0], "customerId": customer_ids[0], "customerName": "Jean Martin", "phone": "+33612345678", "address": "10 Avenue des Champs", "orderType": "DELIVERY", "status": "CONFIRMED", "items": [{"name": "Steak Frites", "quantity": 1, "price": 25.0}, {"name": "Café", "quantity": 1, "price": 3.0}]},
            {"callId": call_ids[1], "customerId": customer_ids[2], "customerName": "Michael Brown", "phone": "+447911123456", "address": "Hotel Le Meurice, Room 204", "orderType": "DELIVERY", "status": "PENDING", "items": [{"name": "Croissant", "quantity": 2, "price": 3.0}, {"name": "Orange Juice", "quantity": 1, "price": 5.0}]},
            {"callId": call_ids[0], "customerId": customer_ids[1], "customerName": "Sophie Laurent", "phone": "+33698765432", "address": "5 Rue de Rivoli", "orderType": "PICKUP", "status": "COMPLETED", "items": [{"name": "Quiche Lorraine", "quantity": 1, "price": 12.0}]}
        ]
        for order_data in orders_data:
            # Upsert by a combination if needed, but for now we just clear and add or ignore if exist.
            # To be safe and repeatable, we will delete old orders for these call IDs first
            order_repo.collection.delete_many({"callId": order_data["callId"]})
            order = OrderModel(**order_data)  # type: ignore
            order_repo.create(order)

    logger.info("Database seeding completed successfully.")
    MongoDBManager.disconnect()

if __name__ == "__main__":
    seed_database()
