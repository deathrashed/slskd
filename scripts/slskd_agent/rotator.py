import time

class PeerRotator:
    def __init__(self, client, max_attempts=3, backoffs=(2, 4, 8)):
        self.client = client
        self.max_attempts = max_attempts
        self.backoffs = backoffs

    def enqueue_with_fallback(self, candidates):
        if not candidates:
            return {"success": False, "reason": "No candidates provided"}

        attempts = 0
        for cand in candidates[:self.max_attempts]:
            user = cand["username"]
            files = cand["files"]
            
            res = self.client.enqueue_download(user, files)
            
            if not res.get("error") and res.get("enqueued"):
                return {
                    "success": True,
                    "user": user,
                    "folder": cand["parent"],
                    "enqueued_count": len(res["enqueued"]),
                    "audio_count": cand["audio_count"]
                }
            
            attempts += 1
            if attempts < len(self.backoffs):
                time.sleep(self.backoffs[attempts - 1])

        return {"success": False, "reason": "All fallback candidates failed or returned empty slots"}
