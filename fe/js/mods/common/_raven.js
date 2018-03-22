Raven.config('https://ebd7e0e6217640df8f392754bde678a5@guihua.com/raven/13').install()
$(document).ajaxError(function (event, jqXHR, ajaxSettings, thrownError) {
  function deparam(data) {
    try {
      var result = {}
      var pairs = data.split('&')
      for (var i = 0; i < pairs.length; i++) {
        var pair = pairs[i].split('=')
        result[decodeURIComponent(pair[0])] = decodeURIComponent(pair[1])
      }
      return result
    } catch (e) {
      return data + '#' + e.toString()
    }
  }

  Raven.captureMessage(
    thrownError || jqXHR.statusText,
    {
      extra: {
        type: ajaxSettings.type,
        url: ajaxSettings.url,
        data: ajaxSettings.data ? deparam(ajaxSettings.data) : null,
        status: jqXHR.status,
        error: thrownError || jqXHR.statusText,
        response: jqXHR.responseText.substring(0, 100)
      }
    }
  )
})
