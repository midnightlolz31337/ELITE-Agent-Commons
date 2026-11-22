import unittest
from elite_commons.cli import load_catalogue, validate


def tool_record(**overrides):
    item = {
        "id": "elite:test",
        "name": "Test Tool",
        "url": "https://github.com/example/test-tool",
        "capabilities": ["evidence"],
        "inputs": ["json"],
        "outputs": ["json"],
        "status": "prototype",
        "evidence": "Capability is documented in the repository.",
    }
    item.update(overrides)
    return item


class CatalogueTests(unittest.TestCase):
    def test_seed_catalogue_validates(self):
        self.assertEqual(validate(load_catalogue()), [])

    def test_duplicate_ids_rejected(self):
        data = {"schema_version": "1.0.0", "tools": [tool_record(), tool_record(name="Second")]}
        self.assertTrue(any("duplicate id" in e for e in validate(data)))

    def test_non_object_entry_rejected(self):
        self.assertIn("tools[0] must be an object", validate({"schema_version": "1.0.0", "tools": [None]}))

    def test_missing_required_fields_rejected(self):
        errors = validate({"schema_version": "1.0.0", "tools": [{"id": "x"}]})
        self.assertTrue(any("missing name" in e for e in errors))
        self.assertTrue(any("missing evidence" in e for e in errors))

    def test_wrong_field_types_rejected(self):
        errors = validate({"schema_version": "1.0.0", "tools": [tool_record(capabilities="evidence")]})
        self.assertTrue(any("capabilities must be a list" in e for e in errors))

    def test_noncanonical_url_rejected(self):
        errors = validate({"schema_version": "1.0.0", "tools": [tool_record(url="http://github.com/example/repo/issues")]})
        self.assertTrue(any("canonical https://" in e for e in errors))

    def test_unknown_status_rejected(self):
        errors = validate({"schema_version": "1.0.0", "tools": [tool_record(status="trusted")]})
        self.assertTrue(any("unsupported status" in e for e in errors))

    def test_malformed_url_rejected_without_crashing(self):
        errors = validate({"schema_version": "1.0.0", "tools": [tool_record(url="https://[invalid")]})
        self.assertTrue(any("canonical https://" in e for e in errors))

    def test_non_object_catalogue_rejected(self):
        self.assertEqual(validate([]), ["catalogue must be a JSON object"])


if __name__ == "__main__":
    unittest.main()
