import { EventEmitter } from 'events'
EventEmitter.prototype.setMaxListeners(100)

let appDispatcher = require('utils/dispatcher')

let _coupon_data
let _deduction_num = 0
let _deduction_status
let _coupon_rate = ''
let _coupon_status = false
let _cancel_text = ''
let _coupon_info = {
  coupon_id: '',
  fulfill_amount: ''
}

function _setCouponStatus(coupon_status) {
  _coupon_status = coupon_status
}

function _setCouponRate(rate) {
  _coupon_rate = rate
}

function _setDeductionStatus(deduction_status) {
  _deduction_status = deduction_status
}

function _setCancelText(text) {
  _cancel_text = text
}

function _checkCouponData(amount) {
  if (_coupon_data) {
    const amount_is_vaild = /^\d+$/.test(amount)
    if (!amount_is_vaild || _coupon_data.usage_requirement.fulfill_amount > amount) {
      _coupon_data = null
      _setCouponInfo(_coupon_data)
      _setCancelText('')
    }
  }
}

function _setCouponInfo(coupon_data) {
  if (coupon_data) {
    _coupon_info.coupon_id = coupon_data.id_
    _coupon_info.fulfill_amount = coupon_data.usage_requirement && coupon_data.usage_requirement.fulfill_amount || ''
  } else {
    _coupon_info.coupon_id = ''
    _coupon_info.fulfill_amount = ''
  }
}

function _setCouponData(data) {
  _coupon_data = data
}

function _setDeductionAmount(num) {
  _deduction_num = num
}

let CouponStore = Object.assign({}, EventEmitter.prototype, {
  getCouponStatus: () => {
    return _coupon_status
  },

  getCouponRate: () => {
    return _coupon_rate
  },

  getDeductionStatus: () => {
    return _deduction_status
  },

  getCouponData: () => {
    return _coupon_data
  },

  getCouponInfo: () => {
    return _coupon_info
  },

  getCancelText: () => {
    return _cancel_text
  },

  getDeductionAmount: () => {
    return _deduction_num
  }
})

appDispatcher.register(function (payload) {
  switch (payload.actionType) {
    case 'input:blur':
      _checkCouponData(payload.blur_amount)
      CouponStore.emit('change')
      break
    case 'coupon:select':
      _setCouponData(payload.coupon_data)
      _setCouponInfo(payload.coupon_data)
      _setCancelText(payload.cancel_text)
      _setCouponRate(payload.coupon_data.benefit.extra_rate)
      CouponStore.emit('change')
      break
    case 'coupon:cancel':
      _setCouponInfo(null)
      _setCouponData(null)
      _setCouponRate('')
      _setCancelText('')
      CouponStore.emit('change')
      break
    case 'deduction:change':
      _setDeductionAmount(payload.deduction_num)
      _setDeductionStatus(payload.deduction_status)
      CouponStore.emit('change')
      break
    case 'coupon:changeStatus':
      _setCouponStatus(payload.coupon_status)
      CouponStore.emit('change')
      break
  }
})

module.exports = CouponStore
