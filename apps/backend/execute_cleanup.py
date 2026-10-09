import json
from datetime import datetime
from bson import ObjectId
from app.db.mongodb import MongoDBManager

# The exact known IDs from the dry run
KNOWN_CALL_IDS = [
    "6ac611f719a6c4f2b0ee5a6d", "6ac611f719a6c4f2b0ee5a6e",
    "6ac611f719a6c4f2b0ee5a6f", "6ac611f719a6c4f2b0ee5a70",
    "6ac611f719a6c4f2b0ee5a71", "6ac8776b48cffba0dbee2eb4"
]
KNOWN_ORDER_IDS = ["6ac611fbbaf9c0e9098d6eb5", "6ac611fbbaf9c0e9098d6eb6", "6ac7a7e01df33cd69261f0ae"]
KNOWN_CUSTOMER_IDS = ["6ac611fabaf9c0e9098d6eb2", "6ac611fabaf9c0e9098d6eb3", "6ac611fabaf9c0e9098d6eb1"]

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def execute_cleanup():
    MongoDBManager.connect()
    db = MongoDBManager.get_db()

    print("Fetching exact records by ID...")
    calls_to_delete = list(db.calls.find({"_id": {"$in": [ObjectId(cid) for cid in KNOWN_CALL_IDS]}}))
    orders_to_delete = list(db.orders.find({"_id": {"$in": [ObjectId(oid) for oid in KNOWN_ORDER_IDS]}}))
    customers_to_delete = list(db.customers.find({"_id": {"$in": [ObjectId(cid) for cid in KNOWN_CUSTOMER_IDS]}}))

    if len(calls_to_delete) != len(KNOWN_CALL_IDS):
        print(f"ERROR: Expected {len(KNOWN_CALL_IDS)} calls but found {len(calls_to_delete)}. Aborting.")
        return
    if len(orders_to_delete) != len(KNOWN_ORDER_IDS):
        print(f"ERROR: Expected {len(KNOWN_ORDER_IDS)} orders but found {len(orders_to_delete)}. Aborting.")
        return
    if len(customers_to_delete) != len(KNOWN_CUSTOMER_IDS):
        print(f"ERROR: Expected {len(KNOWN_CUSTOMER_IDS)} customers but found {len(customers_to_delete)}. Aborting.")
        return
        
    print("Exact matching verified.")

    # Check relationships
    print("Verifying relationships...")
    test_call_ids_str = [str(c["_id"]) for c in calls_to_delete]
    test_provider_ids = [c.get("providerCallId") for c in calls_to_delete]
    
    # Are there any OTHER orders referencing these calls?
    other_orders = list(db.orders.find({
        "$or": [
            {"callId": {"$in": test_call_ids_str}},
            {"callId": {"$in": test_provider_ids}}
        ],
        "_id": {"$nin": [o["_id"] for o in orders_to_delete]}
    }))
    if other_orders:
        print(f"ERROR: Found {len(other_orders)} OTHER orders referencing these calls. Aborting.")
        return
        
    # Are there any OTHER orders referencing these customers?
    other_orders_cust = list(db.orders.find({
        "customerId": {"$in": KNOWN_CUSTOMER_IDS},
        "_id": {"$nin": [o["_id"] for o in orders_to_delete]}
    }))
    if other_orders_cust:
        print(f"ERROR: Found {len(other_orders_cust)} OTHER orders referencing these customers. Aborting.")
        return

    # Are there any OTHER calls referencing these customers (by phone)?
    test_phones = [c.get("phone") for c in customers_to_delete]
    other_calls_cust = list(db.calls.find({
        "fromNumber": {"$in": test_phones},
        "_id": {"$nin": [c["_id"] for c in calls_to_delete]}
    }))
    if other_calls_cust:
        print(f"ERROR: Found {len(other_calls_cust)} OTHER calls referencing these customers. Aborting.")
        return
        
    print("No dangling relationships found.")

    # Backup
    backup_data = {
        "calls": calls_to_delete,
        "orders": orders_to_delete,
        "customers": customers_to_delete
    }
    
    backup_filename = f"backup_test_records_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(backup_filename, "w", encoding="utf-8") as f:
        json.dump(backup_data, f, cls=CustomEncoder, indent=2)
    print(f"Backed up {len(calls_to_delete) + len(orders_to_delete) + len(customers_to_delete)} records to {backup_filename}")

    # Delete
    print("Executing deletion...")
    call_del = db.calls.delete_many({"_id": {"$in": [ObjectId(cid) for cid in KNOWN_CALL_IDS]}})
    order_del = db.orders.delete_many({"_id": {"$in": [ObjectId(oid) for oid in KNOWN_ORDER_IDS]}})
    cust_del = db.customers.delete_many({"_id": {"$in": [ObjectId(cid) for cid in KNOWN_CUSTOMER_IDS]}})

    print(f"Deleted {call_del.deleted_count} calls.")
    print(f"Deleted {order_del.deleted_count} orders.")
    print(f"Deleted {cust_del.deleted_count} customers.")

    # Post-deletion verification
    remaining_calls = db.calls.count_documents({})
    remaining_orders = db.orders.count_documents({})
    remaining_custs = db.customers.count_documents({})
    print(f"Remaining calls: {remaining_calls}")
    print(f"Remaining orders: {remaining_orders}")
    print(f"Remaining customers: {remaining_custs}")
    
    MongoDBManager.disconnect()
    print("Cleanup successful.")

if __name__ == "__main__":
    execute_cleanup()
