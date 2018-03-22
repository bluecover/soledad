// 请求 svg sprite 文件
try {
  var ajax = new XMLHttpRequest()
  ajax.open('GET', '{{{img/common_svg_icon/common_icon.svg}}}', true)
  ajax.send()
  ajax.onload = function (e) {
    if (ajax.status === '404') {
      return
    }
    var div = document.createElement('div')
    div.innerHTML = ajax.responseText
    document.body.insertBefore(div, document.body.childNodes[0])
  }
} catch (e) {}
