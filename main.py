import inquirer, csv
import locale, pyperclip
from tabulate import tabulate, SEPARATING_LINE
from typing import Dict, List
from enum import Enum
from inquirer import errors
from inquirer.themes import BlueComposure,GreenPassion
from util import clear_terminal, break_text_lines
from printer import send_to_printer
from os import getcwd

class Menus(Enum):
    CLASSIC = "Clássico"
    SPECIAL = "Especial"
    NOT_SELECTED = None
    
class Application:
    DEFAULT_CLASSIC_MENU_PATH = 'src/cardapios/classic.csv'
    DEFAULT_SPECIAL_MENU_PATH = 'src/cardapios/special.csv'
    print(getcwd())
    def __init__(self):
        locale.setlocale(locale.LC_ALL, '')
        self.requests: List(Dict[str, str | int]) = []
        self.client_name: str = ""
        self.selected_menu: Menus = Menus.CLASSIC 
        self.menu: List(Dict[str, str]) = {}
        self.should_ask_for_different_menus = True
        self.order = ""
        self.whatsapp_order = ""
        self.printer_order = ""


    def show_menus(self):
        if self.selected_menu == Menus.CLASSIC.value:
            self.show_classic_menu()
        elif self.selected_menu == Menus.SPECIAL.value:
            self.show_special_menu()
        
    def show_classic_menu(self) -> str:
        classic_csv_file = open(Application.DEFAULT_CLASSIC_MENU_PATH, "r", encoding="utf8")
        classic_csv = csv.reader(classic_csv_file)
        tabulate_data = []
        for idx,line in enumerate(classic_csv):
            if idx == 0:
                continue
            key,name,value = line
            value_number = float(value)
            tabulate_data.append((name,value_number))
            if not self.menu.get(key):
                self.menu[key] = {
                    "name":name,
                    "value":value
                }
        menu = tabulate(
            tabulate_data,
            headers=["Nome", "Valor"],
            tablefmt="pretty",
            colalign=("left","right")
        )
        classic_csv_file.close()
        print(menu)
        
    def show_special_menu(self) -> str:
        special_csv_file = open(Application.DEFAULT_SPECIAL_MENU_PATH, "r", encoding="utf8")
        special_csv = csv.reader(special_csv_file)
        tabulate_data = []
        for idx,line in enumerate(special_csv):
            if idx == 0:
                continue
            key,name,value,active = line
            if not bool(int(active)):
                continue
            value_number = float(value)
            tabulate_data.append((name,value_number))
            if not self.menu.get(key):
                self.menu[key] = {
                    "name":name,
                    "value":value
                }
        menu = tabulate(
            tabulate_data,
            headers=["Nome", "Valor"],
            tablefmt="pretty",
            colalign=("left","right")
        )
        special_csv_file.close()
        print(menu)

    def name_question(self) -> None:
        questions = [
            inquirer.Text('name',message='Nome do cliente',validate=self.__validate_name),
        ]
        answer = inquirer.prompt(questions,theme=GreenPassion())
        self.client_name = answer.get('name')

    def menu_question(self):
        menus_choices = [menu.value for menu in Menus if menu != Menus.NOT_SELECTED]
        question = [
            inquirer.List('menu',message='Qual menu deseja comprar', choices=menus_choices,default=Menus.CLASSIC)
        ]
        answer=inquirer.prompt(question, theme=GreenPassion())
        self.selected_menu = answer.get('menu')
        self.menu = {}
        self.show_menus()

    def clear_fields(self):
        self.client_name = ""
        self.selected_menu = Menus.NOT_SELECTED
        self.requests = []
        self.whatsapp_order = ""
        self.printer_order = ""
        self.order = ""
        self.menu = {}


    def plate_and_quantity_questions(self):
        choices = [(self.menu.get(plate).get('name'),plate) for plate in self.menu]
        quantity_range = [i for i in range(1,6)]
        should_continue_adding_plates = True
        answers= {}
        while should_continue_adding_plates:
            clear_terminal()
            self.show_menus()
            questions = [
                inquirer.List('plate',message='Escolha um prato', choices=choices, carousel=True),
                inquirer.List('quantity', message="Qual a quantidade", choices=quantity_range, carousel=True),
                inquirer.Text('obs',message="Obs?"),
                inquirer.Confirm('continue',message="Deseja incluir mais pratos?", default=False)
            ]
            answers = inquirer.prompt(questions,theme=BlueComposure())
            plate = answers.get('plate')
            quantity = int(answers.get('quantity'))
            observation = answers.get('obs')
            request = self.menu.get(plate)
            plate_value = float(request.get("value"))
            plate_total = quantity * plate_value

            request_object = {"name":request.get('name'), 
                                 "sum_value": plate_total,
                                 "value": plate_value, 
                                 "quantity": quantity,
                                 "obs": observation
            }
            if len(self.requests) == 0:
                self.requests.append(request_object)
            else:
                plate_found = False
                for already_registered_request in self.requests:
                    if already_registered_request.get('name') == request.get('name') and len(observation)!= 0:
                        already_registered_request['sum_value'] += plate_total
                        already_registered_request['quantity'] += quantity
                        plate_found = True
                        break
                if not plate_found:
                    self.requests.append(request_object)
            should_continue_adding_plates = answers['continue']
      

    

    def __format_obs(self,obs,table="whats") -> str:
        if len(obs) == 0:
            return ''
        if(table == "whats"):
            return f' (Obs {obs})'
        return f'\n(Obs {break_text_lines(obs,10)})'

    def prepare_order(self):
        order = f"Nome do cliente: *{self.client_name}*\nResumo do Pedido:\n{"-"*32}\n"
        whatsapp_tabulate_data = []
        printer_tabulate_data = []
        total = 0
        printer_order=f"{order.replace('*','')}"
        whatsapp_order = f"{order}```"
        for request in self.requests:
            name = request.get("name").strip()
            obs = request.get("obs").strip()
            whatsapp_formatted_name = f"{name:<12}{self.__format_obs(obs=obs)}"
            printer_formatted_name = f"{name:<12}{self.__format_obs(obs=obs, table='printer')}"
            printer_formatted_name = break_text_lines(printer_formatted_name, 13)
            value = locale.currency(request.get("value"))
            quantity = f'{request.get("quantity")}x'
            total += float(request.get("sum_value"))
            whatsapp_tabulate_data.append([whatsapp_formatted_name, quantity,value])
            printer_tabulate_data.append([printer_formatted_name, quantity, value])
        total = float(f"{total:.2f}")
        value_brl = locale.currency(total)
        whatsapp_tabulate_data.append(['-'*5,'-'*5,'-'*5])
        printer_tabulate_data.append(['-'*3,'-'*3,'-'*3])
        whatsapp_tabulate_data.append(["Total","-"*5,value_brl])
        printer_tabulate_data.append(["Total","---",value_brl])
        whatsapp_table = tabulate(whatsapp_tabulate_data,headers=['Nome','Qtd','Vl Unt.'], colalign=('left', 'center','right'), tablefmt="rounded_outline",)
        printer_table = tabulate(printer_tabulate_data,headers=['Nome','Qtd','Vl Unt.'], colalign=('left', 'center','right'), tablefmt="plain")
        whatsapp_order+=f"{whatsapp_table}\n"
        printer_order+=f"{printer_table}\n"
        
        whatsapp_order+="```"
        self.whatsapp_order = whatsapp_order
        self.printer_order = f"{printer_order}\n\n\n\n"
        self.order = whatsapp_order.replace('`','')
     
    
    def print_and_copy_to_clipboard(self):
        pyperclip.copy(self.whatsapp_order)   
        printer_file = open("./order.txt","w", encoding="utf8")
        printer_file.write(self.printer_order)
        send_to_printer() # CALLS UTILS FILE TO PRINT ORDER
        printer_file.close()

    
    def show_order_overview(self):
        print(self.order)


    def run(self):
        while True:
            try:
                self.name_question()
                while self.should_ask_for_different_menus:
                    self.menu_question()
                    self.plate_and_quantity_questions()
                    question = [
                        inquirer.Confirm("continue", message="Gostaria de adicionar pratos de outros cardápios", default=False)
                    ]
                    answer = inquirer.prompt(question,theme=GreenPassion())
                    if not answer.get('continue'):
                        break
                self.prepare_order()
                self.show_order_overview()
                question = [
                    inquirer.Confirm("should_end", message="Deseja finalizar? ", default=True)
                ]             
                answer= inquirer.prompt(question,theme=GreenPassion())
                if not answer.get("should_end"):
                    self.should_ask_for_different_menus = False
                else:
                    self.print_and_copy_to_clipboard()
                    clear_terminal()
                self.clear_fields()
                

            except Exception as error:
                print(error)
                question = [
                    inquirer.Confirm("continue",message="Gostaria de tentar novamente?",default=True)
                ]
                answer = inquirer.prompt(question)
                if answer.get('continue'):
                    clear_terminal()
                    continue
                else:
                    break


    # PRIVATE METHODS

    def __validate_name(self, _, current):
        if len(current) < 3:
            raise errors.ValidationError(
                "",
                reason=f"Nome não pode ser vazio ou ter menos de 3 letras{current}")
        return True
     
if __name__ == "__main__":
    clear_terminal()
    app = Application()
    app.run()
