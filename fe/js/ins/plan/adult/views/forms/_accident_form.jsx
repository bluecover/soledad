import SurveyForm from 'ins/plan/views/forms/_survey_form.jsx'
import { InputGroup, Input } from 'ins/plan/views/forms/_input.jsx'
import Select from 'ins/plan/views/forms/_select.jsx'

import getSubject from 'ins/plan/utils/_get_subject.js'

class AccidentForm extends SurveyForm {
  constructor(props) {
    props.fields = ['annual_revenue_personal', 'annual_revenue_family', 'resident']
    super(props)

    this._show_revenue_error = false
  }

  validateRevenue() {
    let {
      validate
    } = this.props

    validate && validate({
      name: 'annual_revenue'
    })
  }

  handleRevenueChange() {
    this.validateRevenue()
    this._show_revenue_error = false
  }

  handleRevenueBlur() {
    this.validateRevenue()
    this._show_revenue_error = true
  }

  beforeSubmit() {
    let {
      annual_revenue = {}
    } = this.props

    return !annual_revenue.error
  }

  componentDidMount() {
    this.validateRevenue()
    this._show_revenue_error = true
  }

  render() {
    let {
      gender = {},
      marriage = {},
      owner = {},
      annual_revenue_family = {},
      annual_revenue_personal = {},
      resident = {},
      annual_revenue = {},
      validate,
      addAnswer
    } = this.props

    let error_personal = annual_revenue_personal.error
    let error_family = annual_revenue_family.error
    let error_revenue = annual_revenue.error

    let form_is_valid = error_personal === null &&
                        (marriage.value === '未婚' || error_family === null) &&
                        resident.error === null &&
                        error_revenue === null

    if (error_family || error_personal || !this._show_revenue_error) {
      error_revenue = ''
    }

    let subject = getSubject({
      owner: owner.value,
      gender: gender.value,
      is_que: false
    })

    let title = subject + '的收入'

    let family_revenue_input
    if (marriage.value === '已婚') {
      family_revenue_input = (
        <Input
          className="annual-revenue-family"
          name="annual_revenue_family"
          title="家庭收入"
          unit="万元/年"
          value={annual_revenue_family.value}
          error={error_family}
          changeValidation="required|positive_integer"
          blurValidation="required|number_1_1000"
          pattern="[0-9]*"
          validate={validate}
          onChange={addAnswer}
        />
      )
    }

    return (
      <SurveyForm
        {...this.props}
        title="家庭信息"
        is_valid={form_is_valid}
        id="js_accident_form"
        className="m-accident-form"
        beforeSubmit={this.beforeSubmit.bind(this)}
        stage={2}>
        <InputGroup
          onBlur={this.handleRevenueBlur.bind(this)}
          onChange={this.handleRevenueChange.bind(this)}
          error={error_revenue}
          title="年收入">
          <Input
            className="annual-revenue-personal"
            name="annual_revenue_personal"
            title={title}
            unit="万元/年"
            value={annual_revenue_personal.value}
            error={error_personal}
            changeValidation="required|positive_integer"
            blurValidation="required|number_0_1000"
            pattern="[0-9]*"
            validate={validate}
            onChange={addAnswer}>
          </Input>
          {family_revenue_input}
        </InputGroup>

        <Select
          name="resident"
          title="所在地"
          value={resident.value}
          changeValidation="required"
          validate={validate}
          onChange={addAnswer}>
          <option value="北上深">北上深</option>
          <option value="一二线城市">一二线城市</option>
          <option value="其他地级市">其他地级市</option>
          <option value="县市、城镇">县市、城镇</option>
        </Select>
      </SurveyForm>
    )
  }
}

// Fallback IE 10 以下不支持 __proto__
AccidentForm.childContextTypes = {
  form: React.PropTypes.object
}

export default AccidentForm
