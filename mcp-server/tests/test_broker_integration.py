import unittest
import threading
import time
import json
import socket
import sys
import os
import requests
from unittest.mock import patch, MagicMock

# Add parent directory to path to import broker
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import broker

class TestBrokerIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Configure broker for testing
        cls.test_port = 8090
        cls.socket_port = 8091
        broker.BROKER_PORT = cls.test_port
        broker.SOCKET_PORT = cls.socket_port
        broker.HISTORY_AUTO_SAVE = False

        # Start broker in a separate thread
        cls.server_thread = threading.Thread(target=lambda: broker.app.run(host='127.0.0.1', port=cls.test_port, threaded=True), daemon=True)
        cls.server_thread.start()

        # Start socket server in a separate thread
        cls.socket_thread = threading.Thread(target=broker.run_socket_server, daemon=True)
        cls.socket_thread.start()

        # Wait for servers to start
        time.sleep(2)

    def setUp(self):
        # Clear state
        broker.pending_requests.clear()
        with broker.request_queue_lock:
            broker.request_queue.clear()
            broker.request_queue_event.clear()

    def test_full_request_cycle_http(self):
        """test full request cycle using HTTP polling (simulating Lightroom plugin)"""

        # 1. MCP Client sends request to Broker
        def send_client_request():
            url = f"http://127.0.0.1:{self.test_port}/request"
            response = requests.post(url, json={"jsonrpc": "2.0", "method": "test_method", "id": 1, "params": {"foo": "bar"}})
            return response.json()

        client_thread = threading.Thread(target=send_client_request)
        # We need a way to get the return value from the thread, but for simplicity let's just run it
        # Actually, requests.post is blocking, so we need to run it in a thread or it will block this test
        # But we also need to simulate the plugin side.

        # Let's use a queue to get the result from the client thread
        import queue
        result_queue = queue.Queue()

        def client_worker():
            try:
                res = send_client_request()
                result_queue.put(res)
            except Exception as e:
                result_queue.put(e)

        t = threading.Thread(target=client_worker)
        t.start()

        # 2. Broker queues request. Plugin polls for it.
        # Simulate Plugin polling
        time.sleep(0.5) # Give time for request to arrive

        poll_url = f"http://127.0.0.1:{self.test_port}/poll"
        poll_response = requests.post(poll_url)

        self.assertEqual(poll_response.status_code, 200)
        request_data = poll_response.json()
        self.assertEqual(request_data["method"], "test_method")
        self.assertTrue("_broker_uuid" in request_data)

        request_uuid = request_data["_broker_uuid"]

        # 3. Plugin processes request and sends response
        response_data = {
            "jsonrpc": "2.0",
            "result": "success",
            "id": request_data["id"],
            "_broker_uuid": request_uuid
        }

        response_url = f"http://127.0.0.1:{self.test_port}/response"
        requests.post(response_url, json=response_data)

        # 4. Broker receives response and returns it to Client
        t.join(timeout=2)

        self.assertFalse(result_queue.empty())
        client_result = result_queue.get()

        self.assertEqual(client_result["result"], "success")

    def test_full_request_cycle_socket(self):
        """test full request cycle using Socket connection (simulating Lightroom plugin)"""

        # 1. Connect simulated plugin via socket
        plugin_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        plugin_socket.connect(('127.0.0.1', self.socket_port))

        # 2. MCP Client sends request
        def send_client_request():
            url = f"http://127.0.0.1:{self.test_port}/request"
            try:
                response = requests.post(url, json={"jsonrpc": "2.0", "method": "socket_test", "id": 2, "params": {}})
                return response.json()
            except Exception as e:
                return {"error": str(e)}

        import queue
        result_queue = queue.Queue()
        def client_worker():
            result_queue.put(send_client_request())

        t = threading.Thread(target=client_worker)
        t.start()

        # 3. Plugin receives request via socket
        plugin_socket.settimeout(2.0)
        data = plugin_socket.recv(4096)
        while b'\n' not in data:
            data += plugin_socket.recv(4096)

        message = json.loads(data.strip())
        self.assertEqual(message["method"], "socket_test")

        # 4. Plugin sends response via socket
        response_data = {
            "jsonrpc": "2.0",
            "result": "socket_success",
            "id": message["id"],
            "_broker_uuid": message["_broker_uuid"]
        }
        plugin_socket.sendall(json.dumps(response_data).encode('utf-8') + b'\n')

        # 5. Client receives response
        t.join(timeout=2)
        client_result = result_queue.get()

        self.assertEqual(client_result.get("result"), "socket_success")

        plugin_socket.close()

if __name__ == '__main__':
    unittest.main()
