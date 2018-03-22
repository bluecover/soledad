import floorTwoDecimal from 'utils/floorTwoDecimal'
let CouponList = require('./_couponList.jsx')
let Deduction = require('./_deduction.jsx')
let appDispatcher = require('utils/dispatcher')
let CouponStore = require('./_couponStore.jsx')
let CouponAction = require('./_couponAction.jsx')

var Moment = require('moment')

var dayStart
var dayEnd
var dates = []
var startRateDay
var layers
var money_amount = ''
var profitRate
var curDiffDays
let deduction_num = 0
let coupon_rate

function diffDay(dueday) {
  dueday = dueday.replace(/\-/g, '/')
  startRateDay = startRateDay.replace(/\-/g, '/')

  var mt = Moment(new Date(startRateDay))
  var md = Moment(new Date(dueday))
  return md.diff(mt, 'days')
}

function computeRate(diff) {
  var rate
  layers.some(function (item, index) {
    if (diff >= item.min_days) {
      rate = item.annual_rate
      return true
    }
  })
  return rate
}

function daysInMonth(month, year) {
  return new Date(year, month, 0).getDate()
}

function makeCanlendar(first, last) {
  var mFirst = Moment(first)
  var mLast = Moment(last)
  var firstMonth = mFirst.get('month') + 1
  var firstYear = mFirst.get('y')

  var lastMonth = mLast.get('month') + 1
  var lastYear = mLast.get('y')
  dayStart = mFirst.get('date')
  dayEnd = mLast.get('date')

  if (firstMonth < lastMonth) {
    for (let i = firstMonth; i <= lastMonth; i++) {
      let data = {}
      data.month = i
      data.year = firstYear
      data.days = daysInMonth(i, firstYear)
      dates.push(data)
    }
  } else {
    for (let i = firstMonth; i <= 12; i++) {
      let data = {}
      data.month = i
      data.year = firstYear
      data.days = daysInMonth(i, firstYear)
      dates.push(data)
    }
    for (var j = 1; j <= lastMonth; j++) {
      let data = {}
      data.month = j
      data.year = lastYear
      data.days = daysInMonth(j, lastYear)
      dates.push(data)
    }
  }
}

function makeDates(start, end, index) {
  var days = []
  var date = dates[index]

  for (var i = start; i <= end; i++) {
    var data = {}
    data.day = i
    data.val = date.year + '-' + date.month + '-' + i
    data.diff = diffDay(data.val)
    data.rate = computeRate(data.diff)
    days.push(data)
  }
  return days
}

function getCouponRate() {
  coupon_rate = CouponStore.getCouponRate()
}

