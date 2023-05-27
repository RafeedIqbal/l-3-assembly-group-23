import re


def eight_chars(label):
    if re.match("_[A-Z]+",label):
        h = hash(label)
        h = h * h
        hx = format(h, 'x')
        hx = "_" + hx[:7]
    else:
        h = hash(label)
        h = h * h
        hx = format(h, 'x')
        hx = "x" + hx[:7]
    return hx

