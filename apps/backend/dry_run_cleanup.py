import sys
from app.db.mongodb import MongoDBManager
from bson.objectid import ObjectId

def run_dry_run():
    MongoDBManager.connect()
    db = MongoDBManager.get_db()
    
    # 1. Find matching calls
    calls_query = {
        "$or": [
            {"providerCallId": {"$regex": "^demo-call-"}},
            {"providerCallId": "test-call-001"}
        ]
    }
    
    test_calls = list(db.calls.find(calls_query))
    test_call_ids = [str(c["_id"]) for c in test_calls]
    test_provider_call_ids = [c["providerCallId"] for c in test_calls]
    
    print("=== DRY RUN REPORT ===")
    print(f"\n[Calls Collection] Found {len(test_calls)} matching calls:")
    for c in test_calls:
        print(f"  - _id: {c['_id']}, providerCallId: {c['providerCallId']}")
        
    # 2. Find matching orders
    # Orders could be linked by the MongoDB ID string or the providerCallId string
    # We also include any order for "Pierre Dupont" as requested
    orders_query = {
        "$or": [
            {"callId": {"$in": test_call_ids}},
            {"callId": {"$in": test_provider_call_ids}},
            {"customerName": "Pierre Dupont"}
        ]
    }
    test_orders = list(db.orders.find(orders_query))
    print(f"\n[Orders Collection] Found {len(test_orders)} matching orders:")
    for o in test_orders:
        reason = "Matches test callId"
        if o.get("customerName") == "Pierre Dupont":
            reason = "Pierre Dupont test order"
        print(f"  - _id: {o['_id']}, customerName: {o.get('customerName')}, callId: {o.get('callId')} ({reason})")
        
    # 3. Find associated customers
    # A customer is associated if their ID is in the test orders
    # or their phone number is one of the test callers.
    # Let's collect customer IDs from test orders
    test_customer_ids = [str(o["customerId"]) for o in test_orders if o.get("customerId")]
    # Also collect phone numbers from test calls
    test_phones = [c["fromNumber"] for c in test_calls if c.get("fromNumber")]
    
    # Now query customers
    cust_query = {
        "$or": [
            {"_id": {"$in": [ObjectId(cid) for cid in test_customer_ids if ObjectId.is_valid(cid)]}},
            {"phone": {"$in": test_phones}}
        ]
    }
    
    potential_test_customers = list(db.customers.find(cust_query))
    
    customers_to_delete = []
    print(f"\n[Customers Collection] Analyzing {len(potential_test_customers)} potential test customers:")
    for cust in potential_test_customers:
        cust_id_str = str(cust["_id"])
        # Check if this customer has any NON-test orders
        non_test_orders = list(db.orders.find({
            "customerId": cust_id_str,
            "_id": {"$nin": [o["_id"] for o in test_orders]}
        }))
        
        # Check if this customer has any NON-test calls
        non_test_calls = list(db.calls.find({
            "fromNumber": cust["phone"],
            "_id": {"$nin": [c["_id"] for c in test_calls]}
        }))
        
        if len(non_test_orders) == 0 and len(non_test_calls) == 0:
            customers_to_delete.append(cust)
            print(f"  - _id: {cust['_id']}, name: {cust.get('name')}, phone: {cust.get('phone')} (Exclusively associated with test records)")
        else:
            print(f"  - _id: {cust['_id']}, name: {cust.get('name')} (KEEPING: Has {len(non_test_orders)} other orders and {len(non_test_calls)} other calls)")

    print("\n=== PROPOSED DELETION COUNTS ===")
    print(f"Calls: {len(test_calls)}")
    print(f"Orders: {len(test_orders)}")
    print(f"Customers: {len(customers_to_delete)}")
    
    MongoDBManager.disconnect()

if __name__ == "__main__":
    run_dry_run()
