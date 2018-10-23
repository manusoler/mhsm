#!/usr/bin/env python
#Este archivo usa encoding: utf-8

'''
Programa principal.
'''

import gtk

from gui import interfaz

def main(argv=None):
    # Creamos una instancia de la ventana principal
    interfaz.wMonitorizar()
    # Inidicamos a gtk que use las macros de Python para permitir
    # multiples hilos
    gtk.gdk.threads_init()
    gtk.gdk.threads_enter()
    # Y la arrancamos
    gtk.main()
    gtk.gdk.threads_leave()

if __name__ == "__main__":
    #Esto se ejecuta al iniciar la aplicación
    try:
        main()
    except KeyboardInterrupt:
        pass
