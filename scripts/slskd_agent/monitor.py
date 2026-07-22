import json

class MonitorFormatter:
    @staticmethod
    def format_downloads(downloads_data):
        if not downloads_data or not isinstance(downloads_data, list):
            return "No active downloads."

        output_lines = []
        output_lines.append(f"{'USER':<15} {'STATE':<20} {'SPEED':<12} {'PROGRESS':<10} {'FILENAME'}")
        output_lines.append("-" * 90)

        for user_entry in downloads_data:
            username = user_entry.get("username", "Unknown")
            directories = user_entry.get("directories", [])
            for d in directories:
                for f in d.get("files", []):
                    state = f.get("state", "Queued")
                    speed_bps = f.get("averageSpeed", 0)
                    speed_kbps = speed_bps / 1024
                    speed_str = f"{speed_kbps:.1f} KB/s" if speed_kbps > 0 else "-"
                    percent = f"{f.get('percentComplete', 0):.1f}%"
                    filename = f.get("filename", "").split("\\")[-1]

                    output_lines.append(f"{username:<15} {state:<20} {speed_str:<12} {percent:<10} {filename[:30]}")

        return "\n".join(output_lines)
