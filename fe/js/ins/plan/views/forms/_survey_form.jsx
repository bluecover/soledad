import cx from 'classnames'

import Form from 'mods/account/_form.jsx'
import dlg_error from 'g-error'

class SurveyForm extends Form {
  constructor(props) {
    super(props)

    this.fields = props.fields
    this.handleSubmit = this.handleSubmit.bind(this)
  }

  getParams() {
    let params = {}

    this.fields && this.fields.forEach((field, index) => {
      let value = this.props[field] && this.props[field].value

      if (typeof value === 'object' && value !== null) {
        value = JSON.stringify(value)
      }

      params[field] = value
    })

    return params
  }

  handleSubmit(e) {
    let {
      stage,
      completeForm,
      is_valid,
      beforeSubmit
    } = this.props

    e.preventDefault()

    if (!is_valid || (beforeSubmit && beforeSubmit()) === false) {
      return
    }

    let params = this.getParams()
    params.stage = stage

    $.ajax({
      url: '/j/ins/plan/add_planning',
      data: params,
      type: 'POST'
    }).done((r) => {
      completeForm({
        ...r,
        stage: stage + 1
      })

      this.refs.close.click()
    }).fail((xhr) => {
      dlg_error(xhr && xhr.responseJSON && xhr.responseJSON.error)
    })
  }

  render() {
    let {
      title,
      subtitle,
      children,
      id,
      className,
      is_valid
    } = this.props

    let classNames = cx('m-survey-form', className)
    let btn_class = cx('btn btn-primary', {
      'btn-disable': !is_valid
    })

    return (
      <form
        onSubmit={this.handleSubmit}
        id={id}
        className={classNames}>
        <div className="hd">
          <h3 className="title">{title}</h3>
          <div className="subtitle">{subtitle}</div>
        </div>
        <div className="bd">
          {children}
        </div>
        <div className="ft">
          <button
            className={btn_class}>确定</button>
          <a
            ref='close'
            href="#"
            rel="onemodal:close"
            className="close">
            <i className="iconfont icon-close"></i>
          </a>
          <p className="tip">
            以上信息多层加密严保安全，请放心规划
          </p>
        </div>
      </form>
    )
  }
}

// Fallback IE 10 以下不支持 __proto__
SurveyForm.childContextTypes = {
  form: React.PropTypes.object
}

export default SurveyForm
