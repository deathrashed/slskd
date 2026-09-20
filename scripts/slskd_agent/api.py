import json
import os
import urllib.request
import urllib.parse
import urllib.error

class SlskdClient:
    def __init__(self, api_url=None, api_key=None, username=None, password=None):
        url = api_url or os.environ.get("SLSKD_API_URL") or "http://127.0.0.1:5030/api/v0"
        key = api_key or os.environ.get("SLSKD_API_KEY") or "LrL7I2k2jMJu7Xc1QX0JcDtgqq0ZP1YzGNy75DYLi8X"
        self.api_url = url.rstrip('/')
        self.api_key = key
        # Username/password (SLSKD_USERNAME / SLSKD_PASSWORD) log in for a bearer token and win over the API key.
        self.username = username or os.environ.get("SLSKD_USERNAME")
        self.password = password or os.environ.get("SLSKD_PASSWORD")
        self._token = None

    def _login(self):
        res = self._send("POST", "/session", {"username": self.username, "password": self.password}, {})
        self._token = res.get("token") if isinstance(res, dict) else None

    def _auth_headers(self):
        if self.username and self.password:
            if not self._token:
                self._login()
            if self._token:
                return {"Authorization": f"Bearer {self._token}"}
        return {"X-API-Key": self.api_key}

    def request(self, method, path, data=None):
        res = self._send(method, path, data, self._auth_headers())
        if self._token and isinstance(res, dict) and res.get("code") == 401:  # token expired
            self._token = None
            res = self._send(method, path, data, self._auth_headers())
        return res

    def _send(self, method, path, data, auth_headers):
        url = f"{self.api_url}{path}"
        headers = {**auth_headers, "Content-Type": "application/json"}
        body = json.dumps(data).encode("utf-8") if data is not None else None
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req) as resp:
                content = resp.read().decode("utf-8")
                return json.loads(content) if content else {}
        except urllib.error.HTTPError as e:
            err_content = e.read().decode("utf-8") if e.fp else ""
            return {"error": True, "code": e.code, "message": err_content}
        except Exception as e:
            return {"error": True, "message": str(e)}

    def get_application(self):
        return self.request("GET", "/application")

    def search(self, text, timeout=15000):
        return self.request("POST", "/searches", {"searchText": text, "searchTimeout": timeout})

    def get_search(self, search_id):
        return self.request("GET", f"/searches/{search_id}")

    def get_search_responses(self, search_id):
        return self.request("GET", f"/searches/{search_id}/responses")

    def enqueue_download(self, username, files):
        payload = [{"filename": f["filename"], "size": f.get("size", 0)} for f in files]
        endpoint = f"/transfers/downloads/{urllib.parse.quote(username)}"
        return self.request("POST", endpoint, payload)

    def get_downloads(self):
        return self.request("GET", "/transfers/downloads")
