#Este archivo esta en encoding: utf-8

"""
Librería para la obtención de información de las cpus de la máquina.

G{importgraph}
"""

import threading
import time


def num_cpus():
    """
    Obtiene el numero de CPU's que existen en el sistema mirando en
    el archivo /proc/cpuinfo.
    Similiar a lo que obtendriamos de ejecutar el comando
    'grep processor /proc/cpuinfo | wc -l'.
    @return: Numero de cpus que tiene la maquina
    @rtype: int
    """
    with open("/proc/cpuinfo", "rb") as arch:
        lineas = arch.readlines()
    cpus = 0
    for linea in lineas:
        if linea.find("processor") >= 0:
            cpus += 1
    del lineas # Eliminamos de memoria el array de lineas
    return cpus


def cpu_info(num_cpu=0, tiempo=0.5):
    """
    Obtiene informacion de la CPU num_cpu leyendo del archivo /proc/stat.
    (Deprecado) Use la funcion cpu_info(num_cpu, cpu_ant) en su lugar
    @param num_cpu: Numero de la CPU
    @type num_cpu: int
    @param tiempo: Tiempo que espera la funcion antes de leer por
        segunda vez el archivo /proc/stat.
    @type tiempo: float
    @return: None o un objeto CPU.
    @rtype: CPU
    """
    try:
        # Leemos el archivo /proc/stat
        with open("/proc/stat", "rb") as arch:
            # Y obtenemos una lista con los tiempos de la cpu num
            info0 = arch.readlines()[num_cpu + 1].split()
        # Esperamos a que se generen mas datos
        time.sleep(tiempo)
        # Ahora volvemos a leer el archivo /proc/stat
        with open("/proc/stat", "rb") as arch:
            info1 = arch.readlines()[num_cpu + 1].split()
        # Finalmente calculamos los tiempos para este intervalo
        total = 0
        for i in range(1, len(info1)):
            info1[i] = int(info1[i]) - int(info0[i])
            total += info1[i]
        info1[-1] = total
        cpu = CPU(num_cpu, info1[1], info1[2], info1[3], info1[4], info1[5],
                    info1[6], info1[7], info1[8], info1[9])
        del info0, info1 # Eliminamos los arrays de memoria
        return cpu
    except IOError:
        return None

def cpu_info(num_cpu=0, cpu_ant=[]):
    """
    Obtiene informacion de la CPU num_cpu leyendo del archivo /proc/stat, y actualiza la lista
    de cpu_ant.
    @param num_cpu: Numero de la CPU
    @type num_cpu: int
    @param cpu_ant: Lista con las estadisticas en el instante anterior (cpu.get_array())
    @type cpu_ant: list
    @return: None o un objeto CPU.
    @rtype: CPU
    """
    try:
        # Leemos el archivo /proc/stat
        with open("/proc/stat", "rb") as arch:
            # Y obtenemos una lista con los tiempos de la cpu num
            info = arch.readlines()[num_cpu + 1].split()
        if cpu_ant:
            #Calculamos la difer. de tiempos con el instante anterior
            total = 0
            for i in range(1, len(info)-1):
                result = int(info[i]) - int(cpu_ant[i-1])
                cpu_ant[i-1] = info[i] # Actualizamos la cpu_ant
                info[i] = result # Nuevo valor de info
                total += int(result) # Se actualiza el valor del tiempo total
            info[-1] = total
        else:
            cpu_ant[0:]=info[1:] # Creamos el primer array de anteriores

        cpu = CPU(num_cpu, info[1], info[2], info[3], info[4], info[5],
                    info[6], info[7], info[8], info[9])
        del info # Borramos el array de memoria
        return cpu
    except IOError:
        return None


