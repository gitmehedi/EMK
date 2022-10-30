from odoo import api, fields, models, tools, _


class Currency(models.Model):
    _inherit = "res.currency"

    in_word_start_map = fields.Char(string='In Word Start Map', required=True, track_visibility=True)
    in_word_end_map = fields.Char(string='In Word End Map', required=True, track_visibility=True)

    @api.model
    def amount_to_word(self, number, is_add_currency=True,currency='BDT'):

        dp = self.env['decimal.precision'].precision_get('Account')
        number = round(number, dp)

        dev = {100: "Hundred", 1000: "Thousand", 100000: "Lac", 10000000: "Crore", 1000000000: "Billion"}
        result = ""
        # Split amount for decimal value
        list = str(number).split('.')
        start_word = int(list[0])
        start_word_total = start_word
        end_word = len(list)>1 and list[1] or 0

        # Amount to word for integer portion
        if start_word is 0:
            result = ''
        if start_word < 100:
            result = self.handel_upto_99(start_word)
        else:
            while start_word >= 100:
                devideby = 1
                length = len(str(start_word))
                for i in range(length - 1):
                    devideby *= 10

                if start_word % devideby == 0:
                    if devideby in dev:
                        res = self.handel_upto_99(start_word / devideby) + " " + dev[devideby]
                    else:
                        res = self.handel_upto_99(start_word / (devideby / 10)) + " " + dev[devideby / 10]
                else:
                    res = self.return_bigdigit(start_word, devideby)

                result = result + ' ' + res

                if devideby not in dev:
                    start_word = start_word - ((devideby / 10) * (start_word / (devideby / 10)))
                else:
                    start_word = start_word - devideby * (start_word / devideby)

            if start_word < 100:
                res = self.handel_upto_99(start_word)
                result = result + ' ' + (res if res != 'Zero' else '')

        if is_add_currency == True:

            if int(end_word) > 0:
                end_word = int(end_word) if len(end_word) > 1 else int(end_word) * 10
                paisa = self.handel_upto_99(end_word)
                res_currency = self.env['res.currency'].search([('name', '=', currency)])
                if start_word_total > 0:
                    result = result + ' ' + res_currency.in_word_start_map + ' and ' + paisa + ' ' + res_currency.in_word_end_map
                else:
                    result = paisa + self.end_word_map.get(currency)
            else:
                result = result + self.start_word_map.get(currency)

        else:
            if int(end_word) > 0:
                end_word = int(end_word) if len(end_word) > 1 else int(end_word) * 10
                paisa = self.handel_upto_99(end_word)
                if start_word_total > 0:
                    result = result + ' Point ' + paisa + ' '
                else:
                    result = ' Point '+paisa
            else:
                result = result



        return result

    def handel_upto_99(self, number):
        predef = {0: "Zero", 1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six", 7: "Seven", 8: "Eight",
                  9: "Nine", 10: "Ten", 11: "Eleven", 12: "Twelve", 13: "Thirteen", 14: "Fourteen", 15: "Fifteen",
                  16: "Sixteen", 17: "Seventeen", 18: "Eighteen", 19: "Nineteen", 20: "Twenty", 30: "Thirty",
                  40: "Forty", 50: "Fifty", 60: "Sixty", 70: "Seventy", 80: "Eighty", 90: "Ninety", 100: "Hundred",
                  100000: "Lac", 10000000: "Crore", 1000000000: "billion"}

        if number in predef.keys():
            return predef[number]
        else:
            return predef[(number / 10) * 10] + ' ' + predef[number % 10]

    def return_bigdigit(self, number, devideby):
        predef = { 0: "Zero", 1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six", 7: "Seven", 8: "Eight",
            9: "Nine", 10: "Ten", 11: "Eleven", 12: "Twelve", 13: "Thirteen", 14: "Fourteen", 15: "Fifteen", 16: "Sixteen",
            17: "Seventeen", 18: "Eighteen", 19: "Nineteen", 20: "Twenty", 30: "Thirty", 40: "Forty", 50: "Fifty",
            60: "Sixty",
            70: "Seventy",
            80: "Eighty",
            90: "Ninety",
            100: "Hundred",
            1000: "Thousand",
            100000: "Lac", 10000000: "Crore", 1000000000: "Billion"}

        if devideby in predef.keys():
            return predef[number / devideby] + " " + predef[devideby]
        else:
            devideby /= 10
            return self.handel_upto_99(number / devideby) + " " + predef[devideby]
