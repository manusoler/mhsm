#Este archivo usa encoding: utf-8

"""
Módulo encargado de la generación de graficas

G{importgraph}
"""

import Gnuplot
import pyExcelerator

from basedatos import bdlog

DATA_FILE = "data.dat"

def create_chart_threads_by_cpus(archivo_bd, archivo_datos=DATA_FILE,
                                    excel=False, png=False):
    """
    Crea un histograma dibujado por Gnuplot del numero de threads
    (por estado) en cada cpu en toda la simulacion.
    @param archivo_bd: El archivo que contiene la bd con toda la informacion
        de la monitorizacion
    @type archivo_bd: string
    @param archivo_datos: El archivo en el que se guardaran los datos de la
        la grafica
    @type archivo_datos: string
    @param excel: Booleano que indica si se quiere generar un archivo excel
        con los datos
    @type excel: bool
    @param png: Booleano que indica si se quiere generar una imagen png en 
        lugar de pintar la grafica con gnuplot
    @type png: bool
    @rtype: void
    """
    # Obtengo los datos necesarios de la BD
    datos = __get_datos_threads_by_cpus(archivo_bd)
    # Creo el archivo de datos que utiliza Gnuplot para dibujar las graficas
    __create_data_file(datos, archivo_datos)
    # Creo la hoja de calculo si se especifica
    if excel:
        __create_spreadsheet_file(datos, archivo_datos)
    # Defino la grafica
    if png:
        gp = __define_histogram("Estados de los threads en cada CPU (%)",
                                "CPUs", "% Threads", archivo_datos)
    else:
        gp = __define_histogram("Estados de los threads en cada CPU (%)",
                                "CPUs", "% Threads")
    # Creo el comando para dibujar la grafica
    num_cpus = bdlog.get_num_cpus(archivo_bd)
    if num_cpus > 1:
        plot = "plot '" + archivo_datos + "' using 2 ti col,"
        for cpu in range(num_cpus-2):
            plot += " '' using " + str(cpu+3) + " ti col, "
        plot += " '' using " + str(num_cpus+1) + ":key(1) ti col"
    else:
        plot = "plot '"+archivo_datos+"' using 2:key(1) ti col"
    # Y la pinto
    gp(plot)


def create_chart_threads_in_cpus(archivo_bd, frame_init=1, frame_end=-1,
                                archivo_datos=DATA_FILE, excel=False,
                                png=False):
    """
    Crea un histograma dibujado por Gnuplot del numero de threads
    por cpu en cada frame.
    @param archivo_bd: El archivo que contiene la bd con toda la informacion
        de la monitorizacion
    @type archivo_bd: string
    @param frame_init: Frame inicial desde cual ver los threads.
    @type frame_init: int
    @param frame_end: Frame final hasta el que ver los threads.
    @type frame_end: int
    @param archivo_datos: El archivo en el que se guardaran los datos de la
        la grafica
    @type archivo_datos: string
    @param excel: Booleano que indica si se quiere generar un archivo excel
        con los datos
    @type excel: bool
    @param png: Booleano que indica si se quiere generar una imagen png en 
        lugar de pintar la grafica con gnuplot
    @type png: bool
    @rtype: void
    """
    if frame_end == -1:
        frame_fin = bdlog.num_reg_bd(archivo_bd)
    else:
        frame_fin = frame_end
    # Obtengo los datos necesarios de la BD
    datos = __get_datos_threads_in_cpus(archivo_bd, frame_init, frame_fin)
    # Creo el archivo de datos que utiliza Gnuplot para dibujar las graficas
    __create_data_file(datos, archivo_datos)
    # Creo la hoja de calculo si se especifica
    if excel:
        __create_spreadsheet_file(datos, archivo_datos)
    # Defino la grafica
    if png:
        gp = __define_histogram("Threads por CPU en cada frame",
                                "Frames", "Número de Threads", archivo_datos, "clustered")
    else:
        gp = __define_histogram("Threads por CPU en cada frame",
                                "Frames", "Número de Threads", "", "clustered")
    # Creo el comando para dibujar la grafica
    num_cpus = bdlog.get_num_cpus(archivo_bd)
    if num_cpus > 1:
        plot = "plot '" + archivo_datos + "' using 2 ti col,"
        for cpu in range(num_cpus-2):
            plot += " '' using " + str(cpu+3) + " ti col, "
        plot += " '' using " + str(num_cpus+1) + ":key(1) ti col"
    else:
        plot = "plot '"+archivo_datos+"' using 2:key(1) ti col"
    # Y la pinto
    gp(plot)


