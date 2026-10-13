"""Tests automatiques du relais cache (seul).

Usage : python3 tests_cache.py [fichier_relais]
Par défaut le relais est cache_http.py (même dossier que ce script).
Code de sortie : 0 si tout réussit, 1 sinon.
"""
import http.client
import os
import subprocess
import sys
import tempfile
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

ICI = os.path.dirname(os.path.abspath(__file__))
RELAI = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(ICI, "..", "..", "http_relay", "cache_http.py")
PORT_RELAI = int(os.environ.get("PORT_RELAI", 1234))  
PORT_SERVEUR = int(os.environ.get("PORT_SERVEUR", 9000))  
GROS = b"x" * 300_000

appels = {}            

class Serveur(BaseHTTPRequestHandler):
    def do_GET(self):
        appels[self.path] = appels.get(self.path, 0) + 1
        if self.path == "/test.html":
            code, corps = 200, b"<h1>test</h1>"
        elif self.path == "/gros.bin":
            code, corps = 200, GROS
        elif self.path.startswith("/page"):
            code, corps = 200, b"page"
        else:
            code, corps = 404, b"introuvable"
        self.send_response(code)
        self.send_header("Content-Length", str(len(corps)))
        self.end_headers()
        self.wfile.write(corps)

    def log_message(self, *a):
        pass


def get(chemin, methode="GET"):
    c = http.client.HTTPConnection("127.0.0.1", PORT_RELAI, timeout=5)
    try:
        c.request(methode, chemin)
        r = c.getresponse()
        return r.status, r.read()
    except Exception:
        return None, b""
    finally:
        c.close()


resultats = []


def verifie(nom, condition):
    resultats.append(bool(condition))
    print(("OK     " if condition else "ÉCHEC  ") + nom)


serveur = HTTPServer(("127.0.0.1", PORT_SERVEUR), Serveur)
threading.Thread(target=serveur.serve_forever, daemon=True).start()

dossier = tempfile.mkdtemp()   
relai = subprocess.Popen([sys.executable, RELAI, "127.0.0.1", str(PORT_SERVEUR)],
                         cwd=dossier, stdout=subprocess.DEVNULL)
time.sleep(1)

try:
    # 1. première requête, transmise au serveur
    s, c = get("/test.html")
    verifie("1. première requête -> 200 et bon contenu", s == 200 and c.endswith(b"<h1>test</h1>"))
    verifie("1. le serveur a été sollicité une fois", appels.get("/test.html") == 1)

    # 2. même requête, servie par le cache
    s, c = get("/test.html")
    verifie("2. requête identique -> même contenu", s == 200 and c.endswith(b"<h1>test</h1>"))
    verifie("2. le serveur n'a pas été resollicité", appels.get("/test.html") == 1)

    # 3. stockage sur disque
    verifie("3. index.json créé", os.path.isfile(os.path.join(dossier, "index.json")))
    verifie("3. un fichier dans cache/",
            os.path.isdir(os.path.join(dossier, "cache"))
            and len(os.listdir(os.path.join(dossier, "cache"))) == 1)

    # 4. gros fichier (réponse reçue en plusieurs morceaux)
    s, c = get("/gros.bin")
    verifie("4. gros fichier reçu intact", s == 200 and c == GROS)
    s, c = get("/gros.bin")
    verifie("4. gros fichier resservi par le cache", c == GROS and appels.get("/gros.bin") == 1)

    # 5. une réponse non 200 ne doit pas être mise en cache
    get("/absent")
    get("/absent")
    verifie("5. un 404 n'est pas mis en cache", appels.get("/absent") == 2)

    # 6. méthode non GET
    s, _ = get("/test.html", "POST")
    verifie("6. POST -> 405", s == 405)

    # 7. clients simultanés
    codes = []

    def client():
        codes.append(get("/page1")[0])

    fils = [threading.Thread(target=client) for _ in range(5)]
    for f in fils:
        f.start()
    for f in fils:
        f.join()
    verifie("7. 5 clients simultanés -> tous 200", codes == [200] * 5)

    # 8. serveur arrêté
    serveur.shutdown()
    serveur.server_close()
    s, c = get("/test.html")
    verifie("8. serveur arrêté, URI en cache -> toujours servie", s == 200 and c.endswith(b"<h1>test</h1>"))
    s, _ = get("/jamais-vu")
    verifie("8. serveur arrêté, URI inconnue -> 502", s == 502)
finally:
    relai.terminate()

print(f"\n{sum(resultats)}/{len(resultats)} tests réussis")
sys.exit(0 if all(resultats) else 1)
