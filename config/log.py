#Este archivo esta en encoding: utf-8

"""
B{I{(OBSOLETO)}} - En su lugar se recomienda el uso del modulo basedatos.bdlog

Librería para el manejo del log que almacenará una serie de registros
que contemplan el estado en un momento determinado de la monitorización
de algún proceso.

G{importgraph}
"""

import threading

from systeminfo import procinfo, cpuinfo


def escribir_log(info_cpus, procesos, hebras, archivo, n_log=50):
    """
    Guarda la informacion recogida en un archivo para poder
    mostrarla mas tarde poco a poco.
    @param info_cpus: Lista con objetos CPU, cada uno de ellos con la
        información de una CPU.
    @type info_cpus: list
    @param procesos: Lista de objetos procinfo.Proceso con la informacion
        de los procesos principal.
    @type procesos: list
    @param hebras: Lista de objetos procinfo.Hebra con la información de
        cada hebra del proceso.
    @type hebras:list
    @param archivo: Archivo en el cual guardar la informacion.
    @type archivo: string
    @param n_log: Numero de registros guardados.
    @type n_log: int
    @rtype: void
    """
    # Abrimos el archivo de log
    arch = open(archivo, "a+")
    # Escribimos el número de cpus
    arch.write(str(len(info_cpus)) + "\n")
    # Escribimos la información de las cpus
    for cpu in info_cpus:
        arch.write(str(cpu.num_cpu) + " " + str(cpu.user) + " " +
                    str(cpu.nice) + " " + str(cpu.system) + " " +
                    str(cpu.idle) + " " + str(cpu.iowait) + " " +
                    str(cpu.irq) + " " + str(cpu.softirq) + " " +
                    str(cpu.steal) + " " + str(cpu.total) + "\n")
    for proc in procesos:
        # Escribimos toda la información del proceso en una línea del archivo
        # (PID, Nombre, Estado, CPU y num_hebras)
        arch.write(proc.pid + " " + proc.nombre + " " + proc.estado + " " +
                    proc.num_cpu + " " + proc.num_hebras + "\n")
        # Y toda la información de cada una de sus hebras (PID, Estado, CPU)
        for hebra in hebras:
            # Comprobamos que sea una hebra del proceso
            if hebra.padre.pid == proc.pid:
                arch.write(hebra.pid + " " + hebra.estado + " " +
                            hebra.num_cpu + "\n")
    # Finalmente escribimos una línea en blanco para identificar
    # el final de registro
    arch.write("\n")
    # Y cerramos el archivo
    arch.close()


def leer_log(archivo, num_reg):
    """
    Lee del archivo de log el registro num_reg.
    @param archivo: Archivo en el cual guardar la informacion.
    @type archivo: int
    @param num_reg: Numero de registro a leer.
    @type num_reg: int
    @return: Una tupla (cpus, proc, hebras) donde:
        - cpus: Es una lista de objetos cpuinfo.CPU
        - procesos: Es una lista de objetos procinfo.Proceso
        - hebras: Una lista con los objetos procinfo.Hebra del proceso proc.
    @rtype: tuple
    """
    try:
        # Abrimos el archivo en modo lectura
        log = open(archivo, "rb")
        # Leemos todas las líneas
        lineas = log.readlines()
        # Cerramos el archivo de log
        log.close()
    except IOError:
        # Si existe algún error devolvemos None
        return (None, None, None)
    else:
        linea, registro = 0, 0
        if num_reg:  # num_reg es disinto de 0
            # Buscamos la línea en la que aparece el registro num_reg
            for i in range(len(lineas)):
                if lineas[i] == "\n":
                    registro += 1
                    if registro == num_reg:
                        linea = i+1
                        break
        # Leemos el número de cpus
        num_cpus = int(lineas[linea].split()[0])
        # Creamos la  lista con los objetos CPU
        cpus, procesos, hebras = [], [], []
        for i in range(1, num_cpus + 1):
            cpui = lineas[linea+i].split()
            cpus.append(cpuinfo.CPU(int(cpui[0]), cpui[1], cpui[2],
                                cpui[3], cpui[4], cpui[5], cpui[6],
                                cpui[7], cpui[8], cpui[9]))
        linea += num_cpus + 1
        # Leer todos los procesos
        while lineas[linea] != "\n":
            # Creamos un objeto proceso con la información de la línea
            j = lineas[linea].split()
            proc = procinfo.Proceso(j[0], j[1], j[2], j[3], j[4])
            # Y lo añadimos a la lista
            procesos.append(proc)
            # Y creamos la lista con la información sobre sus hebras
            for i in range(1, int(proc.num_hebras) + 1):
                j = lineas[linea+i].split()
                hebras.append(procinfo.Hebra(j[0], j[1], j[2], proc))
            # Avanzamos en el fichero
            linea += int(proc.num_hebras) + 1
        # Finalmente devolvemos la tupla
        return (cpus, procesos, hebras)


