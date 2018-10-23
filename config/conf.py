#coding: utf-8

"""
Modulo para la gestion del archivo de configuracion del monitor de hebras.

G{importgraph}
"""

import os
import string
import ConfigParser


DIR_CONF_PATH = os.path.join(os.environ["HOME"],".monitorhebras")
"""Localizacion de la carpeta con la configuracion del monitor
para el usuario"""

CONF_PATH = os.path.join(DIR_CONF_PATH,"monitor.conf")
"""Localizacion del archivo de configuracion del usuario"""

DICT_ESTADOS = {0: "running", 1: "sleeping", 2: "waiting", 3: "zombie",
                4: "stopped", 5: "pagging" }
"""Estados de los procesos"""

LOAD_WORK = { "Without ACS": 0,
            "Signals": 1,
            "Mono-socket bloqueante": 2,
            "Mono-socket no bloqueante": 3,
            "Multi-socket bloqueante": 4,
            "Multi-socket no bloqueante": 5,
            "Memoria Compartida": 6 }
"""Metodos de carga de trabajo"""

LANGUAGES = { "Español": 0, "English": 1 }
"""Idiomas de la interfaz"""

REPRODUCCION = {"PRINCIPIO": 0, "ACTUAL": 1, "PREGUNTAR": 2}
"""Modos de comenzar la reproduccion"""

PRINCIPIO = 0
ACTUAL = 1
PREGUNTAR = 2

SORT = {"PID":0, "NOMBRE":1, "ESTADO":2}
"""Orden de las hebras mostradas"""

SORT_BY_PID = 0
SORT_BY_NOMBRE = 1
SORT_BY_ESTADO = 2


class ConfigError(Exception):
    """
    Excepcion lanzada cuando existen errores al leer/escribir en el
    archivo de configuracion.
    """
    def __init__(self, value):
        """
        Instanciador de la clase.
        @param value: Mensaje de la excepcion.
        @type value: string
        """
        self.value = value
        Exception.__init__(self, value)


def crear_configuracion2(procesos="", colores=["#00ff00", "#0000ff", "#ffff00", "#000000", "#ff0000", "#ff00ff"],
                    log_path=os.path.join(DIR_CONF_PATH, "monitor.log"), t_refresco="0.5", tipo_monit=1, 
                    num_tasks=100, num_threads=32, load_work="Without ACS", debug=True, get_tid="224", 
                    periodicity=1, incr=10, comandos=[], lang="Español"):
    """
    Crea un nuevo archivo de configuracion con valores por defecto o bien
    con lo valores especificados. Tambien crea la  carpeta de configuracion
    del proyecto en la home del usuario en caso de no existir.
    @param procesos: Una lista con los nombres de los procesos que se
        quieren monitorizar.
    @type procesos: list
    @param colores: Una lista con los colores para cada uno de los estados
        de un proceso.
    @type colores: list
    @param log_path: Ruta del archivo de log.
    @type log_path: string
    @param t_refresco: Tiempo en el que se van monitorizando los procesos.
    @type t_refresco: float
    @param tipo_monit: Tipo de monitorizacion. Puede tomar los valores 1, si la
        monitorizacion es leyendo de /proc, o 2, si la monitorizacion
        es del planificador ACS.
    @type tipo_monit: int
    @param num_tasks: Numero de tareas ...
    @type num_tasks: int
    @param num_threads: Numero de hebras...
    @type num_threads: int
    @param load_work: Metodo de carga de trabajo que utilizara el
        planificador ACS. Toma un valor de los siguientes:
            - "Without ACS"
            - "Signals"
            - "Mono-socket bloqueante"
            - "Mono-socket no bloqueante"
            - "Multi-socket bloqueante"
            - "Multi-socket no bloqueante"
            - "Memoria Compartida"
    @type load_work: string
    @param debug: Indica si el planificador debe o no
        mostrar mensajes sobre lo que esta pasando con los 
        comandos.
    @type debug: bool
    @param get_tid: Numero de la llamada al sistema con la que obtener el 
        TID de una hebra
    @type get_tid: int
    @param periodicity: Periodicidad de los informes de las hebras al planificador.
        Puede ser 1, si va a ser mediante incrementos/decrementos de cargas
        de trabajo o 2, si sera mediante señales.
    @type periodicity: int
    @param incr: Numero de incrementos/decrementos de cargas de trabajo para informar.
    @type incr: int
    @param comandos: Lista de objetos procinfo.Comandos, con los comandos a ejecutar
        para que el planificador ACS los planifique.
    @type comandos: list
    @param lang: Lenguaje del programa. Puede ser
        - "Español"
        - "English"
    @type lang: string
    @rtype: void
    """
    if not os.path.lexists(DIR_CONF_PATH):
        os.mkdir(DIR_CONF_PATH)  # Creamos la carpeta .monitorhebras en la home del usuario si no esta creada

    conf = ConfigParser.ConfigParser()
    # En primer lugar se crean las distintas secciones
    conf.add_section("proc")
    conf.add_section("acs")
    conf.add_section("advanced")
    # Ahora creamos las opciones y le añadimos sus valores
    # En primer lugar las opciones de monitorizar de /proc
    proc = ""
    if procesos:
        proc = string.join(procesos, " ")
    conf.set("proc", "procesos", proc)
    # Ahora la conf del planificador ACS
    conf.set("acs", "tasks", str(num_tasks))
    conf.set("acs", "threads", str(num_threads))
    conf.set("acs", "load_work", load_work)
    conf.set("acs", "debug", str(debug))
    conf.set("acs", "get_tid", str(get_tid))
    conf.set("acs", "periodicity", str(periodicity))
    conf.set("acs", "incr", str(incr))
    #TODO: for cmd in comandos:

    # Finalmente la configuracion avanzada
    for i in range(len(DICT_ESTADOS)):
        conf.set("advanced", DICT_ESTADOS[i], colores[i])
    conf.set("advanced", "bd_log", log_path)
    conf.set("advanced", "delay", t_refresco)
    conf.set("advanced", "lang", lang)
    conf.set("advanced", "monit", str(tipo_monit))
    # Finalmente creamos el archivo y escribimos la configuracion.
    f = open(CONF_PATH, "w")
    conf.write(f)
    f.close()
    open(log_path, "w").close()      # Creamos el archivo de log vacio
    # Devolvemos las caracteristicas aplicadas
    return (procesos, colores, log_path, t_refresco, tipo_monit,
                    num_tasks, num_threads, load_work, debug, get_tid, 
                    periodicity, incr, comandos, lang)


