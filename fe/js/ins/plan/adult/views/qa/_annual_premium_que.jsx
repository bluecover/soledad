import Dialog from 'ins/plan/views/_dialog.jsx'
import PlannerBubble from 'ins/plan/views/bubbles/_planner_bubble.jsx'
import ClickBubble from 'ins/plan/views/bubbles/_click_bubble.jsx'

class AnnualPremiumQue extends Dialog {
  constructor(props) {
    super(props)

    this._paragraphs_show_rule = [0, 1200, 1200]
  }

  render() {
    let {
      marriage,
      showForm,
      isCompleted
    } = this.props

    marriage = marriage.value

    let p1 = (
      <PlannerBubble
        key="0"
      >
        最后我们再看看保费，合理的保费规划让您保障、理财两不误。
      </PlannerBubble>
    )

    let subject = marriage === '未婚' ? '您负担的' : '您全家的'
    let p2 = (
      <PlannerBubble key="1" >
        {subject}商业保险，每年要交多少保费？
      </PlannerBubble>
    )

    let p3 = (
      <ClickBubble
        key="2"
        show_form='annual_premium_form'
        isCompleted={isCompleted}
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

export default AnnualPremiumQue
