import ShareWeixin from 'mods/share/_shareWeixin.jsx'
import tmpl from './_trading_detail.hbs'

let weixinDefaultConfig = {
  title: '微信分享二维码',
  desc: '打开手机微信，选择「微信」标签，点击右上角「+」，选择「扫一扫」。',
  picUrl: ''
}

module.exports = {
  show: function (data) {
    let options = {...data}

    if (options.spring_festival) {
      options['img_src'] = '{{{img/savings/share_wx.png}}}'
    }

    options.qrcode_url ? weixinDefaultConfig['picUrl'] = options.qrcode_url : null

    let $tmpl = $(tmpl(options))
    $('body').append($tmpl)

    let $btn_share = $tmpl.find('.js-wx-share')
    $btn_share.on('click', function () {
      let shareQr = ReactDOM.render(<ShareWeixin data={weixinDefaultConfig} />, document.getElementById('share_wrapper'))
      shareQr.handleClick()
    })

    $tmpl.onemodal({
      removeAfterClose: true
    })
    return $tmpl
  }
}
