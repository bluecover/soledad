import Dialog from 'ins/plan/views/_dialog.jsx'
import PlannerBubble from 'ins/plan/views/bubbles/_planner_bubble.jsx'

import getSubject from 'ins/plan/utils/_get_subject.js'

const res_p1 = function (props) {
  let {
    owner,
    gender,
    ci_period,
    ci_coverage,
    ci_coverage_with_social_security,
    has_social_security,
    annual_revenue_personal
  } = props

  owner = owner.value
  gender = gender.value
  has_social_security = has_social_security.value
  annual_revenue_personal = annual_revenue_personal.value

  let subject = getSubject({
    owner,
    gender
  })

  annual_revenue_personal = Number(annual_revenue_personal)

  let advice_1
  let advice_2
  if (has_social_security === '无') {
    advice_1 = (
      <p>首先，建议{subject}<strong>尽快参投社保</strong>，获得最基础、性价比最高的健康保障。</p>
    )
    advice_2 = (
      <p>
        <span>综合考虑收入与保障现状，</span>
        <span><strong>{subject}至少需要 {ci_coverage} 万元重疾险保额</strong>；</span>
        <span>如果可以尽快参投社保，仍需要至少 {ci_coverage_with_social_security} 万元保额。</span>
        <span>请对照现有保险，酌情增补。</span>
      </p>
    )
  } else {
    advice_2 = (
      <p>
        <span>综合考虑保障现状与家庭收入，</span>
        <span><strong>{subject}至少需要 {ci_coverage} 万元重疾险保额</strong>。</span>
        <span>请对照现有保险，酌情增补。</span>
      </p>
    )
  }

  let advice_3 = (
    <p>
      根据{subject}的年龄，推荐投保<strong> {ci_period} 年期的消费型重疾险</strong>，性价比最高。
    </p>
  )

  return (
    <div>
      {advice_1}
      {advice_2}
      {advice_3}
      <p>稍后生成的完整规划书中，将推荐具体产品，您可以随时查阅。</p>
    </div>
  )
}

class CIRes extends Dialog {
  constructor(props) {
    super(props)

    this._paragraphs_show_rule = [0]
  }

  render() {
    let last_index = this.state.show_paragraphs_num
    let paragraphs = [
      <PlannerBubble key="1">
        {res_p1(this.props)}
      </PlannerBubble>
    ]

    return (
      <div className="m-res">
        <div className="bd">
          {paragraphs.slice(0, last_index)}
        </div>
      </div>
    )
  }
}

export default CIRes
