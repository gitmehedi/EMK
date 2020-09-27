# I stands for INDIVIDUAL
# R stands for ROASTING (COMBINATION)
# C stands for COMPLEX
# VS stands for VAT SELECTION

I_VS_CASE = {

}
I_CASE = {
    1: [
        {
            'qty': 1,
            'unit_price': 500000,
            'vat_name': '',
            'tds_name': 'SLAB 2-5'
        }
    ],
    2: [
        {
            'qty': 1,
            'unit_price': 1800000,
            'vat_name': '',
            'tds_name': 'SLAB 2-5'
        }
    ],
    3: [
        {
            'qty': 1,
            'unit_price': 6100000,
            'vat_name': '',
            'tds_name': 'SLAB 2-5'
        }
    ],
    4: [
        {
            'qty': 1,
            'unit_price': 12000000,
            'vat_name': '',
            'tds_name': 'SLAB 2-5'
        }
    ],
    5: [
        {
            'qty': 1,
            'unit_price': 300000,
            'vat_name': '',
            'tds_name': 'SLAB 2-5'
        },
        {
            'qty': 1,
            'unit_price': 450000,
            'vat_name': '',
            'tds_name': 'SLAB 2-5'
        }
    ],
    6: [
        {
            'qty': 1,
            'unit_price': 1000000,
            'vat_name': '',
            'tds_name': 'SLAB 2-5'
        },
        {
            'qty': 1,
            'unit_price': 600000,
            'vat_name': '',
            'tds_name': 'SLAB 2-5'
        }
    ],
    7: [
        {
            'qty': 5,
            'unit_price': 1000000,
            'vat_name': '',
            'tds_name': 'SLAB 2-5'
        },
        {
            'qty': 2,
            'unit_price': 600000,
            'vat_name': '',
            'tds_name': 'SLAB 2-5'
        }
    ],
    8: [
        {
            'qty': 7,
            'unit_price': 1000000,
            'vat_name': '',
            'tds_name': 'SLAB 2-5'
        },
        {
            'qty': 9,
            'unit_price': 700000,
            'vat_name': '',
            'tds_name': 'SLAB 2-5'
        }
    ]
}
I_CASE_RESULT = {
    1: {
        'amount_untaxed': 500000,
        'amount_tax': 0,
        'amount_total': 500000,
        'amount_tds': 10000,
        'amount_vat_payable': 0
    },
    2: {
        'amount_untaxed': 1800000,
        'amount_tax': 0,
        'amount_total': 1800000,
        'amount_tds': 54000,
        'amount_vat_payable': 0
    },
    3: {
        'amount_untaxed': 6100000,
        'amount_tax': 0,
        'amount_total': 6100000,
        'amount_tds': 244000,
        'amount_vat_payable': 0
    },
    4: {
        'amount_untaxed': 12000000,
        'amount_tax': 0,
        'amount_total': 12000000,
        'amount_tds': 600000,
        'amount_vat_payable': 0
    },
    5: {
        'amount_untaxed': 750000,
        'amount_tax': 0,
        'amount_total': 750000,
        'amount_tds': 15000,
        'amount_vat_payable': 0
    },
    6: {
        'amount_untaxed': 1600000,
        'amount_tax': 0,
        'amount_total': 1600000,
        'amount_tds': 48000,
        'amount_vat_payable': 0
    },
    7: {
        'amount_untaxed': 6200000,
        'amount_tax': 0,
        'amount_total': 6200000,
        'amount_tds': 248000,
        'amount_vat_payable': 0
    },
    8: {
        'amount_untaxed': 13300000,
        'amount_tax': 0,
        'amount_total': 13300000,
        'amount_tds': 665000,
        'amount_vat_payable': 0
    }
}

