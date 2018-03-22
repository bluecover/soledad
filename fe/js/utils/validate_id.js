module.exports = function (card_num) {
  var year = card_num.substring(6, 10)
  var month = card_num.substring(10, 12)
  var day = card_num.substring(12, 14)
  var birthday = new Date(year, parseFloat(month) - 1, parseFloat(day))

  if (birthday.getFullYear() !== parseFloat(year) ||
      birthday.getMonth() !== parseFloat(month) - 1 ||
      birthday.getDate() !== parseFloat(day)) {
    return false
  }

  var Wi = [ 7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2, 1 ]
  var Y = [ 1, 0, 10, 9, 8, 7, 6, 5, 4, 3, 2 ]

  var sum = 0
  var _cardNo = card_num.split('')

  if (_cardNo[17].toLowerCase() === 'x') {
    _cardNo[17] = 10
  }
  for (var i = 0; i < 17; i++) {
    sum += Wi[i] * _cardNo[i]
  }
  var mod = sum % 11

  if (_cardNo[17] !== Y[mod]) {
    return false
  }
  return true
}
