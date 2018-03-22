require('utils/form_helper')

var dlg_error = require('g-error')
var dlg_loading = require('g-loading')
var phone_verify = require('mods/phone/modal_phone_verify')
var idCard = require('lib/re').ID
let moment = require('moment')

phone_verify('.js-phone-verify')

var name_input = $('.js-name')
var phone_input = $('.js-phone')
var id_input = $('.js-id')
var code_input = $('.js-code')

var next_url = $('input[name=next-url]').data('val')
var channel_url = $('input[name=channel-url]').data('val')

function handle_done(dfd) {
  return function (data) {
    if (data.r) {
      dfd.resolve(data)
    } else {
      if (data.next_url) {
        $('.js-dlg-waiting').addClass('hide')
        $('.js-dlg-tips').removeClass('hide')
        setTimeout(function () {
          window.location.href = data.next_url
        }, 4000)
      } else if (data.refresh) {
        dlg_error.show(data.error).on('onemodal:close', function () {
          window.location.reload()
        })
      } else {
        dlg_error.show(data.error)
      }
      dfd.reject(data)
    }
  }
}

function handle_fail(dfd) {
  return function (e) {
    if (e && e.responseJSON && e.responseJSON.error) {
      dlg_error.show(e.responseJSON.error)
      dfd.reject(e.responseJSON)
    } else {
      dlg_error.show()
      dfd.reject()
    }
  }
}

// 绑定手机号
function try_to_bind_mobile() {
  var dfd = $.Deferred()
  if (phone_input.length && !phone_input.prop('disabled')) {
    $.ajax({
      type: 'POST',
      url: '/j/account/confirm_bind',
      data: {
        mobile: phone_input.val(),
        code: code_input.val()
      }
    }).done(handle_done(dfd)).fail(handle_fail(dfd)).done(function (data) {
      if (data.r) {
        phone_input.prop('disabled', true)
      }
    })
  } else {
    dfd.resolve()
  }
  return dfd.promise()
}

// 绑定身份证
function try_to_bind_identity() {
  var dfd = $.Deferred()
  if (id_input.length && !id_input.prop('disabled')) {
    $.ajax({
      type: 'POST',
      url: '/j/auth/identity',
      data: {
        person_name: name_input.val(),
        person_ricn: id_input.val()
      }
    }).done(handle_done(dfd)).fail(handle_fail(dfd))
  } else {
    dfd.resolve()
  }
  return dfd.promise()
}

// 激活第三方渠道 (宜人贷、指旺)
function try_to_activate_channel() {
  var dfd = $.Deferred()
  if (channel_url) {
    $.ajax({
      type: 'POST',
      url: channel_url
    }).done(handle_done(dfd)).fail(handle_fail(dfd))
  } else {
    dfd.resolve()
  }
  return dfd.promise()
}

function authData() {
  if ($('.js-need-fillup').length) {
    $('.js-dlg-auth').onemodal({
      clickClose: false,
      escapeClose: false
    })
  } else {
    dlg_loading.show({
      loading_title: '正在提交',
      loading_info: '正在提交，请稍候...'
    })
  }

  try_to_bind_mobile().done(function () {
    try_to_bind_identity().done(function () {
      try_to_activate_channel().done(function () {
        window.location.href = next_url
      })
    })
  })
}

$('.js-btn-verified').on('click', function () {
  $('.js-auth-form').submit()
})

var auth_rules = {
  idCard: {
    test: function (val) {
      if (val && idCard.test(val)) {
        return false
      }
      return true
    },
    msg: '请正确填写身份证号码'
  },
  ageVerify: {
    test: function (val) {
      let adult_year = Number(val.substring('6', '10')) + 18
      let birth_month = val.substring('10', '12')
      let birth_day = val.substring('12', '14')
      if (moment().format() >= moment(adult_year + birth_month + birth_day, 'YYYYMMDD').format()) {
        return false
      }
      return true
    },
    msg: '您尚未满18周岁，欢迎您在成年之后使用好规划'
  }
}

var helper = $.validate
var rules = $.extend(helper.guihuaFormRules, auth_rules)
var config = {
  errorHandler: helper.errorHandler,
  optionHandler: helper.optionHandler,
  failCallback: helper.scrollToError,
  successCallback: authData
}

$('.js-auth-form').validateForm(rules, config)
