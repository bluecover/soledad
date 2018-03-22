function getScrollBottom() {
  let $win = $(window)
  let $doc = $(document)

  return $doc.height() - $win.scrollTop() - $win.height()
}

export default getScrollBottom
