// floatbar的feedback和feedback页面逻辑控制

require('utils/form_helper')
var dlg_error = require('g-error')
var dlg_success = require('mods/modal/modal_success')
var tmpl = require('./tmpl_feedback_form.hbs')

$('.floatbar-feedback').click(function () {
  $('.js-feedback-wrapper').onemodal()
})

var default_opt = {
  wechat_img: '{{{img/misc/qrcode.png}}}',
  user_email: $('.js-user-email').val()
}

var $tmpl = $(tmpl(default_opt))
$('.js-feedback-main').append($tmpl)

var mytext = $('.js-feedback-textarea')

$('.js-show-operate-btn').click(function () {
  $('.js-feedback-txt').hide()
  $('.js-feedback-operate').show()
})

function feedback() {
  var myurl = window.location.href
  var user_email = function () {
    if ($('.js-user-email').val()) {
      return $('.js-user-email').val()
    } else {
      return $('.js-ail-input').val()
    }
  }
  var params = {
    content: mytext.val(),
    contact: user_email,
    current_url: myurl
  }
  $.ajax({
    url: '/j/feedback',
    type: 'POST',
    data: params,
    dataType: 'json'
  }).done(function (c) {
    if (c.r) {
      dlg_success.show()
    } else {
      dlg_error.show()
    }
  })
}
var feedback_rules = {
  count: {
    test: function () {
      var len = mytext.val().length
      var len_max = 500
      if (len >= len_max) {
        return true
      }
      return false
    },
    msg: '不能超过500字!'
  }
}
var helper = $.validate
var rules = $.extend(helper.guihuaFormRules, feedback_rules)
var config = {
  errorHandler: helper.errorHandler,
  optionHandler: helper.optionHandler,
  failCallback: helper.scrollToError,
  successCallback: feedback
}
$('.js-feedback-form').validateForm(rules, config)
$('.js-feed-submit').click(function () {
  $('.js-feedback-form').submit()
})
