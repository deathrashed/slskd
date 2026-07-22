import unittest
from slskd_agent.completeness import AlbumCompletenessChecker, extract_track_number

class TestCompleteness(unittest.TestCase):
    def test_extract_track_number(self):
        self.assertEqual(extract_track_number("01 Malevolence.mp3"), 1)
        self.assertEqual(extract_track_number("02 - Anguish.flac"), 2)
        self.assertEqual(extract_track_number("Demolition Hammer - [05] - Infectious Hospital Waste.flac"), 5)

    def test_album_completeness_valid(self):
        files = [
            {"filename": "01 Track.mp3", "bitRate": 320, "size": 1000},
            {"filename": "02 Track.mp3", "bitRate": 320, "size": 1000},
            {"filename": "03 Track.mp3", "bitRate": 320, "size": 1000},
            {"filename": "cover.jpg", "size": 500}
        ]
        valid, reason, download_files = AlbumCompletenessChecker.validate(files, min_bitrate=320)
        self.assertTrue(valid)
        self.assertEqual(len(download_files), 4)

    def test_album_completeness_sequence_gap(self):
        files = [
            {"filename": "01 Track.mp3", "bitRate": 320, "size": 1000},
            {"filename": "03 Track.mp3", "bitRate": 320, "size": 1000},
            {"filename": "04 Track.mp3", "bitRate": 320, "size": 1000}
        ]
        valid, reason, download_files = AlbumCompletenessChecker.validate(files, min_bitrate=320)
        self.assertFalse(valid)
        self.assertIn("Missing tracks", reason)

    def test_album_completeness_low_bitrate(self):
        files = [
            {"filename": "01 Track.mp3", "bitRate": 192, "size": 1000},
            {"filename": "02 Track.mp3", "bitRate": 320, "size": 1000}
        ]
        valid, reason, download_files = AlbumCompletenessChecker.validate(files, min_bitrate=320)
        self.assertFalse(valid)
        self.assertIn("below threshold", reason)

if __name__ == '__main__':
    unittest.main()
