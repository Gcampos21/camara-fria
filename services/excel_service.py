from openpyxl import load_workbook
from config import ARQUIVO_EXCEL


def abrir_planilha(data_only=False):
    return load_workbook(ARQUIVO_EXCEL, data_only=data_only)


def salvar_planilha(wb):
    wb.save(ARQUIVO_EXCEL)