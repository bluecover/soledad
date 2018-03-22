let classNames = require('classnames')
let appDispatcher = require('utils/dispatcher')
let CouponAction = require('./_couponAction.jsx')
let CouponStore = require('./_couponStore.jsx')

function getCouponId() {
  return {
    coupon_id: CouponStore.getCouponInfo().coupon_id
  }
}

let CouponItem = React.createClass({
  getInitialState: function () {
    return getCouponId()
  },

  componentDidMount: function () {
    CouponStore.on('change', function () {
      this.setState(getCouponId())
    }.bind(this))
  },

  getCouponType: function () {
    let benefit = this.props.item.benefit

    if (benefit.extra_rate) {
      return (
        <h5><em>＋</em>{benefit.extra_rate}<em>％</em></h5>
      )
    }

    if (benefit.deduct_amount) {
      return (
        <h5><em>减</em>{benefit.deduct_amount}<em>元</em></h5>
      )
    }
  },

  getCouponValid: function () {
    let item_data = this.props.item
    let fulfill_amount = item_data.usage_requirement && item_data.usage_requirement.fulfill_amount
    let amount_is_valid = /^\d+$/.test(this.props.moneyAmount)
    let coupon_valid = true
    if (!amount_is_valid && fulfill_amount || fulfill_amount > this.props.moneyAmount) {
      coupon_valid = false
    }
    return coupon_valid
  },

  handleSelectCoupon: function () {
    let coupon_is_valid = this.getCouponValid()

    if (!coupon_is_valid) {
      return
    }

    appDispatcher.dispatch({
      actionType: 'coupon:select',
      coupon_data: this.props.item,
      cancel_text: '取消使用'
    })
    CouponAction.setCouponStatus(false)
  },

  render: function () {
    let item_data = this.props.item
    let coupon_title = this.getCouponType()
    let coupon_void = !this.getCouponValid()

    let classes = classNames({
      'coupon-item': true,
      'coupon-void': coupon_void,
      'coupon-selected': item_data.id_ === this.state.coupon_id
    })

    return (
      <div className={classes} onClick={this.handleSelectCoupon}>
        <span className="text-lighter text-12">未满足</span>
        <img src="{{{img/misc/unmet.png}}}" alt="未满足"/>
        {coupon_title}
        <p>{item_data.name}，{item_data.description}</p>
        <p>{item_data.product_requirement}</p>
        <p>有效期至{item_data.expire_time}</p>
      </div>
    )
  }
})

module.exports = CouponItem
