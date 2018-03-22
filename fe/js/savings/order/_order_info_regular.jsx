import floorTwoDecimal from 'utils/floorTwoDecimal'
let CouponList = require('./_couponList.jsx')
let Deduction = require('./_deduction.jsx')
let appDispatcher = require('utils/dispatcher')
let CouponStore = require('./_couponStore.jsx')
let CouponAction = require('./_couponAction.jsx')

var money_amount = ''
var props_data
let deduction_num = 0
let coupon_rate

function getCouponRate() {
  coupon_rate = CouponStore.getCouponRate()
}

var OrderInfo = React.createClass({
  getInitialState: function () {
    props_data = this.props.orderData
    getCouponRate()
    return {
      compute_expect: '',
      error_info: ''
    }
  },

  componentDidMount: function () {
    CouponStore.on('change', function () {
      this.forceUpdate(getCouponRate())
    }.bind(this))
  },

  checkError: function (final_check) {
    var res = ''
    var val = money_amount

    if (val && !(/^\d+$/.test(val))) {
      res = '请正确输入金额(请勿输入数字以外的字符)'
    }

    if (final_check && val < props_data.invest_min_amount) {
      res = '最小需购买' + props_data.invest_min_amount + '元'
    }

    this.setState({
      error_info: res
    })
    if (res) {
      return true
    }
    return false
  },

  handleChange: function (e) {
    money_amount = e.target.value
    if (this.checkError(false)) {
      return
    }

    let compute_expect = money_amount * props_data.annual_rate / 100 / 365 * props_data.frozen_days
    compute_expect = floorTwoDecimal(compute_expect)

    this.setState({
      compute_expect: compute_expect
    })

    deduction_num = Math.floor(money_amount / 200)
    deduction_num < 1 ? deduction_num = 0 : null
    deduction_num > this.props.orderData.user_balance ? deduction_num = this.props.orderData.user_balance : null

    CouponAction.setDeductionData(deduction_num, CouponStore.getDeductionStatus())

  },

  handleBlur: function () {
    appDispatcher.dispatch({
      actionType: 'input:blur',
      blur_amount: money_amount
    })
    this.checkError(true)
  },

  getOrderInfo: function () {
    if (this.checkError(true)) {
      return false
    }
    return {
      amount: money_amount
    }
  },

  getTipText: function () {
    let coupon_expect_text = ''

    if (coupon_rate) {
      let couponsProfit = money_amount * coupon_rate / 100 / 365 * props_data.frozen_days
      couponsProfit = floorTwoDecimal(couponsProfit)
      coupon_expect_text = <span>| 礼券收益 <em className="text-bold">{couponsProfit}</em> 元</span>
    }

    if (this.state.error_info) {
      return (
        <div className="tips-info has-error">
          <span className="text-12 text-light">{this.state.error_info}</span>
        </div>
      )
    }

    if (money_amount) {
      return (
        <div className="tips-info profit-info">
          <span className="text-12 text-light">预期收益：<em className="text-bold">{this.state.compute_expect}</em>元 {coupon_expect_text}</span>
        </div>
      )
    } else {
      return (
        <div className="tips-info date-info">
          <i className="iconfont icon-percent"></i>
          <span className="text-12 text-light">封闭期：<em className="text-orange">{props_data.frozen_days}</em>天 | 年化收益率：<em className="text-orange">{props_data.annual_rate }%</em></span>
        </div>
      )
    }
  },

  render: function () {
    var detail_tip = this.getTipText()
    let placeholder_text = '请输入大于' + props_data.invest_min_amount + '的整数'

    return (
      <div className="block-wrapper order-info">
        <div>
          <h2 className="block-title">攒钱金额</h2>
          <div className="input-box">
            <span className="input-prefix">金额</span>
            <input
              type="text"
              className="input-money"
              placeholder={placeholder_text}
              onChange={this.handleChange}
              onBlur={this.handleBlur}
              pattern="[0-9]*"/>
            <span className="input-unit">元</span>
          </div>
          {detail_tip}
        </div>
        <Deduction deductionNum={deduction_num} userBalance={this.props.orderData.user_balance} springFestival={this.props.springFestival}/>
        <CouponList couponsData={this.props.couponsData} moneyAmount={money_amount}/>
      </div>
    )
  }
})

module.exports = OrderInfo
