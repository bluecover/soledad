$(window).on('scroll', function () {
  $('.js-fix-bar').each(function (index, el) {
    var scroll_top = $(window).scrollTop()
    var title_top = $('.js-title').eq(index).offset().top
    if (scroll_top > title_top) {
      $(el).removeClass('hide').css('top', $('.js-fix-bar').height() * index)
    } else {
      $(el).addClass('hide').css('top', 'auto')
    }
  })
})

if ($('.js-change-chart').length > 0) {
  draw_change()
}

if ($('.js-rent-chart').length > 0) {
  draw_rent()
}

if ($('.js-outlay-chart').length > 0) {
  draw_outlay()
}

if ($('.js-savings-chart').length > 0) {
  draw_savings()
}

function draw_change() {
  var change_data = $('.js-change-chart').data('arr')
  $('.js-change-chart').highcharts({
    chart: {
      type: 'column'
    },
    title: {
      text: ''
    },
    xAxis: {
      text: '',
      tickWidth: 0,
      labels: {
        enabled: false
      }
    },
    yAxis: {
      min: 0,
      title: {
        text: ''
      },
      gridLineWidth: 0,
      labels: {
        enabled: false
      },
      stackLabels: {
        style: {
          color: 'red'
        },
        enabled: true,
        formatter: function () {
          return 'mm'
        }
      }
    },
    tooltip: {
      enabled: false
    },
    plotOptions: {
      column: {
        dataLabels: {
          enabled: true,
          formatter: function () {
            return this.y + '%'
          }
        },
        pointWidth: 30
      },
      series: {
        events: {
          legendItemClick: function (event) {
            return false
          }
        }
      }
    },
    legend: {
      align: 'center',
      verticalAlign: 'bottom',
      itemStyle: {
        fontWeight: 'normal'
      }
    },
    credits: {
      enabled: false
    },
    series: [{
      name: '零钱包收益率',
      data: change_data[0],
      color: '#FDCD7A'
    }, {
      name: '活期存款收益率',
      data: change_data[1],
      color: '#80cbc4'
    }]
  })
}

function draw_savings() {
  var savings_arr = $('.js-savings-chart').data('arr')
  $('.js-savings-chart').highcharts({
    chart: {
      type: 'column'
    },
    title: {
      text: ''
    },
    credits: {
      enabled: false
    },
    xAxis: {
      categories: ['第一年', '第二年', '第三年', '第四年', '第五年']
    },
    yAxis: {
      min: 0,
      title: {
        text: ''
      },
      gridLineColor: '#D1D1D1',
      stackLabels: {
        enabled: true,
        style: {
          fontWeight: 'normal'
        },
        formatter: function () {
          return this.total + '元'
        }
      }
    },
    legend: {
      align: 'center',
      verticalAlign: 'bottom',
      itemStyle: {
        fontWeight: 'normal'
      }
    },
    tooltip: {
      followTouchMove: true,
      formatter: function () {
        var s = '<b>' + this.x + '</b><br/>'
        $.each(this.points, function () {
          s += this.series.name + ': ' + this.y + '元<br/>'
        })
        return s
      },
      shared: true
    },
    plotOptions: {
      column: {
        stacking: 'normal'
      },
      series: {
        events: {
          legendItemClick: function (event) {
            return false
          }
        }
      }
    },
    series: [{
      name: '本金',
      data: savings_arr[0],
      color: '#80cbc4'
    }, {
      name: '投资收益',
      data: savings_arr[1],
      color: '#FDCD7A'
    }]
  })
}

function draw_rent() {
  $('.js-rent-chart').highcharts({
    chart: {
      type: 'column'
    },
    title: {
      text: ''
    },
    credits: {
      enabled: false
    },
    xAxis: {
      categories: ['第一月', '第二月', '第三月', '第一月', '第二月', '第三月'],
      tickWidth: 0,
      plotLines: [{
        color: '#999',
        dashStyle: 'shortdash',
        width: 1,
        value: 2.5
      }]
    },
    yAxis: {
      min: 0,
      title: {
        text: ''
      },
      gridLineWidth: 0,
      labels: {
        enabled: false
      },
      tickWidth: 0
    },
    legend: {
      align: 'center',
      itemDistance: 15,
      verticalAlign: 'bottom',
      itemStyle: {
        fontWeight: 'normal'
      }
    },
    tooltip: {
      enabled: false
    },
    plotOptions: {
      column: {
        stacking: 'normal'
      },
      series: {
        events: {
          legendItemClick: function (event) {
            return false
          }
        }
      }
    },
    series: [{
      name: '自选到期日收益',
      data: [3, 2, 1, 0, 0, 0],
      color: '#FDCD7A'
    }, {
      name: '活期存款收益',
      data: [0, 0, 0, 0.6, 0.4, 0.2],
      color: '#9ED8AD'
    }, {
      name: '房租',
      data: [5, 5, 5, 5, 5, 5],
      color: '#80cbc4'
    }]
  })
}

function draw_outlay() {
  var monthly_payment = $('.js-outlay-chart').data('arr')
  $('.js-outlay-chart').highcharts({
    chart: {
      type: 'bar'
    },
    title: {
      text: ''
    },
    xAxis: {
      text: '',
      tickWidth: 0,
      labels: {
        enabled: false
      }
    },
    yAxis: {
      min: 0,
      title: {
        text: ''
      },
      gridLineWidth: 0,
      labels: {
        enabled: false
      }
    },
    tooltip: {
      enabled: false
    },
    plotOptions: {
      bar: {
        dataLabels: {
          enabled: true,
          formatter: function () {
            return this.y + '元/月'
          }
        }
      },
      series: {
        events: {
          legendItemClick: function (event) {
            return false
          }
        }
      }
    },
    legend: {
      align: 'center',
      verticalAlign: 'bottom',
      itemStyle: {
        fontWeight: 'normal'
      }
    },
    credits: {
      enabled: false
    },
    series: [{
      name: '自选到期日收益',
      data: monthly_payment[1],
      color: '#FDCD7A'
    }, {
      name: '活期存款收益',
      data: monthly_payment[0],
      color: '#80cbc4'
    }]
  })
}