def escribir_configuracion2(procesos, colores, log_path, t_refresco, tipo_monit,
                    num_tasks, num_threads, load_work, debug, get_tid, 
                    periodicity, incr, comandos, lang):
    """
    Escribe en el archivo de configuracion los nuevos valores establecidos.
    @param procesos: Una lista con los nombres de los procesos que se
        quieren monitorizar.
    @type procesos: list
    @param colores: Una lista con los colores para cada uno de los estados
        de un proceso.
    @type colores: list
    @param log_path: Ruta del archivo de log.
    @type log_path: string
    @param t_refresco: Tiempo en el que se van monitorizando los procesos.
    @type t_refresco: float
    @param tipo_monit: Tipo de monitorizacion. Puede tomar los valores 1, si la
        monitorizacion es leyendo de /proc, o 2, si la monitorizacion
        es del planificador ACS.
    @type tipo_monit: int
    @param num_tasks: Numero de tareas ...
    @type num_tasks: int
    @param num_threads: Numero de hebras...
    @type num_threads: int
    @param load_work: Metodo de carga de trabajo que utilizara el
        planificador ACS. Toma un valor de los siguientes:
            - "Without ACS"
            - "Signals"
            - "Mono-socket bloqueante"
            - "Mono-socket no bloqueante"
            - "Multi-socket bloqueante"
            - "Multi-socket no bloqueante"
            - "Memoria Compartida"
    @type load_work: string
    @param debug: Indica si el planificador debe o no
        mostrar mensajes sobre lo que esta pasando con los 
        comandos.
    @type debug: bool
    @param get_tid: Numero de la llamada al sistema con la que obtener el 
        TID de una hebra
    @type get_tid: int
    @param periodicity: Periodicidad de los informes de las hebras al planificador.
        Puede ser 1, si va a ser mediante incrementos/decrementos de cargas
        de trabajo o 2, si sera mediante señales.
    @type periodicity: int
    @param incr: Numero de incrementos/decrementos de cargas de trabajo para informar.
    @type incr: int
    @param comandos: Lista de objetos procinfo.Comandos, con los comandos a ejecutar
        para que el planificador ACS los planifique.
    @type comandos: list
    @param lang: Lenguaje del programa. Puede ser
        - "Español"
        - "English"
    @type lang: string
    @rtype: void
    @raise ConfigError: Cuando no se encuentra el archivo de configuracion
        o bien cuando este esta mal formado. En cualquier caso la mejor
        solucion seria volver a crearlo con los nuevos valores.
    """
    conf = ConfigParser.ConfigParser()
    if not conf.read([CONF_PATH]):
        raise ConfigError("Archivo de configuración no encontrado.")
    try:    
        # Escribimos los procesos a monitorizar
        if procesos:
            conf.set("proc", "procesos", string.join(procesos, " "))
        else:        
            conf.set("proc", "procesos", "")
        # Ahora la conf del planificador ACS
        conf.set("acs", "tasks", str(num_tasks))
        conf.set("acs", "threads", str(num_threads))
        conf.set("acs", "load_work", load_work)
        conf.set("acs", "debug", str(debug))
        conf.set("acs", "get_tid", str(get_tid))
        conf.set("acs", "periodicity", str(periodicity))
        conf.set("acs", "incr", str(incr))
        #TODO: for cmd in comandos:
    
        # Finalmente la configuracion avanzada
        for i in range(len(DICT_ESTADOS)):
            conf.set("advanced", DICT_ESTADOS[i], colores[i])
        conf.set("advanced", "bd_log", log_path)
        conf.set("advanced", "delay", t_refresco)
        conf.set("advanced", "lang", lang)
        conf.set("advanced", "monit", str(tipo_monit))
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        raise ConfigError("Archivo de configuración mal formado.")
    else:
        f = open(CONF_PATH, "w")
        conf.write(f)
        f.close()


