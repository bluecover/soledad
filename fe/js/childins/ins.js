require('./_wx_share.js')
let loading_dlg = require('mods/redirect_dlg/_loading_dlg')

$('.js-btn-start').on('click', function () {
  let redirect_url = $(this).data('url')
  switch ($(this).data('type')) {
    case '700du':
      loading_dlg.show({
        partner_logo: 'l700-logo',
        partner_logo_src: '{{{img/logo/700_logo.png}}}',
        redirect_url: redirect_url
      })
      break
    case 'zm':
      loading_dlg.show({
        partner_logo: 'zm-logo',
        partner_logo_src: '{{{img/logo/zm_logo.png}}}',
        redirect_url: redirect_url
      })
      break
    default:
      loading_dlg.show({
        partner_logo: 'zm-logo',
        partner_logo_src: '{{{img/logo/zm_logo.png}}}',
        redirect_url: redirect_url
      })
  }

})
