var dlg_error = require('g-error')
var dlg_loading = require('g-loading')
var dlg_redirect = require('./_modal_redirect')

$('body')
  .on('click', '.js-btn-start', function () {
    dlg_loading.show()

    var that = $(this)
    var verifyUrl = $(this).data('verify-url')

    $.ajax({
      type: 'POST',
      url: verifyUrl
    }).done(function (data) {
      if (data.r) {
        window.location.href = that.data('url')
      } else {
        if (data.next_url) {
          dlg_redirect.show()
          setTimeout(function () {
            window.location.href = data.next_url
          }, 3000)
        } else {
          dlg_error.show(data.error)
        }
      }
    }).fail(function () {
      dlg_error.show()
    })
  })
