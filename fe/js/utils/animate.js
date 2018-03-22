let Animate = {}

Animate.run = function ($eles) {
  $eles.map((index, item) => {
    let $item = $(item)
    let delay = $item.data('delay') || 0
    let duration = $item.data('duration') || null
    let cls = $item.data('animate')

    setTimeout(()=> {
      duration ? $item.css({animationDuration: duration}) : null
      $item.addClass(cls).css({visibility: 'visible'})
    }, delay)
  })
}

Animate.out = function ($eles) {
  $eles.map((index, item) => {
    let $item = $(item)
    let delay = $item.data('out-delay') || 0
    // let duration = $item.data('duration') || null
    let cls = $item.data('animate')

    setTimeout(()=> {
      let out = cls.replace('In', 'Out').replace('Down', 'Up')
      $(item).removeClass(cls).addClass(out + ' animated')
    }, delay)
  })
}

Animate.cancel = function ($eles) {
  $eles.map((index, item) => {
    let $item = $(item)
    let cls = $item.data('animate')
    let out = cls.replace('In', 'Out').replace('Down', 'Up')

    $item.removeClass(cls)
      .removeClass('animated wow ' + out)
      .css({
        visibility: '',
        animationDelay: '',
        animationDuration: ''
      })
  })
}

export default Animate
