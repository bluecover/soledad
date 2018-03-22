import { phone as phone_reg } from 'lib/re'
import dlg_tips from 'mods/modal/modal_tips'
import dlg_error from 'mods/modal/error'

let phone_val

class PhoneForm extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      error_info: '',
      phone_val: ''
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

    return !!res
  }

  handleBlur(e) {
    phone_val = e.target.value
    this.checkError()
    if (!this.checkError()) {
      this.setState({
        phone_val: e.target.value
      })
    }
  }

  handleSubmit() {
    if (this.checkError()) {
      return
    }

    const phoneData = this.props.phoneData

    $.ajax({
      url: phoneData.submit_url,
      type: 'POST',
      dataType: 'json',
      data: { mobile: this.state.phone_val }
    })
    .done((e) => {
      if (e.is_new_user) {
        dlg_tips.show({
          tips_title: phoneData.new_user.tips_title,
          tips_main: phoneData.new_user.tips_main
        })
      } else {
        dlg_tips.show({
          tips_title: phoneData.old_user.tips_title,
          tips_main: phoneData.old_user.tips_main
        })
      }
    })
    .fail(function () {
      dlg_error.show()
    })
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
      <div className="phone-form">
        <input type="text" onBlur={this.handleBlur} name="mobile" placeholder="请输入您的手机号" pattern="[0-9]*"/>
        <a href="#" className="btn btn-primary" onClick={this.handleSubmit}>立即领取</a>
        {tip_text}
      </div>
    )
  }
}

export default PhoneForm
