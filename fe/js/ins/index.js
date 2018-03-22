import loading_dlg from 'mods/redirect_dlg/_loading_dlg.js'

$('.js-product-detail').on('click', function (e) {
  let redirect_url = $(this).data('url')
  if (redirect_url) {
    e.preventDefault()

    loading_dlg.show({
      redirect_url: redirect_url,
      partner_logo_src: $(this).data('partner-logo-src')
    })
  }
})

$('.ins-children-banner').on('click', function (e) {
  let $this = $(this)
  if (!$(e.target).hasClass('btn-start')) {
    window.open($this.data('url'))
    return false
  }
})
