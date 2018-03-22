import SurveyForm from 'ins/plan/views/forms/_survey_form.jsx'
import Select from 'ins/plan/views/forms/_select.jsx'

import convertNumber from 'ins/plan/utils/_convert_number'

class AnnualPremiumForm extends SurveyForm {
  constructor(props) {
    props.fields = ['annual_premium']
    super(props)
  }

  render() {
    let {
      annual_premium = {},
      ins_premium_up,
      ins_premium_least,
      addAnswer,
      validate
    } = this.props

    let form_is_valid = annual_premium.error === null
    ins_premium_up = convertNumber(ins_premium_up)
    ins_premium_least = convertNumber(ins_premium_least)

    return (
      <SurveyForm
        {...this.props}
        title="保障现状"
        is_valid={form_is_valid}
        id="js_annual_premium_form"
        className="m-annual-premium-form"
        stage={6}>
        <Select
          className="annual-premium"
          name="annual_premium"
          title="商业保险费"
          value={annual_premium.value}
          changeValidation="required"
          validate={validate}
          onChange={addAnswer}>
          <option value="a">暂无商业险</option>
          <option value="b">{ins_premium_least}元以内</option>
          <option value="c">{ins_premium_least} - {ins_premium_up}元</option>
          <option value="d">{ins_premium_up}元以上</option>
        </Select>
      </SurveyForm>
    )
  }
}

// Fallback IE 10 以下不支持 __proto__
AnnualPremiumForm.childContextTypes = {
  form: React.PropTypes.object
}

export default AnnualPremiumForm