R_VS_CASE = {
    17: 'Mushok-6.3'
}
R_CASE = {
    1: [
        {
            'qty': 1,
            'unit_price': 50000,
            'vat_name': '2% INCLUDING',
            'tds_name': '5% TDS'
        }
    ],
    2: [
        {
            'qty': 1,
            'unit_price': 5000,
            'vat_name': '5% INCLUDING',
            'tds_name': '5% INCLUDING'
        },
        {
            'qty': 1,
            'unit_price': 12000,
            'vat_name': '5% INCLUDING',
            'tds_name': '5% INCLUDING'
        },
        {
            'qty': 1,
            'unit_price': 7000,
            'vat_name': '5% INCLUDING',
            'tds_name': '5% INCLUDING'
        },
        {
            'qty': 1,
            'unit_price': 76000,
            'vat_name': '5% INCLUDING',
            'tds_name': '5% INCLUDING'
        }
    ],
    3: [
        {
            'qty': 10,
            'unit_price': 500,
            'vat_name': '7.5% INCLUDING',
            'tds_name': 'SLAB 2-5'
        }
    ],
    4: [
        {
            'qty': 1,
            'unit_price': 20000,
            'vat_name': '10% EXCLUDING',
            'tds_name': '2% EXCLUDED'
        }
    ],
    5: [
        {
            'qty': 2,
            'unit_price': 499,
            'vat_name': '15% EXCLUDING [OFFICE] [Dr.]',
            'tds_name': '7.5% INCLUDING'
        }
    ],
    6: [
        {
            'qty': 1,
            'unit_price': 39000,
            'vat_name': '15% INCLUDING',
            'tds_name': '5% INCLUDING'
        }
    ],
    7: [
        {
            'qty': 1,
            'unit_price': 2000,
            'vat_name': '',
            'tds_name': ''
        }
    ],
    8: [
        {
            'qty': 1,
            'unit_price': 7999,
            'vat_name': '5% EXCLUDING',
            'tds_name': '5% INCLUDING'
        }
    ],
    9: [
        {
            'qty': 1,
            'unit_price': 999,
            'vat_name': '5% INCLUDING',
            'tds_name': '2% INCLUDED'
        }
    ],
    10: [
        {
            'qty': 1,
            'unit_price': 500000,
            'vat_name': '7.5% INCLUDING',
            'tds_name': '2% INCLUDED'
        }
    ],
    11: [
        {
            'qty': 1,
            'unit_price': 607000,
            'vat_name': '10% INCLUDING',
            'tds_name': 'SLAB 2-5'
        }
    ],
    12: [
        {
            'qty': 1,
            'unit_price': 100000,
            'vat_name': '15% INCLUDING',
            'tds_name': '2% INCLUDED'
        }
    ],
    13: [
        {
            'qty': 1,
            'unit_price': 115000,
            'vat_name': '15% INCLUDING',
            'tds_name': '5% INCLUDING'
        }
    ],
    14: [
        {
            'qty': 1,
            'unit_price': 115000,
            'vat_name': '15% INCLUDING',
            'tds_name': '10% INCLUDING [PROFESSIONAL]'
        }
    ],
    15: [
        {
            'qty': 1,
            'unit_price': 115000,
            'vat_name': '2% EXCLUDING',
            'tds_name': '2% INCLUDED'
        }
    ],
    16: [
        {
            'qty': 1,
            'unit_price': 115000,
            'vat_name': '15% GROUP VAT [RESIDENCE]',
            'tds_name': '7.5% INCLUDING'
        }
    ],
    17: [
        {
            'qty': 1,
            'unit_price': 500000,
            'vat_name': '15% INCLUDING',
            'tds_name': '4% INCLUDING'
        }
    ],
    18: [
        {
            'qty': 1,
            'unit_price': 1800000,
            'vat_name': '15% GROUP VAT [OFFICE]',
            'tds_name': '5% INCLUDING'
        }
    ],
    19: [
        {
            'qty': 5,
            'unit_price': 15000,
            'vat_name': '7.5% EXCLUDING',
            'tds_name': '7.5% EXCLUDING'
        }
    ]
}
R_CASE_RESULT = {
    1: {
        'amount_untaxed': 49019.61,
        'amount_tax': 980.39,
        'amount_total': 50000,
        'amount_tds': 2450.98,
        'amount_vat_payable': 980.39
    },
    2: {
        'amount_untaxed': 95238.09,
        'amount_tax': 4761.91,
        'amount_total': 100000,
        'amount_tds': 4761.90,
        'amount_vat_payable': 4761.91
    },
    3: {
        'amount_untaxed': 4651.16,
        'amount_tax': 348.84,
        'amount_total': 5000,
        'amount_tds': 93.02,
        'amount_vat_payable': 348.84
    },
    4: {
        'amount_untaxed': 20408.16,
        'amount_tax': 2040.82,
        'amount_total': 22448.98,
        'amount_tds': 408.16,
        'amount_vat_payable': 2040.82
    },
    5: {
        'amount_untaxed': 998,
        'amount_tax': 149.7,
        'amount_total': 1147.7,
        'amount_tds': 74.85,
        'amount_vat_payable': 0
    },
    6: {
        'amount_untaxed': 33913.04,
        'amount_tax': 5086.96,
        'amount_total': 39000,
        'amount_tds': 1695.65,
        'amount_vat_payable': 5086.96
    },
    7: {
        'amount_untaxed': 2000,
        'amount_tax': 0,
        'amount_total': 2000,
        'amount_tds': 0,
        'amount_vat_payable': 0
    },
    8: {
        'amount_untaxed': 7999,
        'amount_tax': 399.95,
        'amount_total': 8398.95,
        'amount_tds': 399.95,
        'amount_vat_payable': 399.95
    },
    9: {
        'amount_untaxed': 951.43,
        'amount_tax': 47.57,
        'amount_total': 999,
        'amount_tds': 19.03,
        'amount_vat_payable': 47.57
    },
    10: {
        'amount_untaxed': 465116.28,
        'amount_tax': 34883.72,
        'amount_total': 500000,
        'amount_tds': 9302.33,
        'amount_vat_payable': 34883.72
    },
    11: {
        'amount_untaxed': 551818.18,
        'amount_tax': 55181.82,
        'amount_total': 607000,
        'amount_tds': 11036.36,
        'amount_vat_payable': 55181.82
    },
    12: {
        'amount_untaxed': 86956.52,
        'amount_tax': 13043.48,
        'amount_total': 100000,
        'amount_tds': 1739.13,
        'amount_vat_payable': 13043.48
    },
    13: {
        'amount_untaxed': 100000,
        'amount_tax': 15000,
        'amount_total': 115000,
        'amount_tds': 5000,
        'amount_vat_payable': 15000
    },
    14: {
        'amount_untaxed': 100000,
        'amount_tax': 15000,
        'amount_total': 115000,
        'amount_tds': 10000,
        'amount_vat_payable': 15000
    },
    15: {
        'amount_untaxed': 115000,
        'amount_tax': 2300,
        'amount_total': 117300,
        'amount_tds': 2300,
        'amount_vat_payable': 2300
    },
    16: {
        'amount_untaxed': 115000,
        'amount_tax': 17250,
        'amount_total': 132250,
        'amount_tds': 8625,
        'amount_vat_payable': 17250
    },
    17: {
        'amount_untaxed': 434782.61,
        'amount_tax': 65217.39,
        'amount_total': 500000,
        'amount_tds': 17391.30,
        'amount_vat_payable': 0
    },
    18: {
        'amount_untaxed': 1800000,
        'amount_tax': 270000,
        'amount_total': 2070000,
        'amount_tds': 90000,
        'amount_vat_payable': 270000
    },
    19: {
        'amount_untaxed': 81081.08,
        'amount_tax': 6081.08,
        'amount_total': 87162.16,
        'amount_tds': 6081.08,
        'amount_vat_payable': 6081.08
    }
}

