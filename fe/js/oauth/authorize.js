$(function () {
  var confirm_field = $('.js-confirm')
  var confirm_form = $('.js-confirm-form')

  $('.js-btn-accept').click(function () {
    confirm_field.prop('disabled', false)
    confirm_form.submit()
  })

  $('.js-btn-deny').click(function () {
    confirm_field.prop('disabled', true)
    confirm_form.submit()
  })
})
