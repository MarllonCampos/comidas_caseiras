from os import walk, path
from pprint import pprint
import csv
class Menus:
  """Classe de load de cardápios dentro da pasta SRC/CARDAPIOS"""
  MENUS_PATH = path.join("src","cardapios")
  def __init__(self):
    self.menu_object = {}
    for (_, _, filenames) in walk(Menus.MENUS_PATH):
      if(len(filenames) == 0):
        continue
      for filename in filenames:
        name,file_format = filename.split('.')
        if(file_format != "csv"):
          continue
        file_path = path.join(Menus.MENUS_PATH,filename)
        csv_file = open(file_path,"r",encoding='utf8')
        csv_object = csv.reader(csv_file)
        for idx,line in enumerate(csv_object):
          if idx == 0:
            continue
          if len(line) == 0:
            continue
          key = line[0]
          plate_name = line[1]
          value = line[2]
          active = False
          if len(line) > 3:
            active = line[3]
          if len(line) > 3 and not bool(int(active)):
              continue
          value = float(value)
          update_object = {
            key: {
              "name": plate_name,
              "value": value,
            }
          }
          if not self.menu_object.get(name):
            self.menu_object[name] = update_object
            continue
          self.menu_object[name].update(update_object)
        csv_file.close()





if __name__ == "__main__":
  menus = Menus()
  pprint(menus.menu_object)