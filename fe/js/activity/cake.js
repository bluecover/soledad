import Bake from './cake/_bake.js'
import Animate from 'utils/animate'
import setWX from './cake/_wx.js'

let $starterWow = $('.start-wrapper .wow')

$('body')
  .on('click', '.js-btn-start', ()=> {
    // 百度事件统计
    _hmt.push(['_trackEvent', 'cake', 'startGame'])

    Animate.out($starterWow)
    $('.js-btn-start').animate({'opacity': 0})
    $('.js-btn-rule').fadeIn('fast')
    animateGame()
  })
  .on('click', '.js-btn-restart', ()=> {
    Bake.restart()
  })

setInterval(()=> {
  $('.js-btn-start').addClass('shaking')
  setTimeout(()=> {
    $('.js-btn-start').removeClass('shaking')
  }, 200)
}, 1000)

// function animateStart() {
  // $('.js-btn-start').hide().fadeIn('fast')
  // Animate.run($starterWow)
// }

function animateGame() {
  setTimeout(function () {
    $('.start-wrapper').fadeOut('fast', function () {
      // $('.start-wrapper').hide()
      $('.game-wrapper').removeClass('hide')
      Animate.run($('.game-wrapper .wow'))
    })

    Bake.init()
  }, 100)
}

$(window).on('load', ()=> {
  $('.page-loading').remove()
  $('.cake-wrapper').removeClass('hide')
  $('.start-wrapper').hide()
  animateGame()
})

setWX()
