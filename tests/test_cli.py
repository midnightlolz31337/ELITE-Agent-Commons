import unittest
from elite_commons.cli import load_catalogue, validate

class CatalogueTests(unittest.TestCase):
    def test_seed_catalogue_validates(self):
        self.assertEqual(validate(load_catalogue()), [])

    def test_duplicate_ids_rejected(self):
        data = {"schema_version":"1.0.0","tools":[
            {"id":"x","name":"A","url":"https://github.com/a/b","capabilities":[],"inputs":[],"outputs":[],"status":"test","evidence":"x"},
            {"id":"x","name":"B","url":"https://github.com/a/c","capabilities":[],"inputs":[],"outputs":[],"status":"test","evidence":"x"}
        ]}
        self.assertTrue(any("duplicate id" in e for e in validate(data)))

if __name__ == "__main__":
    unittest.main()
