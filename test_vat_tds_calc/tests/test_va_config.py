# I stands for INDIVIDUAL
# R stands for ROASTING (COMBINATION)
# C stands for COMPLEX

I_CASE = {
    1: {
        'advance_amount': 500000,
        'vat_name': '',
        'tds_name': 'SLAB 2-5'
    },
    2: {
        'advance_amount': 1800000,
        'vat_name': '',
        'tds_name': 'SLAB 2-5'
    },
    3: {
        'advance_amount': 6100000,
        'vat_name': '',
        'tds_name': 'SLAB 2-5'
    },
    4: {
        'advance_amount': 12000000,
        'vat_name': '',
        'tds_name': 'SLAB 2-5'
    }
}
I_CASE_RESULT = {
    1: {
        'vat_amount': 0,
        'tds_amount': 10000
    },
    2: {
        'vat_amount': 0,
        'tds_amount': 54000
    },
    3: {
        'vat_amount': 0,
        'tds_amount': 244000
    },
    4: {
        'vat_amount': 0,
        'tds_amount': 600000
    }
}

R_CASE = {
    # 1: {
    #     'advance_amount': 50000,
    #     'vat_name': '2% INCLUDING',
    #     'tds_name': '5% TDS'
    # },
    2: {
        'advance_amount': 100000,
        'vat_name': '5% INCLUDING',
        'tds_name': '5% INCLUDING'
    },
    3: {
        'advance_amount': 5000,
        'vat_name': '7.5% INCLUDING',
        'tds_name': 'SLAB 2-5'
    },
    4: {
        'advance_amount': 20000,
        'vat_name': '10% EXCLUDING',
        'tds_name': '2% EXCLUDED'
    },
    5: {
        'advance_amount': 998,
        'vat_name': '15% EXCLUDING [OFFICE] [Dr.]',
        'tds_name': '7.5% INCLUDING'
    },
    6: {
        'advance_amount': 39000,
        'vat_name': '15% INCLUDING',
        'tds_name': '5% INCLUDING'
    },
    7: {
        'advance_amount': 7999,
        'vat_name': '5% EXCLUDING',
        'tds_name': '5% INCLUDING'
    },
    8: {
        'advance_amount': 999,
        'vat_name': '5% INCLUDING',
        'tds_name': '2% INCLUDED'
    },
    9: {
        'advance_amount': 500000,
        'vat_name': '7.5% INCLUDING',
        'tds_name': '2% INCLUDED'
    },
    10: {
        'advance_amount': 607000,
        'vat_name': '10% INCLUDING',
        'tds_name': 'SLAB 2-5'
    },
    11: {
        'advance_amount': 100000,
        'vat_name': '15% INCLUDING',
        'tds_name': '2% INCLUDED'
    },
    12: {
        'advance_amount': 115000,
        'vat_name': '15% INCLUDING',
        'tds_name': '5% INCLUDING'
    },
    13: {
        'advance_amount': 115000,
        'vat_name': '15% INCLUDING',
        'tds_name': '10% INCLUDING [PROFESSIONAL]'
    },
    14: {
        'advance_amount': 115000,
        'vat_name': '2% EXCLUDING',
        'tds_name': '2% INCLUDED'
    },
    15: {
        'advance_amount': 500000,
        'vat_name': '15% INCLUDING',
        'tds_name': '4% INCLUDING'
    },
    16: {
        'advance_amount': 75000,
        'vat_name': '7.5% EXCLUDING',
        'tds_name': '7.5% EXCLUDING'
    }
}
R_CASE_RESULT = {
    # 1: {
    #     'vat_amount': 980.39,
    #     'tds_amount': 2450.98
    # },
    2: {
        'vat_amount': 4761.91,
        'tds_amount': 4761.90
    },
    3: {
        'vat_amount': 348.84,
        'tds_amount': 93.02
    },
    4: {
        'vat_amount': 2040.82,
        'tds_amount': 408.16
    },
    5: {
        'vat_amount': 0,
        'tds_amount': 74.85
    },
    6: {
        'vat_amount': 5086.96,
        'tds_amount': 1695.65
    },
    7: {
        'vat_amount': 399.95,
        'tds_amount': 399.95
    },
    8: {
        'vat_amount': 47.57,
        'tds_amount': 19.03
    },
    9: {
        'vat_amount': 34883.72,
        'tds_amount': 9302.33
    },
    10: {
        'vat_amount': 55181.82,
        'tds_amount': 11036.36
    },
    11: {
        'vat_amount': 13043.48,
        'tds_amount': 1739.13
    },
    12: {
        'vat_amount': 15000,
        'tds_amount': 5000
    },
    13: {
        'vat_amount': 10000,
        'tds_amount': 15000
    },
    14: {
        'vat_amount': 2300,
        'tds_amount': 2300
    },
    15: {
        'vat_amount': 270000,
        'tds_amount': 90000
    },
    16: {
        'vat_amount': 6081.08,
        'tds_amount': 6081.08
    }
}

C_CASE = {
    1: [
        {
            'is_vb': True,
            'is_action_validate': True,
            'vals': [
                {
                    'qty': 1,
                    'unit_price': 500000,
                    'vat_name': '',
                    'tds_name': 'SLAB 2-5'
                }
            ]
        },
        {
            'is_vb': False,
            'is_action_validate': True,
            'vals': {
                'advance_amount': 500000,
                'vat_name': '',
                'tds_name': 'SLAB 2-5'
            }
        },
        {
            'is_vb': True,
            'is_action_validate': True,
            'vals': [
                {
                    'qty': 1,
                    'unit_price': 400000,
                    'vat_name': '',
                    'tds_name': 'SLAB 2-5'
                }
            ]
        },
        {
            'is_vb': True,
            'is_action_validate': True,
            'vals': [
                {
                    'qty': 1,
                    'unit_price': 100000,
                    'vat_name': '',
                    'tds_name': 'SLAB 2-5'
                }
            ]
        },
        {
            'is_vb': False,
            'is_action_validate': False,
            'vals': {
                'advance_amount': 200000,
                'vat_name': '',
                'tds_name': 'SLAB 2-5'
            }
        }
    ]
}
C_CASE_RESULT = {
    1: {
        'vat_amount': 0,
        'tds_amount': 4000
    }
}
