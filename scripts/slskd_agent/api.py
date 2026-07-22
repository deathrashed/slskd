import json
import os
import urllib.request
import urllib.parse
import urllib.error

class SlskdClient:
    def __init__(self, api_url=None, api_key=None):
        url = api_url or os.environ.get("SLSKD_API_URL") or "http://127.0.0.1:5030/api/v0"
        key = api_key or os.environ.get("SLSKD_API_KEY") or "LrL7I2k2jMJu7Xc1QX0JcDtgqq0ZP1YzGNy75DYLi8X"
        self.api_url = url.rstrip('/')
        self.api_key = key

    def request(self, method, path, data=None):
        url = f"{self.api_url}{path}"
        headers = {"X-API-Key": self.api_key, "Content-Type": "application/json"}
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
