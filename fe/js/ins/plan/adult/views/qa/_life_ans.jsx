import UserBubble from 'ins/plan/views/bubbles/_user_bubble.jsx'

import { FAMILY_DUTY } from 'ins/plan/_constant'
import getSubject from 'ins/plan/utils/_get_subject.js'

const LifeAns = (props) => {
  let {
    gender,
    owner,
    family_duty
  } = props

  gender = gender.value
  owner = owner.value
  family_duty = family_duty.value

  let subject = getSubject({
    owner,
    gender,
    is_que: false
  })

  family_duty = family_duty.map((duty) => {
    if (duty === 'clear') {
      return duty
    }

    return FAMILY_DUTY[duty]
  })

  let duty = family_duty.join('、')
  let ans
  if (family_duty.length === 1 && family_duty.indexOf('clear') !== -1) {
    ans = <p>{subject}没有负担主要的家庭经济责任。</p>
  } else {
    ans = <p>{subject}的收入会用于{duty}。</p>
  }

  return (
    <UserBubble>
      {ans}
    </UserBubble>
  )
}

export default LifeAns