def leer_configuracion2():
    """
    Lee el archivo de configuracion del usuario y devuelve una lista con
    los datos de la configuracion.
    @return: Una lista con los siguientes elementos:
        - Lista con los procesos a monitorizar.
        - Una lista con los colores para los diferentes estados.
        - La ruta del archivo de log 
        - El tiempo de refresco de los datos
        - Tipo de monitorizacion. Puede tomar los valores
            - 1, si la monitorizacion es leyendo de /proc
            - 2 si la monitorizacion es del planificador ACS
        - Numero de tareas
        - Numero de hebras
        - Metodo de carga de trabajo que utilizara el planificador ACS.
            Toma un valor de los siguientes:
                - "Without ACS"
                - "Signals"
                - "Mono-socket bloqueante"
                - "Mono-socket no bloqueante"
                - "Multi-socket bloqueante"
                - "Multi-socket no bloqueante"
                - "Memoria Compartida"
        - Booleano que indica si el planificador debe o no mostrar mensajes
            sobre lo que esta pasando con los comandos.
        - Numero de la llamada al sistema con la que obtener el TID
            de una hebra
        - Periodicidad de los informes de las hebras al planificador.
            Puede ser:
                - 1 si va a ser mediante incrementos/decrementos de cargas
                    de trabajo 
                - 2 si sera mediante señales
        - Numero de incrementos/decrementos de cargas de trabajo para informar
        - Lista de objetos procinfo. Lista de comandos con los comandos a
            ejecutar para que el planificador ACS los planifique.
        - Lenguaje del programa. Es un string que puede ser "Español", "English"
    @rtype: list
    @raise ConfigError: Si el archivo no se encuentra.
    """
    conf = ConfigParser.ConfigParser()
    try:
        if not conf.read([CONF_PATH]):
            raise ConfigError("Archivo de configuración no encontrado.")
    except ConfigParser.MissingSectionHeaderError:
        raise ConfigError("Archivo de configuración mal formado.")

    try:
        # Obtenemos los procesos
        procesos = conf.get("proc", "procesos").split()
        # Numero de tareas
        num_tasks = int(conf.get("acs", "tasks"))
        # Num hebras        
        num_threads = int(conf.get("acs", "threads"))
        # Metodo de carga de trabajo
        load_work = conf.get("acs", "load_work")
        # Debug
        debug = True
        if conf.get("acs", "debug") == "False":
            debug = False
        # Get_TID
        get_tid = int(conf.get("acs", "get_tid"))
        # Periodicidad
        periodicity = int(conf.get("acs", "periodicity"))
        # Incrementos
        incr = int(conf.get("acs", "incr"))
        # TODO: Comandos
        comandos = []
        # Obtenemos los colores
        colores = []
        for i in range(len(DICT_ESTADOS)):
            colores.append(conf.get("advanced", DICT_ESTADOS[i]))
        # Obtenemos la ruta del archivo log
        log_path = conf.get("advanced", "bd_log")
        # Tiempo de refresco
        t_refresco = conf.get("advanced", "delay")
        # Idioma
        lang = conf.get("advanced", "lang")
        # Tipo de monitorizacion
        tipo_monit = int(conf.get("advanced", "monit"))
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        raise ConfigError("Archivo de configuraciￃﾳn mal formado.")
    else:
        return (procesos, colores, log_path, t_refresco, tipo_monit,
                    num_tasks, num_threads, load_work, debug, get_tid, 
                    periodicity, incr, comandos, lang)


