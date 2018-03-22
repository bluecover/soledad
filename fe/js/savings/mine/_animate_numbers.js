$.fn.animateNumbers = function (stop, commas, duration, ease) {
  return this.each(function () {
    var $this = $(this)
    var start = parseInt($this.text().replace(/,/g, ''), 10)
    commas = (commas === undefined) ? true : commas
    $({
      value: start
    }).animate({
      value: stop
    }, {
      duration: duration === undefined ? 1000 : duration,
      easing: ease === undefined ? 'swing' : ease,
      step: function () {
        $this.text(Math.floor(this.value))
        if (commas) {
          $this.text($this.text().replace(/(\d)(?=(\d\d\d)+(?!\d))/g, '$1,'))
        }
      },
      complete: function () {
        if (parseInt($this.text(), 10) !== stop) {
          $this.text(stop)
          if (commas) {
            $this.text($this.text().replace(/(\d)(?=(\d\d\d)+(?!\d))/g, '$1,'))
          }
        }
      }
    })
  })
}