C_VS_CASE = {

}
C_CASE = {
    1: [
        {
            'is_vb': False,
            'is_action_validate': True,
            'is_adjusted': False,
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
                    'unit_price': 500000,
                    'vat_name': '',
                    'tds_name': 'SLAB 2-5'
                }
            ]
        },
        {
            'is_vb': False,
            'is_action_validate': True,
            'is_adjusted': False,
            'vals': {
                'advance_amount': 400000,
                'vat_name': '',
                'tds_name': 'SLAB 2-5'
            }
        },
        {
            'is_vb': False,
            'is_action_validate': True,
            'is_adjusted': True,
            'vals': {
                'advance_amount': 100000,
                'vat_name': '',
                'tds_name': 'SLAB 2-5'
            }
        },
        {
            'is_vb': True,
            'is_action_validate': False,
            'vals': [
                {
                    'qty': 1,
                    'unit_price': 100000,
                    'vat_name': '',
                    'tds_name': 'SLAB 2-5'
                }
            ]
        }
    ],
    2: [
        {
            'is_vb': False,
            'is_action_validate': True,
            'is_adjusted': False,
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
                    'unit_price': 500000,
                    'vat_name': '',
                    'tds_name': 'SLAB 2-5'
                }
            ]
        },
        {
            'is_vb': False,
            'is_action_validate': True,
            'is_adjusted': False,
            'vals': {
                'advance_amount': 400000,
                'vat_name': '',
                'tds_name': 'SLAB 2-5'
            }
        },
        {
            'is_vb': False,
            'is_action_validate': True,
            'is_adjusted': True,
            'vals': {
                'advance_amount': 100000,
                'vat_name': '',
                'tds_name': 'SLAB 2-5'
            }
        },
        {
            'is_vb': True,
            'is_action_validate': False,
            'vals': [
                {
                    'qty': 1,
                    'unit_price': 200000,
                    'vat_name': '',
                    'tds_name': 'SLAB 2-5'
                }
            ]
        }
    ]
}
C_CASE_RESULT = {
    1: {
        'amount_untaxed': 100000,
        'amount_tax': 0,
        'amount_total': 100000,
        'amount_tds': 2000,
        'amount_vat_payable': 0
    },
    2: {
        'amount_untaxed': 200000,
        'amount_tax': 0,
        'amount_total': 200000,
        'amount_tds': 21000,
        'amount_vat_payable': 0
    }
}
