from kivy.utils import get_color_from_hex


def rgba(s, *args):
    '''
    Return a kivy color (4 value from 0-1 range) from either a hex string or a
    list of 0-255 values
    '''
    if isinstance(s, str):
        return get_color_from_hex(s)
    elif isinstance(s, (list, tuple)):
        s = [x / 255. for x in s]
        if len(s) == 3:
            return s + [1]
        return s
    elif isinstance(s, int):
        if len(args) == 2: # rgb
            return [x / 255. for x in (s, *args)] + [1]
        else:
            return [x / 255. for x in (s, *args)[:-1]] + [args[-1]]
    raise Exception('Invalid value (not a string / list / tuple)')
