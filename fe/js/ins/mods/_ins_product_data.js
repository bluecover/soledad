// const hzw_logo = '{{{img/logo/hzw_logo.png}}}'

const products_list = {
  accident: {
    name: 'accident',
    ins_name: '意外险',
    logo: '<svg src="{svg{{img/ins/c01.svg}}}"></svg>',
    products: [
      {
        category: '全网底价',
        title: '中民无忧综合意外基本计划（中国人寿）',
        desc: '意外身故 | 意外残疾 | 意外医疗',
        price: '60.00',
        activity_tag: true,
        url: 'https://www.guihua.com/ins/product/A001/'
      },
      {
        category: '无医保必投',
        title: '国寿“住院宝”必备版',
        desc: '意外身故残疾 | 意外医疗 | 住院医疗',
        price: '128.00',
        price_desc: '/年',
        url: 'https://www.guihua.com/ins/product/A003/'
      },
      {
        category: '灵活自选',
        title: '苏黎世-意外自选计划',
        desc: '意外身故残疾 | 意外医疗 | 扩展社保用药',
        price: '28.00',
        url: 'https://www.guihua.com/ins/product/A002/'
      }
    ]
  },

  dread: {
    name: 'dread',
    ins_name: '重疾险',
    logo: '<svg src="{svg{{img/ins/c02.svg}}}"></svg>',
    products: [
      {
        category: '性价比超高',
        title: '新华 i 健康定期重大疾病保障计划',
        desc: '45种重疾 | 身故',
        price: '210.00',
        activity_tag: true,
        url: 'https://www.guihua.com/ins/product/CI001/'
      }
      // {
      //   category: '针对女性疾病',
      //   title: '新华 i 她女性特定疾病保障计划',
      //   desc: '女性特定疾病 | 特定骨折烧伤 | 意外整形',
      //   price: '65.00',
      //   url: 'https://www.guihua.com/ins/product/CI002/'
      // }
    ]
  },

  life: {
    name: 'life',
    ins_name: '寿险',
    logo: '<svg src="{svg{{img/ins/c03.svg}}}"></svg>',
    products: [
      {
        category: '无需体检',
        title: '合众爱家无忧定期寿险',
        desc: '身故即赔',
        price: '100.00',
        activity_tag: true,
        url: 'https://www.guihua.com/ins/product/L002/'
      },
      {
        category: '越健康越便宜',
        title: '人保寿险精心优选定期寿险（可附加重疾险）',
        desc: '身故即赔',
        price: '150.00',
        url: 'https://www.guihua.com/ins/product/L001/'
      }
    ]
  },

  children: {
    name: 'children',
    ins_name: '儿童险',
    logo: '<svg src="{svg{{img/ins/c04.svg}}}"></svg>',
    footer: true,
    products: [
      {
        category: '30天-0周岁',
        title: '平安宝贝健康保障计划 A',
        desc: '意外伤害 | 意外医疗 | 住院医疗 | 重大疾病',
        price: '480.00',
        price_desc: '/年',
        url: 'https://www.guihua.com/ins/product/CA001/'
      },
      {
        category: '1-2周岁',
        title: '中民国寿健康宝贝 A 计划',
        desc: '意外伤残 | 意外门诊 | 住院医疗',
        price: '350.00',
        price_desc: '/年',
        url: 'https://www.guihua.com/ins/product/CA002/'
      },
      {
        category: '3-17周岁',
        title: '中国人寿安心学生吉祥保障计划',
        desc: '意外残疾 | 意外医疗 | 住院医疗 | 重大疾病',
        price: '190.00',
        price_desc: '/年',
        activity_tag: true,
        url: 'https://www.guihua.com/ins/product/CA003/'
      },
      {
        category: '针对儿童重疾',
        title: '合众定期重大疾病保险（20年期）',
        desc: '24种少儿重疾',
        price: '65.00',
        url: 'https://www.guihua.com/ins/product/CI003/'
      }
    ]
  },

  travel: {
    name: 'travel',
    ins_name: '旅行险',
    logo: '<svg src="{svg{{img/ins/c05.svg}}}"></svg>',
    products: [
      {
        category: '境内游',
        title: '美亚畅游神州境内旅行保险',
        desc: '意外伤害 | 医药补偿 | 紧急救援',
        price: '10.00',
        url: 'https://www.guihua.com/ins/product/T001/'
      },
      {
        category: '境外游',
        title: '美亚万国游踪旅游保险',
        desc: '意外伤害 | 医药补偿 | 紧急救援',
        price: '85.00',
        url: 'https://www.guihua.com/ins/product/T002/'
      }
    ]
  }
}

export default products_list
