import 'fullpage.js'
import WaterCircle from 'mods/_waterCircle.jsx'
import WXModal from 'mods/modal/modal_wx'

function animate(sectionIndex) {
  sectionIndex = sectionIndex - 1
  let eles = $('.section:eq(' + sectionIndex + ')').find('.wow').addClass('animated')

  eles.map((index, item) => {
    let delay = $(item).data('delay') || 0
    setTimeout(() => {
      let cls = $(item).data('animate')
      $(item).addClass(cls).css({visibility: 'visible'})
    }, delay)
  })

  let others = $('.section').not(':eq(' + sectionIndex + ')').find('.wow')
  others.map((index, item) => {
    let cls = $(item).data('animate')
    $(item).removeClass(cls).css({visibility: 'hidden'})
  })
}

$('#fullpage').removeClass('hide').fullpage({
  scrollingSpeed: 600,
  sectionsColor: ['#ff625c', '#dfa834', '#4fd6ff', '#4f68bd'],
  verticalCentered: false,
  fixedElements: '.btn-music',
  afterLoad: (anchorLink, index) => {
    animate(index)

    switch (index) {
      case 2:
        let savings = {
          saving_amount: 50000,
          rate: 0.9
        }
        setTimeout(()=>{
          ReactDOM.render(<WaterCircle data={savings} />, document.getElementById('savings'))
        }, 500)
        break
      default:
        $('#savings').empty()
    }
  }
})

$('body').on('click', '.js-wechat', e => {
  WXModal.show()
}).on('click', '.btn-music', function () {
  $(this).toggleClass('off')
  if ($(this).hasClass('off')) {
    $(this).find('audio')[0].pause()
  } else {
    $(this).find('audio')[0].play()
  }
})

$('.page-loading').remove()
$('.btn-music').find('audio')[0].play()

// wechat share
var config = $('#wx_config').data('val')
var url = window.location.href
var desc = {
  title: '一岁啦！百元周年礼包限时赠送中',
  link: url,
  imgUrl: 'https://dn-ghimg.qbox.me/400m.png'
}

wx.config(config)
wx.ready(function () {
  wx.onMenuShareAppMessage(desc)
  wx.onMenuShareTimeline(desc)
  wx.onMenuShareQQ(desc)
})