var zhiwangOrder = React.createClass({
  getInitialState: function () {
    return {
      days: [],
      compute_expect: '',
      error_info: '',
      diff_days: ''
    }
  },

  componentDidMount: function () {
    CouponStore.on('change', function () {
      this.forceUpdate(getCouponRate())
    }.bind(this))
  },

  getOrderInfo: function () {
    if (this.checkError(true)) {
      return false
    }

    return {
      amount: this.refs.amount.value,
      date: this.refs.day.value
    }
  },

  checkError: function (final_check) {
    var res = ''
    var val = money_amount

    if (val && !(/^\d+$/.test(val))) {
      res = '请正确输入金额(请勿输入数字以外的字符)'
    }

    if (final_check && val < 1000) {
      res = '最小需购买' + this.props.orderData.invest_min_amount + '元'
    }

    this.setState({
      error_info: res
    })
    if (res) {
      return true
    }

    if (final_check && !this.refs.day || !(this.refs.day.value)) {
      return true
    }

    return false
  },

  profitCal: function () {
    var compute_expect = money_amount * profitRate / 100 * curDiffDays / 365
    compute_expect = floorTwoDecimal(compute_expect)
    this.setState({
      compute_expect: compute_expect
    })
  },

  handleInputChange: function (e) {
    money_amount = e.target.value
    let is_valid = /^\d+$/.test(money_amount)
    if (is_valid) {
      deduction_num = Math.floor(money_amount / 200)
      deduction_num < 1 ? deduction_num = 0 : null
      deduction_num > this.props.orderData.user_balance ? deduction_num = this.props.orderData.user_balance : null
    } else {
      deduction_num = 0
    }

    CouponAction.setDeductionData(deduction_num, CouponStore.getDeductionStatus())

    if (this.checkError(false)) {
      return
    }

    this.profitCal()

  },

  handleMonthChange: function (e) {
    var res = []
    var index = e.target.value
    var days = index ? dates[index].days : null
    if (index === '0') { // such js
      res = makeDates(dayStart, days, index)
    } else if (parseInt(index, 10) + 1 === dates.length) {
      res = makeDates(1, dayEnd, index)
    } else if (index) {
      res = makeDates(1, days, index)
    }

    this.setState({
      days: res
    })
  },

  handleDayChange: function (e) {
    var sel = e.target
    var index = sel.selectedIndex
    var opt = sel.options[index]

    var diffDays = opt.getAttribute('data-diff')
    var rate = opt.getAttribute('data-rate')

    profitRate = rate
    curDiffDays = diffDays
    this.setState({
      diff_days: diffDays
    })
    this.profitCal()
  },

  handleBlur: function () {
    appDispatcher.dispatch({
      actionType: 'input:blur',
      blur_amount: money_amount
    })
    this.checkError(true)
  },

  getTipText: function () {
    let coupon_expect_text = ''

    if (coupon_rate) {
      let coupons_profit = parseFloat(money_amount * coupon_rate / 100 * curDiffDays / 365).toFixed(2)
      coupon_expect_text = <span> + <em className="text-orange">{coupons_profit}</em> 元</span>
    }

    if (!this.refs.day || !(this.refs.day.value)) {

      return (
        <div className="tips-info date-info">
          <span className="text-12 text-light">请先选择日期</span>
        </div>
      )
    }
    if (this.state.error_info) {
      return (
        <div className="tips-info has-error">
          <span className="text-12 text-light">{this.state.error_info}</span>
        </div>
      )
    }

    if (money_amount || this.state.diff_days) {
      var money_tips = money_amount ? <span>预期收益：<em className="text-orange">{this.state.compute_expect}</em>元 {coupon_expect_text} | </span> : null
      return (
        <div className="tips-info profit-info">
          <span className="text-12 text-light">{ money_tips }封闭期：<em className="text-orange">{this.state.diff_days}</em>天</span>
        </div>
      )
    }
  },

  componentWillMount: function () {
    var data = this.props.orderData
    layers = data.rate_layers
    startRateDay = data.start_date
    makeCanlendar(data.first_due_date, data.last_due_date)
  },

  render: function () {
    var detail_tip = this.getTipText()
    return (
      <div className="block-wrapper order-info">
        <div className="order-section">
          <h2 className="block-title">选择到期日</h2>
          <select className="select-date" ref="month" onChange={this.handleMonthChange}>
            <option value="">到期月份</option>
            {dates.map(function (item, index) {
              return <option key={index} value={index}>{item.year}年 {item.month}月</option>
            })}
          </select>

          <select className="select-date" ref="day" onChange={this.handleDayChange}>
            <option value="">到期日</option>
            {this.state.days.map(function (item) {
              return <option value={item.val} key={item.val} data-diff={item.diff} data-rate={item.rate}>{item.day}日 {item.rate}%</option>
            })}
          </select>
        </div>

        <div className="order-section">
          <h2 className="block-title">攒钱金额</h2>
          <div className="input-box">
            <span className="input-prefix">金额</span>
            <input
              type="text"
              className="input-money"
              placeholder="请输入大于1000的整数"
              ref="amount"
              onChange={this.handleInputChange}
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

module.exports = zhiwangOrder
