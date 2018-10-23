#Este archivo esta en encoding: utf-8

"""
Modulo con todas las clases de la interfaz de la aplicacion.

G{importgraph}
"""

import pygtk
import gtk
import gtk.glade
import os
import sys
import webbrowser
import pdb

import threads
import events
from config import conf
from basedatos import bdlog
from systeminfo import procinfo, cpuinfo
from stadgen import chartsgen
from pysqlite2 import dbapi2 as sqlite
import widgets

pygtk.require("2.0")

PIX_PATH = "gui/pixmaps"
"""Ruta de las imagenes de la aplicacion"""

class wPrincipal:
    """
    Ventana que posee todo los comun de las demas ventanas principales de la aplicacion,
    como wMonitorizar y wVisualizar.
    """
    def __init__(self, nombre_ventana, num_cpus):
        """Constructor de la clase
        @param nombre_ventana: El nombre de la ventana
        @type nombre_ventana: string
        @param num_cpus: Numero de cpus
        @type num_cpus: int
        """
        self.nombre_ventana = nombre_ventana
        # Construimos a partir del archivo glade la ventana
        self.glade = gtk.glade.XML("gui/monitorhebras.glade", root=nombre_ventana)
        # Conectamos todas las señales especificadas en el archivo
        self.glade.signal_autoconnect(self)
        # Establecemos un icono
        self.glade.get_widget(nombre_ventana).set_icon(gtk.gdk.pixbuf_new_from_file("gui/pixmaps/monitor.png"))

        # Listener de la clase
        self.lst = None

        # Establecemos todas las imagenes
        self.glade.get_widget("imgProcesos").set_from_file("gui/pixmaps/procesos.png")

        try:
            # Leemos el archivo de configuracion
            (self.procesos, self.colores, self.log_path, self.t_refresco,
                    self.lang, self.tmp_rep, self.comenz_rep, self.sort_by) = conf.leer_configuracion3()
        except conf.ConfigError:
            # Si no existe lo creamos con la configuracion por defecto
            (self.procesos, self.colores, self.log_path, self.t_refresco,
                    self.lang, self.tmp_rep, self.comenz_rep, self.sort_by) = conf.crear_configuracion3()

        # Dibujamos las listas de las CPUs
        self.dibujar_cpus(num_cpus)

        # Lista de los procesos
        # Creamos las listas y definimos su contenido (String)
        self.lista_proc = gtk.ListStore(str, str, str)
        # Ahora le establecemos al tree de los procesos como modelo la lista creada
        self.glade.get_widget("treeProcesos").set_model(self.lista_proc)
        # Creamos las columnas que vamos a mostrar en cada tree
        column_pid = gtk.TreeViewColumn("PID")
        column_nom = gtk.TreeViewColumn("Nombre Proceso")
        column_num_hebras = gtk.TreeViewColumn("Num. hebras")
        # Hacemos las columnas resizables
        column_pid.set_resizable(True)
        column_nom.set_resizable(True)
        column_num_hebras.set_resizable(True)
        # Le añadimos al tree estas columnas
        self.glade.get_widget("treeProcesos").append_column(column_pid)
        self.glade.get_widget("treeProcesos").append_column(column_nom)
        self.glade.get_widget("treeProcesos").append_column(column_num_hebras)
        # Creamos un cell renderer que sera el que nos renderice el contenido de cada celda
        cell = gtk.CellRendererText()
        # Se lo establecemos a cada columna
        column_nom.pack_start(cell, True)
        column_pid.pack_start(cell, True)
        column_num_hebras.pack_start(cell, True)
        # Y le especificamos que las renderice como text y markup, que sea el tipo que nos permita establecer colores
        column_pid.add_attribute(cell, 'text', 0)  # 0 es el numero en el que aparece la columna
        column_nom.add_attribute(cell, 'markup', 1)  # 1 es el numero en el que aparece la columna
        column_num_hebras.add_attribute(cell, 'text', 2)  # 2 es el numero en el que aparece la columna

        # Popup de leyenda
        self.leyenda = DialogLeyenda(self.colores)

        if nombre_ventana == "wVisualizar":
            # Creamos el widget de la regla
            self.regla = widgets.SpecialRule()
            # Y lo establecemos
            self.glade.get_widget("scrwinRule").add_with_viewport(self.regla)

        # Finalmente mostramos la ventana
        self.glade.get_widget(nombre_ventana).show_all()
        
    def actualizar_configuracion(self, procesos, colores, log_path, t_refresco,
                    lang, tmp_rep, comenz_rep, sort_by):
        """
        Actualiza los atributos de la configuracion
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
        self.procesos = procesos
        self.colores = colores
        # Cambiamos ellog_path solo a laventana de monitorizacion
        # para que en la visualizacion no se cambie la BD visualizada
        if self.nombre_ventana == "wMonitorizar":
            self.log_path = log_path
        self.t_refresco = t_refresco
        self.lang = lang
        self.tmp_rep = tmp_rep
        self.comenz_rep = comenz_rep
        self.sort_by = sort_by
        # Actualizamos la leyenda
        self.leyenda = DialogLeyenda(self.colores)
        
    def on_wPrincipal_delete_event(self, widget, event):
        """
        Evento al cerrar la ventana.
        """
        gtk.main_quit()  # Salimos de la aplicacion
        
    def on_salir_activate(self, widget):
        """
        Evento al activar el boton salir del menu.
        """
        gtk.main_quit()  # Salimos de la aplicacion
        
    def on_btnLeyenda_clicked(self, widget):
        """
        Evento al pulsar el boton
        """
        if widget.get_active():
            rect = widget.get_allocation()
            # Mostrar la ventana de la leyenda
            x, y = self.glade.get_widget(self.nombre_ventana).get_position()
            self.leyenda.mostrar(rect.x + x, rect.y + y + rect.height + 23)
        else:
            self.leyenda.ocultar()
            
    def on_btnLeyenda_enter_notify_event(self, widget, event):
        """
        Evento al pasar el cursor por encima del boton
        """
        if not widget.get_active():
            rect = widget.get_allocation()
            # Mostrar la ventana de la leyenda
            x, y = self.glade.get_widget(self.nombre_ventana).get_position()
            self.leyenda.mostrar(rect.x + x, rect.y + y + rect.height + 23)
            
    def on_btnLeyenda_leave_notify_event(self, widget, event):
        """
        Evento al dejar de pasar el cursor por encima del boton
        """
        if not widget.get_active():
            self.leyenda.ocultar()

    # TODO: Refinarlo y hacer que se ejecute al cambiar el tamaño de
    # el scroll o ventana. Ahora se ejecuta al pulsar sobre el scroll
    def on_scrwin_size_allocate(self, widget, allocation):
        fixwin = self.glade.get_widget("fixwin")
        hijos = fixwin.get_children()
        num_cpus = 2
        lv = self.glade.get_widget("scrwin").get_allocation().width
        eu = 190 * num_cpus + 25 * (num_cpus - 1)
        if eu > lv:
            pos_x = 25 #pos_x, pos_y = 25, 10
        else:
            pos_x = lv / 2 - eu / 2
        pos_y = 10
        for cpu in range(bdlog.get_num_cpus(self.log_path)):
            pos_ini = pos_x
            i = cpu*3
            fixwin.move(hijos[i], pos_x, pos_y)
            pos_x += hijos[i].size_request()[0]
            fixwin.move(hijos[i+1], pos_x, pos_y)
            pos_x = pos_ini
            pos_y += hijos[i].size_request()[1] + 5
            fixwin.move(hijos[i+2], pos_x, pos_y)
            # Establecemos las nuevas coordenadas x e y
            if not (cpu + 1) % 8:
                if eu > lv:
                    pos_x = 25
                else:
                    pos_x = lv / 2 - eu / 2
            else:
                pos_x += hijos[i+2].size_request()[0] + 25
            pos_y = (cpu + 1) / 8 * 260 + 10
            
    def dibujar_cpus(self, num_cpus):
        """
        Dibuja las listas de las cpus en la interfaz
        @param num_cpus: Numero de cpus
        @type num_cpus: int
        @rtype: void
        """
        fixwin = self.glade.get_widget("fixwin")
        lv = self.glade.get_widget("scrwin").get_allocation().width
        eu = 190 * num_cpus + 25 * (num_cpus - 1)
        if eu > lv:
            pos_x = 25 #pos_x, pos_y = 25, 10
        else:
            pos_x = lv / 2 - eu / 2
        pos_y = 10
        self.trees, self.listas, self.labels_uso = [], [], []
        # Listas de las CPUS
        # Construimos la interfaz dependiendo del numero de cpus
        for cpu in range(num_cpus):
            #TODO: Mejorar el aspecto de la interfaz (posiciones)
            pos_ini = pos_x
            # Establecemos el tooltip con informacion sobre el modelo
            modelo = bdlog.get_cpu_model(self.log_path, cpu)
            if not modelo:
                modelo = cpuinfo.cpu_model(cpu)
            # Etiqueta de la CPU
            lbl_cpu = gtk.Label()
            lbl_cpu.set_tooltip_text(modelo)
            lbl_cpu.set_markup("<big><b>CPU"+str(cpu)+"</b></big>")
            fixwin.put(lbl_cpu, pos_x, pos_y)
            pos_x += lbl_cpu.size_request()[0]
            # Etiqueta del % de Uso
            lbl_uso = gtk.Label("% Uso")
            lbl_uso.set_size_request(190 - 5 - lbl_cpu.size_request()[0],
                                lbl_cpu.size_request()[1])            
            self.labels_uso.append(lbl_uso)
            fixwin.put(lbl_uso, pos_x, pos_y)
            pos_x = pos_ini
            pos_y += lbl_cpu.size_request()[1] + 5
            # Ventana con scrollbars para la lista
            scrw = gtk.ScrolledWindow()
            scrw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
            scrw.set_size_request(190, 215)
            # ListStore
            lista = gtk.ListStore(str, str)
            # TreeView
            treeCpu = gtk.TreeView(lista)
            # Creamos las columnas que vamos a mostrar en cada tree
            columnPid = gtk.TreeViewColumn("PID")
            columnNom = gtk.TreeViewColumn("Proceso")
            # Le añadimos a los trees estas columnas
            treeCpu.append_column(columnPid)
            treeCpu.append_column(columnNom)
            # Creamos un cell renderer que sera el que nos renderice el contenido de cada celda
            cell = gtk.CellRendererText()
            # Se lo establecemos a cada columna
            columnNom.pack_start(cell, True)
            columnPid.pack_start(cell, True)
            # Y le especificamos que las renderice como markup, que sea el tipo que nos permita establecer colores
            columnNom.add_attribute(cell, 'markup', 1) # 1 es el numero en el que aparece la columna
            columnPid.add_attribute(cell, 'markup', 0) # 0 es el numero en el que aparece la columna
            # Añadimos la lista y el tree a sus respectivas listas
            self.listas.append(lista)
            self.trees.append(treeCpu)
            # Añadimos el tree al scrolledWindow
            scrw.add_with_viewport(treeCpu)
            # Y este al fixwin
            fixwin.put(scrw, pos_x, pos_y)
            # Establecemos las nuevas coordenadas x e y
            if not (cpu + 1) % 8:
                pos_x = 25
            else:
                pos_x += scrw.size_request()[0] + 25
            pos_y = (cpu + 1) / 8 * 260 + 10

    def on_cargar_monitorizacion_activate(self, widget):
        """
        Evento al activar el boton de cargar monitorizacion
        """
        dialogo = gtk.FileChooserDialog(title="Cargar Monitorización", parent=self.glade.get_widget(self.nombre_ventana), action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                      gtk.STOCK_OK, gtk.RESPONSE_ACCEPT), backend=None)
        respuesta = dialogo.run()
        if respuesta == gtk.RESPONSE_ACCEPT:
            wVisualizar(dialogo.get_filename())
            dialogo.destroy()
            self.glade.get_widget(self.nombre_ventana).destroy()
        else:
            dialogo.destroy()
        
    def on_preferencias_activate(self, widget):
        """
        Evento al activar el boton preferencias del menu.
        """
        preferencias = wPreferencias(self)  # Creo una ventana de preferencias

    def on_acerca_de_activate(self, widget):
        """
        Evento al activar el boton Acerca de del menu.
        """
        acercade = AboutDialog()  # Creo la ventana de 'Acerca de'

    def on_ayuda_activate(self, widget):
        """
        Evento al activar el boton de Ayuda.
        """
        webbrowser.open("doc/index.html")

    def get_pids(self):
        '''
        Devuelve la lista de pids a monitorizar
        '''
        return self.pids

    def get_procesos(self):
        '''
        Devuelve la lista de procesos a monitorizar
        '''
        return self.procesos

    def get_log_path(self):
        return self.log_path

    def get_t_refresco(self):
        return self.t_refresco

    def get_lista_proc(self):
        return self.lista_proc

    def get_listas(self):
        return self.listas
            
    def get_listas(self):
        return self.listas

    def get_glade(self):
        return self.glade

    def get_colores(self):
        return self.colores

    def get_labels_uso(self):
        return self.labels_uso

    def get_sort_by(self):
        return self.sort_by

    def get_tmp_rep(self):
        return self.tmp_rep

    def get_trees(self):
        return self.trees

    def get_lst(self):
        return self.lst


class wMonitorizar(wPrincipal):
    """
    Ventana para la monitorizacion de hebras de uno o varios procesos.
    Esta debe ser la que se cree en primera instancia.
    Desde ella se crearan los demas objetos.
    """

    def __init__(self):
        """Constructor de la clase"""
        # Invocamos al constructor del padre
        wPrincipal.__init__(self, "wMonitorizar", cpuinfo.num_cpus())
        
        self.pids = []
        self.monit_terminada = False

        # Inicializamos el num_reg
        self.num_reg = 0
        # Eliminamos el antiguo archivo de log y cremos uno nuevo
        if os.path.lexists(self.log_path):
            os.remove(self.log_path)
        bdlog.crearBD(self.log_path)
        # Popup de leyenda
        self.leyenda = DialogLeyenda(self.colores)
        # Hebra para la monitorizacion
        self.monitor = None
        
    def on_btnVisualizar_clicked(self, widget):
        """
        Evento al pulsar el boton de Visualizar
        """
        dialogo = gtk.FileChooserDialog(title="Visualizar Registro", parent=self.glade.get_widget(self.nombre_ventana), action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                      gtk.STOCK_OK, gtk.RESPONSE_ACCEPT), backend=None)
        respuesta = dialogo.run()
        if respuesta == gtk.RESPONSE_ACCEPT:
            archivo = dialogo.get_filename()
            dialogo.destroy()
            wVisualizar(archivo)
            self.glade.get_widget("wMonitorizar").destroy()
        else:
            dialogo.destroy()

    def on_btnMonit_clicked(self, widget):
        """
        Evento al pulsar el boton Monitorizar/Parar.
        """
        # Si el boton era parar
        if widget.get_label() == "Parar":
            # Mostramos un mensaje de advertencia
            if Dialogo(mensaje="¿Está seguro de que desea para el monitor?").mostrar() == gtk.RESPONSE_OK:
                # Cambiamos la propiedades del boton
                widget.set_image(gtk.image_new_from_stock(gtk.STOCK_MEDIA_PLAY,
                                                    gtk.ICON_SIZE_BUTTON))
                widget.set_label("Monitorizar")
                # Ponemos un mensaje en el status bar
                self.glade.get_widget("stbar").push(0, "Monitor parado.")
                # Y paramos las hebras que estan monitorizando los procesos
                self.monitor.monitorizando = False
                self.monitor.stop_event.set()
                # Finalmente cargamos la ventana de visualizacion con este archivo
                wVisualizar(self.log_path)
                self.glade.get_widget("wMonitorizar").destroy()
        else:
            # Comprobamos que haya procesos
            if not self.procesos:
                # Informamos al usuario y salimos
                Dialogo(tipo=gtk.MESSAGE_WARNING, botones=gtk.BUTTONS_OK,
                        mensaje="No se han especificado procesos a monitorizar.",
                        titulo="Información").mostrar()
                return
            # Establecemos las propiedades del boton a monitorizando
            widget.set_image(gtk.image_new_from_stock(gtk.STOCK_MEDIA_STOP, gtk.ICON_SIZE_BUTTON))
            widget.set_label("Parar")
            # Ponemos un mensaje en el status bar
            self.glade.get_widget("stbar").push(0, "Monitorizando...")
            # Borramos el archivo log
            try:
                os.remove(self.log_path)
            except OSError:
                pass  # Si el archivo no existia se creara
            # Y a continuacion lo creamos
            bdlog.crearBD(self.log_path)
            # Comenzamos a monitorizar
            self.monitor = threads.Monitorizar(self)
            self.monitor.start()

    def finalizar_monitorizacion(self):
        # Finalmente cargamos la ventana de visualizacion con este archivo
        wVisualizar(self.log_path, monit_fin=True)
        self.glade.get_widget("wMonitorizar").destroy()

    def get_monitor(self):
        return self.monitor


class wVisualizar(wPrincipal):
    """
    Ventana para la visualizacion de registros de una monitorizacion.
    """

    def __init__(self, log_path, monit_fin=False):
        """
        Constructor de la clase.
        @param log_path: El path del fichero bd de los registros a
            visualizar.
        @type log_path: string
        """        
        try:
            # Invocamos al constructor del padre
            wPrincipal.__init__(self, "wVisualizar", bdlog.get_num_cpus(log_path))
            self.log_path = log_path
            # Ponemos las imagenes que faltan
            self.glade.get_widget("imgCpus").set_from_file("gui/pixmaps/cpu.png")
            self.glade.get_widget("imgComent").set_from_file("gui/pixmaps/coment.png")

            # Inicializamos el num_reg
            self.num_reg = 1
            # Inicializamos a None la hebra encargada de reproducir los registros
            self.reproductor = None
            self.total_reg = bdlog.num_reg_bd(self.log_path)
            if self.total_reg <= 0:
                # La BD esta vacia
                self.glade.get_widget("wVisualizar").destroy()
                Dialogo(tipo=gtk.MESSAGE_ERROR, botones=gtk.BUTTONS_OK,
                        mensaje="El archivo especificado no contine registros.",
                        titulo="Error").mostrar()
                wMonitorizar()
            else:
                # Establecemos parametros al widget regla
                self.regla.set_total_ticks(self.total_reg)
                self.regla.set_function(self.funcion_regla)
                self.regla.set_big_mark(list(bdlog.get_num_reg_comentados(self.log_path)))
                # Cargo el primer registro
                (cpus, procesos, hebras, mensaje) = bdlog.leer_info(self.log_path, 1)
                # Y las dibujo
                self.dibujar_hebras(cpus, procesos, hebras, mensaje)
                # Ponemos un mensaje en el status bar
                self.glade.get_widget("stbar").push(0, ("Visualizando registro " +
                                                str(self.num_reg) + " de " +
                                                str(self.total_reg)))

        except sqlite.DatabaseError:
            # Mostrar un mensaje de error y volver a la ventana de monitorizacion
            self.glade.get_widget("wVisualizar").destroy()
            Dialogo(tipo=gtk.MESSAGE_ERROR, botones=gtk.BUTTONS_OK,
                        mensaje="El archivo especificado esta encriptado o no es del tipo requerido.",
                        titulo="Error").mostrar()
            wMonitorizar()

    def mostrar_registro(self, num_registro):
        """
        Muestra el registro especificado, estbleciendolo como
        registro actual.
        @param num_registro: Numero de registro a visualizar.
        @type num_registro: int
        @rtype: void
        """
        if not self.total_reg:  # Comprobamos que haya registros
            # Si no, informamos al usuario y salimos
            Dialogo(tipo=gtk.MESSAGE_WARNING, botones=gtk.BUTTONS_OK,
                    mensaje="No existen registros en el log.", titulo="Información").mostrar()
            return
        self.num_reg = num_registro
        # Comprobamos que no se ha pasado del limite
        if self.num_reg > self.total_reg:
            self.num_reg = 1
        elif self.num_reg < 1:
            self.num_reg = self.total_reg
        # Lo leemos del archivo de log
        (cpus, procesos, hebras, mensaje) = bdlog.leer_info(self.log_path, self.num_reg)
        # Y lo dibujamos
        self.dibujar_hebras(cpus, procesos, hebras, mensaje)
        # Ponemos un mensaje en el status bar
        self.glade.get_widget("stbar").push(0, ("Visualizando registro " +
                                        str(self.num_reg) + " de " +
                                        str(self.total_reg)))
        self.regla.set_actual(self.num_reg)

    def funcion_regla(self):
        """
        Evento al pulsar sobre el scroll de la regla
        """
        self.mostrar_registro(self.regla.get_actual())

    def on_btnSiguiente_clicked(self, widget):
        """
        Evento al pulsar el boton Adelante
        """
        self.mostrar_registro(self.num_reg + 1)

    def on_btnAnterior_clicked(self, widget):
        """
        Evento al pulsar el boton Atras.
        """
        self.mostrar_registro(self.num_reg - 1)
    
    def on_ir_a_activate(self,widget):
        """
        Evento al pulsar el boton Ir a del menu
        """
        # Muestra el popup y obtenemos el numero de registro del usuario
        try:        
            x, y = self.glade.get_widget("wVisualizar").get_position()
            # TODO: Estos son posiciones absolutas, relativas a la ventana
            # convendria cambiarlas a relativas totales.
            reg = int(DialogIra(x+1, y+50).mostrar())
        except ValueError:
            return  # Si el usuario no he metido ningun numero salimos
        self.mostrar_registro(reg)

    def on_siguiente_activate(self, widget):
        """
        Evento al pulsar el boton Siguiente del menu.
        """
        self.mostrar_registro(self.num_reg + 1)

    def on_anterior_activate(self, widget):
        """
        Evento al pulsar el boton Siguiente del menu.
        """
        self.mostrar_registro(self.num_reg - 1)

    def on_btnMonitor_clicked(self, widget):
        """
        Evento al pulsar el boton monitorizar
        """
        self.glade.get_widget("wVisualizar").destroy()
        wMonitorizar()
        
    def on_guardar_monitorizacion_activate(self, widget):
        """
        Evento al activar el boton de guardar monitorizacion
        """
        dialogo = gtk.FileChooserDialog(title="Guardar Monitorización",
                    parent=self.glade.get_widget("wVisualizar"),
                    action=gtk.FILE_CHOOSER_ACTION_SAVE,
                    buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                                gtk.STOCK_OK, gtk.RESPONSE_ACCEPT),
                    backend=None)
        respuesta = dialogo.run()
        if respuesta == gtk.RESPONSE_ACCEPT:
            bdlog.guardar_monitorizacion(self.log_path, dialogo.get_filename())
        dialogo.destroy()

    def on_generar_graficas_activate(self, widget):
        """
        Evento al activar el boton de generar documento
        """
        # Creo la ventana de generar documento
        gen_doc = wGenerarGraficas(self.log_path, self.colores)

    def on_btnEditar_clicked(self, widget):
        """
        Evento al pulsar sobre el boton de Editar(Comentario)
        """
        # Almaceno el comentario del registro en la BD
        start, end = self.glade.get_widget("txtComentario").get_buffer().get_bounds()
        texto = self.glade.get_widget("txtComentario").get_buffer().get_text(start, end)
        bdlog.guardar_comentario(self.log_path, self.num_reg, texto)
        if texto != "":
            self.regla.set_big_mark(self.num_reg)
        else:
            self.regla.remove_big_mark(self.num_reg)

    def on_btnLimpiar_clicked(self, widget):
        """
        Evento al pulsar sobre el boton limpiar
        """
        buf = gtk.TextBuffer()
        buf.set_text("")
        self.glade.get_widget("txtComentario").set_buffer(buf)
        
    def on_btnPlay_clicked(self, widget):
        """
        Evento al pulsar el boton Reproducir/Parar.
        """
        # Si el boton era parar
        if widget.get_label() == "Parar":
            # Cambiamos la propiedades del boton
            widget.set_image(gtk.image_new_from_stock(gtk.STOCK_MEDIA_PLAY,
                                                    gtk.ICON_SIZE_BUTTON))
            widget.set_label("Reproducir")
            # Ponemos un mensaje en el status bar
            self.glade.get_widget("stbar").push(0, "Reproducción parada.")
            # Y paramos las hebras que estan visualizando los registros
            self.reproductor.reproduciendo = False
            self.reproductor.stop_event.set()
            self.num_reg = self.reproductor.num_reg_act
            del self.reproductor
        else:
            # Comprobamos desde donde comenzar la reproduccion
            if self.comenz_rep == conf.PRINCIPIO:
                self.num_reg = 1
            elif self.comenz_rep == conf.PREGUNTAR:
                if Dialogo(tipo=gtk.MESSAGE_QUESTION, botones=gtk.BUTTONS_OK_CANCEL,
                    mensaje="¿Desea reproducir desde el registro actual?", titulo="Reproducir").mostrar() == gtk.RESPONSE_CANCEL:
                    self.num_reg = 1
            # Establecemos las propiedades del boton a parado
            widget.set_image(gtk.image_new_from_stock(gtk.STOCK_MEDIA_STOP, gtk.ICON_SIZE_BUTTON))
            widget.set_label("Parar")
            # Ponemos un mensaje en el status bar
            self.glade.get_widget("stbar").push(0, "Comenzando la reproducción...")
            # Comenzamos a reproducir
            self.reproductor = threads.Reproducir(self)
            self.reproductor.start()

    def get_regla(self):
        return self.regla

    def get_num_reg(self):
        return self.num_reg

    def get_total_reg(self):
        return self.total_reg

    def get_reproductor(self):
        return self.reproductor

    def dibujar_hebras(self, info_cpus, procesos, hebras, mensaje):
        """
        Rellena los trees de las cpus y de los procesos.
        """
        # Limpiamos las listas
        self.lista_proc.clear()
        for lista in self.listas:
            lista.clear()
        start, end = self.glade.get_widget("txtComentario").get_buffer().get_bounds()
        self.glade.get_widget("txtComentario").get_buffer().delete(start, end)
        color = {"R": self.colores[0],
                "S": self.colores[1],
                "D": self.colores[2],
                "Z": self.colores[3],
                "T": self.colores[4],
                "W": self.colores[5]}
        # Mostramos la informacion de cada CPU
        for i in range(len(info_cpus)):
            self.labels_uso[i].set_text(info_cpus[i].get_percen_busy() + "% Uso")
        # Añadimos los procesos
        for proceso in procesos:
            self.lista_proc.append((proceso.pid,
                                "<span foreground='" + color[proceso.estado] + "'>" + proceso.nombre + "</span>",
                                proceso.num_hebras))
        # Ahora añadimos cada hebra
        for hebra in hebras:
            self.listas[int(hebra.num_cpu)].append(("<span foreground='" + color[hebra.estado] + "'>" + str(hebra.pid) + "</span>",
                                "<span foreground='" + color[hebra.estado] + "'>" + hebra.padre.nombre + "</span>"))
        # Finalmente se refrescan los componentes graficos trees
        self.glade.get_widget("treeProcesos").queue_draw()
        for tree in self.trees:
            tree.queue_draw()
        # Por ultimo establecemos el mensaje
        self.glade.get_widget("txtComentario").get_buffer().set_text(mensaje)


class wPreferencias:
    """
    Ventana de preferencias.
    Es la encargada de mostrar y modificar las opciones que haya establecido
    el usuario para la monitorización de hebras.
    """
    def __init__(self, padre):
        """
        Constructor de la clase
        """
        self.padre = padre
        # Creamos el objeto a partir del archivo glade
        self.glade = gtk.glade.XML("gui/monitorhebras.glade", root="wPreferencias")
        # Conectamos todas las señales
        self.glade.signal_autoconnect(self)
        self.wpreferencias = self.glade.get_widget("wPreferencias")

        # Establecemos todas las imagenes
        self.glade.get_widget("imgProc").set_from_file("gui/pixmaps/proc.png")
        self.glade.get_widget("imgIdioma").set_from_file("gui/pixmaps/internacional.png")
        self.glade.get_widget("imgTiempo").set_from_file("gui/pixmaps/clock.png")
        self.glade.get_widget("imgColores").set_from_file("gui/pixmaps/colores.png")
        self.glade.get_widget("imgTmpRep").set_from_file("gui/pixmaps/clock.png")
        # TODO: Buscar icono para el comienzo
        self.glade.get_widget("imgComRep").set_from_file("gui/pixmaps/proc.png")

        # Lista de procesos a monitorizar
        # Creamos las listas y definimos su contenido (String)
        self.lista = gtk.ListStore(str)
        # Ahora le establecemos al tree de la interfaz como modelo la lista creada
        self.glade.get_widget("lstProc").set_model(self.lista)
        # Creamos las columnas que vamos a mostrar en los trees
        columnProc = gtk.TreeViewColumn("Proceso")
        # Le añadimos a los tree estas columnas
        self.glade.get_widget("lstProc").append_column(columnProc)
        # Creamos un cell renderer que sera el que nos renderice el contenido de cada celda
        cell = gtk.CellRendererText()
        # Se lo establecemos a cada columna
        columnProc.pack_start(cell, True)
        # Y le especificamos que las renderice como texto simple
        columnProc.add_attribute(cell, 'text', 0) # 0 es el numero en el que aparece la columna
        # Ahora leemos del archivo de configuración
        (procesos, colores, log_path, t_refresco, lang, tmp_rep, comenz_rep, sort) = conf.leer_configuracion3()
        # Y establecemos los procesos
        for proc in procesos:
            self.lista.append((proc,))
        # Y los colores
        self.glade.get_widget("btnRunning").set_color(gtk.gdk.color_parse(colores[0]))
        self.__cambiar_color("Running", colores[0])
        self.glade.get_widget("btnSleeping").set_color(gtk.gdk.color_parse(colores[1]))
        self.__cambiar_color("Sleeping", colores[1])
        self.glade.get_widget("btnWaiting").set_color(gtk.gdk.color_parse(colores[2]))
        self.__cambiar_color("Waiting", colores[2])
        self.glade.get_widget("btnZombie").set_color(gtk.gdk.color_parse(colores[3]))
        self.__cambiar_color("Zombie", colores[3])
        self.glade.get_widget("btnStopped").set_color(gtk.gdk.color_parse(colores[4]))
        self.__cambiar_color("Stopped", colores[4])
        self.glade.get_widget("btnPagging").set_color(gtk.gdk.color_parse(colores[5]))
        self.__cambiar_color("Pagging", colores[5])
        # Y el archivo y el tiempo de refresco
        self.glade.get_widget("btnLog").set_filename(log_path)
        self.glade.get_widget("spnRefresco").set_value(float(t_refresco))
        # Y la conf de la reproduccion
        self.glade.get_widget("spnbtnTmpRep").set_value(float(tmp_rep))
        if comenz_rep == conf.ACTUAL:
            self.glade.get_widget("rdbtnActual").set_active(True)
        elif comenz_rep == conf.PRINCIPIO:
            self.glade.get_widget("rdbtnPrincipio").set_active(True)
        else:
            self.glade.get_widget("rdbtnPreguntar").set_active(True)

        # Orden de las hebras al mostrarse por pantalla
        if sort == str(conf.SORT["NOMBRE"]):
            self.glade.get_widget("rdbNombre").set_active(True)
        elif sort == str(conf.SORT["ESTADO"]):
            self.glade.get_widget("rdbEstado").set_active(True)
        else:
            self.glade.get_widget("rdbPID").set_active(True)
        # El idioma
        self.glade.get_widget("cmbIdioma").set_active(conf.LANGUAGES[lang])
        # Finalmente mostramos la ventana
        self.wpreferencias.show_all()

    def on_btnCancelar_clicked(self, widget):
        """
        Evento al pulsar sobre el botón Cancelar.
        Sale de la ventana sin realizar ningun cambio.
        """
        self.wpreferencias.destroy()  # Destruimos la ventana
        
    def on_btnAceptar_clicked(self, widget):
        """
        Evento al pulsar sobre el boton Aceptar.
        Sale de la ventana y realiza los cambios escribiendolos en el
        fichero de preferencias.
        """
        # Creamos una lista con los procesos a monitorizar
        # Obtenemos un iterador que apunta a la primera fila de los procesos
        iterador = self.lista.get_iter_first()
        procesos = []
        # Recorremos la lista añadiendo a procesos los procesos de la misma
        while iterador is not None:
            procesos.append(self.lista.get_value(iterador, 0))
            iterador = self.lista.iter_next(iterador)
        # Ahora obtenemos los colores
        colores = [self.glade.get_widget("btnRunning").get_color().to_string()]
        colores.append(self.glade.get_widget("btnSleeping").get_color().to_string())
        colores.append(self.glade.get_widget("btnWaiting").get_color().to_string())
        colores.append(self.glade.get_widget("btnZombie").get_color().to_string())
        colores.append(self.glade.get_widget("btnStopped").get_color().to_string())
        colores.append(self.glade.get_widget("btnPagging").get_color().to_string())
        # Y la ruta y el tiempo de refresco
        log_path = self.glade.get_widget("btnLog").get_filename()
        t_refresco = str(self.glade.get_widget("spnRefresco").get_value())
        # Y la conf de la reproduccion
        tmp_rep = str(self.glade.get_widget("spnbtnTmpRep").get_value())
        if self.glade.get_widget("rdbtnPrincipio").get_active():
            comenz_rep = conf.PRINCIPIO
        elif self.glade.get_widget("rdbtnActual").get_active():
            comenz_rep = conf.ACTUAL
        else:
            comenz_rep = 2
        
        # Idioma
        lang = self.glade.get_widget("cmbIdioma").get_active_text()
        # Orden de las hebras al mostrarse
        if self.glade.get_widget("rdbEstado").get_active():
            sort_by = conf.SORT["ESTADO"]
        elif self.glade.get_widget("rdbPID").get_active():
            sort_by = conf.SORT["PID"]
        else:
            sort_by = conf.SORT["NOMBRE"]
        # Escribimos los cambios en el archivo
        conf.escribir_configuracion3(procesos, colores, log_path, t_refresco,
                                        lang, tmp_rep, comenz_rep, sort_by)
        # Y los actualizamos en la interfaz padre
        self.padre.actualizar_configuracion(procesos, colores, log_path, t_refresco,
                                                lang, tmp_rep, comenz_rep, sort_by)
        # Destruimos la ventana
        self.wpreferencias.destroy()

    def on_btnInsertar_clicked(self, widget):
        """
        Evento al pulsar sobre el botón Añadir.
        Añade un nuevo proceso a la lista de procesos a monitorizar.
        """
        # Mostramos un dialogo para que el usuario introduzca el nombre del proceso
        proc = DialogProceso().mostrar()
        if proc.strip():
            self.lista.append((proc,))

    def on_btnBorrar_clicked(self, widget):
        """
        Evento al pulsar sobre el boton Borrar.
        Elimina el proceso seleccionado de la lista.
        """
        # Obtenemos el numero del elemento seleccionado en la lista
        seleccion = self.glade.get_widget("lstProc").get_selection()
        fila = seleccion.get_selected()[1]
        if fila is not None:
            self.lista.remove(fila)  # Lo eliminamos

    def on_btnRunning_color_set(self, widget):
        """
        Evento al establecer un nuevo color para los procesos en ejecución.
        """
        self.__cambiar_color("Running", widget.get_color().to_string())

    def on_btnSleeping_color_set(self, widget):
        """
        Evento al establecer un nuevo color para los procesos dormidos.
        """
        self.__cambiar_color("Sleeping", widget.get_color().to_string())

    def on_btnWaiting_color_set(self, widget):
        """
        Evento al establecer un nuevo color para los procesos en espera.
        """
        self.__cambiar_color("Waiting", widget.get_color().to_string())

    def on_btnZombie_color_set(self, widget):
        """
        Evento al establecer un nuevo color para los procesos en estado Zombie.
        """
        self.__cambiar_color("Zombie", widget.get_color().to_string())
        
    def on_btnStopped_color_set(self, widget):
        """
        Evento al establecer un nuevo color para los procesos parados.
        """
        self.__cambiar_color("Stopped", widget.get_color().to_string())

    def on_btnPagging_color_set(self, widget):
        """
        Evento al establecer un nuevo color para los procesos que estan paginando.
        """
        self.__cambiar_color("Pagging", widget.get_color().to_string())

    def __cambiar_color(self, nombre, color):
        """
        Método privado para cambiar el color de las etiquetas de los procesos.
        """
        self.glade.get_widget("lbl"+nombre).set_label("<b><span foreground='"+color+"'>"+nombre+"</span></b>")

class wGenerarGraficas:
    """
    Ventana de generar documento
    Es la encargada de generar un documento con las estadisticas seleccionadas por el usuario
    acerca de la ejecución monitorizada 
    """
    def __init__(self, archivo_bd, colores):
        """
        Constructor de la clase
        """
        self.archivo_bd = archivo_bd
        self.colores = colores
        # Creamos el objeto a partir del archivo glade
        self.glade = gtk.glade.XML("gui/monitorhebras.glade", root="wGenerarGraficas")
        # Conectamos todas las señales
        self.glade.signal_autoconnect(self)
        self.wgenerar = self.glade.get_widget("wGenerarGraficas")
        # Establecemos el rango de los spnbtn y sus valores
        fin = bdlog.num_reg_bd(archivo_bd)
        self.glade.get_widget("spnInicio").set_range(1, fin)
        self.glade.get_widget("spnFin").set_range(1, fin)
        self.glade.get_widget("spnInicio").set_value(1)
        self.glade.get_widget("spnFin").set_value(fin)
        # Finalmente ponemos las cpus
        cmb_store = gtk.ListStore(str)
        for i in range(bdlog.get_num_cpus(archivo_bd)):
            cmb_store.append(["CPU"+str(i)])
        self.glade.get_widget("cmbCPUs").set_model(cmb_store)
        self.glade.get_widget("cmbCPUs").set_text_column(0)
        self.glade.get_widget("cmbCPUs").set_active(0)
        # Y creamos la lista de CPUs
        self.glade.get_widget("treeCPUs").set_model(gtk.ListStore(str))
        # Creamos las columnas que vamos a mostrar en los trees
        columnProc = gtk.TreeViewColumn("CPUs")
        # Le añadimos a los tree estas columnas
        self.glade.get_widget("treeCPUs").append_column(columnProc)
        # Creamos un cell renderer que sera el que nos renderice el contenido de cada celda
        cell = gtk.CellRendererText()
        # Se lo establecemos a cada columna
        columnProc.pack_start(cell, True)
        # Y le especificamos que las renderice como texto simple
        columnProc.add_attribute(cell, 'text', 0) # 0 es el numero en el que aparece la columna
        # Finalmente marcamos  la grafica 1
        self.glade.get_widget("rdbGrafica1").set_active(True)

    def on_rdbGrafica1_toggled(self, widget):
        """
        Evento al des/seleccionar la grafica 1
        """
        if self.glade.get_widget("rdbGrafica1").get_active():
            self.glade.get_widget("spnInicio").set_sensitive(False)
            self.glade.get_widget("spnFin").set_sensitive(False)
            self.glade.get_widget("cmbCPUs").set_sensitive(True)
            self.glade.get_widget("btnAnadir").set_sensitive(True)
            self.glade.get_widget("btnEliminar").set_sensitive(True)
            self.glade.get_widget("scrolledwindow").set_sensitive(True)

    def on_rdbGrafica2_toggled(self, widget):
        """
        Evento al des/seleccionar la grafica 2
        """
        if self.glade.get_widget("rdbGrafica2").get_active():
            self.glade.get_widget("spnInicio").set_sensitive(True)
            self.glade.get_widget("spnFin").set_sensitive(True)
            self.glade.get_widget("cmbCPUs").set_sensitive(True)
            self.glade.get_widget("btnAnadir").set_sensitive(True)
            self.glade.get_widget("btnEliminar").set_sensitive(True)
            self.glade.get_widget("scrolledwindow").set_sensitive(True)

    def on_rdbGrafica3_toggled(self, widget):
        """
        Evento al des/seleccionar la grafica 3
        """
        if self.glade.get_widget("rdbGrafica3").get_active():
            self.glade.get_widget("spnInicio").set_sensitive(True)
            self.glade.get_widget("spnFin").set_sensitive(True)
            self.glade.get_widget("cmbCPUs").set_sensitive(True)
            self.glade.get_widget("btnAnadir").set_sensitive(True)
            self.glade.get_widget("btnEliminar").set_sensitive(True)
            self.glade.get_widget("scrolledwindow").set_sensitive(True)

    def on_rdbGrafica4_toggled(self, widget):
        """
        Evento al des/seleccionar la grafica 4
        """
        if self.glade.get_widget("rdbGrafica4").get_active():
            self.glade.get_widget("spnInicio").set_sensitive(True)
            self.glade.get_widget("spnFin").set_sensitive(True)
            self.glade.get_widget("cmbCPUs").set_sensitive(True)
            self.glade.get_widget("btnAnadir").set_sensitive(True)
            self.glade.get_widget("btnEliminar").set_sensitive(True)
            self.glade.get_widget("scrolledwindow").set_sensitive(True)

    def on_btnAnadir_clicked(self, widget):
        """Evento al pulsar sobre el boton de anadir"""
        # Cogemos la cpu seleccionada del combobox
        cpu = self.glade.get_widget("cmbCPUs").get_active_text()
        # Lo añadimos a la lista y lo borramos del combobox
        self.glade.get_widget("treeCPUs").get_model().append((cpu,))
        #TODO: Lo borramos del combobox
        self.glade.get_widget("cmbCPUs").remove_text(self.glade.get_widget("cmbCPUs").get_active())
        # Habilitamos el boton de eliminar
        self.glade.get_widget("btnEliminar").set_sensitive(True)
        # Comprobamos si hay mas elementos en el combobox
        #if self.glade.get_widget("cmbCPUs").get_active() == -1:
            # Sino deshabilitamos el boton de anadir
            #self.glade.get_widget("btnAnadir").set_sensitive(False)

    def on_btnEliminar_clicked(self, widget):
        """
        Evento al pulsar sobre el boton Eliminar.
        Elimina la cpu seleccionado de la lista y la devuelve al combobox
        """
        # Obtenemos el numero del elemento seleccionado en la lista
        seleccion = self.glade.get_widget("treeCPUs").get_selection()
        fila = seleccion.get_selected()[1]
        # Lo metemos en el combobox
        self.glade.get_widget("cmbCPUs").get_model().append(("CPU1",))
        #cmb_store = self.glade.get_widget("cmbCPUs").get_model()
        #cmb_store.append([])
        if fila is not None:
            self.glade.get_widget("treeCPUs").get_model().remove(fila)  # Lo eliminamos
        
        # Habilitamos el boton de insertar
        self.glade.get_widget("btnAnadir").set_sensitive(True)
        # Si no hay mas elementos en la lista, deshabilitamos el boton de eliminar
        
    def on_btnCancelar_clicked(self, widget):
        """
        Evento al pulsar sobre el boton Cancelar.
        Sale de la ventana sin realizar ningun cambio.
        """
        self.wgenerar.destroy()  # Destruimos la ventana

    def on_btnAceptar_clicked(self, widget):
        """
        Evento al pulsar sobre el boton Aceptar.
        Obtiene las estadisticas seleccionadas por el usuario y genera graficas
        """
        ruta = os.path.join(self.glade.get_widget("btnRuta").get_current_folder(), self.glade.get_widget("txtNombre").get_text())
        inicio, fin = int(self.glade.get_widget("spnInicio").get_value()), int(self.glade.get_widget("spnFin").get_value())
        excel, png = False, False
        # Comprobamos si se quiere sacar a excel o a png
        if self.glade.get_widget("chkbtnExcel").get_active():
            excel = True
        if self.glade.get_widget("chkbtnPng").get_active():
            png = True
        # Vemos cual ha sido la opcion escogida
        if self.glade.get_widget("rdbGrafica1").get_active():
            #chartsgen.create_chart_threads_in_cpus(self.archivo_bd, inicio, fin, ruta, excel, png)
            chartsgen.create_chart_threads_by_cpus(self.archivo_bd, ruta, excel, png)
        elif self.glade.get_widget("rdbGrafica2").get_active():
            chartsgen.create_chart_threads_by_frames(self.archivo_bd, -1, inicio, fin, ruta, excel, png)
        elif self.glade.get_widget("rdbGrafica3").get_active():
            chartsgen.create_chartline_threads_by_frames(self.archivo_bd, self.colores, -1, inicio, fin, ruta, excel, png)
        else:
            chartsgen.create_thread_migration(self.archivo_bd, inicio, fin, ruta, excel, png)
        # Obtener la ruta donde se quiere guardar el documento
        self.wgenerar.destroy()  # Destruimos la ventana

class DialogProceso:
    """
    Dialogo para la introducción del nombre del proceso.
    """
    def __init__(self):
        """
        Constructor de la clase.
        """
        # Creamos la ventana a partir del archivo glade
        self.glade = gtk.glade.XML("gui/monitorhebras.glade", root="dialogProceso")
        # Conectamos todos las señales
        self.glade.signal_autoconnect(self)
        self.about = self.glade.get_widget("dialogProceso")
        # Establecemos su icono
        self.about.set_icon(gtk.gdk.pixbuf_new_from_file("gui/pixmaps/proc.png"))

    def mostrar(self):
        """
        Muestra el dialogo, devuelve el valor introducido por el usuario y se destruye.
        """
        # Mostramos el dialogo
        respuesta = self.about.run()
        texto = ''
        # Si el usuario ha aceptado
        if respuesta == gtk.RESPONSE_OK:
            # Obtenemos el nombre introducido
            texto = self.glade.get_widget("txtProceso").get_text()
        # Destruimos el dialogo
        self.about.destroy()
        # Y devolvemos el texto
        return texto

    def on_okbutton_clicked(self, widget):
        """
        Evento al pulsar sobre el botón Aceptar.
        Envia una respuesta de RESPONSE_OK que hara que el método
        run() pare devolviendo gtk.RESPONSE_OK.
        """
        self.about.response(gtk.RESPONSE_OK)

    def on_cancelbutton_clicked(self, widget):
        """
        Evento al pulsar sobre el botón Cancelar.
        Envia una respuesta de RESPONSE_CANCEL que hara que el método
        run() pare devolviendo gtk.RESPONSE_CANCEL.
        """
        self.about.response(gtk.RESPONSE_CANCEL)


class DialogIra:
    """
    Popup para la introducción de un nￃﾺmero de registro al que ir.
    """
    def __init__(self, parent_x, parent_y):
        """
        Constructor de la clase.
            parent_x: Coordenada X de la posición de la ventana que invoca
                    al dialogo.
            parent_y: Coordenada Y de la posición de la ventana que invoca
                    al dialogo.
        """
        # Creamos la ventana a partir del archivo glade
        self.glade = gtk.glade.XML("gui/monitorhebras.glade",
                                root="dialogIra")
        # Conectamos todos las señales
        self.glade.signal_autoconnect(self)
        self.popup = self.glade.get_widget("dialogIra")
        
        # Movemos la ventana a la posición del padre
        self.popup.move(parent_x, parent_y)

    def mostrar(self):
        """
        Muestra el popup, devuelve el valor introducido por el usuario
        y se destruye.
        """
        # Mostramos el dialogo
        self.popup.run()
        texto = self.glade.get_widget("txtIra").get_text()
        # Destruimos el dialogo
        self.popup.destroy()
        # Y devolvemos el texto
        return texto

    def on_txtIra_changed(self, widget):
        """
        Evento al cambiar el txt, que borrara todos los caracteres
        que no sean numero.
        """
        pos = widget.get_position()
        char = widget.get_chars(pos, pos + 1)
        if char not in "0123456789":
            widget.select_region(pos, pos + 1)
            widget.delete_selection()

    def on_okbutton_clicked(self, widget):
        """
        Evento al pulsar sobre el botón Aceptar.
        Envia una respuesta de RESPONSE_OK que hara que el método
        run() pare devolviendo gtk.RESPONSE_OK.
        """
        self.popup.response(gtk.RESPONSE_OK)
        
        
class DialogLeyenda:
    """
    Popup para la vision de la leyenda de colores de las tareas
    """
    def __init__(self, colores):
        """
        Constructor de la clase.
            parent_x: Coordenada X de la posición de la ventana que invoca
                    al dialogo.
            parent_y: Coordenada Y de la posición de la ventana que invoca
                    al dialogo.
        """
        # Creamos la ventana a partir del archivo glade
        self.glade = gtk.glade.XML("gui/monitorhebras.glade",
                                root="wLeyenda")
        # Conectamos todos las señales
        self.glade.signal_autoconnect(self)
        self.popup = self.glade.get_widget("wLeyenda")
        self.popup.hide()
        
        # Ponemos los colores de la leyenda
        self.glade.get_widget("cellRunning").set_background_color(gtk.gdk.color_parse(colores[0]))
        self.glade.get_widget("cellSleeping").set_background_color(gtk.gdk.color_parse(colores[1]))
        self.glade.get_widget("cellWaiting").set_background_color(gtk.gdk.color_parse(colores[2]))
        self.glade.get_widget("cellZombie").set_background_color(gtk.gdk.color_parse(colores[3]))
        self.glade.get_widget("cellStopped").set_background_color(gtk.gdk.color_parse(colores[4]))
        self.glade.get_widget("cellPagging").set_background_color(gtk.gdk.color_parse(colores[5]))
        
        self.glade.get_widget("lblRunning").set_tooltip_text("Tarea en ejecución")
        self.glade.get_widget("lblSleeping").set_tooltip_text("Tarea en espera")
        self.glade.get_widget("lblWaiting").set_tooltip_text("Tarea accediendo a disco")
        self.glade.get_widget("lblZombie").set_tooltip_text("Tarea huérfana")
        self.glade.get_widget("lblStopped").set_tooltip_text("Tarea parada por una señal")
        self.glade.get_widget("lblPagging").set_tooltip_text("Tarea paginando")

    def mostrar(self, parent_x, parent_y):
        """
        Muestra el popup
        """
        # Movemos la ventana a la posicion del padre
        self.popup.move(parent_x, parent_y)
        # Mostramos el dialogo
        self.popup.show()
        
    def ocultar(self):
        """
        Oculta el popup
        """
        # Mostramos el dialogo
        self.popup.hide()


class AboutDialog(gtk.AboutDialog):
    """
    Ventana Acerca de la aplicación.
    """
    def __init__(self):
        """
        Constructor de la clase.
        """
        # Llamamos al constructor del padre
        super(AboutDialog, self).__init__()
        # Establecemos todos los datos
        self.set_icon(gtk.gdk.pixbuf_new_from_file(os.path.join(PIX_PATH,"about.png")))
        self.set_name("Monitor Hebras")
        self.set_comments("Monitoriza las hebras de los procesos\nseleccionados pudiendo ver cual es\nsu estado actual, CPU en la que se ejecuta,\netc.")
        self.set_version("0.1")
        self.set_copyright("Copyright (c) 2009 Manuel Soler Moreno")
        # self.set_license(file(os.path.join(PATH, "LICENSE"), "r").read())
        self.set_authors(["Manuel Soler Moreno"])
        self.set_artists(["Icons by the Tango Desktop Project"])
        self.set_logo(gtk.gdk.pixbuf_new_from_file(os.path.join(PIX_PATH, "monitor.png")))
        self.set_modal(True)
        self.show_all()
        # Lo iniciamos
        self.run()
        # Y cuando termine lo destruimos
        self.destroy()

class Dialogo(gtk.MessageDialog):
    """
    Clase que hereda de gtk.MessageDialog y ofrece una interfaz algo mas
    cómoda para generar dialogos.
    """
    def __init__(self, tipo=gtk.MESSAGE_QUESTION, botones=gtk.BUTTONS_OK_CANCEL, mensaje=None, titulo="Dialogo"):
        """
        Constructor de la clase.
        """
        # Primero ejecutamos el constructor de la clase padre
        gtk.MessageDialog.__init__(self, parent=None,
                                flags=gtk.DIALOG_DESTROY_WITH_PARENT,
                                type=tipo, buttons=botones,
                                message_format=mensaje)
        # Y establecemos el titulo y su icono
        self.set_title(titulo)
        self.set_icon(gtk.gdk.pixbuf_new_from_file(os.path.join(PIX_PATH,"dialog-warning.png")))

    def mostrar(self):
        """
        Muestra el dialogo y tras obtener una respuesta
        (GTK response type constants) por parte del usuario lo destruye
        y devuelve la respuesta.
        """
        # Mostramos el dialogo
        respuesta = self.run()
        # Lo destruimos
        self.destroy()
        # Devolvemos la respuesta por parte del usuario
        return respuesta
    
