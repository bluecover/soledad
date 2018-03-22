for (var i = 0; i < $('.js-data-num').length; i++) {
  if (Number($('.js-data-num').eq(i).text()) < 0) {
    $('.js-data-num').eq(i).parent().addClass('text-green')
  }
}