def escribir_configuracion3(procesos, colores, log_path, t_refresco, lang, tmp_rep, comenz_rep, sort):
    """
    Escribe en el archivo de configuracion los nuevos valores establecidos.
    @param procesos: Una lista con los nombres de los procesos que se
        quieren monitorizar.
    @type procesos: list
    @param colores: Una lista con los colores para cada uno de los estados
        de un proceso.
    @type colores: list
    @param log_path: Ruta del archivo de log
    @type log_path: string
    @param t_refresco: Tiempo en el que se van monitorizando los procesos
    @type t_refresco: float
    @param lang: Lenguaje del programa. Puede ser
        - "Español"
        - "English"
    @type lang: string
    @param tmp_rep: Tiempo de visualizacion entre registros en la pantalla
        de reproduccion
    @type tmp_rep: float
    @param comenz_rep: Modo en el que se comienza la reproduccion:
        - siempre por el primer registro (PRIMERO - 0)
        - siempre por el actual (ACTUAL - 1)
        - se pregunta al reproducir (PREGUNTAR - 2)
    @type comenz_rep: int
    @param sort: El orden que llevaran las hebras al mostrarse en la lista:
        - C{SORT['PID']}
        - C{SORT['NOMBRE']}
        - C{SORT['ESTADO']}
    @type sort: int
    @rtype: void
    @raise ConfigError: Cuando no se encuentra el archivo de configuracion o
        bien cuando este esta mal formado. En cualquier caso la mejor solucion
        seria volver a crearlo con los nuevos valores.
    """
    conf = ConfigParser.ConfigParser()
    if not conf.read([CONF_PATH]):
        raise ConfigError("Archivo de configuración no encontrado.")
    try:    
        # Escribimos la conf de la monitorizacion
        if procesos:
            conf.set("monitoring", "processes", string.join(procesos, " "))
        else:        
            conf.set("monitoring", "processes", "")
        conf.set("monitoring", "delay", t_refresco)
        
        # Ahora la conf de la visualizacion
        conf.set("visualize", "start", str(comenz_rep))
        conf.set("visualize", "delay", str(tmp_rep))
    
        # Finalmente la configuracion avanzada
        for i in range(len(DICT_ESTADOS)):
            conf.set("advanced", DICT_ESTADOS[i], colores[i])
        conf.set("advanced", "bd_log", log_path)
        conf.set("advanced", "lang", lang)
        conf.set("advanced", "sort", sort)
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        raise ConfigError("Archivo de configuración mal formado.")
    else:
        with open(CONF_PATH, "w") as f:
            conf.write(f)


def leer_configuracion3():
    """
    Lee el archivo de configuracion del usuario y devuelve una lista con
    los datos de la configuracion del usuario.
    @return: Una lista compuesta por:
        - Una lista con los procesos a monitorizar.
        - Una lista con los colores para los diferentes estados.
        - La ruta del archivo de log 
        - El tiempo de refresco de los datos
        - Lenguaje del programa
            - "Español"
            - "English"
        - Tiempo de visualizacion entre registros en la pantalla de
            reproduccion
        - Modo en el que se comienza la reproduccion
            - siempre por el primer registro (PRIMERO - 0)
            - siempre por el actual (ACTUAL - 1)
            - se pregunta al reproducir (PREGUNTAR - 2)
        - El orden que llevaran las hebras al mostrarse en la lista:
            - C{SORT['PID']}
            - C{SORT['NOMBRE']}
            - C{SORT['ESTADO']}
    @rtype: list
    @raise ConfigError: Si el archivo no se encuentra
    """
    conf = ConfigParser.ConfigParser()
    try:
        if not conf.read([CONF_PATH]):
            raise ConfigError("Archivo de configuración no encontrado.")
    except ConfigParser.MissingSectionHeaderError:
        raise ConfigError("Archivo de configuración mal formado.")

    try:
        # Obtenemos los procesos
        procesos = conf.get("monitoring", "processes").split()
        # Tiempo de refresco
        t_refresco = conf.get("monitoring", "delay")
        # Obtenemos el tiempo entre registros en reproduccion
        tmp_rep = conf.get("visualize", "delay")
        #Obtenemos el modo de comenzar la reproduccion
        comenz_rep = int(conf.get("visualize", "start"))
        # Obtenemos los colores
        colores = []
        for i in range(len(DICT_ESTADOS)):
            colores.append(conf.get("advanced", DICT_ESTADOS[i]))
        # Obtenemos la ruta del archivo log
        log_path = conf.get("advanced", "bd_log")
        # Idioma
        lang = conf.get("advanced", "lang")
        # Orden de las hebras
        sort = conf.get("advanced", "sort")
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        raise ConfigError("Archivo de configuración mal formado.")
    else:
        return (procesos, colores, log_path, t_refresco, lang,
                tmp_rep, comenz_rep, sort)
        
