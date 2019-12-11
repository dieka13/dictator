def key_name(key_code):

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
        self.history = []

    def add_hist(self, pos, tag):

        if self.is_tagged(pos):
            return False

        self.history.append((pos, tag))
        print(self.history)
        return True

    def is_tagged(self, pos):
        b, e = pos

        for h in self.history:
            tb, te = h[0]
            if b >= tb and e <= te:
                return True
            else:
                continue

        return False

    def pop_hist(self):
        return self.history.pop()