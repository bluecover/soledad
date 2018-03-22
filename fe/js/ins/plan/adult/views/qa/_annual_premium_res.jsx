import Dialog from 'ins/plan/views/_dialog.jsx'
import PlannerBubble from 'ins/plan/views/bubbles/_planner_bubble.jsx'

import convertNumber from 'ins/plan/utils/_convert_number'

const res_p1 = function (props) {
  let {
    marriage,
    annual_premium,
    ins_premium_least,
    ins_premium_up
  } = props

  marriage = marriage.value
  annual_premium = annual_premium.value
  ins_premium_up = convertNumber(ins_premium_up)
  ins_premium_least = convertNumber(ins_premium_least)

  let subject = marriage === '未婚' ? '您' : '您与家人'
  let subject_2 = marriage === '未婚' ? '您' : '您家'

  let advice
  let advice_1
  if (annual_premium === 'c') {
    advice_1 = <p>现在{subject}的保费适中，随着家庭情况的变化，<strong>请持续优化配置</strong>、补充保障。</p>
  } else if (annual_premium === 'd') {
    advice_1 = <p>现在{subject}的保费较高，过大的保费压力可能影响其他理财需求，<strong>建议检查现有保险</strong>，适当选择消费型产品。</p>
  } else {
    advice_1 = <p>现在{subject}的保障较少，<strong>建议尽快补充。</strong></p>
  }

  advice = (
    <div className="m-res-paragraph">
      <p>
        <span>全家保费支出占年收入的 5% 左右比较适宜，不要超过 7%；</span>
        <span>
          对{subject_2}来说，相当于<strong>每年 {ins_premium_least} - {ins_premium_up}元保费</strong>。
        </span>
      </p>
      {advice_1}
    </div>
  )

  return advice
}

class AnnualPremiumRes extends Dialog {
  constructor(props) {
    super(props)

    this._paragraphs_show_rule = [0, 1200]
  }

  render() {
    let last_index = this.state.show_paragraphs_num
    let paragraphs = [
      <PlannerBubble key="1">
        {res_p1(this.props)}
      </PlannerBubble>,
      <PlannerBubble key="2">
        <p>
          <span>保险配置不必一步到位，如果保费预算有限，可以先选择较短期限的保险，等将来收入增长了，再补投更理想的保险。</span>
          <span>也建议您每年更新保险规划、检查全家的保障。</span>
        </p>
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

export default AnnualPremiumRes
