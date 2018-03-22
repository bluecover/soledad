# -*- coding: utf-8 -*-

import re


__all__ = ['trunc_utf8']


def trunc_utf8(string, num, etc='...'):
    """Truncate a utf-8 string, show as num chars.

    :param string: string, a utf-8 encoding string or unicode.
    :param num: look like num chars.
    :returns: the truncated utf-8 string.
    """
    if not isinstance(string, unicode):
        string = string.decode('utf8', 'ignore')
    if not etc:
        etc = u''
    if not isinstance(etc, unicode):
        etc = etc.decode('utf8', 'ignore')

    gb = string.encode('gb18030', 'ignore')
    if num >= len(gb):
        return string.encode('utf8')
    if etc:
        etc_len = len(etc.encode('gb18030', 'ignore'))
        trunc_idx = num - etc_len
    else:
        trunc_idx = num
    ret = gb[:trunc_idx].decode('gb18030', 'ignore').encode('utf8')
    if etc:
        ret += etc.encode('utf8')
    return ret


def trunc_utf8_by_char(string, num, etc='...'):
    unistr = string.decode('utf8', 'ignore')
    if num >= len(unistr):
        return string
    str = unistr[:num].encode('utf8')
    if etc:
        str += etc
    return str


def utf8_length(string):
    return string and \
        len(string.decode('utf8', 'ignore').encode('gb18030', 'ignore')) or 0


__width_map = [
    (126, 1), (159, 0), (687, 1), (710, 0), (711, 1),
    (727, 0), (733, 1), (879, 0), (1154, 1), (1161, 0),
    (4347, 1), (4447, 2), (7467, 1), (7521, 0), (8369, 1),
    (8426, 0), (9000, 1), (9002, 2), (11021, 1), (12350, 2),
    (12351, 1), (12438, 2), (12442, 0), (19893, 2), (19967, 1),
    (55203, 2), (63743, 1), (64106, 2), (65039, 1), (65059, 0),
    (65131, 2), (65279, 1), (65376, 2), (65500, 1), (65510, 2),
    (120831, 1), (262141, 2), (1114109, 1),
]
# from East_Asian_Width
# http://www.unicode.org/Public/4.0-Update/EastAsianWidth-4.0.0.txt


def utf8_length2(s):
    """
    >>> utf8_length2('abc')
    3

    >>> utf8_length2('中文')
    4

    >>> utf8_length('♥')
    4

    >>> utf8_length2('♥')
    1
    """
    def _(c):
        c = ord(c)
        for num, wid in __width_map:
            if c <= num:
                return wid
        return 1
    return sum((_(c) for c in s.decode('utf8', 'ignore')))


_RE_STRIPSPACE = re.compile(r'(?mu)^\s+|\s+$')


def strip_utf8(utf8_str):
    if not utf8_str:
        return ''
    s = _RE_STRIPSPACE.sub('', utf8_str.decode('utf8', 'ignore'))
    return s.encode('utf8')


def iif(b, s1, s2):
    return s1 if b else s2


# 数字金额转化为汉语大写金额
def num2chn(nin=None):
    cs = ('零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖', '◇', '分', '角', '圆', '拾', '佰',
          '仟', '万', '拾', '佰', '仟', '亿', '拾', '佰', '仟', '万')
    st = ''
    st1 = ''
    s = '%0.2f' % nin
    sln = len(s)
    if sln > 15:
        return None
    fg = (nin < 1)

    for i in range(0, sln - 3):
        ns = ord(s[sln - i - 4]) - ord('0')
        st = iif((ns == 0) and (fg or (i == 8) or (i == 4) or (i == 0)), '', cs[ns]) + \
            iif((ns == 0) and ((i != 8) and (i != 4) and (i != 0) or fg and (i == 0)), '',
                cs[i + 13]) + st
        fg = (ns == 0)
    fg = False

    for i in [1, 2]:
        ns = ord(s[sln - i]) - ord('0')
        st1 = iif((ns == 0) and ((i == 1) or (i == 2) and (fg or (nin < 1))), '', cs[ns]) + \
            iif((ns > 0), cs[i + 10], iif((i == 2) or fg, '', '整')) + st1
        fg = (ns == 0)
    st.replace('亿万', '万')

    return iif(nin == 0, '零', st + st1)
