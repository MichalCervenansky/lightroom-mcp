import socket
import json
import logging

logger = logging.getLogger(__name__)

class LrCClient:
    def __init__(self, host='localhost', port=54321):
        self.host = host
        self.port = port
        self.sock = None

    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(5.0) # 5 second timeout
            self.sock.connect((self.host, self.port))
            logger.info(f"Connected to LrC at {self.host}:{self.port}")
            return True
        except ConnectionRefusedError:
            logger.error("Connection refused. Is LrC running with the plugin enabled?")
            return False
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False

    def send_command(self, method, params=None):
        if not self.sock:
            if not self.connect():
                raise ConnectionError("Not connected to LrC")

        request_id = 1 # Simple ID management
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": request_id
        }

        try:
            msg = json.dumps(request) + "\n"
            self.sock.sendall(msg.encode('utf-8'))
            
            # Read response
            # Simple readline implementation assuming newline delimited JSON
            response_data = b""
            while True:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                response_data += chunk
                if b"\n" in chunk:
                    break
            
            response_str = response_data.decode('utf-8').strip()
            if not response_str:
                return None
            
            return json.loads(response_str)

        except Exception as e:
            logger.error(f"Error communicating with LrC: {e}")
            self.sock.close()
            self.sock = None
            raise

    def close(self):
        if self.sock:
            self.sock.close()
            self.sock = None

