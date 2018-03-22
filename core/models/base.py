class EntityModel(object):
    """The base class of entity models.

    All entity models are comparable and hashable. There are some meta
    attributes:

     - ``id_attr_name``
     - ``repr_attr_names``

    Example::
        >>> class Article(EntityModel):
        ...     class Meta:
        ...         id_attr_name = 'article_id'
        ...         repr_attr_names = ['title', 'is_public']
        ...     def __init__(self, article_id):
        ...         self.article_id = article_id
        ...         self.title = 'TITLE {0}'.format(article_id)
        ...         self.is_public = True
        >>> article = Article('1000001')
        >>> article
        Article(article_id='1000001', title='TITLE 1000001', is_public=True)
        >>> str(article).startswith('<core.models.base.Article at 0x')
        True
        >>> str(article).endswith(' article_id:1000001>')
        True
        >>> article == Article('1000001')
        True
        >>> article != Article('1000001')
        False
        >>> article == Article('1000002')
        False
        >>> sorted([
        ...     a.article_id
        ...     for a in {article, Article('1000001'), Article('1000002')}])
        ['1000001', '1000002']
    """

    def __eq__(self, other):
        id_attr_name, id_attr_value = get_id_attr(self)

        if not isinstance(other, self.__class__) or \
           not id_attr_name or \
           not hasattr(self, id_attr_name) or \
           not hasattr(other, id_attr_name):
            return NotImplemented

        return id_attr_value == getattr(other, id_attr_name)

    def __ne__(self, other):
        rv = self.__eq__(other)
        if isinstance(rv, bool):
            return not rv
        return rv

    def __hash__(self):
        id_attr_name, id_attr_value = get_id_attr(self, default=missing)
        return hash((self.__class__, id_attr_name, id_attr_value))

    def __repr__(self):
        name = self.__class__.__name__
        kwargs = ', '.join('%s=%r' % pair for pair in iter_repr_attrs(self))
        return '{0}({1})'.format(name, kwargs)

    def __unicode__(self):
        name = get_qual_name(self.__class__)
        id_attr = u'%s:%s' % get_id_attr(self)
        return u'<{0} at {1} {2}>'.format(name, hex(id(self)), id_attr)

    def __str__(self):
        return self.__unicode__().encode('utf-8')


#: A symbol object which means "missing value"
missing = object()


def get_meta_attr(cls, name, default=None):
    """Gets the meta attribute from the instance of Meta class of the host
    class.
    """
    meta = getattr(cls, 'Meta', object)()
    return getattr(meta, name, default)


def get_qual_name(cls):
    """Just like the ``__qualname__`` in Python 3."""
    return '{cls.__module__}.{cls.__name__}'.format(cls=cls)


def get_id_attr(self, default=None):
    """Gets the id attribute key-value pair of this entity."""
    id_attr_name = get_meta_attr(self.__class__, 'id_attr_name', 'id_')
    id_attr_value = getattr(self, id_attr_name, default)
    return id_attr_name, id_attr_value


def get_repr_attr_names(self):
    """Gets the names of representation attributes."""
    id_attr_name = get_meta_attr(self.__class__, 'id_attr_name', 'id_')
    repr_attr_names = get_meta_attr(self.__class__, 'repr_attr_names', [])

    repr_attr_names = list(repr_attr_names)
    if id_attr_name and id_attr_name not in repr_attr_names:
        repr_attr_names = [id_attr_name] + repr_attr_names

    return repr_attr_names


def iter_repr_attrs(self):
    repr_attr_names = get_repr_attr_names(self)
    for attr_name in repr_attr_names:
        if not hasattr(self, attr_name):
            continue
        yield attr_name, getattr(self, attr_name)
