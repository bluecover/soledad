import SurveyForm from './_survey_form.jsx'
import Select from './_select.jsx'

class StartForm extends React.Component {
  constructor(props) {
    props.fields = ['marriage', 'owner', 'gender']
    super(props)
  }

  renderOwnerSelect() {
    let {
      marriage = {},
      owner = {},
      addAnswer,
      id,
      validate
    } = this.props

    let show_owner = owner.value === undefined || id === undefined
    let disabled_owner = marriage.value === '未婚'

    return show_owner ? (
      <Select
        name="owner"
        title="规划对象"
        value={owner.value}
        changeValidation="required"
        validate={validate}
        disabled={disabled_owner}
        onChange={addAnswer}
      >
        <option value="自己">自己</option>
        <option value="配偶">配偶</option>
      </Select>
    ) : null
  }

  renderMarriageSelect() {
    let {
      marriage = {},
      owner = {},
      addAnswer,
      id,
      validate
    } = this.props

    let show_marriage = owner.value !== '配偶' || id === undefined

    return show_marriage ? (
      <Select
        name="marriage"
        title="婚否"
        value={marriage.value}
        changeValidation="required"
        validate={validate}
        onChange={addAnswer}
      >
        <option value="未婚">未婚</option>
        <option value="已婚">已婚</option>
      </Select>
    ) : null
  }

  renderGenderSelect() {
    let {
      gender = {},
      owner = {},
      addAnswer,
      validate
    } = this.props

    let show_gender = owner.value !== undefined
    let gender_title = (owner.value === '自己' || owner.value === undefined) ? '您的性别'
                                                                             : `${owner.value}的性别`

    return show_gender ? (
      <Select
        className="m-select-gender"
        name="gender"
        title={gender_title}
        value={gender.value}
        changeValidation="required"
        validate={validate}
        onChange={addAnswer}
      >
        <option value="男性">
          <img src="{{{img/ins/plan/male_gray.png}}}" className="gray" alt="" />
          <img src="{{{img/ins/plan/male_white.png}}}" className="white" alt="" />
          <span className="desktop-element name">男</span>
        </option>
        <option value="女性">
          <img src="{{{img/ins/plan/female_gray.png}}}" className="gray" alt="" />
          <img src="{{{img/ins/plan/female_white.png}}}" className="white" alt="" />
          <span className="desktop-element name">女</span>
        </option>
      </Select>
    ) : null
  }

  render() {
    let {
      gender = {},
      marriage = {},
      owner = {}
    } = this.props

    let form_is_valid = gender.error === null &&
                        marriage.error === null &&
                        owner.error === null

    return (
      <SurveyForm
        {...this.props}
        title="基础信息"
        subtitle="请填写信息，以便理财师量身规划"
        id="js-start-form"
        className="m-start-form"
        is_valid={form_is_valid}
        stage={0}
      >
        {this.renderMarriageSelect()}
        {this.renderOwnerSelect()}
        {this.renderGenderSelect()}
      </SurveyForm>
    )
  }
}

// Fallback IE 10 以下不支持 __proto__
StartForm.childContextTypes = {
  form: React.PropTypes.object
}

export default StartForm
