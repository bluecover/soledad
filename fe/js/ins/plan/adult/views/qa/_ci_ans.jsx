import UserBubble from 'ins/plan/views/bubbles/_user_bubble.jsx'

import getSubject from 'ins/plan/utils/_get_subject.js'

const CIAns = (props) => {
  let {
    gender,
    owner,
    has_social_security,
    has_complementary_medicine
  } = props

  gender = gender.value
  owner = owner.value
  has_social_security = has_social_security.value
  has_complementary_medicine = has_complementary_medicine.value

  let subject = getSubject({
    owner,
    gender,
    is_que: false
  })

  return (
    <UserBubble>
      {subject}{has_social_security}城镇社保/农村医保；{has_complementary_medicine}单位补充医疗保险。
    </UserBubble>
  )
}

export default CIAns
