var edit_input = $('.js-saving-input')
var error_text = $('.js-target-error')

edit_input
  .keyup(function (event) {
    if (event.which === 13) {
      $('.js-confirm-target').click()
    }
  })
  .one('click', function () {
    edit_input.select()
  })

$('body').on('click', '.js-confirm-target', function () {
  var params = {
    amount: edit_input.val()
  }

  $.ajax({
    url: '/j/savings/update_amount',
    type: 'POST',
    data: params,
    dataType: 'json'
  }).done(function (c) {
    if (c.r) {
      location.reload()
    } else if (c.error) {
      error_text.text(c.error)
      error_text.fadeIn('fast')
    }
  })
})

$('body').on('click', '.js-edit-target', function () {
  $('.js-dlg-target').onemodal()
})
