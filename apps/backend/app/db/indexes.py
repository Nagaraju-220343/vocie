import logging

from app.db.mongodb import MongoDBManager

logger = logging.getLogger(__name__)

def ensure_indexes() -> None:
    """Create all required MongoDB indexes."""
    db = MongoDBManager.get_db()
    
    logger.info("Ensuring MongoDB indexes...")
    
    # Calls indexes
    calls = db.calls
    calls.create_index("providerCallId", unique=True)
    calls.create_index("createdAt")
    calls.create_index("intent")
    calls.create_index("status")
    
    # Orders indexes
    orders = db.orders
    orders.create_index("createdAt")
    
    # Customers indexes
    customers = db.customers
    customers.create_index("phone")
    
    logger.info("MongoDB indexes ensured.")
