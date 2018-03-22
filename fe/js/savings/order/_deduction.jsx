let appDispatcher = require('utils/dispatcher')
let CouponAction = require('./_couponAction.jsx')
let VirtualMoney = require('./_virtual_money.jsx')
let deduction_status

let Deduction = React.createClass({
  getInitialState: function () {
    return {
      deduction_status: false
    }
  },

  handleChange: function () {
    deduction_status = !this.state.deduction_status
    this.setState({
      deduction_status
    })
    let deduction_num = deduction_status ? this.props.deductionNum : 0
    CouponAction.setDeductionData(deduction_num, deduction_status)
  },

  handleDeductionDetail: function () {
    appDispatcher.dispatch({
      actionType: 'deduction:modalDetail'
    })
  },

  getDeductionText: function () {
    if (this.state.deduction_status) {
      return (
        <label htmlFor="deduction-checkbox">抵扣<em className="text-orange">{this.props.deductionNum}</em>元</label>
      )
    } else {
      return (
        <label htmlFor="deduction-checkbox">使用红包抵扣</label>
      )
    }
  },

  getDeductionTips: function () {
    if (Number(this.props.userBalance) === 0) {
      return (
        <a target="_blank" href="/invite/mine">如何获得</a>
      )
    } else {
      return (
        <span>每200元可抵扣1元</span>
      )
    }
  },

  render: function () {
    let deduction_text = this.getDeductionText()
    let deduction_tips = this.getDeductionTips()
    return (
      <div className="deduction-box">
        <input onChange={this.handleChange} checked={this.state.deduction_status} id="deduction-checkbox" name="deduction-checkbox" type="checkbox"/>
        {deduction_text}
        <span className="text-lighter">（总共有{this.props.userBalance}元红包，{deduction_tips}）</span>
        <i onClick={this.handleDeductionDetail} className="iconfont icon-exclamation text-lighter"></i>
        {this.props.placeboData ? <VirtualMoney/> : null}
      </div>
    )
  }
})

module.exports = Deduction
