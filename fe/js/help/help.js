var url = window.location.href
var sub_title = $('.js-help-main').find('h4')

for (var i = 0; i < sub_title.length; i++) {
  var title_id = sub_title.eq(i).attr('id')
  if (url.match(title_id)) {
    sub_title.eq(i).next().removeClass('hide')
  }
}

$(sub_title).on('click', function () {
  $(this).next().toggleClass('hide')
})

