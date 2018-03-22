var WaterCircle = require('mods/_waterCircle.jsx')

var plan_amount = $('.js-plan-amount').data('plan-amount')
var saving_amount = $('.js-saving-amount').data('saving-amount')
var saving_rate = Number((saving_amount / plan_amount).toFixed(2))

var invest_info = {
  saving_amount: saving_amount,
  rate: saving_rate
}

var invest_water = $('.js-invest-goal').find('.bd')[0]
var $saving_product = $('.js-saving-product')
if (invest_water && $saving_product.css('display') !== 'none') {
  ReactDOM.render(<WaterCircle data={invest_info} />, invest_water)
}

var $tabs = $('.js-product-tabs')
!$tabs ? null : $tabs.on('click', '.tab', function (e) {
  var index = $tabs.children().index($(this))

  index === 1 ? $tabs.addClass('saving-active') : $tabs.removeClass('saving-active')

  $(this).addClass('active').siblings().removeClass('active')

  $('.center-products').find('.bd')
    .children().eq(index).removeClass('desktop-element')
    .siblings().addClass('desktop-element')

  if (invest_water && index === 1) {
    ReactDOM.render(<WaterCircle data={invest_info} />, invest_water)
  }

})
