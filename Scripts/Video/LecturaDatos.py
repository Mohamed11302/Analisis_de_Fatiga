import json

RUTA_JSON = "Output_fatigue/Jsons/Fatigue_default_20231207_135831.json"
with open(RUTA_JSON, "r") as archivo:
    datos_json = json.load(archivo)

d = datos_json['repeticiones'][0]["avisos"]
string = ""
for i in d:
    string += i + "\n"

print(string)

#print(datos_json)
