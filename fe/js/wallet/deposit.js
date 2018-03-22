var dlg_error = require('g-error')
var dlg_loading = require('g-loading')

var OrderInfo = require('./deposit/_order_info.jsx')
var Pay = require('./deposit/_pay.jsx')
var appDispatcher = require('utils/dispatcher')
var dlg_sms = require('mods/modal/sms')
var CardAction = require('mods/card/_cardAction.jsx')

var $data = $('#origin_data')
var bankcards_data = $('#origin_data').data('bankcards') || []
var balance_data = $data.data('balance')
var bank_data = $data.data('bank') || {}
var order_data = $data.data('order') || {}
var order_type = $data.data('type') // 'withdraw' or 'purchase'
var order_date = $data.data('date')
var product_category = $data.data('product-category')

order_data = {invest_min_amount: '1.00'}

var order_info = ReactDOM.render(<OrderInfo balance_data={balance_data} orderData={order_data} orderType={order_type} orderDate={order_date}/>, document.getElementById('deposit_wrapper'))
ReactDOM.render(<Pay cards={bankcards_data} bankData={bank_data} orderType={order_type} productCategory={product_category}/>, document.getElementById('js_pay_info'))

function sendSubmitCode(val, amount, bankcard_id) {
  dlg_loading.show()
  $.ajax({
    type: 'post',
    url: '/j/wallet/' + order_type,
    data: {
      sms_code: val,
      amount: amount,
      bankcard_id: bankcard_id
    }
  }).done(function (data) {
    if (data.r) {
      window.location = '/wallet'
    } else {
      dlg_error.show(data.error)
    }
  }).fail(function (data) {
    dlg_error.show(data && data.responseJSON && data.responseJSON.error)
  })
}

function walletSubmit(current_card) {
  var bankcard_id = current_card.card_id
  var order_info_data = order_info.getOrderInfo()
  var amount = order_info_data.amount

  if (!order_info_data) {
    dlg_error.show('请填写完整的订单信息')
    return
  }

  if (order_type === 'deposit' && amount > current_card.bank_limit) {
    dlg_error.show('所输入金额超出该银行卡限额')
    return
  }

  dlg_loading.show()
  $.ajax({
    type: 'post',
    url: '/j/wallet/' + order_type,
    data: {
      amount: amount,
      bankcard_id: bankcard_id
    }
  }).done(function (data) {
    if (data.r) {
      dlg_sms.show('请输入验证码完成支付').on('sms:submit', function (e, val) {
        sendSubmitCode(val, amount, bankcard_id)
      })
    } else {
      dlg_error.show(data.error)
    }
  }).fail(function (data) {
    dlg_error.show(data && data.responseJSON && data.responseJSON.error)
  })
}

function bindCard(card_id) {
  dlg_loading.show({
    loading_title: '正在绑定',
    loading_info: '正在绑定，请稍后...'
  })

  $.ajax({
    type: 'post',
    url: '/j/wallet/bankcard/' + card_id + '/verify'
  }).done(function (data) {
    if (data.r) {
      dlg_sms.show('请输入验证码完成绑卡').on('sms:submit', function (e, val) {
        sendCode(val, card_id)
      })
    } else {
      dlg_error.show(data.error)
    }
  }).fail(function (data) {
    dlg_error.show(data && data.responseJSON && data.responseJSON.error)
  })
}

function sendCode(val, card_id) {
  dlg_loading.show({
    loading_title: '正在提交',
    loading_info: '正在提交，请稍后...'
  })

  $.ajax({
    type: 'post',
    url: '/j/wallet/bankcard/' + card_id + '/verify',
    data: {
      sms_code: val
    }
  }).done(function (data) {
    if (data.r) {
      dlg_loading.close()
      CardAction.updateCards(data.bankcards)
    } else {
      dlg_error.show(data.error)
    }
  }).fail(function (data) {
    dlg_error.show(data && data.responseJSON && data.responseJSON.error)
  })
}

appDispatcher.register(function (payload) {
  switch (payload.actionType) {
    case 'wallet:submit':
      walletSubmit(payload.current_card)
      break
    case 'bankcard:bindCard':
      bindCard(payload.card_id)
      break
  }
})
