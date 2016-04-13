from openerp import api
from openerp.osv import osv
import re 
from openerp import _
from openerp.exceptions import Warning

def _validate_email(values):
    msg_store = {}
    for val in values:
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", values[val]) == None:
            msg_store[val] = val + ': ' + msg['email']
            
    return msg_store

def _validate_special_char(name):
    if re.search("[^A-Za-z0-9 ]", name) == None:
        return True
    return False

# validate percentage value for float data type
def _validate_percentage(values):
    msg_store = {}
    for val in values:
        percent = float(values[val])
        if  not (0 <= percent <= 100):
            msg_store[val] = val + ': ' + msg['percentage']
            
    return msg_store

def _validate_character(values, special=False):
    msg_store = {}

    for val in values:
        if values[val]:
            checkIllegal = values[val].strip()
            if special:
                if re.search("[^A-Za-z0-9 ]", checkIllegal) != None:
                    msg_store[val] = val + ': ' + msg['special_char']

            if not checkIllegal:
                msg_store[val] = val + ': ' + msg['space']

    return msg_store



def _validate_number(values):
    msg_store = {}
    for val in values:
        floatVal = float(values[val])
        if floatVal < 0.0:
            msg_store[val] = val + ': ' + msg['valid_number']
    return msg_store


def _check_illegal_char(self, values, msg):
    flag = True
    for value in values:
        checkIllegal = values[value].strip()
        if checkIllegal:
            if re.search("[^A-Za-z0-9 ]", checkIllegal) == None:
                flag = True
            else:
                msg = value + ': ' + msg['special_char']
                raise osv.except_osv(('Validation Error'), (msg))
                flag = False
        else:
            flag = False
    if(flag):
        return flag
    else:
        msg = value + ': ' + msg['space']
        raise osv.except_osv(('Validation Error'), (msg))
        return flag
    
def _check_space(self, values, msg):
    flag = True
    msg_store = {}
    for value in values:
        checkIllegal = values[value].strip()    
        if checkIllegal:
            flag = True
        else:
            flag = False
            msg_store[value] = value + ': ' + msg['space']
    return msg_store

# Check space in character type fields
# def _check_space2(values):
#     msg_store = {}
#     for value in values:
#         checkIllegal = values[value].strip()    
#         if not checkIllegal:
#             msg_store[value] = value + ': ' + msg['space']
#              
#     return msg_store

def _check_special_char(self, values, msg):
    flag = True
    msg_store = {}
    # for value in values:
    #     checkIllegal = values[value].strip()
    #     if checkIllegal:
    #         if re.search("[^A-Za-z0-9 ]", checkIllegal) == None:
    #             flag = True
    #         else:
    #             msg_store[value] = value + ': ' + msg['special_char']
    #             flag = False
    return msg_store

# Check for special character 

def _check_space2(values):
    msg_store = {}
    for value in values:
        if values[value]:
            checkIllegal = values[value].strip()   
            if not checkIllegal:
                msg_store[value] = value + ': ' + msg['space']
             
    return msg_store

def _check_special_char2(values):
    msg_store = {}
    for val in values:
        if values[val]:
            checkIllegal = values[val]
            if re.search("[^A-Za-z0-9 ]", checkIllegal) != None:
                msg_store[val] = val + ': ' + msg['special_char']
                
    return msg_store

def _check_duplicate_data(self, check_val, field_name, records, msg):
    flag = False
    msg_store = {}
    
    if check_val and field_name:
        for record in records:
            if(check_val.lower() == record[field_name].lower()):
                flag = True
                msg_store['Name'] = msg['unique']
                # msg_store[field_name] = field_name + ': ' + msg['unique']
            else:
                flag = False
    # raise Warning(_(msg_store))            
    return msg_store 

# Raise all kinds of validation message
def validation_msg(validate_msg):
    msg_str = ""
    for msg in validate_msg:
        msg_str = msg_str + validate_msg[msg] + "\n"
        
    if msg_str:
        raise osv.except_osv(('Validation Error'), (msg_str))

def generate_validation_msg(check_space, check_special_char):    
    validation_msg = {}
    validation_msg.update(check_space)
    validation_msg.update(check_special_char)
    msg_store = ""
    for msg in validation_msg:
        msg_store = msg_store + validation_msg[msg] + "\n"
        
    if msg_store:
        raise osv.except_osv(('Validation Error'), (msg_store))

             

def debug(param, all=False):
    print '--------------------START-------------------------'
    if all:
        for val in param:
            print val
    else:
        print param
    print '--------------------END-------------------------'


### All kinds of warning message ###

msg = {}
msg['special_char'] = 'Please remove special character.'
msg['image_uniq'] = 'Two image with the same name? Impossible!'
msg['region_uniq'] = 'Two region with the same name? Impossible!'
msg['unique'] = 'Two record with the same name'
msg['delete_style'] = 'Confirmed style cannot be deleted.'
msg['confirm_delete'] = 'Confirmed record cannot be deleted.'
msg['percentage'] = 'Please provide valid percentage value.'
msg['valid_number'] = 'Please provide valid number.'
msg['record_not_exist'] = 'No record exists! Please give a try with different value.'
msg['space'] = 'Only space is not allowed.'
msg['email'] = 'Please provide valid email.'
msg['size_attr'] = 'Please enter size attribute or check size selection value.'
msg['bwo_data'] = 'Please provide valid Work Order Data.'
msg['mc_data'] = 'Please provide valid Material Consumption Data.'
msg['percent_100']='Yarn Percentage summation should not greater than 100'
