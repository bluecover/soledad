import Dialog from 'ins/plan/views/_dialog.jsx'
import PlannerBubble from 'ins/plan/views/bubbles/_planner_bubble.jsx'
import ClickBubble from 'ins/plan/views/bubbles/_click_bubble.jsx'

import getSubject from 'ins/plan/utils/_get_subject.js'

class FoundationQue extends Dialog {
  constructor(props) {
    super(props)

    this._paragraphs_show_rule = [0, 1200]
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
      <PlannerBubble key="1">
        好的，请允许我了解一下{subject}的基本情况。
      </PlannerBubble>
    )

    let p2 = (
      <ClickBubble
        key="2"
        show_form='foundation_form'
        showForm={showForm} />
    )

    let paragraphs = [p1, p2]

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

export default FoundationQue
