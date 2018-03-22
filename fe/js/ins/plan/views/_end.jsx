import Dialog from 'ins/plan/views/_dialog.jsx'
import PlannerBubble from 'ins/plan/views/bubbles/_planner_bubble.jsx'
import ClickBubble from 'ins/plan/views/bubbles/_click_bubble.jsx'

class EndQue extends Dialog {
  constructor(props) {
    super(props)

    this._paragraphs_show_rule = [0, 1200, 200]
  }

  render() {
    let {
      is_login
    } = this.props

    let p_4 = (
      <PlannerBubble key="4">
        <p>如有更多问题，欢迎随时咨询好规划专业理财师：</p>
        <div className="m-plan-weixin">
          <div className="hd">
            <img className="qrcode" src="{{{img/misc/qrcode.png}}}" alt="微信公众号"/>
          </div>
          <div className="bd">
            <p>好规划微信号: <strong>plan141</strong></p>
            <p className="tip">扫码关注后直接提问即可</p>
          </div>
        </div>
      </PlannerBubble>
    )

    let anchor
    let next = $.param({
      next: '/ins/plan/',
      dcm: 'guihua',
      dcs: 'ins_plan'
    })
    let mobile_url = `/accounts/login?${next}`
    if (is_login) {
      anchor = <a href="/ins/plan">查看完整规划书</a>
    } else {
      anchor = (
        <a
          className="js-g-login"
          href={mobile_url}
          data-url="/ins/plan/"
          data-dcm="guihua"
          data-dcs="ins_plan"
        >
          查看完整规划书
        </a>
      )
    }
    let p_3 = <ClickBubble key="2">{anchor}</ClickBubble>

    let p_1 = (
      <PlannerBubble
        key="1">
        <span>规划已经完成！请查看完成规划书。<br/></span>
        <span>规划书包含精选保险推荐、简明投保指南，供您进一步明确投保方案。<br/></span>
        <span>每支精选保险都由我和同事精心挑选、为您量身推荐。我们承诺保障为本、高质低价、中立推荐。</span>
      </PlannerBubble>
    )

    let paragraphs = [
      p_1,
      p_3,
      p_4
    ]

    let last_index = this.state.show_paragraphs_num

    return (
      <div className="m-que">
        <div className="bd">
          {paragraphs.slice(0, last_index)}
        </div>
      </div>
    )
  }
}

export default EndQue
