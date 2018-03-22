const dialogs_show_rule = [
  [
    {
      name: 'start_que',
      timeout: 0
    }
  ],
  [
    {
      name: 'start_ans',
      timeout: 0
    },
    {
      name: 'foundation_que',
      timeout: 200
    }
  ],
  [
    {
      name: 'foundation_ans',
      timeout: 0
    },
    {
      name: 'foundation_res',
      timeout: 200
    },
    {
      name: 'accident_que',
      timeout: 1200
    }
  ],
  [
    {
      name: 'accident_ans',
      timeout: 0
    },
    {
      name: 'accident_res',
      timeout: 200
    },
    {
      name: 'ci_que',
      timeout: 1200
    }
  ],
  [
    {
      name: 'ci_ans',
      timeout: 0
    },
    {
      name: 'ci_res',
      timeout: 200
    },
    {
      name: 'life_que',
      timeout: 1200
    }
  ],
  [
    {
      name: 'life_ans',
      timeout: 0
    },
    {
      name: 'life_res',
      timeout: 200
    },
    {
      name: 'annual_premium_que',
      timeout: 1200
    }
  ],
  [
    {
      name: 'life_complement_ans',
      timeout: 0
    },
    {
      name: 'life_complement_res',
      timeout: 200
    },
    {
      name: 'annual_premium_que',
      timeout: 1200
    }
  ],
  [
    {
      name: 'annual_premium_ans',
      timeout: 0
    },
    {
      name: 'annual_premium_res',
      timeout: 200
    },
    {
      name: 'end',
      timeout: 2200
    }
  ]
]

export default dialogs_show_rule
