let classNames = require('classnames')
let CouponItem = require('./_couponItem.jsx')
let appDispatcher = require('utils/dispatcher')
let CouponStore = require('./_couponStore.jsx')
let CouponAction = require('./_couponAction.jsx')

function getCouponState() {
  return {
    coupon_data: CouponStore.getCouponData(),
    coupon_status: CouponStore.getCouponStatus(),
    cancel_coupon: CouponStore.getCancelText()
  }
}

let CouponList = React.createClass({
  getInitialState: function () {
    return getCouponState()
  },

  componentDidMount: function () {
    CouponStore.on('change', function () {
      this.setState(getCouponState())
    }.bind(this))
  },

  handleChangeCoupon: function () {
    if (!this.props.couponsData.length) {
      return
    }

    let coupon_status = !this.state.coupon_status
    CouponAction.setCouponStatus(coupon_status)
  },

  handleCancelCoupon: function () {
    appDispatcher.dispatch({
      actionType: 'coupon:cancel'
    })
    CouponAction.setCouponStatus(false)
  },

  hideCoupon: function () {
    CouponAction.setCouponStatus(false)
  },

  getCouponText: function () {
    if (this.state.coupon_data) {
      return (
        <em>{this.state.coupon_data.name}：<em className="text-orange">{this.state.coupon_data.description}</em></em>
      )
    } else {
      return (
        <em>使用优惠券（有<em className='text-orange'>{this.props.couponsData.length}</em>张可用）</em>
      )
    }
  },

  render: function () {

    let arrow_class = classNames({
      'iconfont icon-forward text-lighter': true,
      'cur': this.state.coupon_status
    })
    let coupon_class = classNames({
      'coupon-main': true,
      'hide': !this.state.coupon_status
    })
    let coupon_text = this.getCouponText()
    let mask = <div className="mask mobile-element" onClick={this.hideCoupon}></div>

    return (
      <div>
        {this.state.coupon_status ? mask : null}
        <div className="coupon-box">
          <i className={arrow_class}></i>
          <span onClick={this.handleChangeCoupon}>{coupon_text}</span>
          <a href="#" onClick={this.handleCancelCoupon}>{this.state.cancel_coupon}</a>
          <div className={coupon_class}>
            {this.props.couponsData.map(function (item, index) {
              return (
                <CouponItem key={index} item={item} moneyAmount={this.props.moneyAmount} />
              )
            }, this)}
          </div>
        </div>
      </div>
    )
  }
})

module.exports = CouponList
