import cx from 'classnames'

import Input from './_input.jsx'
import Form from './_form.jsx'
import {PicCaptcha, SmsCaptcha} from './_captcha.jsx'

function handleServiceError(errors) {
  let new_errors = {}

  for (let error of errors) {
    if (error.field) {
      new_errors[error.field] = error.message
    } else {
      new_errors.commonError = error.message
    }
  }

  return new_errors
}

const PropTypes = React.PropTypes

class RegForm extends Form {
  constructor(props) {
    super(props)

    this._api_url = '/j/account/register'
  }

  // 切换为登录状态
  switchToLogin() {
    this.props.switchAccount('login')
  }

  updatePiccaptcha() {
    this.refs.piccaptcha.handleClick()
  }

  handleSmsValidation() {
    this._fields_map.get('captcha').validate()
    this._fields_map.get('mobile').validate()

    return this.isValid('captcha') && this.isValid('mobile')
  }

  setSmsError(errors) {
    let new_errors = null

    // return obj: {field_name: error_msg, ...}
    new_errors = handleServiceError(errors)

    if (new_errors.commonError) {
      this._fields_map.get('verify_code').setError(new_errors.commonError)
      delete new_errors.commonError
    }

    this.setError(new_errors)
  }

  getFieldValueForSms() {
    return {
      'captcha': this.getFieldValue('captcha'),
      'mobile': this.getFieldValue('mobile')
    }
  }

  render() {
    let classNames = cx('m-account-form', 'm-reg-form', this.props.className)

    return (
      <form
        className={classNames}>

        <div className="hd desktop-element">
          <h3 className="title">注册</h3>
        </div>

        <div className="bd">
          <Input
            id="remove-username-autofill"
            name="remove-username-autofill"
            type="text"
            className="hide" />
          <Input
            id="remove-password-autofill"
            name="remove-password-autofill"
            type="password"
            className="hide" />

          <Input
            name="mobile"
            id="reg-username"
            placeholder="注册手机号"
            pattern="[0-9]*"
            className="username"
            iconClass="icon-phone"
            validation="required|phone"
            tip="好规划不会在任何地方泄漏您的手机号" />
          <Input
            name="captcha"
            id="captcha"
            placeholder="图形验证码"
            pattern="[0-9]*"
            className="pic-captcha"
            validation="required|captcha">
            <PicCaptcha ref='piccaptcha'/>
          </Input>
          <Input
            name="verify_code"
            id="sms_captcha"
            placeholder="短信验证码"
            pattern="[0-9]*"
            className="sms-captcha"
            validation="required|captcha">
            <SmsCaptcha
              ref='smscaptcha'
              url='/j/account/register/captcha'
              updatePiccaptcha={this.updatePiccaptcha.bind(this)}
              handleValidation={this.handleSmsValidation.bind(this)}
              getFieldValue={this.getFieldValueForSms.bind(this)}
              setError={this.setSmsError.bind(this)} />
          </Input>
          <Input
            name="password"
            id="reg-password"
            placeholder="请设置至少 6 位字符的登录密码"
            type="password"
            className="password"
            iconClass="icon-lock"
            validation="required|password" />

          <button
            onClick={this.handleSubmit.bind(this)}
            className="btn btn-primary btn-register-submit">
            {this.props.register_btn_text ? this.props.register_btn_text : '免费注册'}</button>

          {this._renderCommonError()}

          <p className="agreement-desc">
            点击“免费注册“将视为您同意
            <a
              className="user-agreement"
              target="_blank" href="/legal/useragreement">好规划用户服务协议</a>
          </p>
          <div className="split-line">
            <span className="circle">OR</span>
          </div>
          <button
            type="button"
            onClick={this.switchToLogin.bind(this)}
            className="btn btn-gray btn-login">登录</button>
        </div>

        <div className="ft">
          <a className="close-btn" rel="onemodal:close" href="#">
            <i className="iconfont icon-close"></i>
          </a>
        </div>

      </form>
    )
  }
}

RegForm.propTypes = {
  className: PropTypes.string,
  switchAccount: PropTypes.func
}

RegForm.childContextTypes = {
  form: PropTypes.object
}

export default RegForm
