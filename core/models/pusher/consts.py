# -*- coding: utf-8 -*-

import re
from functools import partial

PUSH_TITLE_MIN_LENGTH = 5
PUSH_CONTENT_MIN_LENGTH = 10

jpush_splitter_sub = partial(re.sub, '\.', '_')