def create_chart_threads_by_frames(archivo_bd, cpu=-1, frame_init=1,
                                    frame_end=-1, archivo_datos=DATA_FILE,
                                    excel=False, png=False):
    """
    Crea un histograma del numero de threads (por estado) por frame de la
    simulacion (desde frame_init hasta frame_end). Siendo cada thread de la
    cpu indicada o los threads totales si cpu = -1.
    @param archivo_bd: El archivo que contiene la bd con toda la informacion
        de la monitorizacion
    @type archivo_bd: string
    @param cpu: Cpu de la cual se quieren ver los threads o todas si es -1.
    @type cpu: int
    @param frame_init: Frame inicial desde cual ver los threads.
    @type frame_init: int
    @param frame_end: Frame final hasta el que ver los threads.
    @type frame_end: int
    @param archivo_datos: El archivo en el que se guardaran los datos de la
        la grafica
    @type archivo_datos: string
    @param excel: Booleano que indica si se quiere generar un archivo excel
        con los datos
    @type excel: bool
    @param png: Booleano que indica si se quiere generar una imagen png en 
        lugar de pintar la grafica con gnuplot
    @type png: bool
    @rtype: void
    """
    if frame_end == -1:
        frame_fin = bdlog.num_reg_bd(archivo_bd)
    else:
        frame_fin = frame_end
    # Obtengo los datos necesarios de la BD
    datos = __get_datos_threads_by_frames(archivo_bd, cpu, frame_init,
                                        frame_fin)
    # Creo el archivo de datos que utiliza Gnuplot para dibujar la grafica
    __create_data_file(datos, archivo_datos)
    # Creo la hoja de calculo
    if excel:
        __create_spreadsheet_file(datos, archivo_datos)
    # Establecemos el titulo
    if cpu == -1:
        titulo = "Estados de los threads totales por frames"
    else:
        titulo = "Estados de los threads en la CPU"+str(cpu)+" por frames"
    titulo += " ( "+str(frame_init)+" a "+str(frame_fin)+" )"
    # Definimos la grafica
    if png:
        gp = __define_histogram(titulo, "Frames", "Número de Threads",
                                archivo_datos)
    else:
        gp = __define_histogram(titulo, "Frames", "Número de Threads")
    # Creamos el comando para dibujar la grafica
    if frame_fin - frame_init > 0:
        plot = "plot '"+archivo_datos+"' using 2 ti col,"
        for frame in range(frame_fin - frame_init - 1):
            plot += " '' using " + str(frame+3) + " ti col, "
        plot += " '' using " + str(frame_fin+1) + ":key(1) ti col"
    else:
        plot = "plot '"+archivo_datos+"' using 2:key(1) ti col"
    # Y la pinto
    gp(plot)


