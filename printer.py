import os
import win32print

def send_to_printer():
    if not os.name == "nt":
        print('here')
        raise Exception("Impressão ainda não suportada no Linux")
        return
    printer_name = win32print.GetDefaultPrinter()
    with open("./order.txt", "r", encoding="utf8") as file_to_print:
        content = file_to_print.read()
    try:
        hprinter = win32print.OpenPrinter(printer_name)
        printer_info = win32print.GetPrinter(hprinter,2)
        if printer_info['Status'] != 0 :
            raise Exception("A impressora não está disponível. Verifique se está conectada e pronta para uso.")

        win32print.StartDocPrinter(hprinter, 1, ("Test Print Job", None, "RAW"))
        
        win32print.EndDocPrinter(hprinter)
        
        win32print.StartDocPrinter(hprinter, 1, ("Print Job", None, "RAW"))
        win32print.StartPagePrinter(hprinter)

        win32print.WritePrinter(hprinter, content.encode('utf-8'))

        win32print.EndPagePrinter(hprinter)
        win32print.EndDocPrinter(hprinter)
    except Exception as error:
        print(error)
        raise Exception("Algum erro ocorreu na hora de imprimir, tente novamente")
    finally:
        win32print.ClosePrinter(hprinter)

# send_to_printer()