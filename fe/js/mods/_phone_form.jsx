import {phone as phone_reg} from 'lib/re'
import Cookies from 'cookies-js'

let phone_val

class PhoneForm extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      error_info: ''
    }
    this.handleBlur = this.handleBlur.bind(this)
    this.handleSubmit = this.handleSubmit.bind(this)
  }

  checkError() {
    let res = ''

    if (!phone_val) {
      res = '请填写手机号'
    } else if (!(phone_reg.test(phone_val))) {
      res = '请填写正确的手机号'
    } else {
      res = ''
    }

    this.setState({
      error_info: res
    })

    if (res) {
      return true
    }
    return false
  }

  handleBlur(e) {
    phone_val = e.target.value
    this.checkError()
  }

  handleSubmit(e) {
    if (this.checkError()) {
      e.preventDefault()
    }
  }

  getTipText() {
    if (this.state.error_info) {
      return (
        <p className="prompt-tip"><i className="iconfont icon-wrong text-16"></i>{this.state.error_info}</p>
      )
    }
  }

  render() {
    let tip_text = this.getTipText()
    return (
      <form className="phone-form" action={this.props.actionUrl} method="post" onSubmit={this.handleSubmit}>
        <input type="hidden" name="csrf_token" defaultValue={Cookies.get('csrf_token')}/>
        <lable><input type="text" onBlur={this.handleBlur} name="mobile" placeholder="请输入您的手机号" pattern="[0-9]*"/></lable>
        <button type="submit" className="btn btn-primary">立即领取</button>
        {tip_text}
      </form>
    )
  }
}

export default PhoneForm