def num_reg_log(archivo):
    """
    Devuelve el numero de registros que hay en el log.
    @param archivo: Archivo en el cual guardar la informacion.
    @type archivo: string
    @return: Numero de registros en el log
    @rtype: int
    """
    try:
        # Abrimos el archivo en modo lectura
        log = open(archivo, "rb")
        # Leemos todas las líneas
        lineas = log.readlines()
        # Cerramos el archivo de log
        log.close()
    except IOError:
        # En caso de error se devuelve 0
        return 0
    else:
        num_reg = 0
        # Recorremos las líneas buscando los saltos de línea que
        # indican comienzo/fin de un registro
        for linea in lineas:
            if linea == "\n":
                num_reg += 1
        # Devolvemos el número de registros
        return num_reg



class SaveToFile(threading.Thread):
    """
    Hilo para guardar la información de un estado concreto
    durante una monitorización.
    """

    def __init__(self, info_cpus, proc, hebras, archivo):
        """
        Constructor de la clase.
        @param info_cpus: Lista con objetos CPU, cada uno de ellos con la
            información de una CPU.
        @type info_cpus: list
        @param proc: Objeto procinfo.Proceso con la información del
            proceso principal.
        @type proc: procinfo.Proceso
        @param hebras: Lista de objetos procinfo.Hebra con la información de
            cada hebra del proceso principal.
        @type hebras: list
        @param archivo: Nombre o ruta del archivo de log.
        @type archivo: string
        """
        self.monitorizando = True
        self.stop_event = threading.Event()
        self.info_cpus = info_cpus
        self.proc = proc
        self.hebras = hebras
        self.archivo = archivo
        threading.Thread.__init__(self)

    def run(self):
        """
        Método que se ejecuta al iniciar la hebra con start().
        Escribe tanto proc como las hebras en el archivo de log.
        @rtype: void
        """
        # Empezamos parados,esperando que nos indiquen
        self.stop_event.wait()
        while self.monitorizando:
            # Establezco el evento a bloqueado
            self.stop_event.clear()
            # Escribimos la información en el log
            escribir_log(self.info_cpus, self.proc, self.hebras, self.archivo)
            # Espero a que me vuelvan a necesitar
            self.stop_event.wait()

    def set_info_cpus(self, info_cpus):
        """
        Establece la nueva informacion sobre las cpus.
        @param info_cpus: La nueva informacion sobre las cpus
        @type info_cpus: list
        @rtype: void
        """
        self.info_cpus = info_cpus

    def set_proc(self, proc):
        """
        Establece la nueva informacion sobre el proceso.
        @param proc: La nueva informacion sobre el proceso.
        @type proc: procinfo.Proceso
        @rtype: void
        """
        self.proc = proc

    def set_hebras(self, hebras):
        """
        Establece la nueva informacion sobre las hebras.
        @param hebras: La nueva informacion sobre las hebras.
        @type hebras: list
        @rtype: void
        """
        self.hebras = hebras

