"""Exercise the real localhost boundary, including upload failures and provenance."""
import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from app import Handler
from engine import export_csv, sample_rows


class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)

    def post(self, body, origin=None):
        headers = {"Content-Type": "application/json"}
        if origin:
            headers["Origin"] = origin
        request = Request(self.base + "/api/analyze",
                          data=json.dumps(body).encode(), headers=headers)
        try:
            with urlopen(request, timeout=10) as response:
                return response.status, json.load(response)
        except HTTPError as error:
            return error.code, json.load(error)

    def test_sample_endpoint(self):
        status, result = self.post({"buffer": 0})
        self.assertEqual(status, 200)
        self.assertTrue(result["synthetic"])
        self.assertEqual(result["evaluation_rows"], 63)

    def test_sample_upload_stays_labeled(self):
        status, result = self.post({"csv": export_csv(sample_rows()), "buffer": 0})
        self.assertEqual(status, 200)
        self.assertTrue(result["synthetic"])
        self.assertTrue(result["uploaded_sample"])

    def test_real_upload_ignores_synthetic_demand(self):
        text = export_csv(sample_rows()).replace("SYNTHETIC_DEMO", "USER_UPLOADED_UNVERIFIED")
        status, result = self.post({"csv": text})
        self.assertEqual(status, 200)
        self.assertFalse(result["synthetic"])

    def test_bad_field_returns_error_and_server_remains_usable(self):
        bad = "date,product,baked,sold,price,cost\n2026-10-01," + "x" * 140000 + ",10,5,500,200"
        status, result = self.post({"csv": bad})
        self.assertEqual(status, 400)
        self.assertIn("error", result)
        self.assertEqual(self.post({})[0], 200)

    def test_cross_origin_rejected(self):
        self.assertEqual(self.post({}, "https://example.com")[0], 403)

    def test_arbitrary_file_route_rejected(self):
        with self.assertRaises(HTTPError) as caught:
            urlopen(self.base + "/engine.py", timeout=3)
        self.assertEqual(caught.exception.code, 404)


if __name__ == "__main__":
    unittest.main()
