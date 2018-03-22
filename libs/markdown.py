# coding: utf-8

from warnings import warn

from misaka import Markdown, HtmlRenderer
from BeautifulSoup import BeautifulSoup

rndr = HtmlRenderer()
md = Markdown(rndr)

VALID_TAGS = [
    'div',
    'h2',
    'h3',
    'span',
    'a',
    'p',
    'br',
    'img',
    'center',
    'b',
    'strong',
    'em',
    'i',
    'ol',
    'ul',
    'li',
    'dl',
    'dt',
    'dd',
    'table',
    'thead',
    'td',
    'tr',
    'th',
    'tbody',
    'tfooter',
]

VALID_ATTRS = dict(
    a=['href', 'target', 'title'],
    img=['src', 'title', 'alt']
)

VALID_ATTR_VALUE = dict(
    a=dict(target='_blank')
)


def sanitize_html(value):

    soup = BeautifulSoup(value)

    for tag in soup.findAll(True):
        # filt tag name
        if tag.name not in VALID_TAGS:
            tag.hidden = True
            continue

        # filt if no contents between tag
        if not tag.contents:
            if tag and tag.name != 'img':
                tag.hidden = True
            continue

        # filt tag attrs
        if tag.attrs:
            _vattr = VALID_ATTR_VALUE.get(tag.name, [])
            _attrs = []

            # for loop tag.attrs
            for att in tag.attrs:
                att_name, att_value = att
                # if attr is valid
                if att_name in VALID_ATTRS.get(tag.name, []):
                    # if we need to set default value
                    # then ignore the attr
                    if _vattr and _vattr.get(att_name):
                        continue
                    _attrs.append((att_name, att_value))
            tag.attrs = _attrs

        # add default attr value to tag
        # if tag not have sucn a attr
        if tag.name in VALID_ATTR_VALUE.keys():
            _attrs = VALID_ATTR_VALUE.get(tag.name, [])
            for k, v in _attrs.items():
                tag.attrs.append((k, v))

    return soup.renderContents().decode('utf-8')


def render_markdown(text):
    if isinstance(text, bytes):
        warn('text should be unicode', DeprecationWarning)
        text = text.decode('utf-8')
    html = md.render(text)
    return sanitize_html(html)

render = render_markdown
