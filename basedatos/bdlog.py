#Este archivo esta en encoding: utf-8

"""
Librería para el almacenamiento y la obtención
de información de las cpus, hebras y procesos resultante
de la monitorización de una ejecución en una BD SQLite.

G{importgraph}
"""

import threading
import shutil
from pysqlite2 import dbapi2 as sqlite

from systeminfo import procinfo, cpuinfo


def crearBD(archivo):
    """
    Crea la BD encargada de contener toda la información recogida por
    la monitorización.
    @param archivo: Archivo en el que se creara la BD
    @type archivo: string
    @rtype: void
    """
    conection = sqlite.connect(archivo)
    cursor = conection.cursor()
    cursor.execute("CREATE TABLE Registro (id_registro INTEGER PRIMARY KEY," +
                   "mensaje TEXT)")
    cursor.execute("CREATE TABLE CPU (num_cpu INTEGER PRIMARY KEY,"+
                    "fabricante TEXT, familia TEXT, modelo TEXT, stepping " +
                    "INTEGER, frecuencia INTEGER, cache INTEGER)")
    cursor.execute("CREATE TABLE Momento_CPU (id_cpu INTEGER PRIMARY KEY," +
                    "num_cpu INTEGER, user INTEGER, nice INTEGER, system " +
                    "INTEGER, idle INTEGER, iowait INTEGER, irq INTEGER," +
                    "softirq INTEGER, steal INTEGER, total INTEGER, " +
                    "id_registro INTEGER, FOREIGN KEY (id_registro) " +
                    "REFERENCES Registro(id_registro) FOREIGN KEY (num_cpu)" +
                    " REFERENCES Registro(num_cpu))")
    cursor.execute("CREATE TABLE Proceso (id_proceso INTEGER PRIMARY KEY,"+
                    "pid_proceso INTEGER, nombre_proceso TEXT," +
                    "estado_proceso CHAR, num_hebras INTEGER," +
                    "id_cpu INTEGER, FOREIGN KEY (id_cpu)" +
                    "REFERENCES Registro(id_cpu))")
    cursor.execute("CREATE TABLE Hebra (id_hebra INTEGER PRIMARY KEY, " +
                    "pid_hebra INTEGER, estado_hebra CHAR," +
                    "id_proceso INTEGER, id_cpu INTEGER," +
                    "FOREIGN KEY(id_cpu) REFERENCES Registro(id_cpu)," +
                    "FOREIGN KEY(id_proceso) REFERENCES Proceso(id_proceso))")
    num = cpuinfo.num_cpus()
    for i in range(num):        
        info = cpuinfo.cpuinfo(i)
        cursor.execute("INSERT INTO CPU VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (info[0], info[1], info[2], info[3], info[4],
                            info[5], info[6]))
    conection.commit()
    cursor.close()
    conection.close()


def leer_info(archivo, num_reg):
    """
    Obtiene la toda la informacion de la BD sobre un registro.
    @param archivo: Archivo en el que se encuentra la BD
    @type archivo: string
    @param num_reg: Numero de registro que se quiere leer
    @type num_reg: int
    @return: Tupla de (cpus, proc, hebras, mensaje) donde
        - cpus: Es una lista de objetos cpuinfo.CPU
        - procesos: Es una lista de objetos procinfo.Proceso
        - hebras: Una lista con los objetos procinfo.Hebra del
            proceso proc.
        - mensaje: Es una cadena de texto con informacion acerca del
            registro, puede estar vacia
    @rtype: tuple
    """
    conection = sqlite.connect(archivo)
    cursor = conection.cursor()
    cpus, procesos, hebras = [], [], []
    # Obtenemos las cpus
    cursor.execute("SELECT id_cpu,num_cpu,user,nice,system,idle,iowait,irq," +
                    "softirq,steal,total FROM Momento_CPU, Registro WHERE " +
                    "Registro.id_registro = Momento_CPU.id_registro AND " +
                    "Registro.id_registro = ?", (num_reg,))
    for cpu in cursor.fetchall():
        cpus.append(cpuinfo.CPU(cpu[1], cpu[2], cpu[3], cpu[4], cpu[5],
                                cpu[6], cpu[7], cpu[8], cpu[9], cpu[10]))
        # Ahora consultamos sus procesos
        cursor.execute("SELECT id_proceso,pid_proceso,nombre_proceso," +
                        "estado_proceso,num_hebras FROM Proceso,Momento_CPU" +
                        " WHERE Momento_CPU.id_cpu = Proceso.id_cpu AND " +
                        "Momento_CPU.id_cpu = ?", (cpu[0],))
        for proceso in cursor.fetchall():
            procesos.append(procinfo.Proceso(proceso[1], proceso[2],
                                                proceso[3], cpu[0],
                                                proceso[4]))
            # Ahora consultamos todas sus hebras
            cursor.execute("SELECT pid_hebra, estado_hebra, Hebra.id_cpu " +
                            "FROM Hebra, Proceso WHERE Hebra.id_proceso = " +
                            "Proceso.id_proceso AND Hebra.id_proceso = ?",
                            (proceso[0],))
            for hebra in cursor.fetchall():
                cursor.execute("SELECT num_cpu FROM Momento_CPU WHERE " +
                                "Momento_CPU.id_cpu = ?", (hebra[2],))
                num_cpu = cursor.fetchone()[0]
                hebras.append(procinfo.Hebra(hebra[0], hebra[1],
                                                num_cpu, procesos[-1]))
    cursor.execute("SELECT mensaje FROM Registro WHERE id_registro = ?",
                    (num_reg,))
    mensaje = cursor.fetchone()[0]
    cursor.close()
    conection.close()
    # Devolver los objetos con la infomación obtenida
    return (cpus, procesos, hebras, mensaje)


