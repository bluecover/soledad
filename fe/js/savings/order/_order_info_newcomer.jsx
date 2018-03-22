import floorTwoDecimal from 'utils/floorTwoDecimal'
let VirtualMoney = require('./_virtual_money.jsx')

var money_amount = ''
var props_data

var OrderInfo = React.createClass({
  getInitialState: function () {
    props_data = this.props.orderData

    return {
      compute_expect: '',
      error_info: ''
    }
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

    if (final_check && val > props_data.invest_max_amount) {
      res = '最多购买不超过' + props_data.invest_max_amount + '元'
    }

    this.setState({error_info: res})
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
  },

  handleBlur: function () {
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
    if (this.state.error_info) {
      return (
        <div className="tips-info has-error">
          <i className="iconfont icon-exclamation"></i>
          <span className="text-12 text-light">{this.state.error_info}</span>
        </div>
        )
    }

    if (money_amount) {
      return (
        <div className="tips-info profit-info">
          <i className="iconfont icon-revdollar"></i>
          <span className="text-12 text-light">预期收益：<em className="text-orange">{this.state.compute_expect}</em>元</span>
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

    return (
      <div className="block-wrapper order-info">
        <h2 className="block-title">攒钱金额</h2>
        <div className="input-box">
          <span className="input-prefix">金额</span>
          <input
            type="text"
            className="input-money"
            placeholder="请输入[1000-10000]的整数"
            onChange={this.handleChange}
            onBlur={this.handleBlur}
            pattern="[0-9]*"/>
          <span className="input-unit">元</span>
        </div>
        {detail_tip}
        <div className="deduction-box">
          {this.props.springFestival ? <VirtualMoney/> : null}
        </div>
      </div>
    )
  }
})

module.exports = OrderInfo
