import UserBubble from 'ins/plan/views/bubbles/_user_bubble.jsx'

import getSubject from 'ins/plan/utils/_get_subject.js'

const StartAns = (props) => {
  let {
    gender,
    marriage,
    owner
  } = props

  let subject = owner.value === '自己' ? '自己' : getSubject({
    owner: owner.value,
    gender: gender.value,
    is_que: false
  })
  let owner_text = '我想为' + subject + '做规划。'

  gender = gender.value === '男性' ? '男' : '女'
  let ending = `我目前${marriage.value}，性别${gender}。`

  return (
    <div className="bd">
      <UserBubble>
        {owner_text}
        {owner.value === '自己' ? ending : null}
      </UserBubble>
    </div>
  )
}

export default StartAns
