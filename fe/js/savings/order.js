var dlg_error = require('g-error')
let dlg_tips = require('mods/modal/modal_tips')
let dlg_payment = require('./mods/_payment_detail')

let CouponStore = require('./order/_couponStore.jsx')
let OrderInfoRegular = require('./order/_order_info_regular.jsx')
let OrderInfoNewcomer = require('./order/_order_info_newcomer.jsx')
let OrderInfoLadder = require('./order/_order_info_ladder.jsx')

var $data = $('#origin_data')
var product_type = $data.data('product-type')
var OrderInfo
if (product_type === 'regular') {
  OrderInfo = OrderInfoRegular
} else if (product_type === 'newcomer') {
  OrderInfo = OrderInfoNewcomer
} else {
  OrderInfo = OrderInfoLadder
}

var Pay = require('./order/_pay.jsx')
var appDispatcher = require('utils/dispatcher')

var order_data = $data.data('order')
var bank_data = $data.data('bank')
var bankcards_data = $data.data('bankcards') || []
var agreement_url = $data.data('agreement-url')
let coupons_data = $data.data('coupons')
let placebo_data = $data.data('placebo')
let partner_data = $data.data('partner')
let product_category = $data.data('product-category')

var deal_text = <div className="input-con text-12">点击提交表示您已同意<a href={agreement_url} target="_blank">出借咨询与服务协议</a></div>
var order_info = ReactDOM.render(<OrderInfo orderData={order_data} couponsData={coupons_data} placeboData={placebo_data} partner={partner_data} />, document.getElementById('js_order_info'))
ReactDOM.render(<Pay bankcards={bankcards_data} bankData={bank_data} deal={deal_text} partner={partner_data} productCategory={product_category}/>, document.getElementById('js_pay_info'))

let dedection_tips = '您可以使用红包账户中的钱，直接在支付时抵扣一部分金额。<br /><br />如果您想要购买1000元的攒钱助手，您的红包中有5元并使用，实际仅需要支付995元，到期返还则是1000元+利息。<br /><br />当前红包可抵扣比例为，每200元允许使用1元的红包，即1000元可抵扣5元，10000元可抵扣50元。'
let virtual_tips = '2016年2月1日到3月10日前，领取新春礼包的用户成功攒钱一笔即可免费获赠8888元体验金；<br />体验金封闭期7天，预期年化收益率为6.6%，到期之后体验金的收益（非体验金）将自动转入用户的银行卡；<br />成功获赠体验金之后，如果于2月8日前将活动信息分享至微信，体验金收益将增加至8.8%。'

function submitOrder(current_card) {
  // 正常获取则返回相关数据，否则返回 false
  let order_info_data = order_info.getOrderInfo()

  if (!order_info_data) {
    dlg_error.show('输入的金额有误，请检查重试')
    return
  }

  let amount = order_info_data && order_info_data.amount
  let pay_amount = amount
  let coupon_id = ''
  let coupon_text = '未使用'
  let bankcard_text = '未绑定'
  let coupon_data = CouponStore.getCouponData()
  let deduction_status = CouponStore.getDeductionStatus()
  let deduction_num = !deduction_status ? 0 : CouponStore.getDeductionAmount()
  let deduction_text = deduction_num ? deduction_num + '元' : '未使用'
  let deduct_amount = coupon_data && coupon_data.benefit && coupon_data.benefit.deduct_amount

  if (amount > current_card.bank_limit) {
    dlg_error.show('所输入金额超出该银行卡限额')
    return
  }

  function getPayAmount(deduct_amount = 0, deduction_num = 0) {
    return amount - deduct_amount - deduction_num
  }

  pay_amount = getPayAmount(deduct_amount, deduction_num)

  if (coupon_data) {
    coupon_id = coupon_data.id_
    coupon_text = coupon_data.name + '（' + coupon_data.description + '）'
  }

  if (current_card) {
    bankcard_text = current_card.bank_name + '（' + current_card.display_card_number + '）'
  }

  dlg_payment.show({
    partner: partner_data,
    savings_product: order_data.product_name,
    order_amount: amount,
    interest_start_date: order_data.start_date,
    due_date: order_info_data.date,
    deduction_text: deduction_text,
    coupon_text: coupon_text,
    bankcard: bankcard_text,
    pay_amount: pay_amount,
    pocket_deduction_amount: deduction_num,
    bankcard_id: current_card.card_id,
    product_id: order_data.product_id,
    wrapped_product_id: order_data.wrapped_product_id,
    coupon_id: coupon_id
  })
}

appDispatcher.register(function (payload) {
  switch (payload.actionType) {
    case 'savings:submit':
      submitOrder(payload.current_card)
      break
    case 'deduction:modalDetail':
      dlg_tips.show({
        tips_title: '抵扣说明',
        tips_main: dedection_tips
      })
      break
    case 'virtual:modalDetail':
      dlg_tips.show({
        tips_title: '新春攒钱送体验金！',
        tips_main: virtual_tips
      })
      break
  }
})
