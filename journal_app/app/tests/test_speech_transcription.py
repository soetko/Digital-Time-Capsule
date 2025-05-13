import unittest
from unittest.mock import patch, MagicMock
from transcribe import transcribe_audio

class TestTranscription(unittest.TestCase):
    @patch("transcribe.sr.Recognizer")
    @patch("transcribe.sr.AudioFile")
    def test_transcribe_audio_success(self, mock_audiofile, mock_recognizer_class):
        mock_recognizer = MagicMock()
        mock_recognizer.record.return_value = "audio"
        mock_recognizer.recognize_google.return_value = "transcribed"
        mock_recognizer_class.return_value = mock_recognizer

        result = transcribe_audio("sample.wav")
        self.assertEqual(result, "transcribed")

if __name__ == "__main__":
    unittest.main()