import UserBubble from 'ins/plan/views/bubbles/_user_bubble.jsx'

import getSubject from 'ins/plan/utils/_get_subject.js'

const FoundationAns = (props) => {
  let { gender, owner, age } = props

  let subject = getSubject({
    owner: owner.value,
    gender: gender.value,
    is_que: false
  })

  return (
    <UserBubble>
      {subject}现在 {age.value} 岁。
    </UserBubble>
  )
}

export default FoundationAns
