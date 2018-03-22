// react-tween-state 使用了 requestAnimationFrame 方法，使用 raf 模块作为 Polyfill
if (window.requestAnimationFrame === undefined) {
  window.requestAnimationFrame = require('raf')
}

var tweenState = require('react-tween-state')

var duration_time = 800

var WaterCircle = React.createClass({
  mixins: [tweenState.Mixin],

  getInitialState: function () {
    return {
      height: 0,
      bottom: -11,
      rate: 0
    }
  },

  getDefaultProps: function () {
    return {
      data: {
        saving_amount: 0,
        // 非百分号表达方式
        rate: 0
      }
    }
  },

  _setAnimation: function () {
    var speed = this.props.data.rate < 1 ? this.props.data.rate : 1

    this.tweenState('height', {
      easing: tweenState.easingTypes.easeOut,
      duration: duration_time,
      endValue: 145 * speed
    })

    this.tweenState('bottom', {
      easing: tweenState.easingTypes.easeOut,
      duration: duration_time,
      endValue: 145 * speed - 11
    })

    this.tweenState('rate', {
      easeing: tweenState.easingTypes.easeOut,
      duration: duration_time,
      endValue: 100 * speed
    })
  },

  componentWillMount: function () {
    // rate 转为百分数形式
    this.rate = this.props.data.rate.toFixed(2) * 100
  },

  componentDidMount: function () {
    this._setAnimation()
  },

  render: function () {

    var isShow = this.rate > 100 ? 'visible' : 'hidden'
    var rate = this.getTweeningValue('rate').toFixed(0)

    var showStyle = {
      visibility: isShow
    }

    var hdStyle = {
      bottom: this.getTweeningValue('bottom')
    }

    var waterStyle = {
      height: this.getTweeningValue('height')
    }

    return (
      <div className="water-circle-mod">
        <div className="hd" style={hdStyle}>
          <span className="measure-line"></span>
          <span className="measure-mark">{this.props.data.saving_amount}元</span>
        </div>
        <div className="bd">
          <p className="exceed-text" style={showStyle}>超过</p>
          <p className="rate"><strong>{rate}</strong>%</p>
          <div className="circle"></div>
          <div className="water" style={waterStyle}></div>
        </div>
      </div>
    )
  }
})

module.exports = WaterCircle
