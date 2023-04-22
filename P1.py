import subprocess
import RPi.GPIO as gpio
import time as delay
import datetime as dataHora

# ---- Mapeamente de Hardware ----
btMove, btDirEnter, btDelete, enable, dir, pulso = 11, 10, 12, 16, 18, 19
ledRestart, ledConfir = 13, 15

# ---- Variáveis Auxiliares ----
tempo1 = contPassos = limiteSuperior = timeLedConfir = tempo3 = 0
bitDir, bit1, libera, liberaLedConfir, flagCalibrado, flagDelayFoto, flagCalibradoX = False, False, True, False, False, False, False
motorPasso = [enable, dir, pulso]
contPress = 0
passoMain = 0.001
passoAjuste = 0.001

# --- Horários De Execusão ----
alarmes = [19.58, 21.39, 0.50]

gpio.setmode(gpio.BOARD)
gpio.setwarnings(False)

gpio.setup(btMove, gpio.IN, pull_up_down=gpio.PUD_UP)
gpio.setup(btDirEnter, gpio.IN, pull_up_down=gpio.PUD_UP)
gpio.setup(btDelete, gpio.IN, pull_up_down=gpio.PUD_UP)
gpio.setup(motorPasso, gpio.OUT)
gpio.setup(ledRestart, gpio.OUT)
gpio.setup(ledConfir, gpio.OUT)

# ---- Inicialização ----
gpio.output(pulso, 0)
gpio.output(enable, 1)
gpio.output(dir, 0)
gpio.output(ledConfir, 0)  # ledConfirm = Led RESTART

gpio.add_event_detect(btDelete, gpio.FALLING, callback=funBtDelete, bouncetime=200)

# ---- Funções Auxiliares ----
def funBtDelete():
    pass

def movimenta(GPIO):  #btMove - Função para movimentar bandeja
    global contPassos, libera, passo, passoAjuste
    tempo4 = 0
    if libera:
        gpio.add_event_detect(btDirEnter, gpio.FALLING, callback=inverteDir, bouncetime=200)
        libera = False
    while not gpio.input(btMove):
        gpio.output(pulso, 1)
        tempo4 = delay.time_ns()
        while delay.time_ns() - tempo4 < 2000000:
            continue
            # delay.sleep(passoAjuste)
        gpio.output(pulso, 0)
        tempo4 = delay.time_ns()
        while delay.time_ns() - tempo4 < 2000000:
            continue
        # delay.sleep(passoAjuste)
        if bitDir:
            contPassos += 1
        else:
            contPassos -= 1

def inverteDir(GPIO):  # btDirEnter -Funçao para mudar de direção a bandeja, e para desativar bloqueio de reinício
    global contPassos, bitDir, limiteSuperior, libera, timeLedConfir, liberaLedConfir, contPress, flagCalibrado
    gpio.remove_event_detect(btDirEnter)
    libera = True
    contTempo = tempo2 = 0
    bitDir = not bitDir
    print(bitDir)
    gpio.output(dir, bitDir)
    while not gpio.input(btDirEnter):
        if 10000 * (delay.time() - tempo2) >= 10:
            tempo2 = delay.time()
            contTempo += 1
            print(contTempo)
            if contTempo >= 500:
                contPress += 1
                if contPress == 1:
                    contPassos = 0
                elif contPress == 2:
                    contPress = 0
                    flagCalibrado = True
                    gpio.output(ledRestart, 1)
                    limiteSuperior = contPassos
                print(contPassos, limiteSuperior)
                gpio.output(ledConfir, 1)
                timeLedConfir = delay.time()
                liberaLedConfir = True
                break

def pulsos():
    global pulso, passoMain
    gpio.output(pulso, 1)
    tempo4 = delay.time_ns()
    while delay.time_ns() - tempo4 < 2000000:
        continue
        # delay.sleep(passoMain)
    gpio.output(pulso, 0)
    tempo4 = delay.time_ns()
    while delay.time_ns() - tempo4 < 2000000:
        continue
        # delay.sleep(passoMain)


def desceSobe(DIR, limiar):  # DIR=False(desce bandeja)
    gpio.output(dir, DIR)
    contador = 0
    while contador < limiar:
        pulsos()
        contador += 1


def procedimentoMain():
    global limiteSuperior
    desceSobe(True, limiteSuperior)  # Sobe bandeja
    delay.sleep(5)  # Delay para bandeja se estabilizar
    subprocess.call("./tiraFoto.sh")  # Tira foto
    delay.sleep(3)  # Delay para descer bandeja
    desceSobe(False, limiteSuperior)  # Desce bandeja


gpio.add_event_detect(btDirEnter, gpio.FALLING)

# ---- Bloqueio de Reinício ----
while not gpio.event_detected(btDirEnter):
    if 1000 * (delay.time() - tempo1) >= 400:
        tempo1 = delay.time()
        bit1 = not bit1
        gpio.output(ledRestart, bit1)

gpio.output(ledRestart, 0)
gpio.remove_event_detect(btDirEnter)
gpio.add_event_detect(btMove, gpio.FALLING, callback=movimenta, bouncetime=200)
# ------------------------------

while True:
    gpio.output(pulso, 0)
    # limiteSuperior=790
    # procedimentoMain()
    if liberaLedConfir and 1000 * (delay.time() - timeLedConfir) >= 1500:  # Aciona Led de confirmação ou de reinício
        gpio.output(ledConfir, 0)
        liberaLedConfir = False
        if flagCalibrado:
            gpio.output(ledRestart, 0)
            desceSobe(False, limiteSuperior)  # Desce bandeja
            flagCalibradoX = True

    if flagCalibradoX:  # Sistema já calibrado
        strHoras = dataHora.datetime.now()
        for x in alarmes:  # Varre lista de horários
            if flagDelayFoto == False and strHoras.hour == int(x) and strHoras.minute == round((x - int(x)) * 100):
                procedimentoMain()  # Executa operação
                flagDelayFoto = True
                tempo3 = delay.time()
                break
        print(round(delay.time() - tempo3))
        if delay.time() - tempo3 >= 55:
            flagDelayFoto = False

gpio.remove_event_detect(btMove)
gpio.cleanup()




