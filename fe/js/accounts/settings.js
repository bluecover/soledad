require('utils/form_helper')
var dlg_error = require('g-error')
var phone_verify = require('mods/phone/modal_phone_verify')
var dlg_success = require('mods/modal/modal_success')

var oldpwd = $('.js-oldpwd-txt')
var newpwd = $('.js-newpwd-txt')
var repwd = $('.js-repwd-txt')

phone_verify('.js-phone-verify')

function modifyPwd() {
  var params = {
    old_password: oldpwd.val(),
    new_password: newpwd.val(),
    repwd_txt: repwd.val()
  }
  $.ajax({
    url: '/j/account/settings',
    type: 'POST',
    data: params,
    dataType: 'json'
  }).done(function (c) {
    if (c.r) {
      dlg_success.show({
        success_title: '修改成功',
        success_msg: '修改成功后请重新登录'
      }).on('onemodal:close', function () {
        location.href = '/accounts/login'
      })
    } else {
      $('.js-form-error').html('<i class="iconfont icon-wrong text-red text-16"></i>错误密码')
    }
  }).fail(function () {
    dlg_error.show()
  })
}

var password_rules = {
  verify: {
    test: function () {
      var newVal = newpwd.val()
      if (newVal.length < 6) {
        return true
      }
      return false
    },
    msg: '密码至少6位'
  },
  confirm: {
    test: function () {
      var newVal = newpwd.val()
      var reVal = repwd.val()
      if (newVal !== reVal) {
        return true
      }
      return false
    },
    msg: '两次输入密码不一致'
  }
}

function phone_bind() {
  $('.js-bind-error').text('')
  var phone_input = $('.js-phone-verify').find('.js-phone')
  var code_input = $('.js-phone-verify').find('.js-code')
  var params = {
    mobile: phone_input.val(),
    code: code_input.val()
  }
  $.ajax({
    url: '/j/account/confirm_bind',
    type: 'POST',
    data: params,
    dataType: 'json'
  }).done(function (c) {
    if (c.r) {
      window.location.reload()
    } else {
      $('.js-bind-error').text(c.error)
    }
  }).fail(function () {
    dlg_error.show()
  })
}

$('.js-bind-text').on('click', function () {
  $('.js-bind-wrapper').onemodal()
})
$('.js-modify-text').on('click', function () {
  $(this).addClass('hide')
  $('.js-modify-password-form').removeClass('hide')
})
$('.js-btn-cancel').on('click', function () {
  $('.js-modify-text').removeClass('hide')
  $('.js-modify-password-form').addClass('hide')
})
$('.js-btn-verified').on('click', function () {
  $('.js-bind-form').submit()
})
$('.js-confirm-password').on('click', function () {
  $('.js-modify-password-form').submit()
})

var helper = $.validate
var rules = $.extend({}, helper.guihuaFormRules, password_rules)
var pwd_config = {
  errorHandler: helper.errorHandler,
  optionHandler: helper.optionHandler,
  failCallback: helper.scrollToError,
  successCallback: modifyPwd
}
var config = {
  errorHandler: helper.errorHandler,
  optionHandler: helper.optionHandler,
  failCallback: helper.scrollToError,
  successCallback: phone_bind
}

$('.js-modify-password-form').validateForm(rules, pwd_config)
$('.js-bind-form').validateForm(helper.guihuaFormRules, config)
