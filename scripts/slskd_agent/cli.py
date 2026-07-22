import sys
import json
import time
from slskd_agent.api import SlskdClient
from slskd_agent.completeness import AlbumCompletenessChecker, is_audio
from slskd_agent.rotator import PeerRotator
from slskd_agent.service import ServiceManager
from slskd_agent.monitor import MonitorFormatter

def main():
    if len(sys.argv) < 2:
        print("Usage: slskd-agent <album|search|downloads|monitor|service> [args] [--json]")
        sys.exit(1)

    json_mode = "--json" in sys.argv
    args = [a for a in sys.argv if a != "--json"]

    cmd = args[1]
    client = SlskdClient()

    if cmd == "service":
        action = args[2] if len(args) > 2 else "status"
        if action == "status":
            res = ServiceManager.status()
            print(json.dumps({"status": res}) if json_mode else res)
        elif action == "ping":
            app = client.get_application()
            reachable = not (isinstance(app, dict) and app.get("error"))
            if json_mode:
                print(json.dumps({"status": "success" if reachable else "failed", "reachable": reachable}))
            else:
                print("slskd API: reachable (HTTP 200)" if reachable else "slskd API: unreachable")
        elif action == "start":
            res = ServiceManager.start()
            print(json.dumps({"status": "started", "output": res}) if json_mode else res)
        elif action == "stop":
            res = ServiceManager.stop()
            print(json.dumps({"status": "stopped", "output": res}) if json_mode else res)

    elif cmd == "downloads":
        print(json.dumps(client.get_downloads(), indent=2 if not json_mode else None))

    elif cmd == "monitor":
        downloads = client.get_downloads()
        if json_mode:
            print(json.dumps({"downloads": downloads}))
        else:
            print(MonitorFormatter.format_downloads(downloads))

    elif cmd == "search" and len(args) > 2:
        query = args[2]
        print(json.dumps(client.search(query), indent=2 if not json_mode else None))

    elif cmd == "album" and len(args) > 2:
        query = args[2]
        min_br = int(args[3]) if len(args) > 3 and args[3].isdigit() else 320

        if not json_mode:
            print(f"Searching for '{query}' (min_bitrate={min_br}kbps)...")
        s_res = client.search(query)
        if s_res.get("error"):
            msg = s_res.get("message", "Search request failed")
            if json_mode:
                print(json.dumps({"status": "failed", "error": msg}))
            else:
                print("Search error:", msg)
            sys.exit(1)

        search_id = s_res.get("id")
        if not json_mode:
            print(f"Search ID: {search_id}. Polling for search results...")

        responses = []
        for _ in range(15):
            time.sleep(2)
            st = client.get_search(search_id)
            if st.get("state", "").startswith("Completed"):
                responses = client.get_search_responses(search_id)
                if responses and isinstance(responses, list):
                    break

        if not isinstance(responses, list) or not responses:
            if json_mode:
                print(json.dumps({"status": "failed", "error": "No search responses returned"}))
            else:
                print("No search responses returned.")
            sys.exit(1)

        candidates = []
        for r in responses:
            user = r.get("username")
            files = r.get("files", [])
            if not files:
                continue

            dirs = {}
            for f in files:
                fn = f.get("filename", "")
                parts = fn.replace("\\", "/").split("/")
                parent = "/".join(parts[:-1]) if len(parts) > 1 else ""
                dirs.setdefault(parent, []).append(f)

            for parent, d_files in dirs.items():
                valid, reason, download_files = AlbumCompletenessChecker.validate(d_files, min_br)
                if not valid:
                    continue

                has_flac = any(f.get("filename", "").lower().endswith(".flac") for f in download_files)
                total_size = sum(f.get("size", 0) for f in download_files)
                audio_count = len([f for f in download_files if is_audio(f.get("filename", ""))])

                candidates.append({
                    "username": user,
                    "parent": parent,
                    "has_flac": has_flac,
                    "audio_count": audio_count,
                    "total_files": len(download_files),
                    "total_size": total_size,
                    "files": download_files
                })

        if not candidates:
            msg = f"No complete album found matching criteria ({min_br}kbps)"
            if json_mode:
                print(json.dumps({"status": "failed", "error": msg}))
            else:
                print(f"No complete album found matching criteria ({min_br}kbps).")
            sys.exit(1)

        candidates.sort(key=lambda c: (0 if c["has_flac"] else 1, c["audio_count"], c["total_size"]), reverse=True)

        rotator = PeerRotator(client)
        result = rotator.enqueue_with_fallback(candidates)

        if result["success"]:
            payload = {
                "status": "success",
                "enqueued_count": result["enqueued_count"],
                "user": result["user"],
                "folder": result["folder"],
            }
            if json_mode:
                print(json.dumps(payload))
            else:
                print(f"SUCCESS: Enqueued {result['enqueued_count']} files from '{result['user']}' (Folder: {result['folder']})")
        else:
            payload = {"status": "failed", "error": result["reason"]}
            if json_mode:
                print(json.dumps(payload))
            else:
                print(f"ERROR: {result['reason']}")
            sys.exit(1)

if __name__ == "__main__":
    main()
