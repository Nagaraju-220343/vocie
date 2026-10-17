import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from bson import ObjectId

# Ensure apps/backend is in sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.db.mongodb import MongoDBManager
from app.config.settings import settings


class MongoJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle MongoDB ObjectIds, datetimes, and bytes."""
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, bytes):
            return obj.hex()
        return super().default(obj)


def reset_demo_database(dry_run: bool = False, backup_dir: str = None, force: bool = False):
    print("=" * 60)
    print(" LE GOURMET — DEMO DATABASE RESET PROCEDURE")
    print("=" * 60)
    print(f"Timestamp:   {datetime.now().isoformat()}")
    print(f"Environment: {settings.app_env}")
    print(f"Database:    {settings.mongodb_database}")
    print(f"Mode:        {'DRY-RUN (PREVIEW ONLY)' if dry_run else 'EXECUTION'}")
    print("=" * 60)

    # Safety guard: prevent running against production
    if settings.app_env.lower() in ["prod", "production"] and not force:
        print("ERROR: Safety Guard Tripped! Database environment is set to PRODUCTION.")
        print("Refusing to run reset on production database.")
        sys.exit(1)

    MongoDBManager.connect()
    db = MongoDBManager.get_db()
    client = MongoDBManager.client

    # 1. Inspect records before cleanup
    calls = list(db.calls.find())
    orders = list(db.orders.find())
    customers = list(db.customers.find())
    faqs = list(db.faqs.find())

    cp_db = client["checkpointing_db"]
    checkpoints_count_before = cp_db.checkpoints.count_documents({})
    checkpoint_writes_count_before = cp_db.checkpoint_writes.count_documents({})

    print("\n[PRE-CLEANUP INVENTORY]")
    print(f"  Calls:             {len(calls)}")
    print(f"  Orders:            {len(orders)}")
    print(f"  Customers:         {len(customers)}")
    print(f"  Knowledge Base FAQs: {len(faqs)} (PRESERVED)")
    print(f"  Checkpoints:       {checkpoints_count_before}")
    print(f"  Checkpoint Writes: {checkpoint_writes_count_before}")

    if len(calls) == 0 and len(orders) == 0 and len(customers) == 0:
        print("\nDatabase is ALREADY in a clean state (0 calls, 0 orders, 0 customers).")
        print(f"Knowledge base FAQs remain intact ({len(faqs)} items).")
        MongoDBManager.disconnect()
        return

    # 2. Extract checkpoints to remove
    # Collect all thread_ids from calls (both providerCallId and internal id)
    call_thread_ids = set()
    for c in calls:
        if c.get("providerCallId"):
            call_thread_ids.add(f"call:{c['providerCallId']}")
            call_thread_ids.add(c["providerCallId"])
        call_thread_ids.add(f"call:{c['_id']}")
        call_thread_ids.add(str(c["_id"]))

    # Also include any known test checkpoint thread patterns
    all_threads = cp_db.checkpoints.distinct("thread_id")
    threads_to_clean = [t for t in all_threads if t in call_thread_ids or t.startswith("call:test") or t.startswith("call:call_") or t == "call:{{call.call_id}}"]

    checkpoints_to_delete = list(cp_db.checkpoints.find({"thread_id": {"$in": threads_to_clean}}))
    checkpoint_writes_to_delete = list(cp_db.checkpoint_writes.find({"thread_id": {"$in": threads_to_clean}}))

    print(f"\n[IDENTIFIED DEMO RECORDS FOR CLEANUP]")
    print(f"  Calls to delete:             {len(calls)}")
    print(f"  Orders to delete:            {len(orders)}")
    print(f"  Customers to delete:         {len(customers)}")
    print(f"  Checkpoints to delete:       {len(checkpoints_to_delete)} (across {len(threads_to_clean)} threads)")
    print(f"  Checkpoint writes to delete: {len(checkpoint_writes_to_delete)}")
    print(f"  FAQs to touch:               0 (FAQS ARE PROTECTED)")

    if dry_run:
        print("\n" + "=" * 60)
        print(" DRY-RUN COMPLETE. No changes were made to the database.")
        print(" Run without --dry-run (or with --force) to execute cleanup.")
        print("=" * 60)
        MongoDBManager.disconnect()
        return

    # 3. Create timestamped backup before deletion
    if not backup_dir:
        backup_dir = str(backend_dir / "backups")
    os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(backup_dir, f"backup_demo_{timestamp}.json")

    backup_payload = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "database": settings.mongodb_database,
            "environment": settings.app_env,
            "counts": {
                "calls": len(calls),
                "orders": len(orders),
                "customers": len(customers),
                "checkpoints": len(checkpoints_to_delete),
                "checkpoint_writes": len(checkpoint_writes_to_delete),
            }
        },
        "calls": calls,
        "orders": orders,
        "customers": customers,
        "checkpoints": checkpoints_to_delete,
        "checkpoint_writes": checkpoint_writes_to_delete
    }

    print(f"\n[CREATING BACKUP]")
    with open(backup_file, "w", encoding="utf-8") as f:
        json.dump(backup_payload, f, cls=MongoJSONEncoder, indent=2)
    print(f"  Successfully backed up records to:\n  {backup_file}")
    file_size_kb = os.path.getsize(backup_file) / 1024
    print(f"  Backup file size: {file_size_kb:.2f} KB")

    # 4. Perform scoped deletion
    print("\n[EXECUTING SCOPED DELETION]")
    del_calls_res = db.calls.delete_many({"_id": {"$in": [c["_id"] for c in calls]}})
    del_orders_res = db.orders.delete_many({"_id": {"$in": [o["_id"] for o in orders]}})
    del_cust_res = db.customers.delete_many({"_id": {"$in": [u["_id"] for u in customers]}})
    del_cp_res = cp_db.checkpoints.delete_many({"thread_id": {"$in": threads_to_clean}})
    del_cpw_res = cp_db.checkpoint_writes.delete_many({"thread_id": {"$in": threads_to_clean}})

    print(f"  Deleted calls:             {del_calls_res.deleted_count}")
    print(f"  Deleted orders:            {del_orders_res.deleted_count}")
    print(f"  Deleted customers:         {del_cust_res.deleted_count}")
    print(f"  Deleted checkpoints:       {del_cp_res.deleted_count}")
    print(f"  Deleted checkpoint writes: {del_cpw_res.deleted_count}")

    # 5. Post-cleanup verification
    print("\n[POST-CLEANUP VERIFICATION]")
    remaining_calls = db.calls.count_documents({})
    remaining_orders = db.orders.count_documents({})
    remaining_custs = db.customers.count_documents({})
    remaining_faqs = db.faqs.count_documents({})
    remaining_cp = cp_db.checkpoints.count_documents({})
    remaining_cpw = cp_db.checkpoint_writes.count_documents({})

    print(f"  Remaining Calls:             {remaining_calls} (Expected: 0)")
    print(f"  Remaining Orders:            {remaining_orders} (Expected: 0)")
    print(f"  Remaining Customers:         {remaining_custs} (Expected: 0)")
    print(f"  Remaining FAQs:              {remaining_faqs} (Expected: {len(faqs)})")
    print(f"  Remaining Checkpoints:       {remaining_cp}")
    print(f"  Remaining Checkpoint Writes: {remaining_cpw}")

    if remaining_calls == 0 and remaining_orders == 0 and remaining_custs == 0 and remaining_faqs == len(faqs):
        print("\n" + "=" * 60)
        print(" VERIFICATION PASSED: Database is in 100% clean state for demo!")
        print(" Knowledge base FAQs remain intact.")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print(" WARNING: Some unexpected records remain. Please inspect logs.")
        print("=" * 60)

    MongoDBManager.disconnect()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Le Gourmet Demo Database Reset Tool")
    parser.add_argument("--dry-run", action="store_true", help="Preview records to be deleted without making changes")
    parser.add_argument("--force", action="store_true", help="Execute cleanup without interactive prompt")
    parser.add_argument("--backup-dir", type=str, default=None, help="Directory to store timestamped backups")
    args = parser.parse_args()

    reset_demo_database(dry_run=args.dry_run, backup_dir=args.backup_dir, force=args.force)
