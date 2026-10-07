import pytest
from pymongo.errors import DuplicateKeyError

from app.config.settings import settings
from app.db.indexes import ensure_indexes
from app.db.mongodb import MongoDBManager
from app.models.call import CallModel
from app.models.customer import CustomerModel
from app.models.faq import FaqModel
from app.models.feedback import FeedbackModel
from app.models.order import OrderItemModel, OrderModel
from app.repositories.call_repository import CallRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.faq_repository import FaqRepository
from app.repositories.feedback_repository import FeedbackRepository
from app.repositories.order_repository import OrderRepository


def test_mongodb_connection() -> None:
    db = MongoDBManager.get_db()
    assert db.name == settings.mongodb_test_database

def test_create_and_get_call() -> None:
    repo = CallRepository()
    call = CallModel(
        providerCallId="test-call-1",
        direction="INBOUND",
        fromNumber="+123",
        toNumber="+456",
        language="EN",
        intent="ORDER",
        status="COMPLETED"
    )
    call_id = repo.create(call)
    assert call_id is not None
    
    retrieved = repo.get_by_id(call_id)
    assert retrieved is not None
    assert retrieved.providerCallId == "test-call-1"

def test_provider_call_id_uniqueness() -> None:
    repo = CallRepository()
    call1 = CallModel(
        providerCallId="test-call-unique",
        direction="INBOUND",
        fromNumber="+123",
        toNumber="+456",
        language="EN",
        intent="ORDER",
        status="COMPLETED"
    )
    repo.create(call1)
    
    call2 = CallModel(
        providerCallId="test-call-unique",
        direction="INBOUND",
        fromNumber="+789",
        toNumber="+456",
        language="EN",
        intent="ORDER",
        status="COMPLETED"
    )
    
    with pytest.raises(DuplicateKeyError):
        repo.create(call2)

def test_create_and_get_customer() -> None:
    repo = CustomerRepository()
    customer = CustomerModel(phone="+1234567890", name="Test Customer")
    c_id = repo.create(customer)
    
    retrieved = repo.get_by_phone("+1234567890")
    assert retrieved is not None
    assert retrieved.id == c_id
    assert retrieved.name == "Test Customer"

def test_create_and_get_order() -> None:
    repo = OrderRepository()
    order = OrderModel(
        callId="some-call-id",
        items=[OrderItemModel(name="Test Item", quantity=1, price=10.0)]
    )
    o_id = repo.create(order)
    
    retrieved = repo.get_by_id(o_id)
    assert retrieved is not None
    assert len(retrieved.items) == 1
    assert retrieved.items[0].name == "Test Item"

def test_create_and_get_faq() -> None:
    repo = FaqRepository()
    faq = FaqModel(
        question="Test Q",
        answerFr="Test A FR",
        answerEn="Test A EN",
        category="TEST"
    )
    f_id = repo.create(faq)
    
    retrieved = repo.get_by_id(f_id)
    assert retrieved is not None
    assert retrieved.question == "Test Q"

def test_create_and_get_feedback() -> None:
    repo = FeedbackRepository()
    feedback = FeedbackModel(
        callId="call-123",
        field="name",
        originalValue="Test",
        correctedValue="Test Corrected"
    )
    fb_id = repo.create(feedback)
    
    retrieved = repo.get_by_id(fb_id)
    assert retrieved is not None
    assert retrieved.correctedValue == "Test Corrected"

def test_indexes_exist() -> None:
    db = MongoDBManager.get_db()
    
    call_indexes = [i["key"] for i in db.calls.list_indexes()]
    assert any("providerCallId" in dict(i).keys() for i in call_indexes)
    
    customer_indexes = [i["key"] for i in db.customers.list_indexes()]
    assert any("phone" in dict(i).keys() for i in customer_indexes)
