function getNotification() {
  $.ajax({
    url: '/j/notification/get_all',
    type: 'GET',
    dataType: 'JSON'
  }).done(function (c) {
    let tmpl = c.template
    if (tmpl) {
      $('body').append(tmpl)
      $(tmpl).onemodal({
        removeAfterClose: true
      })
    }
  })
}

if ($('#notification').length) {
  getNotification()
}
