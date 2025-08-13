import sys
import os
import shutil
from datetime import datetime

import openpyxl
from openpyxl.styles import Font, DEFAULT_FONT, Color, PatternFill, Border, Side
from openpyxl.formatting.rule import FormulaRule

auto_open_flg = True

# styles
RedFill = PatternFill(start_color='EE1111', end_color='EE1111', bgColor='EE1111', fill_type='solid')
norm_side = Side(border_style='thin', color='000000')

def normal_border_style(directs):
    kwargs = {}
    if 'h' in directs:
        kwargs['left'] = norm_side
    if 'l' in directs:
        kwargs['right'] = norm_side
    if 'k' in directs:
        kwargs['top'] = norm_side
    if 'j' in directs:
        kwargs['bottom'] = norm_side
    return Border(**kwargs)
nbs = normal_border_style

def set_text(cell):
    cell.number_format = '@'
st = set_text

def set_link(worksheet, pos, linksheet, linkpos):
    hyperlink = Font(underline='single', color='0563C1')
    worksheet[pos].font = hyperlink
    if linksheet:
        worksheet[pos].hyperlink = f'#{linksheet}!{linkpos}'
    else:
        worksheet[pos].hyperlink = f'#{worksheet.title}!{linkpos}'
sl = set_link

def set_conditional_format(worksheet, cell_range, formula, font=DEFAULT_FONT, border=None, fill=None):
    kwargs = {'font' : font}
    if border: kwargs['border'] = border
    if fill: kwargs['fill'] = fill

    fr = FormulaRule(formula=[formula], stopIfTrue=False, **kwargs)
    worksheet.conditional_formatting.add(cell_range, fr)
scf = set_conditional_format

def reflect_formula(formula:str, src:str, dst:str):
    '''generate new excel formula string based on original formula and cell'''
    return formula.upper().replace(src.upper(), dst)
rf = reflect_formula # short cut

# ############################## ↓↓↓ script here ↓↓↓ ##############################

def process_sheet(ws):
    formula = '=AND(NOT(ISBLANK(F5)), NOT(NUMBERVALUE(F5) = 0), NOT(NUMBERVALUE(F5) = 1))'
    formula2 = '=ISBLANK(F5)'
    for c in ['F','G','H','I','J','K','Q','BP','BQ','BS']:
        print(f'process col {c}')
        for i in range(5, 3000):
            scf(ws, f'{c}{i}', rf(formula, 'F5', f'{c}{i}'), fill=RedFill)
            scf(ws, f'{c}{i}', rf(formula2, 'F5', f'{c}{i}'), fill=RedFill)

def process(fp):
    wb = openpyxl.load_workbook(fp) # load workbook
    print(wb.sheetnames)
    ws = wb['取引先情報'] # active worksheet

    process_sheet(ws)

    wb.save(fp) # save workbook
    wb.close()

# ############################## ↑↑↑ script here ↑↑↑ ##############################

def to_win_path(wsl_path):
    path = wsl_path[5:]
    return f'{path[0]}:{path[1:]}'

if __name__ == '__main__':
    if len(sys.argv) < 2: print('No file given... exit'); exit(0)
    fp = sys.argv[1]
    root, extension = os.path.splitext(fp)
    if extension != '.xlsx': print('Not excel file... exit'); exit(0)
    # back up first
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    dst = f'{root}-{timestamp}{extension}'
    shutil.copyfile(fp, dst)
    print(f'backup to {dst}')

    print('Processing...')
    process(fp)
    print('Done')

    if auto_open_flg:
        print('Opening...')
        os.system(f'wslview {to_win_path(fp)}')
        print('Done')
