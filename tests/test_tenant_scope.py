import unittest

from fastapi.testclient import TestClient

from app import app, audit_log
from auth import User


class TenantScopeTests(unittest.TestCase):
    def test_tenant_header_cannot_override_token_scope(self):
        headers = {"Authorization": "Bearer secret-token", "X-Tenant-ID": "tenant1"}
        with TestClient(app) as client:
            allowed = client.post("/generate", headers=headers, json={"prompt": "Hello"})
            self.assertEqual(allowed.status_code, 200)
            denied = client.post(
                "/generate",
                headers={**headers, "X-Tenant-ID": "tenant2"},
                json={"prompt": "Hello"},
            )
            self.assertEqual(denied.status_code, 403)

    def test_audit_reads_filter_other_tenants(self):
        entries = audit_log.entries[:]
        self.addCleanup(lambda: audit_log.entries.__setitem__(slice(None), entries))
        audit_log.record(User("other", "admin", "tenant2"), "/generate", "POST")
        with TestClient(app) as client:
            response = client.get(
                "/audit",
                headers={"Authorization": "Bearer secret-token", "X-Tenant-ID": "tenant1"},
            )
        self.assertEqual(response.status_code, 200)
        rows = response.json()
        self.assertTrue(rows)
        self.assertEqual({row["tenant_id"] for row in rows}, {"tenant1"})