def escribir_info(info_cpus, procesos, hebras, archivo):
    """
    Guarda la informacion recogida en la BD para poder
    mostrarla mas tarde poco a poco.
    @param info_cpus: Lista con objetos CPU, cada uno de ellos con la
        información de una CPU.
    @type info_cpus: list
    @param procesos: Lista de objetos procinfo.Proceso con la informacion
        de los procesos principal.
    @type procesos: list
    @param hebras: Lista de objetos procinfo.Hebra con la información de
        cada hebra del proceso.
    @type hebras: list
    @param archivo: Archivo en el cual guardar la informacion.
    @type archivo: string
    @rtype: void
    """
    if info_cpus and procesos and hebras:
        conection = sqlite.connect(archivo)
        cursor = conection.cursor()
        # Almaceno el registro
        cursor.execute("INSERT INTO Registro VALUES (null, '')")
        id_reg = cursor.lastrowid
    
        # Almacenamos las CPUs
        id_cpus = []
        for cpu in info_cpus:
            cursor.execute("INSERT INTO Momento_CPU VALUES (null, ?, ?, ?, " +
                            "?, ?, ?, ?, ?, ?, ?, ?)", (cpu.num_cpu, cpu.user,
                            cpu.nice, cpu.system, cpu.idle, cpu.iowait,
                            cpu.irq, cpu.softirq, cpu.steal, cpu.total,
                            id_reg))
            id_cpus.append(cursor.lastrowid)
            
        # Ahora almacenamos los procesos
        for proceso in procesos:
            cursor.execute("INSERT INTO Proceso VALUES (null, ?, ?, ?, ?, ?)",
                           (proceso.pid, proceso.nombre, proceso.estado,
                            proceso.num_hebras,
                            id_cpus[int(proceso.num_cpu)]))
            id_proceso = cursor.lastrowid
            # Finalmente almacenamos sus hebras
            for hebra in hebras:
                if hebra.padre == proceso:
                    cursor.execute("INSERT INTO Hebra VALUES (null, ?, ?, " +
                                    "?, ?)", (hebra.pid, hebra.estado,
                                    id_proceso, id_cpus[int(hebra.num_cpu)]))
        conection.commit()
        cursor.close()
        conection.close()

        
def guardar_comentario(archivo, num_reg, comentario):
    """
    Guarda o edita el comentario de un registro.
    @param archivo: Archivo en el que se encuentra la BD
    @type archivo: string
    @param num_reg: Numero de registro del comentario
    @type num_reg: int
    @param comentario: El comentario a guardar
    @type comentario: string
    @rtype: void
    """
    conection = sqlite.connect(archivo)
    cursor = conection.cursor()
    cursor.execute("UPDATE Registro SET mensaje = ? WHERE id_registro = ?",
                    (comentario, num_reg))
    conection.commit()
    cursor.close()
    conection.close()

    
def num_reg_bd(archivo):
    """
    Obtiene el numero de registros almacenados en la BD.
    @param archivo: Archivo en el que se encuentra la BD
    @type archivo: string
    @return: Numero de registros en la BD
    @rtype: int
    """
    conection = sqlite.connect(archivo)
    cursor = conection.cursor()
    try:
        cursor.execute("SELECT count(*) FROM Registro")
        num_reg = cursor.fetchone()
    except sqlite.OperationalError:
        num_reg = [0]
    cursor.close()
    conection.close()
    return num_reg[0]


