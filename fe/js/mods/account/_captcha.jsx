import countdown from 'utils/countdown.js'
import cx from 'classnames'

const PropTypes = React.PropTypes

class PicCaptcha extends React.Component {
  constructor(props) {
    super(props)

    // 保留初始 src 值
    let random_num = (Math.random(0, 1) * 9999).toFixed(0)
    let url = '/captcha/get?blur=' + random_num
    this._src = props.src || url

    this.state = {
      src: this._src
    }
  }

  handleClick(e) {
    let date = new Date()
    let src = this._src + date.getTime()
    this.setState({
      src: src
    })
  }

  render() {
    return (
      <a
        href="#"
        onClick={this.handleClick.bind(this)}
        className="captcha">
        <img
          className="captcha-img"
          src={this.state.src}
          alt="加载失败"
          title="点我换一张"/>
      </a>
    )
  }
}

let countdownObj
const SMS_CAPTCHA_RESET_TIME_S = 60

class SmsCaptcha extends React.Component {
  constructor(props) {
    super(props)

    this.state = {
      text: '获取验证码',
      disabled: false
    }
  }

  activateBtn() {
    if (countdownObj) {
      countdownObj.getRemainingTime() > 0 ? countdownObj.abort() : null
    }

    this.setState({
      text: '获取验证码',
      disabled: false
    })
  }

  handleValidation() {
    return this.props.handleValidation()
  }

  handleClick() {
    // 提交前先验证手机号和图形验证码
    let res = this.handleValidation()

    if (res) {
      this._sendSmsCaptcha()
    } else {
      return
    }

  }

  _setCountdownBtn(time_s = 60) {
    countdownObj = countdown(time_s, (secondsLeft) => {
      this.setState({
        text: secondsLeft + '后重新发送',
        disabled: true
      })
    }, () => {
      this.setState({
        text: '获取验证码',
        disabled: false
      })
    })
  }

  _sendSmsCaptcha() {
    // 图形验证码和手机号
    let params = this.props.getFieldValue()

    $.ajax({
      url: this.props.url,
      type: 'POST',
      data: params,
      dataType: 'json'
    }).done(() => {

      this._setCountdownBtn()

    }).fail((c) => {
      let reset_time_s = c.getResponseHeader('X-RateLimit-Reset')
      let reset_time_remaining_s = 0

      // 如果存在有效期时间，计算剩余时间
      if (reset_time_s) {
        let current_time_ms = new Date(c.getResponseHeader('Date')).valueOf()
        reset_time_remaining_s = reset_time_s - current_time_ms / 1000
      }

      // 如果之前已经收到过验证码，且在 60s 的锁定期内，则发送按钮失效
      if (SMS_CAPTCHA_RESET_TIME_S > reset_time_remaining_s && reset_time_remaining_s > 0) {
        this._setCountdownBtn(reset_time_remaining_s)
      }

      if (c && c.responseJSON) {
        this.props.setError(c.responseJSON.errors)
      } else {
        this.props.setError('操作失败，请重新操作!')
      }

      // 刷新图形验证码
      this.props.updatePiccaptcha()

    })
  }

  render() {
    let classNames = cx({
      'captcha': true,
      'btn': true,
      'btn-blue': !this.state.disabled,
      'btn-disable': this.state.disabled
    })

    return (
      <a
        className={classNames}
        disabled={this.state.disabled}
        href="#"
        onClick={this.handleClick.bind(this)}>
        {this.state.text}</a>
    )
  }
}

SmsCaptcha.propTypes = {
  url: PropTypes.string.isRequired,
  handleValidation: PropTypes.func,
  getFieldValue: PropTypes.func,
  setError: PropTypes.func
}

export {PicCaptcha, SmsCaptcha}
