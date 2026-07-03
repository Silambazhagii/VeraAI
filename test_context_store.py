from app.services.context_store import get_context_store
from app.core.enums import TriggerScope

store = get_context_store()

# Insert Category
store.insert_sample_category()
assert store.count_categories() == 1
assert store.exists(TriggerScope.CATEGORY, "cat_1")

# Get Context
cat = store.get_context(TriggerScope.CATEGORY, "cat_1")
assert cat.slug == "salon"

# Ignore same version
res = store.save_context(TriggerScope.CATEGORY, "cat_1", 1, cat)
assert res.status == "ignored"

# Reject older version
res = store.save_context(TriggerScope.CATEGORY, "cat_1", 0, cat)
assert res.status == "rejected"

# Replace newer version
res = store.save_context(TriggerScope.CATEGORY, "cat_1", 2, cat)
assert res.status == "replaced"
assert res.previous_version == 1
assert res.new_version == 2

# Count total
store.insert_sample_merchant()
store.insert_sample_customer()
assert store.count() == 3

# Delete
res = store.delete_context(TriggerScope.CATEGORY, "cat_1")
assert res.status == "deleted"
assert not store.exists(TriggerScope.CATEGORY, "cat_1")

print("All ContextStore verifications passed!")
