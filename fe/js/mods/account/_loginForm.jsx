import cx from 'classnames'
import Input from './_input.jsx'
import Form from './_form.jsx'

const PropTypes = React.PropTypes

class LoginForm extends Form {
  constructor(props) {
    super(props)

    this._api_url = '/j/account/login'
  }

  // 切换为注册状态
  switchToReg() {
    this.props.switchAccount('register')
  }

  render() {
    let classNames = cx('m-account-form', 'm-reg-form', this.props.className)

    return (
      <form
        className={classNames}>

        <div className="hd desktop-element"><h3 className="title">登录</h3></div>

        <div className="bd">
          <Input
            name="alias"
            id="login-username"
            placeholder="注册的手机号或邮箱"
            className="username"
            iconClass="icon-phone"
            validation="required|username" />
          <Input
            name="password"
            id="login-password"
            placeholder="密码"
            type="password"
            className="password"
            iconClass="icon-lock"
            validation="required|password" />
          <div className="forget-psd">
            <a href="/accounts/password/forgot" target="_blank">忘记密码?</a>
          </div>

          <button
            onClick={this.handleSubmit.bind(this)}
            className="btn btn-primary btn-login-submit">
            {this.props.login_btn_text ? this.props.login_btn_text : '登录'}</button>

          {this._renderCommonError()}

          <div className="split-line">
            <span className="circle">OR</span>
          </div>
          <button
            type="button"
            onClick={this.switchToReg.bind(this)}
            className="btn btn-gray btn-register">免费注册</button>
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

LoginForm.propTypes = {
  className: PropTypes.string,
  switchAccount: PropTypes.func
}

// Fallback IE 10 以下不支持 __proto__
LoginForm.childContextTypes = {
  form: PropTypes.object
}

export default LoginForm
