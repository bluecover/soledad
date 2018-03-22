# -*- coding: utf-8 -*-

from core.models.mixin.props import SecretPropsMixin


class PlanSecretDataMixin(SecretPropsMixin):

    def get_uuid(self):
        return 'plan:secret:data:%s' % self.id

    def get_db(self):
        return 'plan_data'
