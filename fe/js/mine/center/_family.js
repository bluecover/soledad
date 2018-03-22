$('.js-block-item-tab li').click(function () {
  var _index = $(this).index()
  $(this).addClass('lisel').siblings('li').removeClass('lisel')
  $('.js-tabcon-list').eq(_index).removeClass('hide').siblings('.js-tabcon-list').addClass('hide')
})
$('.js-tabcon-suggest-btn').click(function () {
  if ($(this).html() === '展开推荐') {
    $(this).html('收起推荐')
    $(this).closest('.js-tabcon-suggest').next('.js-tabcon-recomment').slideDown(400)
  }else {
    $(this).closest('.js-tabcon-suggest').next('.js-tabcon-recomment').slideUp(200)
    $(this).html('展开推荐')
  }
})
