import SurveyForm from 'ins/plan/views/forms/_survey_form.jsx'
import { InputGroup, Input } from 'ins/plan/views/forms/_input.jsx'

import getSubject from 'ins/plan/utils/_get_subject.js'

class FoundationForm extends SurveyForm {
  constructor(props) {
    props.fields = ['age']
    super(props)
  }

  render() {
    let {
      addAnswer,
      age = {},
      gender = {},
      owner = {},
      validate
    } = this.props

    let form_is_valid = age.error === null

    let subject = getSubject({
      owner: owner.value,
      gender: gender.value,
      is_que: false
    })

    let title = subject + '的年龄'

    return (
      <SurveyForm
        {...this.props}
        title="基础信息"
        is_valid={form_is_valid}
        id="js-foundation-form"
        className="m-foundation-form"
        stage={1}>
        <InputGroup
          title={title}>
          <Input
            className="age"
            name="age"
            unit="岁"
            value={age.value}
            error={age.error}
            changeValidation="required|positive_integer"
            blurValidation="required|positive_integer|child|older"
            pattern="[0-9]*"
            validate={validate}
            onChange={addAnswer}>
          </Input>
        </InputGroup>
      </SurveyForm>
    )
  }
}

// Fallback IE 10 以下不支持 __proto__
FoundationForm.childContextTypes = {
  form: React.PropTypes.object
}

export default FoundationForm
