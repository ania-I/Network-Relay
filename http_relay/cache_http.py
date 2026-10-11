from socket import *
from threading import *
import sys
import os
import json
import hashlib


class HttpRelay:
    def __init__(self):
        self._local_port: int = 1234
        self._remote_addr: str = ""
        self._remote_port: int = 0
        self._timeout: int = 2

    def _build_response(self, status, body):
        return (f"HTTP/1.1 {status}\r\nContent-Length: {len(body)}\r\n\r\n{body}").encode()

    def _get_from_cache(self, uri):
        try:
            with open("index.json", "r", encoding="utf-8") as f:
                index = json.load(f)
        except FileNotFoundError:
            return None

        if uri in index and os.path.isfile(index[uri]):
            with open(index[uri], "rb") as f:
                return f.read()
        return None

    def _handle_response(self, uri, response):
        os.makedirs("cache", exist_ok=True)
        cache_path = os.path.join("cache", hashlib.sha256(uri.encode()).hexdigest())
        with open(cache_path, "wb") as f:
            f.write(response)
        try:
            with open("index.json", "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {}

        data[uri] = cache_path

        with open("index.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def _transfere(self, uri, version):
        exit_point = socket(AF_INET, SOCK_STREAM)
        exit_point.settimeout(self._timeout)

        try:
            exit_point.connect((self._remote_addr, self._remote_port))
            exit_point.sendall(
                f"GET {uri} {version}\r\nHost: {self._remote_addr}\r\nConnection: close\r\n\r\n".encode()
            )
            response = b""
            while True:
                chunk = exit_point.recv(2048)
                if not chunk:
                    break
                response += chunk

        except OSError:
            print(f"Impossible de joindre {self._remote_addr}:{self._remote_port}")
            return None

        finally:
            exit_point.close()

        return response

    def _handle_request(self, request):
        parts = request.split("\r\n")[0].split()

        if len(parts) != 3:
            return self._build_response("400 Bad Request", "<h1>400 Bad Request</h1>")

        method, uri, version = parts

        if method != "GET":
            return self._build_response("405 Method Not Allowed", "<h1>405 Method Not Allowed</h1>")

        response = self._get_from_cache(uri)
        if response is not None:
            print(f"[CACHE] {uri}")
            return response

        print(f"[RELAI] {uri}")
        response = self._transfere(uri, version)
        if response is None:
            return self._build_response("502 Bad Gateway", "<h1>502 Bad Gateway</h1>")
        
        status=response.split(b"\r\n",1)[0]
        if b"200" in status:
          self._handle_response(uri, response)
        return response

    def _handle_client(self, ClientSocket) -> None:
        try:
            data = b""
            while b"\r\n\r\n" not in data:
                chunk = ClientSocket.recv(1024)
                if not chunk:
                    return
                data += chunk
            ClientSocket.sendall(self._handle_request(data.decode(errors="replace")))
        except OSError:
            pass
        finally:
            ClientSocket.close()

    def start(self) -> None:
        if len(sys.argv[1:]) != 2:
            print("Usage: script.py [remote_addr] [remote_port]")
            print("Example: script.py 127.0.0.1 8080")
            sys.exit(1)

        self._remote_addr = sys.argv[1]
        self._remote_port = int(sys.argv[2])

        listener = socket(AF_INET, SOCK_STREAM)

        try:
            listener.bind(('', self._local_port))
        except error as e:
            print(f"Binding failed: {e}")
            sys.exit(1)

        listener.listen(1)

        while True:
            connectionSocket, address = listener.accept()
            print(f"addresse connectée {address}")
            Thread(target=self._handle_client, args=(connectionSocket,)).start()


if __name__ == "__main__":
    relay = HttpRelay()
    relay.start()