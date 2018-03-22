import Dialog from 'ins/plan/views/_dialog.jsx'
import PlannerBubble from 'ins/plan/views/bubbles/_planner_bubble.jsx'
import ClickBubble from 'ins/plan/views/bubbles/_click_bubble.jsx'
import { PLANNER_NAME } from 'ins/plan/_constant.js'

class StartQue extends Dialog {
  constructor(props) {
    super(props)

    this._paragraphs_show_rule = [0, 1200, 1200, 1200]
  }

  render() {
    let {
      id,
      showForm,
      isCompleted
    } = this.props

    let que_text = id === undefined ? '请问您要为谁做保险规划？' : '首先，请问您几项基础信息。'

    let p1 = (
      <PlannerBubble key="1">您好！我是好规划 CFP {PLANNER_NAME}，很高兴为您服务。</PlannerBubble>
    )

    let p2 = (
      <PlannerBubble
        key="0"
        loading_timeout={1000}>
        <span>接下来的 5 分钟，我将为您量身定制一份保险规划。</span>
        <span>
          您只需按提示填写少量信息即可（规划中的任何信息，我们都会多层加密且绝不外泄，请放心规划）。
        </span>
      </PlannerBubble>
    )

    let paragraphs = [
      p1,
      p2,
      <PlannerBubble key="2">{que_text}</PlannerBubble>,
      <ClickBubble
        key="3"
        show_form="start_form"
        forms_container="#ins_start_forms"
        showForm={showForm}
      />
    ]

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

export default StartQue