def cpuinfo(num_cpu=0):
    """
    Obtiene informacion de la cpu.
    @param num_cpu: Numero de la CPU
    @type num_cpu: int
    @return: None o [num_cpu, fabricante, familia, modelo, stepping,
        frecuencia, cache] donde:
            - B{num_cpu}: Numero de procesador
            - B{fabricante}: Fabricante
            - B{familia}: Familia de la CPU
            - B{modelo}: Modelo
            - B{stepping}: Stepping
            - B{frecuencia}: Frecuenca Mhz
            - B{cache}: Cache
    @rtype: list
    """
    try:
        # Leemos el archivo /proc/cpuinfo
        with open("/proc/cpuinfo", "rb") as arch:
            archivo = arch.readlines()
        info = [num_cpu] # Numero de cpu
        inicio, cpu_found = 0, -1
        for line in archivo:    # Buscamos el inicio de la informacion de la CPU
            if "processor" in line:
                cpu_found += 1
                if cpu_found == num_cpu:
                    break
            inicio += 1
        # Obtenemos el fabricante
        info.append(archivo[inicio+1].split(":")[1].strip())
        # Obtenemos la familia de la CPU
        info.append(archivo[inicio+2].split(":")[1].strip())
        # Modelo
        info.append(archivo[inicio+4].split(":")[1].strip("\n"))
        # Stteping
        info.append(archivo[inicio+5].split(":")[1].strip())
        # Frecuencia
        info.append(archivo[inicio+6].split(":")[1].strip())
        # Cache
        info.append(archivo[inicio+7].split(":")[1].strip())
        del archivo
        return info
    except IOError:
        return None


def cpu_model(num_cpu=0):
    """
    Obtiene el modelo de la cpu num_cpu del archivo.
    @param num_cpu: Numero de la cpu
    @type num_cpu: int
    @return: El modelo de la cpu
    @rtype: string
    """
    # Leemos el archivo /proc/cpuinfo
    with open("/proc/cpuinfo", "rb") as arch:
        archivo = arch.readlines()
    inicio = 27*num_cpu
    # Modelo
    try:
        model = archivo[inicio+4].split(":")[1].strip("\n")
    except IndexError:
        model = "unknown"
    del archivo
    return model



