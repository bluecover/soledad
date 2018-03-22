var dlg_error = require('g-error')
var appDispatcher = require('utils/dispatcher')
var CardWrapper = require('mods/card/_cardWrapper.jsx')
var CardStore = require('mods/card/_cardStore.jsx')

var Pay = React.createClass({
  getCurrentCard: function () {
    return CardStore.getCurrentCard()
  },

  handleSubmit: function (e) {
    var current_card = this.getCurrentCard()
    if (current_card) {
      appDispatcher.dispatch({
        actionType: 'wallet:submit',
        current_card: current_card
      })
    } else {
      dlg_error.show('请选择可用的银行卡')
    }
  },

  render: function () {
    let btn_text = this.props.orderType === 'withdraw' ? '取出' : '支付'
    return (
      <div className="block-wrapper">
        <CardWrapper cards={this.props.cards} bankData={this.props.bankData} partner="zs" productCategory={this.props.productCategory}/>
        <div className="submit-con">
          <a className="btn btn-primary btn-large" href="#" onClick={this.handleSubmit}>{btn_text}</a>
        </div>
        <p className="text-12">点击提交表示您已同意<a href="/wallet/agreement" target="_blank">零钱包理财服务协议</a></p>
      </div>
    )
  }
})

module.exports = Pay
