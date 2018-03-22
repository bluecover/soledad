// var time = ['25-29', '30-59', '60－89', '90-119', '120-149', '150-179']
var profit = ['1.64', '1.67', '1.75', '1.81', '1.92', '2.00']

$('.js-chart-box').highcharts({
  chart: {
    type: 'column',
    backgroundColor: '#ffb74d',
    events: {
      load: function () {
        var index = this.series[0].points[5]
        this.tooltip.refresh(index)
      }
    }
  },
  title: {
    text: '享最高7.3%年化收益率',
    align: 'left',
    x: 45,
    y: 50,
    style: {
      color: '#fff',
      fontSize: '16px'
    }
  },
  credits: {
    enabled: false
  },
  xAxis: {
    lineColor: '#F9DCAB',
    categories: [
      '25-29天',
      '30-59天',
      '60-89天',
      '90-119天',
      '120-149天',
      '150-179天'
    ],
    tickWidth: 0,
    labels: {
      align: 'center',
      style: {
        fontSize: '10px',
        color: '#6e4c40'
      }
    },
    align: 'left'
  },
  yAxis: {
    min: 5,
    max: 10,
    gridLineWidth: 0,
    lineWidth: 1,
    lineColor: '#F9DCAB',
    labels: {
      enabled: false
    },
    title: {
      align: 'high',
      text: '预期年收益率',
      style: {
        color: '#fff'
      }
    }
  },
  legend: {
    enabled: false
  },
  tooltip: {
    followTouchMove: true,
    useHTML: true,
    positioner: function (boxWidth, boxHeight, point) {
      return {
        x: point.plotX,
        y: point.plotY - 30
      }
    },
    formatter: function () {
      var index = this.series.data.indexOf(this.point)
      return "万份收益<br><em style='color: #f57c00'>" + profit[index] + '</em>元/天'
    }
  },
  plotOptions: {
    series: {
      borderWidth: 0
    }
  },
  series: [{
    data: [6.0, 6.1, 6.4, 6.6, 7.0, 7.3],
    pointPadding: 0.1,
    color: '#F9DCAB',
    dataLabels: {
      enabled: true,
      color: '#fff',
      align: 'center',
      format: '{y}％',
      x: 0,
      y: 0,
      style: {
        fontSize: '10px',
        textShadow: '0'
      }
    }
  }]
})
