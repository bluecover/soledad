import Dialog from 'ins/plan/views/_dialog.jsx'
import PlannerBubble from 'ins/plan/views/bubbles/_planner_bubble.jsx'

const res_p1 = function (props) {
  return (
    <div className="m-res-paragraph">
      <div className="hd">
        <p>{props.age.value} 岁的{props.gender.value}主要面临 3 大风险，相应地需要 3 种保险：</p>
      </div>
      <div className="bd">
        <ul className="m-ins-reclist">
          <li>
            <span className="title">意外风险：</span>
            <span className="desc">交通事故、摔伤烫伤等突发意外，轻则导致医药支出，重则造成残疾、身故。意外险专门应对此类风险。</span>
          </li>
          <li>
            <span className="title"> 重疾风险：</span>
            <span className="desc">重大疾病的巨额医药费，往往导致“一人生病全家致贫”。重疾险确诊即赔，可以极大缓解经济压力、帮助治病救人。</span>
          </li>
          <li>
            <span className="title"> 身故风险：</span>
            <span className="desc">一旦不幸身故，父母、子女可能会生活无依。寿险身故即赔，帮助我们更长久地守护家人。</span>
          </li>
        </ul>
      </div>
    </div>
  )
}

class FoundationRes extends Dialog {
  constructor(props) {
    super(props)

    this._paragraphs_show_rule = [0]
  }

  render() {
    let last_index = this.state.show_paragraphs_num
    let paragraphs = [
      <PlannerBubble
        key="1"
      >
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

export default FoundationRes
