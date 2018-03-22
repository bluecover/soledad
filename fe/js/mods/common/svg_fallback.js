var isSupportSvg = supportsSvg()

function supportsSvg() {
  var div = document.createElement('div')
  div.innerHTML = '<svg/>'
  return (div.firstChild && div.firstChild.namespaceURI) === 'http://www.w3.org/2000/svg'
}

if (!isSupportSvg) {
  $(window).load(function () {
    var $svgs = $('.svgicon')
    svgFallback($svgs)
  })
}

function svgFallback($svgs) {
  $svgs.each(function () {
    var img = new Image()

    $.each(this.attributes, function () {
      if (this.name === 'viewBox') {
        return
      }
      if (this.specified) {
        img.setAttribute(this.name, this.value)
      }
    })

    $(this).replaceWith(img)
  })
}
