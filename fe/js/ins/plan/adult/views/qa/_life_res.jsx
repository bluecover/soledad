import Dialog from 'ins/plan/views/_dialog.jsx'
import PlannerBubble from 'ins/plan/views/bubbles/_planner_bubble.jsx'
import ClickBubble from 'ins/plan/views/bubbles/_click_bubble.jsx'

import getSubject from 'ins/plan/utils/_get_subject.js'

const res_p1 = function (props) {
  let {
    owner,
    gender,
    marriage,
    family_duty,
    annual_revenue_personal,
    annual_revenue_family = {}
  } = props

  owner = owner.value
  gender = gender.value
  marriage = marriage.value
  family_duty = family_duty.value
  annual_revenue_family = Number(annual_revenue_family.value)
  annual_revenue_personal = Number(annual_revenue_personal.value)

  let subject = getSubject({
    owner,
    gender
  })

  let advice_1
  let revenue_rate = annual_revenue_personal / annual_revenue_family

  if (marriage === '未婚' || revenue_rate < 0.35) {
    advice_1 = <span>承担着重要家庭责任的</span>
  } else if (marriage === '已婚' && revenue_rate < 0.65) {
    advice_1 = <span>身为家庭经济支柱之一的</span>
  } else {
    advice_1 = <span>贡献了一大半家庭收入的</span>
  }

  let advice_2
  if (family_duty.length === 1 && family_duty.indexOf('clear') !== -1) {
    advice_2 = (
      <p>
        <span>目前{subject}没有肩负重大的家庭责任，所以暂不投保寿险也没有问题。</span>
        <span>定期寿险保费较低，日后随着家庭责任的增加，可以随时补投。</span>
      </p>
    )
  } else {
    advice_2 = (
      <p>
        {advice_1}家庭成员若不幸身故，全家的生活都可能陷入困境。因此对{subject}来说，<strong>寿险也是必需险种</strong>。
      </p>
    )
  }

  return (
    <div>
      {advice_2}
    </div>
  )
}

class LifeRes extends Dialog {
  constructor(props) {
    super(props)

    this._paragraphs_show_rule = [0, 1200, 1200]
  }

  render() {
    let {
      family_duty,
      showForm,
      isCompleted
    } = this.props

    family_duty = family_duty.value

    let last_index = this.state.show_paragraphs_num
    let paragraphs
    if (family_duty.length === 1 && family_duty.indexOf('clear') !== -1) {
      paragraphs = [
        <PlannerBubble key="1">
          {res_p1(this.props)}
        </PlannerBubble>
      ]
    } else {
      paragraphs = [
        <PlannerBubble key="1">
          {res_p1(this.props)}
        </PlannerBubble>,
        <PlannerBubble key="2">
          我们还需要进一步明确寿险保额，请您补充信息。
        </PlannerBubble>,
        <ClickBubble
          key="3"
          show_form='life_complement_form'
          isCompleted={isCompleted}
          showForm={showForm} />
      ]

      isCompleted ? last_index -= 1 : null
    }

    return (
      <div className="m-res">
        <div className="bd">
          {paragraphs.slice(0, last_index)}
        </div>
      </div>
    )
  }
}

export default LifeRes
