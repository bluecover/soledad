var Coupon = React.createClass({
  propTypes: {
    updateCoupon: React.PropTypes.func.isRequired,
    couponRate: React.PropTypes.number.isRequired
  },

  getInitialState: function () {
    return {
      checked: true
    }
  },

  componentDidMount: function () {
    this.props.updateCoupon(this.state.checked)
  },

  handleChange: function (e) {
    var checked = e.target.checked
    this.setState({
      checked: checked
    })
    this.props.updateCoupon(checked)
  },

  render: function () {
    return (
      <div className="coupon-con">
        <label>
          <input type="checkbox" checked={this.state.checked} onChange={this.handleChange} />
          <img src="{{{img/savings/ico_coupon.png}}}" width="12" />
          <span className="text-12 text-light">&nbsp;使用礼券年收益 +{this.props.couponRate}%</span>
        </label>
      </div>
    )
  }
})

module.exports = Coupon
