import SurveyForm from 'ins/plan/views/forms/_survey_form.jsx'
import Select from 'ins/plan/views/forms/_select.jsx'

import getSubject from 'ins/plan/utils/_get_subject.js'

class LifeForm extends SurveyForm {
  constructor(props) {
    props.fields = ['family_duty']
    super(props)
  }

  render() {
    let {
      owner,
      gender,
      family_duty = {},
      addAnswer,
      validate
    } = this.props

    let is_valid = family_duty.error === null

    let subject = getSubject({
      owner: owner.value,
      gender: gender.value,
      is_que: false
    })

    let title = subject + '的收入会用于'

    return (
      <SurveyForm
        {...this.props}
        title="家庭责任"
        is_valid={is_valid}
        id="js_life_form"
        className="m-life-form"
        stage={4}>
        <Select
          name="family_duty"
          multiple={true}
          value={family_duty.value}
          title={title}
          changeValidation="required"
          validate={validate}
          className="family_duty"
          onChange={addAnswer}>
          <option value="older">照料父母</option>
          <option value="spouse">照顾配偶</option>
          <option value="child">抚养子女</option>
          <option value="loan">偿还贷款</option>
          <option value="clear">以上皆无</option>
        </Select>
      </SurveyForm>
    )
  }
}

// Fallback IE 10 以下不支持 __proto__
LifeForm.childContextTypes = {
  form: React.PropTypes.object
}

export default LifeForm
