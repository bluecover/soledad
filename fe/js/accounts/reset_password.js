var resend_countdown = require('utils/resend_countdown')
var dlg_error = require('g-error')

// 声明变量
var newpwd = $('.newpwd-txt')
var repwd = $('.repwd-txt')
var code_txt = $('.code-txt')
var reset_submit_btn = $('.js-reset-submit')
var reset_ajax_btn = $('.js-reset-ajax')
var newpwd_val = ''
var my_form = $('.modify-password-form')
var phone_num = $('.js-phone-number')
var form_error = $('.js-form-error')
var request_running = false

var prompt_txt = {
  code_null: '请输入验证码',
  newpwd_null: '密码不能为空',
  repwd_null: '再次输入新密码',
  newpwd_wrong: '密码至少6位',
  repwd_wrong: '两次输入密码不一致'
}

var verify = function (txt, prompt, empty_prompt, wrong_condition, wrong_prompt) {
  if (arguments.length === 3) {
    if (txt === '') {
      setPrompt(prompt, 0, empty_prompt)
    } else {
      setPrompt(prompt, 1)
    }
  } else if (arguments.length === 5) {
    if (txt === '') {
      setPrompt(prompt, 0, empty_prompt)
    } else if (wrong_condition) {
      setPrompt(prompt, 0, wrong_prompt)
    } else {
      setPrompt(prompt, 1)
    }
  }
}

function setPrompt(prompt, pass, txt) {
  prompt.show()
  if (pass) {
    prompt.hide()
  } else {
    prompt.show()
    prompt.html(txt)
  }
}

// 修改密码btn
$('.password-modify-btn').click(function () {
  $(this).parent().hide()
  my_form.show()
})

// prompt===============================
// code_txt
code_txt.blur(function () {
  var prompt = $(this).parent().find('.input-prompt')
  var myTxt = $(this).val()
  verify(myTxt, prompt, prompt_txt.code_null)
})

// newpwd
newpwd.blur(function () {
  var prompt = $(this).parent().find('.input-prompt')
  var myTxt = $(this).val()
  newpwd_val = myTxt
  verify(myTxt, prompt, prompt_txt.newpwd_null, (myTxt.length < 6), prompt_txt.newpwd_wrong)
})

// repwd
repwd.blur(function () {
  var prompt = $(this).parent().find('.input-prompt')
  var myTxt = $(this).val()

  verify(myTxt, prompt, prompt_txt.repwd_null, (myTxt !== newpwd_val), prompt_txt.repwd_wrong)
})

// 回车 ==============================
newpwd.keydown(function (event) {
  if (event.keyCode === 13) {
    repwd.focus()
  }
})

// submit
reset_submit_btn.click(function () {
  var ready = readySubmit()
  if (ready) {
    my_form.submit()
  }
})

reset_ajax_btn.click(function () {
  var ready = readySubmit()
  if (request_running) {
    return
  }
  if (ready) {
    $('.js-reset-ajax').text('提交中...').addClass('btn-disable')
    var params = {
      mobile: phone_num.val(),
      code: code_txt.val(),
      new_password: newpwd.val(),
      confirmed_password: repwd.val()
    }
    request_running = true
    $.ajax({
      url: '/j/account/reset_mobile_user_password',
      type: 'POST',
      data: params,
      dataType: 'json'
    }).done(function (c) {
      if (c.r) {
        window.location.href = '/accounts/password/reset/success'
      } else if (c.error) {
        form_error.html(c.error)
        request_running = false
        $('.js-reset-ajax').text('确认修改').removeClass('btn-disable')
      }
    }).always(function () {
      request_running = false
    })
  }
})

// getcode
var btn_getcode = $('.js-btn-getcode')
var btn_getcoding = $('.js-btn-disable')
var btn_countdown_num = $('.js-btn-countdown-num')

btn_getcode.click(function () {
  getcode($(this))
})

function readySubmit() {
  $('input').blur()
  var prompt_list = $('.input-prompt')
  var ready = 1

  for (var i = 0; i < prompt_list.length; i++) {
    if ($(prompt_list[i]).css('display') !== 'none') {
      ready = 0
    }
  }
  return ready
}

function getcode(btn) {
  btn.addClass('btn-getcoding')
  btn.text('验证码获取中...')
  var params = {
    mobile: phone_num.val()
  }
  $.ajax({
    url: '/j/account/request_reset_mobile_user_password_verify',
    type: 'POST',
    data: params,
    dataType: 'json'
  }).done(function (c) {
    btn.html('获取验证码')
    btn.removeClass('btn-getcoding')
    if (c.r) {
      resend_countdown(btn, btn_getcoding, btn_countdown_num, 60)
    } else if (c.error) {
      form_error.html(c.error)
    } else {
      btn.html('获取验证码')
      btn.removeClass('btn-getcoding')
      dlg_error.show()
    }
  })
}