def guardar_monitorizacion(bd, archivo):
    """
    Guarda en un archivo una copia de la base de datos creada
    en la monitorización.
    @param bd: Archivo en el que se encuentra la BD
    @type bd: string
    @param archivo: Archivo destino de la copia de la BD
    @type archivo: string
    @rtype: void
    """
    shutil.copyfile(bd, archivo)


def cargar_monitorizacion(bd, archivo):
    """
    Carga un archivo como BD de una monitorización.
    @param bd: Archivo en el que se encuentra la BD
    @type bd: string
    @param archivo: Archivo destino de la carga de la BD
    @type archivo: string
    @rtype: void
    """
    shutil.copyfile(archivo, bd)


def get_num_cpus(archivo):
    """
    Obtiene el numero de CPUs de la monitorizacion del archivo.
    @param archivo: Archivo en el que se encuentra la BD
    @type archivo: string
    @return: Numero de CPUs de la monitorizacion
    @rtype: int
    """
    conection = sqlite.connect(archivo)
    cursor = conection.cursor()
    cursor.execute("SELECT COUNT(*) FROM CPU")
    num_cpus = cursor.fetchone()[0]
    cursor.close()
    conection.close()
    return num_cpus


def get_cpu_info(archivo, num_cpu=0):
    """
    Obtiene la informacion de la cpu especificada.
    @param archivo: Archivo en el que se encuentra la BD
    @type archivo: string
    @param num_cpu: Numero de la cpu de la que se quiere informacion
    @type num_cpu: int
    @return: None o lista formada por:
            - num_cpu: Numero de procesador
            - fabricante: Fabricante
            - familia: Familia de la CPU
            - modelo: Modelo
            - stepping: Stepping
            - frecuencia: Frecuenca Mhz
            - cache: Cache
    @rtype: list
    """
    conection = sqlite.connect(archivo)
    cursor = conection.cursor()
    try:
        cursor.execute("SELECT * FROM CPU WHERE num_cpu = ?", (num_cpu,))
        info = cursor.fetchone()
        cursor.close()
        conection.close()
        return info
    except sqlite.OperationalError:
        cursor.close()
        conection.close()
        return None


def get_cpu_model(archivo, num_cpu=0):
    """
    Obtiene el modelo de la cpu especificada en el archivo.
    @param archivo: Archivo en el que se encuentra la BD
    @type archivo: string
    @param num_cpu: Numero de la cpu de la que se quiere informacion
    @type num_cpu: int
    @return: Modelo de la cpu
    @rtype: string
    """
    conection = sqlite.connect(archivo)
    cursor = conection.cursor()
    try:
        cursor.execute("SELECT modelo FROM CPU WHERE num_cpu = ?", (num_cpu,))
        modelo = cursor.fetchone()
        cursor.close()
        conection.close()
        if modelo is not None:
            return modelo[0]
        return None
    except sqlite.OperationalError:
        cursor.close()
        conection.close()
        return None


def get_num_reg_comentados(archivo):
    """
    Obtiene una lista con los registros que tienen algun comentario.
    @param archivo: Archivo en el que se encuentra la BD
    @type archivo: string
    @return: Una lista con los numeros de los registros que tienen
        comentarios.
    @rtype: list
    """
    conection = sqlite.connect(archivo)
    cursor = conection.cursor()
    try:
        cursor.execute("SELECT id_registro FROM Registro WHERE " +
                        "mensaje != ''")
        modelo = cursor.fetchall()
        cursor.close()
        conection.close()
        if modelo is not None:
            ids = []
            for i in modelo:
                ids.append(i[0])
        return ids
    except sqlite.OperationalError:
        cursor.close()
        conection.close()
        return []


def get_num_threads(archivo, num_cpu):
    """
    Obtiene la suma total de threads que se han ejecutado en una CPU.
    @param archivo: Archivo en el que se encuentra la BD
    @type archivo: string
    @param num_cpu: Numero de la cpu de la que se quiere informacion
    @type num_cpu: int
    @return: Suma total de threads que se han ejecutado en la CPU.
    @rtype: int
    """
    conection = sqlite.connect(archivo)
    cursor = conection.cursor()
    try:
        cursor.execute("SELECT count(*) FROM Hebra, Momento_CPU WHERE " +
                        "Hebra.id_cpu = Momento_CPU.id_cpu AND num_cpu = ?",
                        (num_cpu,))
        modelo = cursor.fetchone()
        cursor.close()
        conection.close()
        if modelo is not None:
            return modelo[0]
        return 0
    except sqlite.OperationalError:
        cursor.close()
        conection.close()
        return 0


