import Dialog from 'ins/plan/views/_dialog.jsx'
import PlannerBubble from 'ins/plan/views/bubbles/_planner_bubble.jsx'
import ClickBubble from 'ins/plan/views/bubbles/_click_bubble.jsx'

import getSubject from 'ins/plan/utils/_get_subject.js'

class LifeQue extends Dialog {
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
        下面我们来说寿险。寿险身故即赔，作用是“身后留笔钱”，帮我们更长久地守护家人。
      </PlannerBubble>
    )

    let p2 = (
      <PlannerBubble
        key="1">
        {subject}肩负着哪些家庭责任呢？
      </PlannerBubble>
    )

    let p3 = (
      <ClickBubble
        key="2"
        show_form='life_form'
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

export default LifeQue
