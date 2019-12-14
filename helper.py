import re

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

    def __init__(self):
        self.history = sortedlist.SortedKeyList(key=lambda x: x[0][0])

    def add_hist(self, pos, tag):

        if self.get_tag_in(pos) is not None:
            return False

        self.history.add((pos, tag))
        print(self.history)
        return True

    def get_tag_in(self, sel_range):
        pos_b, pos_e = sel_range
        in_idx = self.history.bisect_key_right(pos_b)

        if in_idx > 0:
            curr_tag = self.history[in_idx-1]
            tb, te = curr_tag[0]
            if pos_b >= tb and pos_e <= te:
                return curr_tag

        return None

    def delete_history(self, hist):
        return self.history.remove(hist)


def suggest_tag(token, text):

    match = re.finditer(r'{}'.format(token), text, re.MULTILINE)
    return match