def get_num_threads_in_frame(archivo, num_cpu, frame):
    """
    Obtiene el numero de threads que se han ejecutado en una CPU
    en un frame determinado.
    @param archivo: Archivo en el que se encuentra la BD
    @type archivo: string
    @param num_cpu: Numero de la cpu de la que se quiere
        informacion
    @type num_cpu: int
    @param frame: Numero del frame del que se quiere informacion
    @type frame: int
    @return: Threads que se han ejecutado en la CPU en el frame
        indicado
    @rtype: int
    """
    conection = sqlite.connect(archivo)
    cursor = conection.cursor()
    try:
        cursor.execute("SELECT count(*) FROM Hebra, Momento_CPU WHERE " +
                        "Hebra.id_cpu = Momento_CPU.id_cpu AND num_cpu = ? AND id_registro = ?",
                        (num_cpu, frame))
        modelo = cursor.fetchone()
        cursor.close()
        conection.close()
        if modelo is not None:
            return modelo[0]
        return 0
    except sqlite.OperationalError:
        cursor.close()
        conection.close()
        return 0


def get_num_threads_by_state(archivo, state, cpu=-1, frame=-1):
    """
    Obtiene el numero de threads en el estado especificado en la
    cpu en el frame especificado.
    @param archivo: Archivo en el que se encuentra la BD
    @type archivo: string
    @param state: Indica el estado de los threads. Puede tomar uno de los
        siguientes valores:
            - 'R': Running
            - 'S': Sleeping 
            - 'D': Waiting
            - 'Z': Zombie
            - 'T': Stopped
            - 'W': Paging]
    @type state: char
    @param cpu: Indica la cpu de la que se quieren obtener el numero de threads
        Si cpu = -1 se obtienen los threads de todas las cpus
    @type cpu: int
    @param frame: Indica el frame del cual se quieren obtener los thread.
        Si frame = -1 se devuelven todos los threads de la monitorizacion
        para la cpu especificada
    @type frame: int
    @return: Numero de threads en el estado 'state' que han estado
        en la cpu 'cpu' en el frame 'frame'
    @rtype: int
    """
    conection = sqlite.connect(archivo)
    cursor = conection.cursor()
    try:
        if frame == -1 and cpu == -1:
            cursor.execute("SELECT count(*) FROM Hebra, Momento_CPU WHERE " +
                            "Hebra.id_cpu = Momento_CPU.id_cpu AND " +
                            "Hebra.estado_hebra = ?", (state,))
        elif frame >= 0 and cpu == -1:
            cursor.execute("SELECT count(*) FROM Hebra, Momento_CPU WHERE " +
                            "Hebra.id_cpu = Momento_CPU.id_cpu AND " +
                            "Hebra.estado_hebra = ? AND id_registro = ?",
                            (state, frame))
        elif frame == -1 and cpu >= 0:
            cursor.execute("SELECT count(*) FROM Hebra, Momento_CPU WHERE " +
                            "Hebra.id_cpu = Momento_CPU.id_cpu AND " +
                            "Hebra.estado_hebra = ? AND num_cpu = ?",
                            (state,cpu))
        else:
            cursor.execute("SELECT count(*) FROM Hebra, Momento_CPU WHERE " +
                            "Hebra.id_cpu = Momento_CPU.id_cpu AND " +
                            "Hebra.estado_hebra = ? AND num_cpu = ? AND " +
                            "id_registro = ?", (state,cpu,frame))
        modelo = cursor.fetchone()
        cursor.close()
        conection.close()
        return modelo[0]
    except sqlite.OperationalError:
        cursor.close()
        conection.close()
        return 0


def get_thread_state(archivo, pid, frame):
    """
    Obtiene el estado del thread en el frame indicado
    @param archivo: Archivo en el que se encuentra la BD
    @type archivo: string
    @param pid: Pid de la hebra
    @type pid: int
    @param frame: Frame del thread
    @type frame: int
    @return: Estado del thread en el frame indicado.
    @rtype: str
    """
    conection = sqlite.connect(archivo)
    cursor = conection.cursor()
    try:
        cursor.execute("SELECT DISTINCT estado_hebra FROM Hebra, " +
                        "Momento_CPU WHERE Hebra.id_cpu = " +
                        "Momento_CPU.id_cpu AND Hebra.pid_hebra = ? AND id_registro = ?",
                        (pid, frame))
        modelo = cursor.fetchone()
        cursor.close()
        conection.close()
        if modelo is not None:
            return modelo[0]
        return None
    except sqlite.OperationalError:
        cursor.close()
        conection.close()
        return None

