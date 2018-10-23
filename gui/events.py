#Este archivo esta en encoding: utf-8

"""
Módulo con clase evento y listener para implementar programacion orientada 
a eventos.

G{importgraph}
"""

# Programación orientada a eventos
#
# La técnica emplea "referencias débiles" (weakref)
# con lo que al saltar un evento no hay problema si
# el objeto oyente (listener) ya no existe

import weakref

class Listener(object):
    '''
    Clase abstracta que implementa el Listener
    '''
    def DoEvent(self,evt): pass

class Event(object):
    '''
    Evento que alertara a los listeners
    '''
    def __init__(self, name, listeners=None):
        '''
        Constructor de la clase
        @param name: Nombre del evento
        @type name: str
        @param name: Listener o lista de ellos que responderan al evento
        @type name: tuple, list or Listener
        '''
        self.name=name
        self.listeners=[]
        if listeners:
            self.Register(listeners)

    def Register(self,lst):
        '''
        Añade un Listener o una lista de ellos al evento
        @param lst: Listener o lista de ellos que responderan al evento
        @type lst: tuple, list or Listener
        '''
        #quitamos morralla (referencias inválidas)
        self.listeners = [ l for l in self.listeners if l() != None]
        if isinstance(lst,Listener):
            self.listeners.append(weakref.ref(lst))
        elif isinstance(lst, (list, tuple)):
            L = [weakref.ref(l) for l in lst if isinstance(l,Listener)]
            self.listeners.extend(L)

    def Cancel(self,lst):
        '''
        Elimina un Listener o una lista de ellos del evento
        @param lst: Listener o lista de ellos que responderan al evento
        @type lst: tuple, list or Listener
        '''
        l=weakref.ref(lst)
        if l in self.listeners:
            self.listeners.remove(l)

    def CancelAll(self):
        '''
        Elimina todos los Listener del evento
        '''
        self.listeners=[]

    def Raise(self):
        '''
        Propaga el evento por todos los listener
        '''
        for lst in self.listeners:
            ref = lst() #weakref handle
            if ref:
                ref.DoEvent(self)

if __name__=="__main__":

    class MyListener(Listener):
        def __init__(self,name):
            self.name=name

        def DoEvent(self,evt):
            print "\tOyente '%s' escuchando evento '%s'" % \
                (self.name,evt.name)

    l1=MyListener("Primero")
    l2=MyListener("Segundo")

    alarm=Event("Alarma", (l1,l2))

    #alternativamente podríamos haber puesto
    #~ alarm.Register(l1)
    #~ alarm.Register(l2)

    print "LANZANDO PRIMER EVENTO..."
    alarm.Raise()

    #borramos el segundo escucha.
    #normalmente se suele cancelar con:
    # alarm.Cancel(l2)
    del l2
    
    print "LANZANDO SEGUNDO EVENTO..."
    alarm.Raise()

    #cancelamos todas las escuchas
    alarm.CancelAll()

    print "LANZANDO TERCER EVENTO..."
    alarm.Raise() #no hace nada, por no existir oyentes