def create_chartline_threads_by_frames(archivo_bd, colores, cpu=-1,
                                        frame_init=1, frame_end=-1,
                                        archivo_datos=DATA_FILE,
                                        excel=False, png=False):
    """
    Crea una grafica del numero de threads (por estado) por frame de la
    simulacion (desde frame_init hasta frame_end). Siendo cada threads de la
    cpu indicada.
    @param archivo_bd: El archivo que contiene la bd con toda la informacion
        de la monitorizacion
    @type archivo_bd: string
    @param colores: Lista con los 6 colores de los estados con los que se
        pintara la grafica
    @type colores: list
    @param cpu: Cpu de la cual se quieren ver los threads.
    @type cpu: int
    @param frame_init: Frame inicial desde cual ver los threads.
    @type frame_init: int
    @param frame_end: Frame final hasta el que ver los threads.
    @type frame_end: int
    @param archivo_datos: El archivo en el que se guardaran los datos de la
        la grafica
    @type archivo_datos: string
    @param excel: Booleano que indica si se quiere generar un archivo excel
        con los datos
    @type excel: bool
    @param png: Booleano que indica si se quiere generar una imagen png en 
        lugar de pintar la grafica con gnuplot
    @type png: bool
    @rtype: void
    """
    if frame_end == -1:
        frame_fin = bdlog.num_reg_bd(archivo_bd)
    else:
        frame_fin = frame_end
    # Obtengo los datos necesarios de la BD
    datos = __get_datos_frames_by_threads(archivo_bd, cpu, frame_init,
                                        frame_fin)
    # Creo el archivo de datos que utiliza Gnuplot para dibujar las graficas
    __create_data_file(datos, archivo_datos)
    # Creo la hoja de calculo si se especifica
    if excel:
        __create_spreadsheet_file(datos, archivo_datos)
    # Definimos el titulo de la grafica
    if cpu == -1:
        titulo = "Estados de los threads totales por frames"
    else:
        titulo = "Estados de los threads en la CPU"+str(cpu)+" por frames"
    titulo += " ( "+str(frame_init)+" a "+str(frame_fin)+" )"
    # Y la grafica
    if png:
        gp = __define_linechart(titulo, "Frames", "Número de Threads",
                                archivo_datos)
    else:
        gp = __define_linechart(titulo, "Frames", "Número de Threads")
    # Ahora se define el rango del eje x
    gp('set xrange ['+str(frame_init)+':'+str(frame_fin)+']')
    # Y se construye el comando para dibujar la grafica
    plot = "plot '" + archivo_datos + "' using 1:2 ti col w lines lc rgb '"
    plot += __change_color_format(colores[0]) + "', '' u 1:3 ti col w \
            lines lc rgb '" + __change_color_format(colores[1]) + "', '' u \
            1:4 ti col w lines lc rgb '" + __change_color_format(colores[2])
    plot += "', '' u 1:5 ti col w lines lc rgb '" 
    plot += __change_color_format(colores[3]) + "', '' u 1:6 ti col w lines \
            lc rgb '" + __change_color_format(colores[4]) + "', '' u 1:7 ti \
            col w lines lc rgb '" + __change_color_format(colores[5]) + "'"
    # Finalmente se dibuja
    gp(plot)


def create_thread_migration(archivo_bd, frame_init=1, frame_end=-1,
                            archivo_datos=DATA_FILE, excel=False, png=False):
    """
    Crea una grafica en la que se muestra la migracion de los threads por
    las distintas cpus.
    @param archivo_bd: El archivo que contiene la bd con toda la informacion
        de la monitorizacion
    @type archivo_bd: string
    @param frame_init: Frame inicial desde cual ver los threads.
    @type frame_init: int
    @param frame_end: Frame final hasta el que ver los threads.
    @type frame_end: int
    @param archivo_datos: El archivo en el que se guardaran los datos de la
        la grafica
    @type archivo_datos: string
    @param excel: Booleano que indica si se quiere generar un archivo excel
        con los datos
    @type excel: bool
    @param png: Booleano que indica si se quiere generar una imagen png en 
        lugar de pintar la grafica con gnuplot
    @type png: bool
    @rtype: void
    """
    if frame_end == -1:
        frame_fin = bdlog.num_reg_bd(archivo_bd)
    else:
        frame_fin = frame_end
    # Obtengo los datos necesarios de la BD
    datos = __get_datos_threads_migration(archivo_bd, frame_init, frame_fin)
    # Creo el archivo de datos que utiliza Gnuplot para dibujar la grafica
    __create_data_file(datos, archivo_datos)
    # Creo la hoja de calculo si se especifica
    if excel:
        __create_spreadsheet_file(datos, archivo_datos)
    # Defino el titulo de la grafica
    titulo = "Migración de threads"
    titulo += " ( "+str(frame_init)+" a "+str(frame_fin)+" )"
    # Y se define la grafica
    if png:
        gp = __define_linechart(titulo, "Frames", "CPUs", archivo_datos)
    else:
        gp = __define_linechart(titulo, "Frames", "CPUs")
    # Ahora se define el rango del eje x
    gp('set xrange ['+str(frame_init)+':'+str(frame_fin)+']')
    # Establezco las etiquetas de la Y en funcion de las cpus
    gp('unset ytics')
    #gp("set yrange [-1:"+str(bdlog.get_num_cpus(archivo_bd))+"]")
    # Obtenemos el numero total de threads
    num_threads = len(bdlog.get_threads_pid(archivo_bd, frame_init, frame_fin))
    ytic = str(float(num_threads-1)/2)
    tics = 'set ytics ( "CPU0" ' + ytic
    cpus = bdlog.get_num_cpus(archivo_bd)
    for i in range(cpus-1):
        ytic = float((num_threads + 1) * (i + 1) + (num_threads - 1) + (num_threads + 1) * (i + 1)) / 2
        tics += ', "CPU' + str(i+1) + '" ' + str(ytic)
    tics += ")"
    gp(tics)
    # Construimos el comando para dibujar la grafica    
    num_pids = len(bdlog.get_threads_pid(archivo_bd, frame_init, frame_fin))
    plot = "plot '"+archivo_datos+"' using 1:2 ti col w linespoint"
    for i in range(num_pids-1):
        plot += ", '' u 1:" + str(i+3) + " ti col w linespoint"
    for i in range(cpus-1):
        plot += ", '' u 1:" + str(num_pids+i+2) + "ti '' w line lw 1.5 lc rgb '#000000'"
    # Y se dibuja
    gp(plot)


