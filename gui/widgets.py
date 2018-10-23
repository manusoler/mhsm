#Este archivo esta en encoding: utf-8

"""
Módulo con widgets GTK.

G{importgraph}
"""

# a pygtk widget that implements a special rule
# porting of Davyd Madeley's

# author: Manuel Soler Moreno <manusoler@gmail.com>
# date: 02 April 2010

import gtk

class SpecialRule(gtk.DrawingArea):
    """
    Widget que implementa una regla especial.
    """

    def __init__(self, total_ticks=0, ticks_per_band=50, num_big_ticks=[], funcion=None):
        """
        Constructor de la clase.
        @param total_ticks: Numero de ticks que tendra la regla.
        @type total_ticks: int
        @param ticks_per_band: Numero de ticks maximos por banda
        @type ticks_per_band: int
        @param num_big_ticks: Lista con los numeros de los ticks
            que estaran marcados de forma especial
        @type num_big_ticks: list
        @param funcion: Funcion a ejecutar cada vez que se pulse el widget
        @type funcion: function
        """
        gtk.DrawingArea.__init__(self)
        # Anadimos eventos de presionado y movimiento de raton
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK |
                        gtk.gdk.POINTER_MOTION_MASK)
        # Conectamos los eventos
        self.connect("expose_event", self.expose)
        self.connect("button_press_event", self.pressing)
        self.connect("motion_notify_event", self.moving)

        # Numero de ticks en la regla
        self.total_ticks = total_ticks
        # Elementos que tendran grandes ticks
        self.num_big_ticks = num_big_ticks
        # Maxima de ticks por bandada
        self.ticks_per_band = ticks_per_band
        # Tick actual
        self.actual = 1
        # Banda actual mostrada
        self.banda = 0
        # Posicion raton
        self.pos_raton = 0
        # Funcion
        self.funcion = funcion

    def pressing(self, widget, event):
        """
        Evento al pulsar con el raton sobre el widget.
        """
        nticks = self.total_ticks
        if self.total_ticks > self.ticks_per_band:
            nticks = self.ticks_per_band
        # Calculamos cual es el tick que se ha presionado
        click = event.x
        incr = self.get_allocation().width / (nticks - 1)
        self.set_actual(int(click / incr) + 1 + self.banda * self.ticks_per_band)
        # Redibujamos el widget
        self.queue_draw()
        # Ejecutamos la funcion (si no es None)
        if self.funcion is not None:
            self.funcion()

    def moving(self, widget, event):
        """
        Evento al mover el raton por encima del widget.
        """
        # Calculamos la posicion del raton
        self.pos_raton = event.x
        # Establecemos en el tooltip el numero de tick
        self.set_tooltip_text(str(self.__tick_in(event.x)))
        # Redibujamos el widget
        self.queue_draw()  

    def set_function(self, function):
        """
        Establece la funcion a ejecutar cada vez que se pulse en el
        widget.
        @param function: La funcion a ejecutar
        @type function: function
        @rtype: void
        """
        self.funcion = function

    def set_big_mark(self, num):
        """
        Dibuja una marca mas grande en el tick numero num.
        @param num: El tick en el cual se ha de dibujar la marca.
        @type num: int | list
        @rtype: void
        """
        if type(num) is list:
            # Si num es una lista la anadimos a la nuestra
            self.num_big_ticks.extend(num)
        else:
            # Anadimos el numero a la lista de grandes ticks
            self.num_big_ticks.append(num)
        # Redibujamos el widget
        self.queue_draw()

    def remove_big_mark(self, num):
        """
        Elimina la marca mas grande en el tick numero num.
        @param num: El tick en el cual se ha de eliminar la marca.
        @type num: int | list
        @rtype: void
        """
        try:
            if type(num) is list:
                # Si num es una lista eliminamos sus elementos
                #de la nuestra
                for i in num:
                    self.num_big_ticks.remove(i)
            else:
                # Eliminamos el numero de la lista de grandes ticks
                self.num_big_ticks.remove(num)
        except ValueError:
            pass
        # Redibujamos el widget
        self.queue_draw()

    def set_total_ticks(self, total_ticks):
        """
        Establece el numero de ticks.
        @param ticks: El numero de ticks.
        @type ticks: int
        @rtype: void
        """
        self.total_ticks = total_ticks
        # Redibujamos el widget
        self.queue_draw()

    def set_actual(self, actual):
        """
        Establece el nuevo tick actual.
        @param actual: El nuevo tick actual.
        @type actual: int
        @rtype: void
        """
        # Comprobamos si el tick es valido  
        if actual not in range(1, self.total_ticks + 1):
            return
        # Comprobamos si el tick esta en la banda actual
        if actual not in range(self.banda * self.ticks_per_band + 1, (self.banda + 1) * self.ticks_per_band + 1):
            # Si no esta calculamos cual sera
            for banda in range(self.total_ticks / self.ticks_per_band + 1):
                if actual in range(banda * self.ticks_per_band + 1, (banda + 1) * self.ticks_per_band + 1):
                    self.banda = banda
                    break
        self.actual = actual
        # Redibujamos el widget
        self.queue_draw()

    def get_actual(self):
        """
        Obtiene el tick actual.
        @return: El tick actual
        @rtype: int
        """
        return self.actual

    def expose(self, widget, event):
        """
        Evento que se llama cada vez que se quiere dibujar
        el widget.
        """
        self.context = widget.window.cairo_create()
        # set a clip region for the expose event
        self.context.rectangle(event.area.x, event.area.y,
                               event.area.width, event.area.height)
        self.context.clip()
        self.draw(self.context)
        return False

    def draw(self, context):
        """
        Dibuja el widget
        """
        rect = self.get_allocation()
        nticks = self.total_ticks
        if self.total_ticks > self.ticks_per_band:
            nticks = self.ticks_per_band
        x = rect.x
        y = (rect.y + rect.height) / 2
        incr = rect.width / (nticks - 1)
        # main line
        context.set_source_rgb(0, 0, 0)
        context.move_to(x, y)
        context.line_to(x + rect.width, y)
        context.stroke()
        
        # rule ticks
        context.set_font_size(8)
        x += 1
        inicio = self.banda * self.ticks_per_band + 1
        fin = (self.banda + 1) * self.ticks_per_band
        if fin > self.total_ticks:
            fin = self.total_ticks
        for i in range(inicio, fin + 1):
            context.save()
            height = 5
            if i in self.num_big_ticks:
                context.set_source_rgb(1, 0, 0)
                height = 7
            if i == self.actual:
                context.set_source_rgb(0, 1, 0)
            context.move_to(x, y + height)
            context.line_to(x, y - height)
            context.stroke()
            context.move_to(x - 4, y + 2 * height + 3)
            context.show_text(str(i))
            context.restore()
            x += incr

        #mouse pos
        context.set_source_pixbuf(gtk.gdk.pixbuf_new_from_file("gui/pixmaps/puntero.png"), self.pos_raton - 7, y - 2 - 14)
        context.paint()

    def __tick_in(self, pos_x):
        nticks = self.total_ticks
        if self.total_ticks > self.ticks_per_band:
            nticks = self.ticks_per_band
        # Calculamos cual es el tick sobre el que esta pos_x
        incr = self.get_allocation().width / (nticks - 1)
        return int(pos_x / incr) + 1 + self.banda * self.ticks_per_band

