def handel_upto_99(number):
    predef = {0: "Zero", 1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six", 7: "Seven", 8: "Eight",
              9: "Nine", 10: "Ten", 11: "Eleven", 12: "Twelve", 13: "Thirteen", 14: "Fourteen", 15: "Fifteen",
              16: "Sixteen", 17: "Seventeen", 18: "Eighteen", 19: "Nineteen", 20: "Twenty", 30: "Thirty",
              40: "Forty", 50: "Fifty", 60: "Sixty", 70: "Seventy", 80: "Eighty", 90: "Ninety", 100: "Hundred",
              100000: "Lac", 10000000: "Crore", 1000000000: "billion"}

    if number in predef.keys():
        return predef[number]
    else:
        return predef[(number / 10) * 10] + ' ' + predef[number % 10]


def return_bigdigit(number, devideby):
    predef = {0: "Zero", 1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six", 7: "Seven", 8: "Eight",
              9: "Nine", 10: "Ten", 11: "Eleven", 12: "Twelve", 13: "Thirteen", 14: "Fourteen", 15: "Fifteen",
              16: "Sixteen", 17: "Seventeen", 18: "Eighteen", 19: "Nineteen", 20: "Twenty", 30: "Thirty", 40: "Forty",
              50: "Fifty", 60: "Sixty", 70: "Seventy", 80: "Eighty", 90: "Ninety", 100: "Hundred", 1000: "Thousand",
              100000: "Lac", 10000000: "Crore", 1000000000: "Billion"}

    if devideby in predef.keys():
        return predef[number / devideby] + " " + predef[devideby]
    else:
        devideby /= 10
        return handel_upto_99(number / devideby) + " " + predef[devideby]


def amountToWords(number):
    dev = {100: "Hundred", 1000: "Thousand", 100000: "Lac", 10000000: "Crore", 1000000000: "Billion"}

    if number is 0:
        return "Zero"
    if number < 100:
        result = handel_upto_99(number)

    else:
        result = ""
        while number >= 100:
            devideby = 1
            length = len(str(number))
            for i in range(length - 1):
                devideby *= 10
                
            if number % devideby == 0:
                if devideby in dev:
                    return handel_upto_99(number / devideby) + " " + dev[devideby]
                else:
                    return handel_upto_99(number / (devideby / 10)) + " " + dev[devideby / 10]
            
            res = return_bigdigit(number, devideby)
            result = result + ' ' + res
            
            if devideby not in dev:
                number = number - ((devideby / 10) * (number / (devideby / 10)))
            
            number = number - devideby * (number / devideby)

        if number < 100:
            result = result + ' ' + handel_upto_99(number)
    
    return result
