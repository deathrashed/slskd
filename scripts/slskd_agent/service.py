import subprocess
import os

class ServiceManager:
    PLIST_PATH = os.path.expanduser("~/Library/LaunchAgents/org.slskd.daemon.plist")

    @staticmethod
    def status():
        cmd = ["launchctl", "list", "org.slskd.daemon"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            return "slskd: service running"
        return "slskd: service stopped"

    @staticmethod
    def start():
        uid = str(os.getuid())
        cmd = ["launchctl", "kickstart", "-k", f"gui/{uid}/org.slskd.daemon"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        return "slskd: service started" if res.returncode == 0 else "slskd: service start failed"

    @staticmethod
    def stop():
        uid = str(os.getuid())
        cmd = ["launchctl", "bootout", f"gui/{uid}/org.slskd.daemon"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        return "slskd: service stopped" if res.returncode == 0 else "slskd: service stop failed"
