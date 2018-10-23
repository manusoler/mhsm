#Este archivo esta en encoding: utf-8

"""
Librería para la obtención de información de procesos y hebras a partir
de la dada en el directorio /proc.
"""

import threading
import subprocess
import os


def pgrep(nom_proc):
    """Obtiene los PIDs asociados al proceso con nombre nom_proc usando
    para ello el comando pgrep.
        @nom_proc: Nombre del proceso
    """
    pids = subprocess.Popen(["pgrep", nom_proc],
                        stdout=subprocess.PIPE).communicate()[0]
    if not pids:
        return None
    return pids.split()


def get_threads(pid):
    """Obtiene los PIDs de los threads que posee el proceso identificado con
    el PID pid. Esta informacion se obtiene de /proc/<pid>/task/
        @pid: Pid del proceso
    Devuelve una lista con los PIDs de sus hebras, incluido el suyo.
    """
    try:
        return os.listdir(os.path.join("/proc", str(pid), "task"))
    except OSError:
        return None


def proc_status(pid):
    """ Obtiene informacion del proceso con PID pid leyendo del
    archivo /proc/pid/stat.
        @pid: Pid del proceso
    Devuelve None o un objeto Proceso.
    """
    try:
        # Abrimos el archivo stat correspondiente
        arch = open(os.path.join("/proc", str(pid), "stat"), "rb")
        # Leemos la primera línea separando por espacios
        campos = arch.readline().split()
        # Cerramos el archivo
        arch.close()
    except IOError:
        # Si existe algún error devolvemos None
        return None
    else:
        # Creamos y devolvemos un proceso con la información leida
        # (PID; Nombre; Estado, Num_CPU, Num_Hebras)
        proceso = Proceso(campos[0], campos[1].strip("()"), campos[2],
                        campos[-6], campos[19])
        del campos
        return proceso


def thread_status(padre, thread_pid):
    """Obtiene el estado de una hebra leyendo de
    /proc/padre.pid/task/thread_pid/stat.
        @padre: Objeto de tipo Proceso, padre de la hebra de la que se
            quiere obtener la informacion.
        @thread_pid: Pid de la hebra de la que se quiere obtener información.
    Devuelve None o un objeto de tipo hebra.
    """
    try:
        # Abrimos el archivo stat correspondiente, a partir del
        # direcotorio del padre
        arch = open(os.path.join("/proc", str(padre.pid), "task",
                            str(thread_pid), "stat"), "rb")
        # Leemos la primera línea separando por espacios
        campos = arch.readline().split()
        # Cerramos el archivo
        arch.close()
    except IOError:
        return None  # Si existe algún error devolvemos None
    else:
        # Creamos y devolvemos una hebra con la información leida
        # (PID; Estado, Num_CPU, Padre)
        hebra = Hebra(campos[0], campos[2], campos[-6], padre)
        del campos
        return hebra


class Proceso:
    """Clase para almacenar la información de un determinado proceso."""

    def __init__(self, pid, nombre, estado, num_cpu, num_hebras):
        """Constructor de la clase."""
        self.__pid = pid
        self.__nombre = nombre
        self.__estado = estado
        self.__num_hebras = num_hebras
        self.__num_cpu = num_cpu

    def get_pid(self):
        return self.__pid

    def set_pid(self, pid):
        self.__pid = pid

    def get_nombre(self):
        return self.__nombre

    def set_nombre(self, nombre):
        self.__nombre = nombre

    def get_estado(self):
        return self.__estado

    def set_estado(self, estado):
        self.__estado = estado

    def get_num_hebras(self):
        return self.__num_hebras

    def set_num_hebras(self, num_hebras):
        self.__num_hebras = num_hebras

    def get_num_cpu(self):
        return self.__num_cpu

    def set_num_cpu(self, num_cpu):
        self.__num_cpu = num_cpu

    # Establecemos las propiedades de los atributos
    pid = property(get_pid, set_pid)
    nombre = property(get_nombre, set_nombre)
    estado = property(get_estado, set_estado)
    num_hebras = property(get_num_hebras, set_num_hebras)
    num_cpu = property(get_num_cpu, set_num_cpu)


class Hebra:
    """Clase para almacenar la información de una determinada hebra."""

    def __init__(self, pid, estado, num_cpu, padre):
        """Constructor de la clase."""
        self.__pid = pid
        self.__estado = estado
        self.__num_cpu = num_cpu
        self.__padre = padre

    def get_pid(self):
        return self.__pid

    def set_pid(self, pid):
        self.__pid = pid

    def get_estado(self):
        return self.__estado

    def set_estado(self, estado):
        self.__estado = estado

    def get_num_cpu(self):
        return self.__num_cpu

    def set_num_cpu(self, num_cpu):
        self.__num_cpu = num_cpu

    def get_padre(self):
        return self.__padre

    def set_padre(self, padre):
        self.__padre = padre

    # Establecemos las propiedades de los atributos
    pid = property(get_pid, set_pid)
    estado = property(get_estado, set_estado)
    num_cpu = property(get_num_cpu, set_num_cpu)
    padre = property(get_padre, set_padre)


class Comando:
    """Clase para almacenar la información de un determinado comando."""

    def __init__(self, path, nombre, args, num_cpus):
        """Constructor de la clase."""
        self.__path = path
        self.__nombre = nombre
        self.__args = args
        self.__num_cpus = num_cpus

    def get_path(self):
        return self.__path

    def set_path(self, path):
        self.__path = path

    def get_nombre(self):
        return self.__nombre

    def set_nombre(self, nombre):
        self.__nombre = nombre

    def get_num_cpus(self):
        return self.__num_cpus

    def set_num_cpus(self, num_cpus):
        self.__num_cpus = num_cpus

    def get_args(self):
        return self.__args

    def set_args(self, args):
        self.__args = args

    # Establecemos las propiedades de los atributos
    path = property(get_path, set_path)
    nombre = property(get_nombre, set_nombre)
    num_cpus = property(get_num_cpus, set_num_cpus)
    args = property(get_args, set_args)


class InfoThreads(threading.Thread):
    """Hilo que obtiene toda la información de las hebras de un proceso."""

    def __init__(self, proc, hebras):
        """Constructor de la clase.
            @proc: Objeto procinfo.Proceso del que se quiere obtener
                información de las hebras.
            @hebras: Lista en la que se añadirán tantos objetos
                procinfo.Hebra como hebras tenga el proceso proc.
        """
        self.proc = proc
        self.hebras = hebras
        threading.Thread.__init__(self)
    
    def run(self):
        """Método que se ejecuta al iniciarse la hebra con start().
        Obtiene la información de las hebras de proc y las almacena
        en hebras.
        """
        # Comprobamos que el proceso no sea nulo
        if self.proc is None:
            return 
        # Para cada hebra del proceso
        for hebra in get_threads(self.proc.pid):
            # Obtenemos su información y la metemos en la lista hebras
            self.hebras.append(thread_status(self.proc, hebra))

