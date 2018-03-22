let appDispatcher = require('utils/dispatcher')

const CouponAction = {
  setCouponStatus: function (coupon_status) {
    appDispatcher.dispatch({
      actionType: 'coupon:changeStatus',
      coupon_status: coupon_status
    })
  },
  setDeductionData: function (deduction_num, deduction_status) {
    appDispatcher.dispatch({
      actionType: 'deduction:change',
      deduction_num: deduction_num,
      deduction_status: deduction_status
    })
  }
}

module.exports = CouponAction
