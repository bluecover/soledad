var countdown_num = $('.js-countdown-num')

var jumptimer = setInterval(function () {
  var temp_num = parseInt(countdown_num.html(), 10)
  temp_num--
  countdown_num.html(temp_num)
  if (temp_num <= 0) {
    clearInterval(jumptimer)
    window.location.href = '/'
  }
}, 1000)
