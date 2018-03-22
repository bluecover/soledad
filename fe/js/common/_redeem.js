import dlg_code from './_redeem_code'
import dlg_tips from 'mods/modal/modal_tips'

$('.js-redeem-code').on('click', function (e, redeem_code, tips_text) {
  let rediect_url = $(this).data('verify-back-url')
  if (rediect_url) {
    dlg_tips.show({
      tips_title: '温馨提示',
      tips_main: '请先验证你的身份后,再使用兑换码。<a href=' + rediect_url + '>去验证</a>'
    })
  } else {
    dlg_code.show({
      redeem_code: redeem_code,
      tips_text: tips_text
    })
  }
})
