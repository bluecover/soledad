let appDispatcher = require('utils/dispatcher')

let VirtualMoney = React.createClass({
  handleVirtualDetail: function () {
    appDispatcher.dispatch({
      actionType: 'virtual:modalDetail'
    })
  },
  render: function () {
    return (
      <div>
        <input type="checkbox" checked/>
        <span> 获赠8888元体验金</span>
        <i onClick={this.handleVirtualDetail} className="iconfont icon-exclamation text-lighter"></i>
      </div>
    )
  }
})

module.exports = VirtualMoney
