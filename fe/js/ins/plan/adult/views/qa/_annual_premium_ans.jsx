import UserBubble from 'ins/plan/views/bubbles/_user_bubble.jsx'

import convertNumber from 'ins/plan/utils/_convert_number'

const AccidentAns = (props) => {
  let {
    annual_premium,
    ins_premium_up,
    ins_premium_least
  } = props

  ins_premium_up = convertNumber(ins_premium_up)
  ins_premium_least = convertNumber(ins_premium_least)

  const ANNUAL_PREMIUM_VALUE = {
    a: '暂无商业险',
    b: `${ins_premium_least}元以内`,
    c: `${ins_premium_least} - ${ins_premium_up}元`,
    d: `${ins_premium_up}元以上`
  }

  let text
  if (!annual_premium || annual_premium.value === 'a') {
    text = '暂无商业险。'
  } else {
    text = `现在商业险保费是每年 ${ANNUAL_PREMIUM_VALUE[annual_premium.value]}。`
  }

  return (
    <UserBubble>
      <p>{text}</p>
    </UserBubble>
  )
}

export default AccidentAns
