# coding: utf-8

'''
Program class
'''

from core.models.mixin.props import PropsMixin, PropsItem


class Program(PropsMixin):

    quota = PropsItem('quota', default={})

    def __init__(self):
        pass

    def get_db(self):
        return 'insurance_program'

    def get_uuid(self):
        return 'insurance_program:quota'
