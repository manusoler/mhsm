#Este archivo esta en encoding: utf-8

"""
Módulo con todas las hebras utilizadas para la monitorizacion, visualizacion
de la aplicacion.

G{importgraph}
"""

import gtk
import gtk.glade
import threading
import time
import gobject

import interfaz
import events
from basedatos import bdlog
from systeminfo import procinfo, cpuinfo


class Monitorizar(threading.Thread):
    """
    Hebra para la captura de informacion desde /proc
    y crear una hebra para su visualizacion en la interfaz.
    """
    def __init__(self, padre):
        """
        Constructor de la clase.
        @param padre: Interfaz que llama a esta hebra
        @type padre: wMonitorizar
        """
        self.stop_event = threading.Event()
        self.monitorizando = True
        self.padre = padre

        # Establecemos el orden en los TreeViews
        for tree in self.padre.get_trees():
            for column in tree.get_columns():
                column.set_sort_column_id(int(self.padre.get_sort_by()))
        # Hebra para la visualizacion de los resultados en la interfaz
        self.dibujar_result = DibujarResultados(self.padre, None, None, None)
        # Hebra para la escritura de la informacion en el registro
        self.registro = bdlog.SaveToBD(None, None, None, self.padre.get_log_path())
        threading.Thread.__init__(self)

    def run(self):
        """
        Monitoriza los procesos indicados en el archivo de configuracion.
        """
        # Obtengo el numero de cpus del sistema
        num_cpus = cpuinfo.num_cpus()
        # Inicializamos el array de estadisticas de
        # cpus anteriores
        cpus_ant = []
        for i in range(num_cpus):
            cpus_ant.append([])
        # Lanzamos la hebras (sin activarlas)
        self.dibujar_result.start()
        self.registro.start()
        while not self.padre.get_pids():
            # Obtenemos los pid de los procesos
            for proc in self.padre.get_procesos():
                pid = procinfo.pgrep(proc)
                if pid is not None:
                    self.padre.get_pids().append(pid[0])
        while self.monitorizando:
            # Desbloqueo el evento por si esta activado
            #print "Desbloqueo el eventos por si esta activado"
            self.stop_event.clear()
            #print "Iniciamos las listas"
            info_cpus, hebras, procesos = [], [], []
            # Comprobamos si hay pids para monitorizar
            #print "Comprobamos si hay pids:", self.padre.get_pids()
            if not self.padre.get_pids():
                break
            
            # Obtengo la informacion de las cpus lanzando una hebra
            #print "Obtenemos informacion de las cpus"
            for i in range(num_cpus):
                # Añadimos la informacion a la lista
                info_cpus.append(cpuinfo.cpu_info(i, cpus_ant[i]))
            # Recoger la informacion para cada proceso
            #print "Recogemos informacion para cada proceso"
            for pid in self.padre.get_pids():
                proceso = procinfo.proc_status(pid)
                if proceso is not None:
                    procesos.append(proceso)
                    # Obtengo la informacion de las hebras del proceso
                    # a partir de su pid
                    #print "\ty para cada hebra"
                    for hebra in procinfo.get_threads(proceso.pid):
                        if hebra is not None:
                            # Y la metemos en la lista hebras
                            thr = procinfo.thread_status(procesos[-1], hebra)
                            if thr is not None:
                                hebras.append(thr)
                else:
                    # El proceso ya no existe se elimina de la lista de pids
                    self.padre.get_pids().remove(pid)
            # Informamos de los nuevos datos a la hebra encargada
            # de escribir en el registro los resultados.
            #print "Informamos de los nuevos datos para almacenar"
            self.registro.set_info_cpus(info_cpus)
            self.registro.set_proc(procesos)
            self.registro.set_hebras(hebras)
            # Y le indicamos que los escriba
            #print "Indicamos que se escriban"
            self.registro.stop_event.set()
            # Informamos de los nuevos datos a la hebra encargada
            # de dibujar los resultados.
            #print "Informamos de los nuevos datos para dibujar"
            self.dibujar_result.set_info_cpus(info_cpus)
            self.dibujar_result.set_procesos(procesos)
            self.dibujar_result.set_hebras(hebras)
            # Y le indicamos que los dibuje
            #print "Indicamos que se dibujen"
            self.dibujar_result.stop_event.set()
            # Espero un tiempo antes de volver a recoger informacion
            #print "Esperamos antes de volver a realizar todo"
            self.stop_event.wait(float(self.padre.get_t_refresco()))
            #print "Fin del tiempo"
            # Esperamos a las hebras que terminen
            #print "Esperando por si no han terminado las hebras"
            while self.registro.stop_event.is_set() and self.dibujar_result.stop_event.is_set():
                continue
            #print "Eliminamos las listas"
            del info_cpus, hebras, procesos
        # Paramos las hebras
        self.dibujar_result.monitorizando = False
        self.dibujar_result.stop_event.set()
        self.registro.monitorizando = False
        self.registro.stop_event.set()
        self.dibujar_result.join() # Y esperamos que terminen
        self.registro.join()
        if not self.padre.get_pids():
            # Informamos a la clase monitorizar que hemos terminado
            self.padre.finalizar_monitorizacion()


