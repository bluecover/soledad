var browser_update = "<div class='browser-update-wrapper' id='js_browser_update'><i class='iconfont icon-close'></i>你的浏览器过于陈旧，我们推荐你使用现代浏览器（<a href='http://www.firefox.com.cn/download/' target='_blank'>火狐</a>，<a href='http://down.tech.sina.com.cn/content/40975.html' target='_blank'>谷歌</a>，<a href='http://windows.microsoft.com/zh-cn/internet-explorer/ie-9-worldwide-languages' target='_blank'>IE9+</a>）浏览来获得更好的体验效果。</div>"
document.body.insertAdjacentHTML('afterend', browser_update)
var browser_wrapper = document.getElementById('js_browser_update')
var close = browser_wrapper.getElementsByTagName('i')[0]

browser_wrapper.style.display = 'block'
close.onclick = function() {
  browser_wrapper.style.display = 'none'
}