def __get_datos_threads_by_frames(archivo_bd, cpu, frame_init, frame_end):
    """
    Obtiene los datos de los threads (por estado) en cada frame
    (desde frame_init hasta frame_end) de la ejecucion dependiendo de la cpu.
    @param archivo_bd: El archivo que contiene la bd con toda la informacion
        de la monitorizacion
    @type archivo_bd: string
    @param cpu: Cpu de la cual se quieren ver los threads. Si cpu = -1 se obtienen
        los datos de todos los threads.
    @type cpu: int
    @param frame_init: Frame inicial desde cual ver los threads.
    @type frame_init: int
    @param frame_end: Frame final hasta el que ver los threads.
    @type frame_end: int
    @return: Lista de los datos de los threads
    @rtype: list
    """
    estados = "RSDZTW"
    nombre_estados = ["Running", "Sleeping", "Waiting", "Zombie",
                        "Sttoped", "Paging"]
    datos = [["Estados", ]]
    # Se ponen los estados en la cabecera de los datos
    for frame in range(frame_init, frame_end+1):
        datos[0].append(str(frame))
    # Se crea la matriz de datos por estados
    for i in range(len(estados)):
        lista_estados = [nombre_estados[i], ]
        # Para cada estado incluimos todos los frames
        for frame in range(frame_init, frame_end+1):
            lista_estados.append(bdlog.get_num_threads_by_state(archivo_bd,
                                                                estados[i],
                                                                cpu, frame))
        datos.append(lista_estados)
    return datos


def __get_datos_threads_by_cpus(archivo_bd):
    """
    Obtiene los datos y crea el vector
    @param archivo_bd: El archivo que contiene la bd con toda la informacion
        de la monitorizacion
    @type archivo_bd: string
    @return: Lista de los datos de los threads
    @rtype: list
    """
    estados = "RSDZTW"
    nombre_estados = ["Running", "Sleeping", "Waiting", "Zombie",
                        "Sttoped", "Paging"]
    datos = [["Estados", ]]
    num_cpus = bdlog.get_num_cpus(archivo_bd)
    # Se ponen las cpus en la cabecera de los datos
    for cpu in range(num_cpus):
        datos[0].append("CPU"+str(cpu))
    # Se crea la matriz de datos por estados
    for i in range(len(estados)):
        lista_estados = [nombre_estados[i], ]
        # Para cada estado incluimos todos las cpus
        for cpu in range(num_cpus):
            thr_estate = bdlog.get_num_threads_by_state(archivo_bd,
                                                        estados[i], cpu)
            tot_thread = bdlog.get_num_threads(archivo_bd, cpu)
            lista_estados.append(thr_estate * 100 / tot_thread)
        datos.append(lista_estados)
    return datos