class Reproducir(threading.Thread):
    """
    Hebra para la obtencion de informacion desde la BD
    y crear una hebra para su visualizacion en la interfaz.
    """
    def __init__(self, padre):
        """
        Constructor de la clase.
        @param padre: Interfaz que llama a esta hebra
        @type padre: wReproducir
        """
        self.stop_event = threading.Event()
        self.reproduciendo = True
        self.padre = padre
        self.num_reg_act = self.padre.get_num_reg()
        self.num_reg_tot = self.padre.get_total_reg()
        threading.Thread.__init__(self)

    def run(self):
        """
        Reproduce los registros de la BD como si de una monitorizacion
        se tratara.
        """
        while self.reproduciendo:
            # Desbloqueo el evento por si esta activado
            self.stop_event.clear()
            # Obtengo la informacion necesaria consultando la BD
            (cpus, procesos, hebras, mensaje) = bdlog.leer_info(self.padre.get_log_path(), self.num_reg_act)
            # Y la pintamos en la interfaz
            self.dibujar_informacion(cpus, procesos, hebras, mensaje)
            del cpus, procesos, hebras, mensaje
            # Por ultimo esperamos antes de volver a mostrar mas informacion
            self.stop_event.wait(float(self.padre.get_tmp_rep()))
            # Incrementamos el numero de registro y comprobamos
            #que no hayamos llegado al fin
            self.num_reg_act += 1
            if self.num_reg_act > self.num_reg_tot:
                self.num_reg_act = 1
                break

    def dibujar_informacion(self, cpus, procesos, hebras, mensaje):
        """
        Representa toda la informacion del registro en la interfaz.
        @param cpus: Lista de cpus
        @type cpus: list
        @param procesos: Lista de procesos a dibujar 
        @type procesos: list
        @param hebras: Lista de hebras a dibujar
        @type hebras: list
        @param mensaje: Mensaje a dibujar en la zona de comentarios
        @type mensaje: str
        """
        # Limpiamos las listas
        self.padre.get_lista_proc().clear()
        for lista in self.padre.get_listas():
            lista.clear()
        start, end = self.padre.get_glade().get_widget("txtComentario").get_buffer().get_bounds()
        self.padre.get_glade().get_widget("txtComentario").get_buffer().delete(start, end)
        color = {"R": self.padre.get_colores()[0],
                "S": self.padre.get_colores()[1],
                "D": self.padre.get_colores()[2],
                "Z": self.padre.get_colores()[3],
                "T": self.padre.get_colores()[4],
                "W": self.padre.get_colores()[5]}
        # Mostramos la informacion de cada CPU
        for i in range(len(cpus)):
            self.padre.get_labels_uso()[i].set_text(cpus[i].get_percen_busy() + "% Uso")
        # Añadimos los procesos
        for proceso in procesos:
            self.padre.get_lista_proc().append((proceso.pid,
                                "<span foreground='" + color[proceso.estado] + "'>" + proceso.nombre + "</span>",
                                proceso.num_hebras))
        # Establecemos el orden en los TreeViews
        for tree in self.padre.get_trees():
            for column in tree.get_columns():
                column.set_sort_column_id(int(self.padre.get_sort_by()))
        # Ahora añadimos cada hebra
        for hebra in hebras:
            self.padre.get_listas()[int(hebra.num_cpu)].append(("<span foreground='" + color[hebra.estado] + "'>" + str(hebra.pid) + "</span>",
                                "<span foreground='" + color[hebra.estado] + "'>" + hebra.padre.nombre + "</span>"))
        # Finalmente se refrescan los componentes graficos trees
        self.padre.get_glade().get_widget("treeProcesos").queue_draw()
        for tree in self.padre.get_trees():
            tree.queue_draw()
        # Por ultimo establecemos el mensaje
        self.padre.get_glade().get_widget("txtComentario").get_buffer().set_text(mensaje)
        # Ponemos un mensaje en el status bar
        self.padre.get_glade().get_widget("stbar").push(0, ("Visualizando registro " +
                                        str(self.num_reg_act) + " de " +
                                        str(self.num_reg_tot)))
        self.padre.get_regla().set_actual(self.num_reg_act)


