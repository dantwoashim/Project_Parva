from __future__ import annotations

from app.billing.service import BillingService

from .test_admin_billing_audit import _service


def test_billing_schema_migrations_install_audit_table_and_hot_path_indexes():
    service: BillingService = _service()
    indexes = service.store.fetchall(
        """
        SELECT name FROM sqlite_master
        WHERE type = 'index' AND name LIKE 'idx_%'
        ORDER BY name
        """
    )
    names = {row["name"] for row in indexes}

    assert service.store.fetchone("SELECT name FROM sqlite_master WHERE name = 'billing_audit_events'")
    assert "idx_api_keys_prefix_active" in names
    assert "idx_billing_audit_object" in names
    assert "idx_usage_counters_subject_period" in names


def test_billing_audit_queries_use_store_placeholders():
    service = _service()

    assert service.store.param() == "?"
    events = service.audit_events_for_object(
        object_type="api_key",
        object_id="key_1' OR 1=1 --",
    )

    assert events == []
