var canvasEl = document.createElement('canvas')
if (canvasEl.getContext) {
  require('lib/circle_progress')
  $('.progress')
    .circleProgress({
      value: $('.js-rate').data('rate'),
      startAngle: -Math.PI / 2,
      size: 90,
      thickness: 2,
      fill: {
        gradient: ['#fff']
      }
    })
    .on('circle-animation-progress', function (event, progress, stepValue) {
      $('.js-rate').text(parseInt(Math.round(100 * stepValue), 10))
    })
}
