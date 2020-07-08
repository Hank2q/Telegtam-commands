import mimetypes
import os
photo = 'readme.png'


def is_type(filetype, file):
    kind, _ = mimetypes.guess_type(file)
    print(kind)
    if kind != None:
        return filetype in kind
    return False


print(is_type('image', photo))