def crear_configuracion3(procesos="", colores=["#00ff00", "#0000ff", "#ffff00", "#000000", "#ff0000", "#ff00ff"],
                    log_path=os.path.join(DIR_CONF_PATH, "monitor.log"), t_refresco="0.5", 
                    lang="Español", tmp_rep="0.5", comenz_rep=PRINCIPIO, sort=SORT["PID"]):
    """
    Crea un nuevo archivo de configuracion con valores por defecto o bien con
    lo valores especificados. Tambien crea la  carpeta de configuracion del
    proyecto en la home del usuario en caso de no existir.
    @param procesos: Una lista con los nombres de los procesos que se
        quieren monitorizar.
    @type procesos: list
    @param colores: Una lista con los colores para cada uno de los estados
        de un proceso.
    @type colores: list
    @param log_path: Ruta del archivo de log
    @type log_path: string
    @param t_refresco: Tiempo en el que se van monitorizando los procesos
    @type t_refresco: float
    @param lang: Lenguaje del programa. Puede ser
        - "Español"
        - "English"
    @type lang: string
    @param tmp_rep: Tiempo de visualizacion entre registros en la pantalla
        de reproduccion
    @type tmp_rep: float
    @param comenz_rep: Modo en el que se comienza la reproduccion:
        - siempre por el primer registro (PRIMERO - 0)
        - siempre por el actual (ACTUAL - 1)
        - se pregunta al reproducir (PREGUNTAR - 2)
    @type comenz_rep: int
    @param sort: El orden que llevaran las hebras al mostrarse en la lista:
        - C{SORT['PID']}
        - C{SORT['NOMBRE']}
        - C{SORT['ESTADO']}
    @type sort: int
    @rtype: void
    """
    if not os.path.lexists(DIR_CONF_PATH):
        os.mkdir(DIR_CONF_PATH)  # Creamos la carpeta .monitorhebras en la home del usuario si no esta creada

    conf = ConfigParser.ConfigParser()
    # En primer lugar se crean las distintas secciones
    conf.add_section("monitoring")
    conf.add_section("visualize")
    conf.add_section("advanced")
    # Ahora creamos las opciones y le añadimos sus valores
    # En primer lugar las opciones de monitorizar de /proc
    proc = ""
    if procesos:
        proc = string.join(procesos, " ")
    conf.set("monitoring", "processes", proc)
    conf.set("monitoring", "delay", t_refresco)
    
    # Ahora la conf de la reproduccion
    conf.set("visualize", "delay", str(tmp_rep))
    conf.set("visualize", "start", str(comenz_rep))

    # Finalmente la configuracion avanzada
    for i in range(len(DICT_ESTADOS)):
        conf.set("advanced", DICT_ESTADOS[i], colores[i])
    conf.set("advanced", "bd_log", log_path)
    conf.set("advanced", "lang", lang)
    conf.set("advanced", "sort", sort)
    
    # Finalmente creamos el archivo y escribimos la configuracion.
    with open(CONF_PATH, "w") as f:
        conf.write(f)
    open(log_path, "w").close()      # Creamos el archivo de log vacio
    # Devolvemos las caracteristicas aplicadas
    return (procesos, colores, log_path, t_refresco,
                    lang, tmp_rep, comenz_rep, sort)
    
