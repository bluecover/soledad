function getSubject({ owner, gender, is_que = true }) {
  if (owner === '自己') {
    if (is_que) {
      return '您'
    } else {
      return '我'
    }
  } else {
    if (is_que) {
      return gender === '男性' ? '您先生' : '您太太'
    } else {
      return gender === '男性' ? '我先生' : '我太太'
    }
  }
}

export default getSubject
