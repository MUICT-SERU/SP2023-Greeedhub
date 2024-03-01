import pytest

from inspire_service_orcid import utils


class TestChunkedSequence(object):
    def setup(self):
        self.sequence = [0, 2, 4, 6, 8, 10, 12, 14]

    def test_chunk_0(self):
        with pytest.raises(ValueError):
            list(utils.chunked_sequence_iter(self.sequence, 0))

    def test_chunk_1(self):
        result = list(utils.chunked_sequence_iter(self.sequence, 1))
        assert result == [[0], [2], [4], [6], [8], [10], [12], [14]]

    def test_chunk_2(self):
        result = list(utils.chunked_sequence_iter(self.sequence, 2))
        assert result == [[0, 2], [4, 6], [8, 10], [12, 14]]

    def test_chunk_3(self):
        result = list(utils.chunked_sequence_iter(self.sequence, 3))
        assert result == [[0, 2, 4], [6, 8, 10], [12, 14]]

    def test_chunk_len_sequence(self):
        result = list(utils.chunked_sequence_iter(self.sequence, len(self.sequence)))
        assert result == [self.sequence]

    def test_chunk_len_larger_than_sequence(self):
        result = list(utils.chunked_sequence_iter(self.sequence, len(self.sequence) + 1))
        assert result == [self.sequence]