def get_threads_pid(archivo, frame_init=0, frame_end=-1, estado='R'):
    """
    Obtiene el pid de los threads en el estado especificado que se han ejecutado
    entre los frames indicados.
    @param archivo: Archivo en el que se encuentra la BD
    @type archivo: string    
    @param frame_init: Frame de inicio
    @type frame_init: int    
    @param frame_end: Frame final
    @type frame_end: int
    @return: Pid de los threads que se han ejecutado entre los frames
        indicados.
    @rtype: int
    """
    conection = sqlite.connect(archivo)
    cursor = conection.cursor()
    try:
        if frame_end == -1:
            cursor.execute("SELECT DISTINCT pid_hebra FROM Hebra, " +
                            "Momento_CPU WHERE Hebra.id_cpu = " +
                            "Momento_CPU.id_cpu AND Hebra.estado_hebra = ? AND id_registro >= ?",
                            (estado, frame_init))
        else:
            cursor.execute("SELECT DISTINCT pid_hebra FROM Hebra, " +
                            "Momento_CPU WHERE Hebra.id_cpu = " +
                            "Momento_CPU.id_cpu AND Hebra.estado_hebra = ? AND id_registro >= ? AND " +
                            "id_registro <= ?", (estado, frame_init, frame_end))
        modelo = cursor.fetchall()
        cursor.close()
        conection.close()
        return modelo
    except sqlite.OperationalError:
        cursor.close()
        conection.close()
        return None


def get_thread_num_cpu_by_frame(archivo_bd, pid, frame):
    """
    Obtiene el numero de la cpu en la que se ejecuta una hebra
    en un frame determinado.
    @param archivo_bd: Archivo en el que se encuentra la BD
    @type archivo_bd: string   
    @param pid: Pid de la hebra
    @type pid: int
    @param frame: Frame
    @type frame: int
    @return: CPU en la que se ejecuta una hebra en un frame determinado.
    @rtype: int
    """
    conection = sqlite.connect(archivo_bd)
    cursor = conection.cursor()
    try:
        cursor.execute("SELECT num_cpu FROM Hebra, Momento_CPU WHERE " +
                        "Hebra.id_cpu = Momento_CPU.id_cpu AND " +
                        "Hebra.pid_hebra = ? AND id_registro = ?",
                        (pid, frame))
        modelo = cursor.fetchone()
        cursor.close()
        conection.close()
        if modelo is None:
            return None
        return modelo[0]
    except sqlite.OperationalError:
        cursor.close()
        conection.close()
        return None


class SaveToBD(threading.Thread):
    """
    Hilo para guardar la informacion de un estado concreto
    durante una monitorizacion en la BD.
    """
    def __init__(self, info_cpus, proc, hebras, archivo):
        """
        Constructor de la clase.
        @param info_cpus: Lista con objetos CPU, cada uno de ellos con la
            informacion de una CPU.
        @type info_cpus: list
        @param proc: Proceso con la informacion del proceso principal.
        @type proc: Proceso
        @param hebras: Lista de objetos Hebra con la informacion de
            cada hebra del proceso principal.
        @type hebras: list
        @param archivo: Nombre o ruta del archivo de la BD.
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
        Metodo que se ejecuta al iniciar la hebra con start().
        Escribe tanto proc como las hebras en el archivo de la BD.
        @rtype: void
        """
        # Empezamos parados,esperando que nos indiquen
        self.stop_event.wait()
        while self.monitorizando:
            # Escribimos la informacion en la BD
            escribir_info(self.info_cpus, self.proc, self.hebras,
                            self.archivo)
            # Establezco el evento a bloqueado
            self.stop_event.clear()
            # Espero a que me vuelvan a necesitar
            self.stop_event.wait()

    def set_info_cpus(self, info_cpus):
        """
        Establece la nueva informacion sobre las cpus.
        @param info_cpus: Lista con objetos CPU, cada uno de ellos con la
            informacion de una CPU.
        @type info_cpus: list
        @rtype: void
        """
        self.info_cpus = info_cpus

    def set_proc(self, proc):
        """
        Establece la nueva informacion sobre el proceso.
        @param proc: Proceso con la informacion del proceso principal.
        @type proc: procinfo.Proceso
        @rtype: void
        """
        self.proc = proc

    def set_hebras(self, hebras):
        """
        Establece la nueva informacion sobre las hebras.
        @param hebras: Lista de objetos Hebra con la informacion de
            cada hebra del proceso principal.
        @type hebras: list
        @rtype: void
        """
        self.hebras = hebras

