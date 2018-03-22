var money_amount = ''
var props_data

var OrderInfo = React.createClass({
  propTypes: {
    data: React.PropTypes.object.isRequired
  },

  getInitialState: function () {
    props_data = this.props.orderData

    return {
      error_info: ''
    }
  },

  checkError: function (final_check) {
    var res = ''
    var val = money_amount

    if (final_check && !val) {
      res = '请正确输入金额'
    }

    if (final_check && val && Number(val) < props_data.invest_min_amount) {
      res = '最小交易金额为' + props_data.invest_min_amount + '元'
    }

    if (val && !(/^[0-9]+(\.\d{1,2})?$/.test(val))) {
      res = '抱歉，您输入的金额格式不正确'
      var integer_length = (val.substring(0, val.indexOf('.'))).length
      if (val.indexOf('.') > -1 && (val.length - integer_length) > 3) {
        res = '所输金额只支持精度到 0.01 元'
      }
    }

    if (this.props.orderType === 'deposit') {
      if (final_check && val && val > 50000) {
        res = '所输入金额不能超过50000元'
      }
    } else {
      if (Number(money_amount) > Number(this.props.balance_data)) {
        res = '所输入金额大于可取出金额'
      }
    }

    this.setState({
      error_info: res
    })

    if (res) {
      return true
    }

    return false
  },

  getOrderInfo: function () {
    if (this.checkError(true)) {
      return false
    }

    return {
      amount: this.refs.amount.value
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
  },

  handleChange: function (e) {
    money_amount = e.target.value
    this.checkError()
  },

  handleBlur: function () {
    this.checkError(true)
  },

  render: function () {
    var title
    var detail_tip = this.getTipText()
    if (this.props.orderType === 'deposit') {
      title = <h2 className="block-title">存入零钱包 <span className="order-date">起息时间 {this.props.orderDate}</span></h2>
    } else {
      title = <h2 className="block-title">取出零钱 <span className="text-12 text-lighter">可取出金额：{this.props.balance_data}元</span></h2>
    }

    return (
      <div className="block-wrapper order-info">
        {title}
        <div className="form-wrapper">
          <div className="input-con">
            <input
              type="text"
              className="two-col input-money"
              placeholder={this.props.orderType === 'deposit' ? '建议持有金额大于100元' : '请输入要取出的金额'}
              ref="amount"
              onChange={this.handleChange}
              onBlur={this.handleBlur}
            />
            <span className="input-unit">元</span>
          </div>
          {detail_tip}
          <p className="text-12 text-red text-tips">因合作方原因，零钱包暂时无法切换银行卡和修改预留手机号，如需上述操作请联系微信客服plan141 进行处理，感谢您的谅解与支持</p>
        </div>
      </div>
    )
  }
})

module.exports = OrderInfo
