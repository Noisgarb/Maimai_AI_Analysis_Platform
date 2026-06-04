import json
import urllib.request


def main() -> None:
    payload = {"username": "FHGY", "b50": "1"}
    req = urllib.request.Request(
        "http://127.0.0.1:8000/analysis/b50",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        body = resp.read().decode("utf-8")
        print(body[:1200])


if __name__ == "__main__":
    main()
