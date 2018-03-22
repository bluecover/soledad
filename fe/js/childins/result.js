$('.js-btn-backup').on('click', function () {
  var $this = $(this)
  if ($this.hasClass('highlight')) {
    $('.js-backup-con').slideUp('fast', function () {
      $this.removeClass('highlight')
      $this.find('.text-bold').addClass('text-orange')
    })
  } else {
    $this.addClass('highlight')
    $('.js-backup-con').hide().removeClass('hide').slideDown('fast')
    $this.find('.text-bold').removeClass('text-orange')
  }
})

$('.js-buy-mobile').on('click', function (event) {
  event.preventDefault()
  var url = $(this).attr('href')
  $('.js-dlg-tips').onemodal()
  $('.js-btn-continue').attr('href', url)
})