def __get_datos_threads_in_cpus(archivo_bd, frame_init, frame_end):
    """
    Obtiene los datos y crea el vector
    @param archivo_bd: El archivo que contiene la bd con toda la informacion
        de la monitorizacion
    @type archivo_bd: string
    @param frame_init: Frame inicial desde cual ver los threads.
    @type frame_init: int
    @param frame_end: Frame final hasta el que ver los threads.
    @type frame_end: int
    @return: Lista de los datos de los threads
    @rtype: list
    """
    datos = [["Estados", ]]
    num_cpus = bdlog.get_num_cpus(archivo_bd)
    # Se ponen las cpus en la cabecera de los datos
    for cpu in range(num_cpus):
        datos[0].append("CPU"+str(cpu))
    # Se crea la matriz de datos por estados
    for i in range(frame_init, frame_end+1):
        lista = [i, ]
        # Para cada estado incluimos todos las cpus
        for cpu in range(num_cpus):
            num_threads = bdlog.get_num_threads_in_frame(archivo_bd,
                                                        cpu, i)
            lista.append(num_threads)
        datos.append(lista)
    return datos


def __get_datos_frames_by_threads(archivo_bd, cpu, frame_init, frame_end):
    """
    Obtiene los datos de los threads (por estado) en cada frame
    (desde frame_init hasta frame_end) de la ejecucion dependiendo de la cpu.
    @param archivo_bd: El archivo que contiene la bd con toda la informacion
        de la monitorizacion
    @type archivo_bd: string
    @param cpu: Cpu de la cual se quieren ver los threads. Si cpu = -1 se obtienen
        los datos de todos los threads.
    @type cpu: int
    @param frame_init: Frame inicial desde cual ver los threads.
    @type frame_init: int
    @param frame_end: Frame final hasta el que ver los threads.
    @type frame_end: int
    @return: Lista de los datos de los threads
    @rtype: list
    """
    estados = "RSDZTW"
    datos = [["Frames", "Running", "Sleeping", "Waiting", "Zombie",
                "Sttoped", "Paging"]]
    # Creamos listas de estados para cada frame y la incluimos en los datos
    for frame in range(frame_init, frame_end+1):
        lista_frame = [str(frame)]
        for estado in estados:
            lista_frame.append(bdlog.get_num_threads_by_state(archivo_bd,
                                                                estado, cpu,
                                                                frame))
        datos.append(lista_frame)
    return datos


def __get_datos_threads_migration(archivo_bd, frame_init, frame_fin):
    """
    Obtiene los datos de los threads en cada frame para obtener
    su migracion por las cpus
    @param archivo_bd: El archivo que contiene la bd con toda la informacion
        de la monitorizacion
    @type archivo_bd: string
    @param frame_init: Frame inicial desde cual ver los threads.
    @type frame_init: int
    @param frame_fin: Frame final hasta el que ver los threads.
    @type frame_fin: int
    @return: Lista de los datos de los threads
    @rtype: list
    """
    datos = [["Frames", ]]
    # Obtenemos los pids de las hebras entre los frames indicados
    pids = bdlog.get_threads_pid(archivo_bd, frame_init, frame_fin)
    # Se incluyen en los datos
    for pid in pids:
        datos[0].append(str(pid[0]))
    # Anadimos las lineas de separacion entre cpus
    for i in range(bdlog.get_num_cpus(archivo_bd)-1):
        datos[0].append("Sep" + str(i))
    # Se generan listas de cpus segun el pid por cada frame
    for frame in range(frame_init, frame_fin+1):
        lista_frame = [str(frame)]
        i = 0
        for pid in pids:
            cpu = None
            # Comprobamos si el thread estaba en ejecucion en este frame
            if bdlog.get_thread_state(archivo_bd, pid[0], frame) == 'R':
                cpu = bdlog.get_thread_num_cpu_by_frame(archivo_bd, pid[0], frame)            
            # valor = cpu -> Todas las hebras estaran en la misma linea
            if cpu is None:
                # En caso contrario no ponemos su valor ?0
                valor = "?0"
            else:
                valor = i + (len(pids)+1) * int(cpu)
            lista_frame.append(valor)
            i += 1
        for i in range(bdlog.get_num_cpus(archivo_bd)-1):
            valor = len(pids) * (i + 1)
            lista_frame.append(valor)
        datos.append(lista_frame)
    return datos


