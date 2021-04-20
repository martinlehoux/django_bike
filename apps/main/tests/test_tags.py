from random import shuffle

from ..views import tag_key


def test_order_tags():
    tags = ["0.7", "0.7.1", "0.10", "0.10.4", "1.1.34", "1.12"]
    shuffled = tags.copy()
    shuffle(shuffled)
    assert tags != shuffled
    wrong_sorted = list(sorted(shuffled))
    assert wrong_sorted != tags
    right_sorted = list(sorted(shuffled, key=tag_key))
    assert right_sorted == tags
