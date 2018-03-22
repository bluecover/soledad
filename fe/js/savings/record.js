require('./mods/_trading_detail')
var trading_detail = require('./mods/_trading_detail.js')
var appDispatcher = require('utils/dispatcher')
var Record = require('mods/record/_recordList.jsx')
var loading = $('#js_record_info').html()
var filter = ''

function getData() {
  $.ajax({
    url: '/j/savings/orders?filter=' + filter,
    type: 'GET'
  }).done(function (c) {
    ReactDOM.render(<Record recordsData={c.records} allRecord={true}/>, document.getElementById('js_record_info'))
  }).fail(function () {
    $('.js-loading').addClass('hide')
    $('.js-reload').removeClass('hide')
  }).complete(function () {
    $('.js-record-nav').show()
  })
}
getData()

$('.js-record').on('click', function () {
  if ($(this).hasClass('on')) {
    return
  }
  $('.js-record-nav').hide()
  $('#js_record_info').html(loading)
  $(this).addClass('on').siblings().removeClass('on')
  filter = $(this).data('filter')
  getData()
})

$('body')
  .on('click', '.js-reload-order', function () {
    getData()
  })

appDispatcher.register(function (payload) {
  switch (payload.actionType) {
    case 'reocrd:modalDetail':
      trading_detail.show(payload.record_detail)
      break
  }
})
