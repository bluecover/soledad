import cookie from 'cookies-js'

$.ajaxSetup({
  beforeSend: function (xhr) {
    let token = cookie.get('csrf_token') || $('meta[name="x-csrf-token"]').attr('content')
    xhr.setRequestHeader('X-CSRFToken', token)
  }
})
