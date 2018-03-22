var dlg_error = require('g-error')
var CardWrapper = require('mods/card/_cardWrapper.jsx')
var CardStore = require('mods/card/_cardStore.jsx')
var appDispatcher = require('utils/dispatcher')

var Pay = React.createClass({
  getCurrentCard: function () {
    return CardStore.getCurrentCard()
  },

  handleSubmit: function (e) {
    var btn = e.target
    btn.setAttribute('disabled', 'disabled')
    setTimeout(function () {
      btn.removeAttribute('disabled')
    }, 2000)
    var current_card = this.getCurrentCard()
    if (current_card) {
      appDispatcher.dispatch({
        actionType: 'savings:submit',
        current_card: current_card
      })
    } else {
      dlg_error.show('请选择可用的银行卡')
    }
  },

  render: function () {
    return (
      <div className="block-wrapper">
        <CardWrapper cards={this.props.bankcards} bankData={this.props.bankData} partner={this.props.partner} productCategory={this.props.productCategory}/>
        <div className="submit-con">
          <a className="btn btn-primary btn-submit" href="#" onClick={this.handleSubmit}>支付</a>
        </div>
        {this.props.deal}
      </div>
    )
  }
})

module.exports = Pay
