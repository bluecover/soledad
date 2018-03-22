import Dialog from 'ins/plan/views/_dialog.jsx'
import PlannerBubble from 'ins/plan/views/bubbles/_planner_bubble.jsx'
import ClickBubble from 'ins/plan/views/bubbles/_click_bubble.jsx'

import getSubject from 'ins/plan/utils/_get_subject.js'

class CIQue extends Dialog {
  constructor(props) {
    super(props)

    this._paragraphs_show_rule = [0, 1200, 1200]
  }

  render() {
    let {
      owner,
      gender,
      showForm,
      isCompleted
    } = this.props

    owner = owner.value
    gender = gender.value

    let subject = getSubject({
      owner,
      gender
    })

    let p1 = (
      <PlannerBubble
        key="0"
      >
        <span>接下来，<strong>重疾险也是必备险种</strong>。</span>
        <span>它确诊即赔，而且不限制这笔钱的用途，是防止“因病返贫”的最重要手段。</span>
      </PlannerBubble>
    )

    let p2 = (
      <PlannerBubble
        key="1" >
        {subject}的保障现状是？
      </PlannerBubble>
    )

    let p3 = (
      <ClickBubble
        key="2"
        show_form='ci_form'
        showForm={showForm} />
    )

    let paragraphs = [p1, p2, p3]

    // 如果当前回答已完成，则不显示点击回答气泡
    let last_index = this.state.show_paragraphs_num
    isCompleted ? last_index -= 1 : null

    return (
      <div className="m-que">
        <div className="bd">
          {paragraphs.slice(0, last_index)}
        </div>
      </div>
    )
  }
}

export default CIQue
