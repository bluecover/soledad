import { DUTY_FIELDS } from 'ins/plan/_constant'
import SurveyForm from 'ins/plan/views/forms/_survey_form.jsx'
import { InputGroup, Input } from 'ins/plan/views/forms/_input.jsx'
import { older_duty, spouse_duty, child_duty, loan_duty } from './_life_complement_controls.jsx'

import getSubject from 'ins/plan/utils/_get_subject.js'

const DUTIES = {
  'older': older_duty,
  'spouse': spouse_duty,
  'child': child_duty,
  'loan': loan_duty
}

class LifeComplementForm extends SurveyForm {
  constructor(props) {
    // 根据家庭责任选项答案配置相应 inputs 内容
    let fields = []
    props.family_duty.value.forEach((value) => {
      fields = fields.concat(DUTY_FIELDS[value])
    })
    fields.push('asset')

    props.fields = fields
    super(props)

    this._fields = fields
  }

  render() {
    let {
      owner,
      gender,
      marriage,
      family_duty,
      asset = {},
      addAnswer,
      validate
    } = this.props

    let form_is_valid = false
    form_is_valid = this._fields.every((field_name) => {
      let field = this.props[field_name]
      return field && (field.error === null)
    })

    let subject = getSubject({
      owner: owner.value,
      gender: gender.value
    })

    let duty_inputs = family_duty.value.map((duty) => {
      return DUTIES[duty] && DUTIES[duty](this.props)
    })

    let tip_1 = (
      <span>请估算{subject}的家庭责任</span>
    )
    let tip_2
    if (marriage.value === '已婚') {
      tip_2 = <span>夫妻共同责任，只考虑其中一方负担的部分</span>
    }
    let subtitle = (
      <h4>
        {tip_1}
        {tip_2}
      </h4>
    )

    return (
      <SurveyForm
        {...this.props}
        title="家庭责任"
        subtitle={subtitle}
        is_valid={form_is_valid}
        id="js_life_complement_form"
        className="m-life-complement-form"
        stage={5}>
        {duty_inputs}
        <InputGroup
          title={marriage.value === '已婚' ? '家庭金融资产' : '个人金融资产'}>
          <Input
            className="asset"
            name="asset"
            unit="万元"
            value={asset.value}
            error={asset.error}
            changeValidation="required|number_0_1000"
            blurValidation="required|number_0_1000"
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
LifeComplementForm.childContextTypes = {
  form: React.PropTypes.object
}

export default LifeComplementForm
