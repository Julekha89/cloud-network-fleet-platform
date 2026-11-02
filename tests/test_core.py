import json
import tempfile
import unittest
from pathlib import Path
from fleet.core import FleetStore, Device, load_sample

class FleetTests(unittest.TestCase):
    def setUp(self):
        self.store = FleetStore()
        self.store.add(Device('id1','r1','ap-south-1','router','healthy'))
        self.store.add(Device('id2','s1','ap-south-1','switch','offline'))

    def tearDown(self):
        self.store.close()

    def test_list(self):
        self.assertEqual(len(self.store.list_devices()), 2)

    def test_region_filter(self):
        self.assertEqual(self.store.list_devices('eu-central-1'), [])

    def test_health(self):
        result = self.store.assess('id1')
        self.assertEqual((result['status'],result['source']),('healthy','simulated'))

    def test_missing_device(self):
        self.assertIsNone(self.store.assess('missing'))

    def test_summary(self):
        summary = self.store.summary()
        self.assertEqual(summary['total'],2)
        self.assertEqual(summary['by_status']['offline'],1)

    def test_audit(self):
        self.store.assess('id1')
        self.assertEqual(self.store.audit_log()[0]['action'],'health_check')

    def test_invalid_status(self):
        with self.assertRaises(ValueError):
            self.store.add(Device('id3','r3','reg','router','UNKNOWN'))

    def test_duplicate_device(self):
        with self.assertRaises(Exception):
            self.store.add(Device('id1','r1','reg','router','healthy'))

    def test_sql_injection_safe(self):
        self.assertEqual(self.store.list_devices("' OR 1=1 --"),[])

    def test_persistence(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'fleet.db'
            s = FleetStore(path)
            s.add(Device('p1','p1','region','switch','healthy'))
            s.close()
            s2 = FleetStore(path)
            self.assertEqual(len(s2.list_devices()),1)
            s2.close()

    def test_sample(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp)/'sample.json'
            data.write_text(json.dumps([{'device_id':'x','hostname':'x','region':'r','device_type':'router','simulated_status':'healthy'}]))
            s=FleetStore()
            self.assertEqual(load_sample(s,data),1)
            s.close()

if __name__ == '__main__':
    unittest.main()
