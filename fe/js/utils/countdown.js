module.exports = function (duration, onTick, onComplete) {
  var secondsLeft = Math.round(duration)
  var tick = function () {
    if (secondsLeft > 0) {
      onTick(secondsLeft)
      secondsLeft -= 1
    } else {
      clearInterval(interval)
      onComplete()
    }
  }

  var interval = setInterval(
    (function (self) {
      return function () { tick.call(self)}
    })(this),
    1000)

  tick.call(this)

  return {
    abort: function () {
      clearInterval(interval)
    },
    getRemainingTime: function () {
      return secondsLeft
    }
  }
}
