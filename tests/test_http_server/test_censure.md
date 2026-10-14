## Tests manuels du censeur

### Lancement
```bash
cd tests/serveur && python3 -m http.server 8000   # terminal 1
cd http_relay && python3 relai.py 127.0.0.1 8000  # terminal 2
```

### Cas à vérifier

| Commande | Attendu |
|---|---|
| `curl -i http://localhost:4567/` | 200 |
| `curl -i http://localhost:4567/public/test.txt` | 200 + contenu |
| `curl -i http://localhost:4567/prive/secret.txt` | 403 Forbidden |
| `curl -i http://localhost:4567/PRIVE/secret.txt` | 403 (insensible à la casse) |