class DibujarResultados(threading.Thread):
    """
    Hebra para la visualizacion de la informacion en la interfaz.
    """
    def __init__(self, padre, info_cpus, procesos, hebras):
        """
        Constructor de la clase
        @param padre: Interfaz de la que hara uso la clase para dibujar en sus componentes
        @type padre: wPrincipal
        @param info_cpus: Lista con informacion de las cpus
        @type info_cpus: list
        @param procesos: Lista de los procesos a dibujar
        @type procesos: list
        @param hebras: Lista con las hebras a dibujar
        @type hebras: list
        """
        self.stop_event = threading.Event()
        self.monitorizando = True
        self.padre = padre
        self.info_cpus = info_cpus
        self.procesos = procesos
        self.hebras = hebras
        threading.Thread.__init__(self)

    def run(self):
        """
        Rellena los trees de las cpus y de los procesos.
        """
        # Le hebra comienza parada hasta que le indiquen que
        # comience a dibujar
        self.stop_event.wait()
        # Mientras se este monitorizando se ejecuta esta hebra
        while self.monitorizando:
            # Limpiamos las listas
            self.padre.get_lista_proc().clear()
            for lista in self.padre.get_listas():
                lista.clear()
            color = {"R": self.padre.get_colores()[0],
                    "S": self.padre.get_colores()[1],
                    "D": self.padre.get_colores()[2],
                    "Z": self.padre.get_colores()[3],
                    "T": self.padre.get_colores()[4],
                    "W": self.padre.get_colores()[5]}
            # Mostramos la informacion de cada CPU
            for i in range(len(self.info_cpus)):
                self.padre.get_labels_uso()[i].set_text(self.info_cpus[i].get_percen_busy() + "% Uso")
            # Añadimos los procesos
            for proceso in self.procesos:
                self.padre.get_lista_proc().append((proceso.pid,
                                    "<span foreground='" + color[proceso.estado] + "'>" + proceso.nombre + "</span>",
                                    proceso.num_hebras))
            # Ahora añadimos cada hebra
            for hebra in self.hebras:
                self.padre.get_listas()[int(hebra.num_cpu)].append(("<span foreground='" + color[hebra.estado] + "'>" + hebra.pid + "</span>",
                                    "<span foreground='" + color[hebra.estado] + "'>" + hebra.padre.nombre + "</span>"))
            # Finalmente se refrescan los componentes graficos trees
            self.padre.get_glade().get_widget("treeProcesos").queue_draw()
            for tree in self.padre.get_trees():
                tree.queue_draw()
            # Desbloqueo el evento por si esta activado
            self.stop_event.clear()
            # Esperamos hasta que nos digan que continuemos
            self.stop_event.wait()

    def set_info_cpus(self, info_cpus):
        """
        Establece la nueva informacion sobre las cpus.
        @param info_cpus: Lista con la informacion de las cpus
        @type info_cpus: list
        """
        self.info_cpus = info_cpus

    def set_procesos(self, procesos):
        """
        Establece la nueva informacion sobre los procesos.
        @param procesos: Lista con la informacion de los procesos a dibujar
        @type procesos: list
        """
        self.procesos = procesos

    def set_hebras(self, hebras):
        """
        Establece la nueva informacion sobre las hebras.
        @param hebras: Lista con la informacion de las hebras a dibujar
        @type hebras: list
        """
        self.hebras = hebras
