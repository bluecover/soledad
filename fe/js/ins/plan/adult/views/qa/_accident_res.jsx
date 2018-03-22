import Dialog from 'ins/plan/views/_dialog.jsx'
import PlannerBubble from 'ins/plan/views/bubbles/_planner_bubble.jsx'

import getSubject from 'ins/plan/utils/_get_subject.js'

const res_p1 = function (props) {
  let {
    owner,
    gender,
    accident_coverage
  } = props

  owner = owner.value
  gender = gender.value

  let subject = getSubject({
    owner,
    gender
  })

  return (
    <div>
      <p>
        <span>
          根据所在地物价估算，<strong>{subject}的意外险保额至少需要 {accident_coverage} 万元</strong>；
        </span>
        <span>如果考虑收入损失，保额可以上浮1至2年的个人年收入。</span>
      </p>
      <p>意外险保费不随年龄、健康状态变化，性价比最高的是：<strong>消费型、1 年期的意外险</strong>，是性价比最高的选择。</p>
      <p>稍后生成的完整规划书中，将推荐具体产品，您可以随时查阅。</p>
    </div>
  )
}

const res_p2 = (props) => {
  let advice_ins_obj

  let {
    annual_revenue_family,
    annual_revenue_personal,
    owner,
    gender
  } = props

  owner = owner.value
  gender = gender.value
  annual_revenue_personal = annual_revenue_personal.value
  annual_revenue_family = annual_revenue_family.value

  let subject = getSubject({
    owner,
    gender
  })

  annual_revenue_family = Number(annual_revenue_family)
  annual_revenue_personal = Number(annual_revenue_personal)
  let revenue_rate = annual_revenue_personal / annual_revenue_family

  if (revenue_rate <= 0.35) {
    advice_ins_obj = <span>{subject}贡献的家庭收入较少，应优先为收入更高的一方投保，</span>
  } else if (revenue_rate <= 0.65) {
    advice_ins_obj = <span>{subject}是家庭的经济支柱之一，应先于老人孩子投保，</span>
  } else {
    advice_ins_obj = <span>{subject}贡献了大半的家庭收入，应优先投保，</span>
  }

  return (
    <p>另外，{advice_ins_obj}以防收入中断后全家生活陷入困境。</p>
  )
}

class AccidentRes extends Dialog {
  constructor(props) {
    super(props)

    if (props.marriage.value === '已婚') {
      this._paragraphs_show_rule = [0, 1200]
    } else {
      this._paragraphs_show_rule = [0]
    }
  }

  render() {
    let {
      marriage
    } = this.props

    marriage = marriage.value

    let last_index = this.state.show_paragraphs_num
    let paragraphs
    if (marriage === '已婚') {
      paragraphs = [
        <PlannerBubble key="1">
          {res_p1(this.props)}
        </PlannerBubble>,
        <PlannerBubble key="2">
          {res_p2(this.props)}
        </PlannerBubble>
      ]
    } else {
      paragraphs = [
        <PlannerBubble key="1">
          {res_p1(this.props)}
        </PlannerBubble>
      ]

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

export default AccidentRes
