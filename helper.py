import re
from itertools import chain

from sortedcontainers import sortedlist


def get_key_name(key_code):

    if key_code < 256:
        if key_code == 0:
            k_name = "NUL"
        elif key_code < 27:
            k_name = "Ctrl-{}".format(chr(ord('A') + key_code - 1))
        else:
            k_name = "{}".format(chr(key_code))
    else:
        k_name = "(%s)" % key_code

    return k_name


class TagHistory:

    def __init__(self, original_txt=None):
        self.tags = sortedlist.SortedKeyList(key=lambda x: x[0][0])
        self.suggestion = sortedlist.SortedKeyList(key=lambda x: x[0][0])
        self.original_txt = original_txt

    def set_original_txt(self, original_txt):
        self.original_txt = original_txt

    def add_tag(self, sel_range, tag):

        if self.get_tag_in(sel_range) is not None:
            return False

        self.tags.add((sel_range, tag))
        return True

    def delete_tag(self, hist):
        return self.tags.remove(hist)

    def get_tag_in(self, sel_range):
        pos_b, pos_e = sel_range
        in_idx = self.tags.bisect_key_right(pos_b)

        if in_idx > 0:
            curr_tag = self.tags[in_idx - 1]
            tb, te = curr_tag[0]
            if pos_b >= tb and pos_e <= te:
                return curr_tag

        return None

    def reset(self):
        self.tags.clear()


def suggest_tag(token, text, with_bigram=True):

    match = re.finditer(r'{}'.format(token), text, re.MULTILINE | re.IGNORECASE)

    token = token.split()
    if with_bigram and len(token) >= 3:
        bigram_match = []

        for i in range(len(token)-1):
            m = re.finditer(' '.join((token[i], token[i+1])), text, re.MULTILINE | re.IGNORECASE)
            bigram_match.extend(m)

        return chain(match, bigram_match)

    return match
