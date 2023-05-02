import pywhatkit
from time import sleep as delay
from time import  sleep
from datetime import datetime
import requests, json

trava = 1

while True:
    try:
        while True:
            delay(5)
            urlBanco = 'https://fir-exemplo-a5c5a.firebaseio.com/.json'
            response = requests.get(urlBanco)
            if(response.status_code == 200):
                codeZap = response.json()['codZap']['code']
                print('ok1')
                if codeZap.find('com/') != -1:
                    nada, codeZap = codeZap.split('com/')
                    print('ok2')
                horarios = response.json()['horarios']
                agora = datetime.now()
                print(f'Horário: {agora}, codeZap: {codeZap}, Horários: {horarios}')
                if horarios:
                    print('ok3')
                    for key in horarios:
                        horario = horarios[key]
                        horas, minutos = horario.split(':')
                        #horas = "0" + horas 
                        print(f'Horas: {horas}, Minutos: {minutos}')
                        if(str(agora.hour) == horas and str(agora.minute) == minutos and trava):
                            trava = 0
                            if(agora.day < 10):
                                stringDay = f'0{agora.day}'
                            else:
                                stringDay = str(agora.day)
                            if(agora.month < 10):
                                stringMes = f'0{agora.month}'
                            else:
                                stringMes = str(agora.month)

                            stringEnviar = f'*{stringDay}-{stringMes}-{agora.year}*: Sistema atuando *{agora.hour}h{agora.minute}min*.'
                            print(stringEnviar)
                            pywhatkit.sendwhats_image(codeZap, "image1.jpg", stringEnviar, 15, True, 3)
                else:
                    print('ok4')
    except:
        print('except')

    finally:
        print('finally')
