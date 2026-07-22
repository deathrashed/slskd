import unittest
from unittest.mock import MagicMock
from slskd_agent.rotator import PeerRotator

class TestRotator(unittest.TestCase):
    def test_enqueue_first_candidate_success(self):
        mock_client = MagicMock()
        mock_client.enqueue_download.return_value = {"enqueued": [{"id": "123"}]}
        
        candidates = [{
            "username": "user1",
            "parent": "Folder",
            "audio_count": 10,
            "files": [{"filename": "01.mp3", "size": 100}]
        }]
        
        rotator = PeerRotator(mock_client, backoffs=(0.01,))
        res = rotator.enqueue_with_fallback(candidates)
        self.assertTrue(res["success"])
        self.assertEqual(res["user"], "user1")
        mock_client.enqueue_download.assert_called_once()

    def test_enqueue_fallback_to_second_candidate(self):
        mock_client = MagicMock()
        # First candidate fails, second candidate succeeds
        mock_client.enqueue_download.side_effect = [
            {"failed": [{}]},
            {"enqueued": [{"id": "456"}]}
        ]
        
        candidates = [
            {"username": "user1", "parent": "F1", "audio_count": 10, "files": [{"filename": "01.mp3", "size": 100}]},
            {"username": "user2", "parent": "F2", "audio_count": 10, "files": [{"filename": "01.mp3", "size": 100}]}
        ]
        
        rotator = PeerRotator(mock_client, backoffs=(0.01, 0.01))
        res = rotator.enqueue_with_fallback(candidates)
        self.assertTrue(res["success"])
        self.assertEqual(res["user"], "user2")
        self.assertEqual(mock_client.enqueue_download.call_count, 2)

if __name__ == '__main__':
    unittest.main()
