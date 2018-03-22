import Account from 'mods/account/_account.jsx'
import Dragdealer from 'dragdealer'

let $accountWrap = $('.js-accounts-form')

if ($accountWrap.length) {
  let redirect_url = $accountWrap.data('url')
  let raise_quota = $accountWrap.data('raise-quota')
  let register_btn_text = '注册查看如何加薪' + raise_quota
  let login_btn_text = '登录查看如何加薪' + raise_quota

  let stats = {}
  stats.dcm = $accountWrap.data('dcm')
  stats.dcs = $accountWrap.data('dcs')
  stats.refer = window.location.href

  let account = ReactDOM.render(<Account type="register" register_btn_text={register_btn_text} login_btn_text={login_btn_text}/>, $accountWrap[0])

  account.setSubmitInfo({
    redirect_url: redirect_url,
    stats: stats
  })
}

var data_arr = JSON.parse($('.js-data-list').val())

new Dragdealer('drag_box', {
  x: 0.1,
  steps: 11,
  snap: true,
  animationCallback: function (x, y) {
    $('.js-bg').width(x * 100 + '%')
    $(data_arr).each(function (index, el) {
      var step = index / 10
      var num = Math.ceil(el / 10) - 1
      if (x === step) {
        $('.js-item-box').eq(num).addClass('cur').siblings().removeClass('cur')
        $('.js-num').text(el)
        x === 0 ? $('.js-date-text').text('') : $('.js-date-text').text(index + '年')
      }
    })
  }
})
