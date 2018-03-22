# coding: utf-8


class Notice(object):
    """推送报文主体，包括标题和内容"""

    def __init__(self, content, title=None):
        if not content:
            raise ValueError('no content provided')

        #: 报文标题
        self.title = title
        #: 报文内容
        self.content = content

    @property
    def payload(self):
        return {
            'alert': self.content,
            'title': self.title
        }
