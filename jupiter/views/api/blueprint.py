# coding: utf-8

"""
    OAuth 2.0 API Blueprint and Conditional Request
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module defines a factory function in order to create blueprints which
    shared by views.
"""

from __future__ import absolute_import, unicode_literals

from flask import Blueprint

from .blueprint_factory import BlueprintFactory

__all__ = ['create_blueprint', 'conditional_for', 'create_blueprint_v2', 'conditional_for_v2']

create_blueprint = BlueprintFactory(
    allowed_versions=['v1'],
    conditional_version='v1',
    common_rate_limit='600/minute',
    blueprint_class=Blueprint)
conditional_for = create_blueprint.conditional_for

create_blueprint_v2 = BlueprintFactory(
    allowed_versions=['v2'],
    conditional_version='v2',
    common_rate_limit='600/minute',
    blueprint_class=Blueprint)
conditional_for_v2 = create_blueprint_v2.conditional_for
