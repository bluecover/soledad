import Dialog from 'ins/plan/views/_dialog.jsx'
import PlannerBubble from 'ins/plan/views/bubbles/_planner_bubble.jsx'

import getSubject from 'ins/plan/utils/_get_subject.js'

const res_p1 = function (props) {
  let {
    owner,
    gender,
    asset,
    life_period,
    life_coverage,
    annual_revenue_family = {}
  } = props

  owner = owner.value
  gender = gender.value
  asset = Number(asset.value)
  annual_revenue_family = Number(annual_revenue_family.value)

  let subject = getSubject({
    owner,
    gender
  })

  let duty_total = life_coverage + asset
  let asset_gap = life_coverage

  let advice_1_1
  if (asset_gap > (annual_revenue_family * 15)) {
    advice_1_1 = '不过，以上保额可能导致保费负担过重，建议适当压缩资金缺口的金额。'
  }

  let advice_1
  if (asset_gap > 0) {
    advice_1 = (
      <p>
        若不幸身故，{subject}的家庭经济责任（约 {duty_total} 万元）减去现有金融资产，家庭财务将出现至少 {asset_gap} 万元的资金缺口，因此<strong>寿险保额应为 {asset_gap} 万元</strong>。{advice_1_1}
      </p>
    )
  }

  let advice_2
  advice_2 = (
    <p>
      <span>上述家庭责任主要集中在 60 岁以前，因此建议<strong>投保 {life_period} 年期寿险</strong>。</span>
      <span>  另外，消费型寿险性价比最高，建议选择。</span>
    </p>
  )

  let advice
  if (asset_gap <= 0) {
    advice = (
      <div>
        <p>
          {subject}的家庭经济责任共计约 {duty_total} 万元，若不幸身故，现有金融资产也足够填补财务缺口，所以{subject}可以暂不投保寿险。
        </p>
        <p>
          未来，{subject}如果肩负了更多的家庭责任，请记得回来重新规划寿险的投保方案。
        </p>
      </div>
    )
  } else {
    advice = (
      <div>
        {advice_1}
        {advice_2}
        <p>稍后生成的完整规划书中，将推荐具体产品，您可以随时查阅。</p>
      </div>
    )
  }

  return advice
}

class LifeComplementRes extends Dialog {
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

export default LifeComplementRes
