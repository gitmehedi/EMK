import os
import xlrd
import shutil


def get_source_dir():
    """:returns: The return value. directory(str)"""
    return '/home/mehedi/Documents'


def get_destination_dir():
    """:returns: The return value. directory(str)"""
    return '/home/mehedi/Music'


def get_file_extension(var_file_path):
    """Separate file extension from file path
    :param var_file_path: file path with file name and extension
    :returns: The return value. only file extension with dot(.)
    """
    file_extension = None
    if var_file_path:
        file_extension = os.path.splitext(var_file_path)[1]

    return file_extension


def get_valid_file_extension():
    """Store valid extension of file
    :returns: The return value. list of extension
    """
    return ['.xls']





def get_formatted_data(var_worksheet):
    """Read Excel sheet and create list from sheet data
    :param var_worksheet: take worksheet
    :returns: The return value. list of dictionary
    """
    worksheet_col = []  # list of columns
    for col in range(var_worksheet.ncols - 1):
        worksheet_col.append(str(var_worksheet.cell(0, col).value))

    formatted_data = []  # collection of dict
    for row in range(1, var_worksheet.nrows - 1):
        my_dict = {}
        for col in range(var_worksheet.ncols - 1):
            my_dict[worksheet_col[col]] = str(var_worksheet.cell(row, col).value)
        formatted_data.append(my_dict)

    return formatted_data


def move_file_from_src_to_des(var_src_dir, var_des_dir):
    """Move file from one to another directory
    :param var_src_dir: source directory
    :param var_des_dir: destination directory
    """
    shutil.move(var_src_dir, var_des_dir)


def print_data(var_data):
    """Display formatted data
    :param var_data: list of dictionary
    """
    print(var_data)


def main():
    """Main function"""

    source = get_source_dir()
    dest = get_destination_dir()
    my_files_path = filter(lambda x:x.endswith('.xls'), os.listdir(source))
    for file_path in my_files_path:
        if get_file_extension(file_path) in get_valid_file_extension():
            full_path = source+'/'+file_path
            file_obj = xlrd.open_workbook(full_path)
            for worksheet_index in range(file_obj.nsheets):
                records = get_formatted_data(file_obj.sheet_by_index(worksheet_index))
                for rec in records:
                    journal = {}
                    depr_debit_1 = {
                        'name': asset_name,
                        'account_id': category_id.account_depreciation_id.id,
                        'credit': 0.0,
                        'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
                        'journal_id': category_id.journal_id.id,
                        'partner_id': line.asset_id.partner_id.id,
                        'analytic_account_id': category_id.account_analytic_id.id if category_id.type == 'purchase' else False,
                        'currency_id': company_currency != current_currency and current_currency.id or False,
                        'amount_currency': company_currency != current_currency and line.amount or 0.0,
                    }

                if records:
                    move_file_from_src_to_des(file_path, get_destination_dir())
        else:
            print("File extension is not valid")


main()  # Execute the main function