import os
import re

AUDIO_EXTS = {".mp3", ".flac", ".m4a", ".alac", ".wav", ".ogg", ".aac"}
META_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".cue", ".log", ".txt", ".pdf", ".nfo", ".m3u", ".m3u8"}

def is_audio(filename):
    return any(filename.lower().endswith(ext) for ext in AUDIO_EXTS)

def is_artwork_or_meta(filename):
    return any(filename.lower().endswith(ext) for ext in META_EXTS)

def extract_track_number(filename):
    base = os.path.basename(filename)
    match = re.search(r'(?:^|[_\s\-\[\(])(\d{1,2})(?:[_\s\-\.\]\)]|$)', base)
    return int(match.group(1)) if match else None

class AlbumCompletenessChecker:
    @staticmethod
    def validate(files_list, min_bitrate=320):
        audio_files = [f for f in files_list if is_audio(f.get("filename", ""))]
        if not audio_files:
            return False, "No audio files in directory", []

        has_flac = any(f.get("filename", "").lower().endswith(".flac") for f in audio_files)
        if not has_flac:
            for f in audio_files:
                if f.get("bitRate", 0) < min_bitrate:
                    return False, f"Bitrate {f.get('bitRate')}kbps below threshold {min_bitrate}kbps", []

        track_nums = [extract_track_number(f.get("filename", "")) for f in audio_files]
        valid_nums = [t for t in track_nums if t is not None]

        if len(valid_nums) >= 3:
            valid_nums.sort()
            min_t, max_t = valid_nums[0], valid_nums[-1]
            expected_count = max_t - min_t + 1
            if len(valid_nums) < expected_count:
                return False, f"Missing tracks: found {len(valid_nums)} tracks across range {min_t}-{max_t}", []

        download_files = [f for f in files_list if is_audio(f.get("filename", "")) or is_artwork_or_meta(f.get("filename", ""))]
        return True, "Complete", download_files