def __create_data_file(datos, data_file):
    """
    Crea el archivo que va a contener los datos leidos por Gnuplot.
    @param datos: Una lista con las filas de datos que contendra el archivo
    @type datos: list
    @param data_file: El archivo donde se guardaran los datos
    @type data_file: string
    @rtype: void
    """
    with open(data_file, "w") as f:
        for fila in datos:
            for dato in fila:
                f.write(str(dato)+"\t")
            f.write("\n")


def __create_spreadsheet_file(datos, data_file):
    """
    Crea una hoja de calculo con formato EXCEL, con los datos pasados
    @param datos: Una lista con las filas de datos que contendra el archivo
    @type datos: list
    @param data_file: El archivo donde se guardaran los datos en excel
    @type data_file: string
    @rtype: void
    """
    w = pyExcelerator.Workbook()
    ws = w.add_sheet('Datos Monitorizados')
    for i in range(len(datos)):
        for j in range(len(datos[i])):
            ws.write(i, j, datos[i][j])
    w.save(data_file+".xls")


def __define_histogram(title="", xlabel="", ylabel="", png="", tipo="columnstacked"):
    """
    Crea el histograma por defecto y lo devuelve para que tan solo se
    le especifique el archivo que debe dibujar
    @param title: Titulo del histograma (puede ser vacio)
    @type title: string
    @param xlabel: Etiqueta del eje x (puede ser vacio)
    @type xlabel: string
    @param ylabel: Etiqueta del eje y (puede ser vacio)
    @type ylabel: string
    @param png: Ruta de la imagen a guardar como png en lugar de pintar la
        grafica con gnuplot o nada si se desea pintar con gnuplot
    @type png: string
    @param tipo: Tipo de histograma (clustered o columnstacked)
    @type tipo: string
    @return: Objeto Gnuplot de la grafica definida
    @rtype: Gnuplot
    """
    gp = Gnuplot.Gnuplot(persist=1)
    if png:
        #gp('set terminal png nocrop enhanced size 1280, 800')
        #gp('set output "'+png+'.png"')
        gp('set term postscript eps enhanced color')
        gp('set output "'+png+'.eps"')
    gp('set key invert reverse Left outside')
    gp('set key autotitle columnheader')
    gp('set style fill solid 1.000000 border -1')
    gp('set data style histograms')
    gp('set style histogram '+tipo)
    gp('set boxwidth 0.75 absolute')
    gp('set yrange [0:*]')
    gp('set tics scale 0.0')
    gp('set ytics')
    gp('set xtics norotate nomirror')
    if title:
        gp('set title "'+title+'"')
    if ylabel:
        gp('set ylabel "'+ylabel+'"')
    if xlabel:
        gp('set xlabel "'+xlabel+'"')
    return gp


def __define_linechart(title="", xlabel="", ylabel="", png=""):
    """
    Define la grafica de lineas normales y la devuelve para que solo se le
    especifique el archivo que debe dibujar
    @param title: Titulo de la gráfica (puede ser vacio)
    @type title: string
    @param xlabel: Etiqueta del eje x (puede ser vacio)
    @type xlabel: string
    @param ylabel: Etiqueta del eje y (puede ser vacio)
    @type ylabel: string
    @param png: Ruta de la imagen a guardar como png en lugar de pintar la
        grafica con gnuplot o nada si se desea pintar con gnuplot
    @type png: string
    @return: Objeto Gnuplot de la grafica definida
    @rtype: Gnuplot
    """
    gp = Gnuplot.Gnuplot(persist = 1)
    if png:
        #gp('set terminal png nocrop enhanced size 1280, 800')
        #gp('set output "'+png+'.png"')
        gp('set term postscript eps enhanced color')
        gp('set output "'+png+'.eps"')
    gp('set key invert reverse Left outside')
    gp('set data style linespoints')
    gp('set tics scale 0.0')
    gp('set ytics')
    gp('set xtics norotate nomirror')
    if title:
        gp('set title "'+title+'"')
    if ylabel:
        gp('set ylabel "'+ylabel+'"')
    if xlabel:
        gp('set xlabel "'+xlabel+'"')
    return gp


def __change_color_format(color):
    """
    Cambia el color en formato #RRRRGGGGBBBB a #RRGGBB
    @param color: El color en formato #RRRRGGGGBBBB
    @type color: string
    @return: El color en formato #RRGGBB
    @rtype: string
    """
    return color[0:3]+color[5:7]+color[9:11]

