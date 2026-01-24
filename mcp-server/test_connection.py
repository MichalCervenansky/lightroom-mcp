import sys
import unittest
from lrc_client import LrCClient

class TestLrcConnection(unittest.TestCase):
    def test_connection_and_info(self):
        client = LrCClient()
        print("Attempting to connect to LrC...")
        if not client.connect():
            print("Skipping test: LrC not connected (Plugin likely not running)")
            return

        print("Connected. Sending get_studio_info...")
        response = client.send_command("get_studio_info")
        print(f"Response: {response}")
        
        self.assertIsNotNone(response)
        self.assertIn("result", response)
        self.assertIn("catalogName", response["result"])
        
        client.close()

if __name__ == '__main__':
    unittest.main()
