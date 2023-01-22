CASE_VAT_SELECTION = {
    17: 'Mushok-6.3'
}

# TEST CASE LINE (PRODUCT LINE)
# HERE, KEY DEFINES CASE NO. AND VAL DEFINES LINE PRODUCTS FOR THAT CASE NO.
CASE_LINE = {
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

# TEST CASE RESULT
# HERE, KEY DEFINES CASE NO. AND VAL DEFINES THE EXPECTED RESULT FOR THAT CASE NO.
CASE_RESULT = {
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
        'amount_tax': 34500,
        'amount_total': 149500,
        'amount_tds': 8625,
        'amount_vat_payable': 17250
    },
    17: {
        'amount_untaxed': 434782.61,
        'amount_tax': 65217.39,
        'amount_total': 434782.61,
        'amount_tds': 17391.30,
        'amount_vat_payable': 0
    },
    18: {
        'amount_untaxed': 1800000,
        'amount_tax': 540000,
        'amount_total': 2340000,
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