class CPU:
    """
    Clase que almacena la información sobre una CPU
    """
    def __init__(self, num_cpu, user, nice, system, idle, iowait, irq,
                softirq, steal, total):
        """
        Constructor de la clase
        @param num_cpu: Numero de la cpu
        @type num_cpu: int
        @param user: Tiempo de usuario
        @type user: int
        @param nice: Tiempo de privilegios
        @type nice: int
        @param system: Tiempo del sistema
        @type system: int
        @param idle: Tiempo ociosa
        @type idle: int
        @param iowait: Tiempo esperando por operaciones de E/S
        @type iowait: int
        @param irq: Tiempo irq
        @type irq: int
        @param softirq: Tiempo softirq
        @type softirq: int
        @param steal: Tiempo de steal
        @type steal: int
        @param total: Tiempo total
        @type total: int
        """
        self.__num_cpu = num_cpu
        self.__user = user
        self.__nice = nice
        self.__system = system
        self.__idle = idle
        self.__iowait = iowait
        self.__irq = irq
        self.__softirq = softirq
        self.__steal = steal
        self.__total = total

    def get_array(self):
        """
        Devuelve la CPU como un array con los tiempos.
        @return: La CPU como un array con los tiempos.
        @rtype: list
        """
        return [self.num_cpu, self.user, self.nice, self.system,
                self.idle, self.iowait, self.irq, self.softirq,
                self.steal, self.total]

    def get_percen_idle(self):
        """
        Proporciona el % de la CPU que ha estado ociosa.
        @return: El % del tiempo que la CPU ha estado ociosa
        @rtype: string
        """
        if self.total:
            return "%.2f" % (int(self.__idle) / float(self.__total) * 100)
        else:
            return "0.00"

    def get_percen_busy(self):
        """
        Proporciona el % de la CPU que ha estado ocupada.
        @return: El % del tiempo que la CPU ha estado ocupada
        @rtype: string
        """
        try:
            return "%.2f" % ((int(self.__user) + int(self.__nice) +
                            int(self.__system)) / float(self.__total) * 100)
        except ZeroDivisionError:
            return "0.00"

    def get_num_cpu(self):
        """
        Obtiene el numero de la cpu
        @return: El numero de la cpu
        @rtype: int
        """
        return self.__num_cpu

    def set_num_cpu(self, num_cpu):
        """
        Establece el nuevo numero de cpu
        @param num_cpu: El nuevo numero de cpu
        @type num_cpu: int
        @rtype: void
        """
        self.__num_cpu = num_cpu

    def get_user(self):
        """
        Obtiene el tiempo de usuario
        @return: El tiempo de usuario
        @rtype: int
        """
        return self.__user

    def set_user(self, user):
        """
        Establece el nuevo tiempo de usuario
        @param user: El nuevo tiempo de usuario
        @type user: int
        @rtype: void
        """
        self.__user = user

    def get_nice(self):
        """
        Obtiene el tiempo de nice
        @return: El tiempo de nice
        @rtype: int
        """
        return self.__nice

    def set_nice(self, nice):
        """
        Establece el nuevo tiempo de nice
        @param nice: El nuevo tiempo de nice
        @type nice: int
        @rtype: void
        """
        self.__nice = nice

    def get_system(self):
        """
        Obtiene el tiempo de sistema
        @return: El tiempo de sistema
        @rtype: int
        """
        return self.__system

    def set_system(self, system):
        """
        Establece el nuevo tiempo de sistema
        @param system: El nuevo tiempo de sistema
        @type system: int
        @rtype: void
        """
        self.__system = system

    def get_idle(self):
        """
        Obtiene el tiempo ociosa
        @return: El tiempo ociosa
        @rtype: int
        """
        return self.__idle

    def set_idle(self, idle):
        """
        Establece el nuevo tiempo de idle
        @param idle: El nuevo tiempo de idle
        @type idle: int
        @rtype: void
        """
        self.__idle = idle

    def get_iowait(self):
        """
        Obtiene el tiempo de E/S
        @return: El tiempo de E/S
        @rtype: int
        """
        return self.__iowait

    def set_iowait(self, iowait):
        """
        Establece el nuevo tiempo de E/S
        @param iowait: El nuevo tiempo de E/S
        @type iowait: int
        @rtype: void
        """
        self.__iowait = iowait

    def get_irq(self):
        """
        Obtiene el tiempo de irq
        @return: El tiempo de irq
        @rtype: int
        """
        return self.__irq

    def set_irq(self, irq):
        """
        Establece el nuevo tiempo de irq
        @param irq: El nuevo tiempo de irq
        @type irq: int
        @rtype: void
        """
        self.__irq = irq

    def get_softirq(self):
        """
        Obtiene el tiempo de softirq
        @return: El tiempo de softirq
        @rtype: int
        """
        return self.__softirq

    def set_softirq(self, softirq):
        """
        Establece el nuevo tiempo de softirq
        @param softirq: El nuevo tiempo de softirq
        @type softirq: int
        @rtype: void
        """
        self.__softirq = softirq

    def get_steal(self):
        """
        Obtiene el tiempo de steal
        @return: El tiempo de steal
        @rtype: int
        """
        return self.__steal

    def set_steal(self, steal):
        """
        Establece el nuevo tiempo de steal
        @param steal: El nuevo tiempo de steal
        @type steal: int
        @rtype: void
        """
        self.__steal = steal

    def get_total(self):
        """
        Obtiene el tiempo total
        @return: El tiempo total
        @rtype: int
        """
        return self.__total

    def set_total(self, total):
        """
        Establece el nuevo tiempo total
        @param total: El nuevo tiempo total
        @type total: int
        @rtype: void
        """
        self.__total = total

    # Establecemos las propiedades para cada atributo
    num_cpu = property(get_num_cpu,set_num_cpu)
    user = property(get_user,set_user)
    nice = property(get_nice,set_nice)
    system = property(get_system,set_system)
    idle = property(get_idle,set_idle)
    iowait = property(get_iowait,set_iowait)
    irq = property(get_irq,set_irq)
    softirq = property(get_softirq,set_softirq)
    steal = property(get_steal,set_steal)
    total = property(get_total,set_total)


class InfoCPUS(threading.Thread):
    """
    Hilo que obtiene información de las cpus de la máquina.
    """

    def __init__(self, num_cpus, info_cpus):
        """
        Constructor de la clase.
        @param num_cpus: Numero de cpus que tiene la maquina.
        @type num_cpus: int
        @param info_cpus: Lista en la que se guardan los objetos CPUs
            con la información de cada CPU.
        @type info_cpus: list
        """
        self.info_cpus = info_cpus
        self.num_cpus = num_cpus
        threading.Thread.__init__(self)

    def run(self):
        """
        Método que se ejecuta al iniciar la hebra con start().
        """
        # Para cada cpu de la máquina
        for i in range(self.num_cpus):
            # Añadimos la información a la lista
            self.info_cpus.append(cpu_info(i, 0.1))

