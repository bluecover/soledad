import tmpl from './tmpl_redeem_code.hbs'
import dlg_success from 'mods/modal/modal_success'
import dlg_error from 'g-error'

function submitCode(code) {
  $.ajax({
    url: '/j/redeemcode/code',
    type: 'POST',
    dataType: 'json',
    data: {
      redeem_code: code
    }
  })
  .done(function (res) {
    let coupon_msg = ''
    let firewood_msg = ''
    let res_data = res.welfare_detail.welfare_info

    if (res_data.coupon_info) {
      for (let n in res_data.coupon_info) {
        coupon_msg += '「' + res_data.coupon_info[n]['name'] + res_data.coupon_info[n]['amount'] + '张」'
      }
    }

    if (res_data.firewood_info) {
      for (let n in res_data.firewood_info) {
        firewood_msg += '「' + res_data.firewood_info[n]['introduction'] + res_data.firewood_info[n]['worth'] + '元」'
      }
    }

    let success_msg = '领取成功：' + firewood_msg + coupon_msg

    dlg_success.show({
      success_title: '兑换成功',
      success_msg: success_msg,
      redirect_url: res.welfare_detail.redirect_url
    })
  })
  .fail(function (res) {
    dlg_error.show(res && res.responseJSON && res.responseJSON.error)
  })
}

module.exports = {
  show: function (options) {
    let default_opt = {
      redeem_code: ''
    }
    options = Object.assign(default_opt, options)
    let $tmpl = $(tmpl(options))
    $('body').append($tmpl)
    $tmpl.onemodal({
      removeAfterClose: true
    })

    $tmpl.find('.js-btn-code').on('click', function () {
      let $error = $tmpl.find('.js-error')
      let code_val = $tmpl.find('.js-code').val()
      $error.text('')
      if (!code_val) {
        $error.text('请输入兑换码')
      }else {
        submitCode(code_val)
      }
    })
    return $tmpl
  }
}
