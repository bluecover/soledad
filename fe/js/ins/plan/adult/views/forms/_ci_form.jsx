import SurveyForm from 'ins/plan/views/forms/_survey_form.jsx'
import Select from 'ins/plan/views/forms/_select.jsx'

class CIForm extends SurveyForm {
  constructor(props) {
    props.fields = ['has_social_security', 'has_complementary_medicine']
    super(props)
  }

  render() {
    let {
      has_social_security = {},
      has_complementary_medicine = {},
      addAnswer,
      validate
    } = this.props

    let form_is_valid = has_social_security.error === null &&
                        has_complementary_medicine.error === null

    return (
      <SurveyForm
        {...this.props}
        title="保障现状"
        is_valid={form_is_valid}
        id="js-ci-form"
        className="m-ci-form"
        stage={3}>
        <Select
          name="has_social_security"
          title="城镇社保/农村医保"
          value={has_social_security.value}
          changeValidation="required"
          validate={validate}
          onChange={addAnswer}>
          <option value="有">有</option>
          <option value="无">无</option>
        </Select>

        <Select
          name="has_complementary_medicine"
          title="单位补充医疗险"
          value={has_complementary_medicine.value}
          changeValidation="required"
          validate={validate}
          onChange={addAnswer}>
          <option value="有">有</option>
          <option value="无">无</option>
        </Select>
      </SurveyForm>
    )
  }
}

// Fallback IE 10 以下不支持 __proto__
CIForm.childContextTypes = {
  form: React.PropTypes.object
}

export default CIForm
