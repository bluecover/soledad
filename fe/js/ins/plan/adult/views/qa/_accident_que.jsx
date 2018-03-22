import Dialog from 'ins/plan/views/_dialog.jsx'
import PlannerBubble from 'ins/plan/views/bubbles/_planner_bubble.jsx'
import ClickBubble from 'ins/plan/views/bubbles/_click_bubble.jsx'

class AccidentQue extends Dialog {
  constructor(props) {
    super(props)

    this._paragraphs_show_rule = [0, 1200, 1200]
  }

  render() {
    let {
      showForm,
      isCompleted
    } = this.props

    let p1 = (
      <PlannerBubble
        key="0"
      >
        我们从意外险说起吧。<strong>意外险是必备险种</strong>，其中最需保障的项目是：意外医疗、意外残疾、意外身故。
      </PlannerBubble>
    )

    let p2 = <PlannerBubble key="1">请补充家庭信息。</PlannerBubble>

    let p3 = (
      <ClickBubble
        key="2"
        show_form='accident_form'
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

export default AccidentQue
