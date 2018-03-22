var dlg_error = require('g-error')

function initTwoFactor() {
  $.post('/j/twofactor/provision').done(function (r) {
    var imageElement = $('<img>')
      .attr('src', r.preview_url + '?t=' + +new Date())
      .addClass('twofactor-qrcode')
    $('.js-btn-enable-twofactor').removeClass('hide')
    $('.js-btn-disable-twofactor').addClass('hide')
    $('.js-twofactor-preview').removeClass('hide')
    $('.js-twofactor-preview .js-img-wrapper').html(imageElement)
    $('.js-twofactor-wrapper').onemodal()
  }).fail(function (e) {
    dlg_error.show(e && e.responseJSON && e.responseJSON.error || undefined)
  })
}

function enableTwoFactor(password) {
  $.ajax({
    url: '/j/twofactor/provision/verify',
    data: {password: password},
    type: 'POST'
  }).done(function (r) {
    window.location.reload()
  }).fail(function (e) {
    $('.js-twofactor-error').text(e.responseJSON.error).closest('div').removeClass('hide')
  })
}

function deinitTwoFactor() {
  $('.js-btn-enable-twofactor').addClass('hide')
  $('.js-btn-disable-twofactor').removeClass('hide')
  $('.js-twofactor-preview').addClass('hide')
  $('.js-twofactor-wrapper').onemodal()
}

function disableTwoFactor(password) {
  $.ajax({
    url: '/j/twofactor/provision',
    data: {password: password},
    type: 'DELETE'
  }).done(function () {
    window.location.reload()
  }).fail(function (e) {
    $('.js-twofactor-error').text(e.responseJSON.error).closest('div').removeClass('hide')
  })
}

$('.js-twofactor-init-text').on('click', function () {
  initTwoFactor()
})
$('.js-twofactor-deinit-text').on('click', function () {
  deinitTwoFactor()
})
$('.js-btn-enable-twofactor').on('click', function () {
  var password = $('.js-twofactor-input').val()
  enableTwoFactor(password)
})
$('.js-btn-disable-twofactor').on('click', function () {
  var password = $('.js-twofactor-input').val()
  disableTwoFactor(password)
})
