# -*- coding: utf-8 -*-


err_ok = (1000, 'err_ok')
err_no_alias = (1001, 'err_no_alias')
err_invalid_email = (1002, 'err_invalid_email')
err_email_provider_in_blacklist = (1003, 'err_email_provider_in_blacklist')
err_email_exists = (1004, 'err_email_exists')
err_invalid_mobile = (1006, 'err_invalid_mobile')
err_mobile_exists = (1007, 'err_mobile_exists')
err_invalid_user_domain = (1008, 'err_invalid_user_domain')
err_user_domain_exists = (1009, 'err_user_domain_exists')
err_invalid_reg_type = (1010, 'err_invalid_reg_type')
err_invalid_captcha = (1011, 'err_invalid_captcha')
err_no_such_user = (1012, 'err_no_such_user')
err_wrong_password = (1013, 'err_wrong_password')
err_user_suicide = (1014, 'err_user_suicide')
err_user_banned = (1015, 'err_user_banned')
err_no_password = (1016, 'err_no_password')
err_invalid_verify_code = (1017, 'err_invalid_verify_code')
err_no_confirm_code = (1018, 'err_no_confirm_code')
err_password_too_short = (1019, 'err_password_too_short')
err_password_too_long = (1020, 'err_password_too_long')
err_too_many_mobile_reg = (1021, 'err_too_many_mobile_reg')
err_generate_verify_code = (1022, 'err_generate_verify_code')
err_add_user_fail = (1023, 'err_add_user_fail')
err_password_too_easy = (1024, 'err_password_too_easy')
err_need_screen_name = (1025, 'err_need_screen_name')
err_email_server_error = (1026, 'err_email_server_error')
err_need_captcha = (1027, 'err_need_captcha')

err_invalid_user_status = (1028, 'err_invalid_user_status')
err_confirm_expired = (1029, 'err_confirm_expired')
err_invalid_confirm_code = (1030, 'err_invalid_confirm_code')
err_register = (1031, 'err_register')
err_invalid_confirm_code_status = (1032, 'err_invalid_confirm_code_status')
err_invalid_mail_user_status = (1033, 'err_invalid_mail_user_status')
err_invalid_mobile_user_status = (1034, 'err_invalid_mobile_user_status')
err_invalid_uuid = (1035, 'err_invalid_uuid')

err_invalid_validate = (1041, 'err_invalid_validate')
err_invalid_default_values = (1042, 'err_invalid_default_values')
err_invalid_range_values = (1043, 'err_invalid_range_values')
err_invalid_phone_number = (1044, 'err_invalid_phone_number')
err_input_value_empty = (1045, 'err_input_value_empty')
err_invalid_json_format = (1046, 'err_invalid_json_format')
err_invalid_data_format = (1047, 'err_invalid_data_format')
err_input_is_xss = (1048, 'err_input_is_xss')


err_invalid_plan_step = (1049, 'err_invalid_plan_step')
err_none_plan_data = (1050, 'err_none_plan_data')

err_value_too_long = (1051, 'err_value_too_long')
err_password_unmatch_confirmation = (1052, 'err_password_unmatch_confirmation')
err_outdate = (1053, 'err_outdate')
err_no_such_code = (1054, 'err_no_such_code')
err_no_such_object = (1055, 'err_no_such_object')


# report
err_report_status_error = (1060, 'err_report_status_error')
err_invalid_static_map_file = (1061, 'err_invalid_static_map_file')
err_html_generate_error = (1062, 'err_no_such_object')
err_pdf_generate_error = (1063, 'err_no_such_object')
err_inter_data_generate_error = (1064, 'err_inter_data_generate_error')
err_render_template_error = (1065, 'err_render_template_error')


err_invalid_post_form = (1065, 'err_invalid_post_form')

# bind
err_too_many_mobile_bind = (1066, 'err_too_many_mobile_bind')
err_bind = (1067, 'err_bind')
err_clear_alias_failed = (1068, 'err_clear_alias_failed')
err_add_alias_failed = (1069, 'err_add_alias_failed')
err_diff_number_in_sequent_requests = (
    1070, 'err_diff_number_in_sequent_requests')

# withdraw
err_too_many_mobile_withdraw = (1080, 'err_too_many_mobile_withdraw')

# captcha
err_outdated_captcha = (1090, 'err_outdated_captcha')
err_wrong_captcha = (1091, 'err_wrong_captcha')
err_unfound_captcha_secret = (1092, 'err_unfound_captcha_secret')

# backward
err_unsupported_reg_type = (1100, 'err_unsupported_reg_tyep')

err_unknown = (1999, 'err_unknown')


class AccountsError(Exception):

    def __init__(self, error):
        self.errno = error[0]
        self.errmsg = error[1]
        # just for Compatible, not Recommended Use!
        self.error = error[1]
        self.raw_error = error

    def __str__(self):
        return 'AccountsError[errno:%s; errmsg:%s;]' % (self.errno,
                                                        self.errmsg)


class LoginError(AccountsError):

    def __str__(self):
        return 'LoginError[errno:%s errmsg:%s]' % (self.errno,
                                                   self.errmsg)


class RegisterError(AccountsError):

    def __str__(self):
        return 'RegisterError[errno:%s errmsg:%s]' % (self.errno,
                                                      self.errmsg)


class BindError(Exception):
    pass


class ValidationError(Exception):
    """The base exception of validation"""


class PasswordValidationError(ValidationError):

    def __unicode__(self):
        return u'密码输入有误'


class MismatchedError(PasswordValidationError):

    def __unicode__(self):
        return u'两次密码输入不一致，请重新输入'


class FormatError(PasswordValidationError):

    def __unicode__(self):
        return u'密码需为至少6位的字符串'


class AccountAliasValidationError(ValidationError):

    def __unicode__(self):
        return u'账号名称有误'


class AccountInactiveError(AccountAliasValidationError):

    def __unicode__(self):
        return u'账号尚未激活'


class AccountNotFoundError(AccountAliasValidationError):

    def __unicode__(self):
        return u'账号不存在'


class UnsupportedAliasError(AccountAliasValidationError):

    def __unicode__(self):
        return u'不支持的账号类型'


class InsecureEmailError(AccountAliasValidationError):

    def __unicode__(self):
        return u'您的注册邮箱存在使用风险，请联系好规划微信客服(plan141)进行密码修改'
