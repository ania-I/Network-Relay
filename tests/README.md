## Ressources and LLMs
















# Tests automatisés pour cache HTTP

> Source: https://claude.ai/chat/0335c433-724a-4491-be99-b3acde19abac



## Utilisateur

*2026-10-14 10:11*

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

voici un code de cache http , je veux un code de test automatisé traitant les cas suivant: 1. tester si le serveur repond bien ; 2.refaire la meme requette pour savoir si le cache fonctionne 3. envoie d'un gros fichier , pou tester l'envoie par morceaux, 4.Demander une ressoure inexistante afin de voir si la reponse est mise en cache ( elle ne doit pas l'etre) 5.tester avec une méthode non get 6.simuler plusier clients


## Claude

*2026-10-14 10:12*

Voici un fichier de tests `test_relay.py` en `unittest`, sans dépendance externe. Il lance un faux serveur d'origine avec compteur de requêtes, puis ton relais en sous-processus dans un dossier temporaire pour ne pas polluer ton `cache/` ni ton `index.json`.

```python
import hashlib
import json
import os
import socket
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

RELAY_SCRIPT = os.path.abspath(os.environ.get("RELAY_SCRIPT", "relay.py"))
RELAY_PORT = 1234          # _local_port du relais
ORIGIN_PORT = 8080
BIG_BODY = os.urandom(3 * 1024 * 1024)   # 3 Mo

hits = {}                  # path -> nombre de requêtes reçues par l'origine
hits_lock = threading.Lock()


class Origin(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *args):
        pass

    def do_GET(self):
        with hits_lock:
            hits[self.path] = hits.get(self.path, 0) + 1

        if self.path == "/big.bin":
            status, body = 200, BIG_BODY
        elif self.path.startswith(("/hello", "/cache", "/page", "/same")):
            status, body = 200, f"contenu de {self.path}".encode()
        else:
            status, body = 404, b"<h1>404 Not Found</h1>"

        self.send_response(status)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(body)


def raw_request(raw: bytes, timeout=10):
    """Envoie des octets bruts au relais, lit jusqu'à la fermeture, renvoie (status, headers, body)."""
    with socket.create_connection(("127.0.0.1", RELAY_PORT), timeout=timeout) as s:
        s.sendall(raw)
        data = b""
        while True:
            chunk = s.recv(65536)
            if not chunk:
                break
            data += chunk
    head, _, body = data.partition(b"\r\n\r\n")
    status_line = head.split(b"\r\n")[0].decode()
    return status_line, head, body


def get(uri):
    return raw_request(f"GET {uri} HTTP/1.1\r\nHost: localhost\r\n\r\n".encode())


class TestRelay(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.origin = ThreadingHTTPServer(("127.0.0.1", ORIGIN_PORT), Origin)
        threading.Thread(target=cls.origin.serve_forever, daemon=True).start()

        cls.tmp = tempfile.TemporaryDirectory()
        cls.proc = subprocess.Popen(
            [sys.executable, RELAY_SCRIPT, "127.0.0.1", str(ORIGIN_PORT)],
            cwd=cls.tmp.name,
        )
        # attendre que le relais écoute
        for _ in range(50):
            try:
                socket.create_connection(("127.0.0.1", RELAY_PORT), timeout=0.2).close()
                break
            except OSError:
                time.sleep(0.1)
        else:
            cls.proc.kill()
            raise RuntimeError("Le relais ne démarre pas")

    @classmethod
    def tearDownClass(cls):
        cls.proc.kill()
        cls.proc.wait()
        cls.origin.shutdown()
        cls.tmp.cleanup()

    def index(self):
        path = os.path.join(self.tmp.name, "index.json")
        if not os.path.exists(path):
            return {}
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    # 1. Le serveur répond
    def test_1_reponse_basique(self):
        status, _, body = get("/hello.html")
        self.assertIn("200", status)
        self.assertEqual(body, b"contenu de /hello.html")

    # 2. Même requête deux fois -> la 2e vient du cache
    def test_2_cache(self):
        uri = "/cache.html"
        _, _, body1 = get(uri)
        self.assertEqual(hits[uri], 1)

        _, _, body2 = get(uri)
        self.assertEqual(hits[uri], 1, "L'origine a été recontactée : pas de cache")
        self.assertEqual(body1, body2)
        self.assertIn(uri, self.index())

    # 3. Gros fichier (envoi par morceaux) + intégrité, puis depuis le cache
    def test_3_gros_fichier(self):
        status, _, body = get("/big.bin")
        self.assertIn("200", status)
        self.assertEqual(len(body), len(BIG_BODY))
        self.assertEqual(hashlib.sha256(body).digest(), hashlib.sha256(BIG_BODY).digest())

        _, _, body2 = get("/big.bin")
        self.assertEqual(hits["/big.bin"], 1)
        self.assertEqual(body2, body)

    # 4. Ressource inexistante : 404 non mis en cache
    def test_4_404_non_cache(self):
        uri = "/inexistant.html"
        status, _, _ = get(uri)
        self.assertIn("404", status)
        get(uri)
        self.assertEqual(hits[uri], 2, "Le 404 a été mis en cache")
        self.assertNotIn(uri, self.index())

    # 5. Méthodes non GET (+ requête mal formée)
    def test_5_methodes_non_get(self):
        for method in ("POST", "PUT", "DELETE", "HEAD"):
            with self.subTest(method=method):
                status, _, _ = raw_request(
                    f"{method} /hello.html HTTP/1.1\r\nHost: localhost\r\nContent-Length: 0\r\n\r\n".encode()
                )
                self.assertIn("405", status)
        status, _, _ = raw_request(b"N'IMPORTE QUOI\r\n\r\n")
        self.assertIn("400", status)

    # 6a. Plusieurs clients, ressources différentes
    def test_6_clients_multiples(self):
        uris = [f"/page{i}.html" for i in range(20)]

        def worker(uri):
            _, _, body = get(uri)
            return uri, body

        with ThreadPoolExecutor(max_workers=10) as ex:
            results = list(ex.map(worker, uris))

        for uri, body in results:
            self.assertEqual(body, f"contenu de {uri}".encode())

        # détecte une éventuelle race condition sur index.json
        idx = self.index()
        missing = [u for u in uris if u not in idx]
        self.assertFalse(missing, f"Entrées perdues dans index.json : {missing}")

    # 6b. Plusieurs clients, même ressource en même temps
    def test_6b_meme_ressource_concurrente(self):
        uri = "/same.html"
        with ThreadPoolExecutor(max_workers=10) as ex:
            results = list(ex.map(lambda _: get(uri)[2], range(10)))
        self.assertTrue(all(b == f"contenu de {uri}".encode() for b in results))
        # puis une requête de plus : doit venir du cache
        before = hits[uri]
        get(uri)
        self.assertEqual(hits[uri], before)


if __name__ == "__main__":
    unittest.main(verbosity=2)
```

**Lancement** (le relais doit être arrêté, car le port 1234 est fixe) :
```
python test_relay.py
```
Si ton script ne s'appelle pas `relay.py` : `RELAY_SCRIPT=mon_fichier.py python test_relay.py` (sous Windows : `set RELAY_SCRIPT=mon_fichier.py`).

**Deux points que les tests peuvent révéler dans ton code :**
- **Race condition sur `index.json`** : plusieurs threads font lecture, modification, écriture sans verrou. Le test 6 peut échouer avec des entrées perdues ou un JSON corrompu. Corrige avec un `threading.Lock()` autour de `_handle_response`.
- **Test du statut** : `b"200" in status` est trop permissif. Préfère `status.split()[1] == b"200"`.

Tu peux aussi réduire `listen(1)` si tu vois des refus de connexion avec beaucoup de clients simultanés (`listen(50)` par exemple).


---

> Exported by SaveAI · https://www.saveai.one