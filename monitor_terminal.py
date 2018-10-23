#!/usr/bin/env python
#Este archivo tiene encoding: utf-8

'''
Monitor de proceso y hebras para la terminal.
'''

import sys
import subprocess
import os
import time
import threading

from system info import procinfo, cpuinfo
from config import log


class PrintInfo(threading.Thread):
	'''
	Thread para la impresion de informacion por pantalla.
	'''
	def __init__(self, info_cpus, proc, hebras):
		'''
		Inicializa el thread pasandole los parametros:
		info_cpus: Lista que contiene la informacion de las cpus.
		proc: Objeto Proceso que contiene la informacion del
				proceso principal.
		hebras: Lista de objetos Hebra con la informacion de una
				hebra del	proceso principal.
		'''
		self.info_cpus = info_cpus
		self.proc = proc
		self.hebras = hebras
		threading.Thread.__init__(self)

	def run(self):
		'''
		Metodo que se ejecuta al ejecutar start() en la hebra.
		Muestra la informacion del objeto por pantalla, es decir,
			la que se le ha pasado por parametros.
		'''
		# Limpiamos la pantalla (clear)
		subprocess.Popen("clear").communicate()
		print "\nCPU INFO"
		print "-"*10
		# Para cada cpu del sistema
		for cpu in self.info_cpus:
			if cpu.total: # cpu.total no es 0
				#Mostramos su nombre (cpu#), y el % en uso y libre
				print ("cpu" + str(cpu.num_cpu) + ":\t" +
						cpu.get_percen_busy() + "% Uso " +
						cpu.get_percen_idle() + "% Libre")
		print "\nPROCESO PRINCIPAL"
		print "-"*10
		# Mostramos informacion del proceso principal
		print "Nombre:", self.proc.nombre
		print "Estado:", self.proc.estado
		print "CPU:", self.proc.num_cpu
		print "Num Hebras:", self.proc.num_hebras
		print "\nHEBRAS"
		print "-"*10
		# Si existen hebras en el proceso principal
		if self.hebras is not None:
			# para cada una de ellas
			for hebra in self.hebras:
				# Mostramos su informacion
				print ("PID:", hebra.pid, "\tEstado:", hebra.estado,
						"\tCPU:", hebra.num_cpu)
		else:
			print "No existen hebras para este proceso."


def main(argv=None):
	'''
	Realiza un seguimiento sobre el estado del proceso.
	'''
	if len(sys.argv) < 2:
		# Si no ha habido argumentos, monitorizamos este programa
		pid = os.getpid()
	else:
		# Obtenemos el pid del programa pasado por parametros
		proc = procinfo.pgrep(sys.argv[1])
		if proc is None:
			# Si no existe se informa con un error
			print "ERROR: No existen procesos con el pid", pid
			sys.exit(1)
		# Establecemos el pid a monitorizar
		pid = proc[0]
	# Establecemos el tiempo de actualizacion de los datos en 0.1 sg
	tiempo = 0.1
	# Obtengo el numero de cpus del sistema
	num_cpus = cpuinfo.num_cpus()
	while True:
		info_cpus, hebras = [], []
		proceso = procinfo.proc_status(pid)
		# Obtengo la informacion de las hebras del proceso a partir de su pid
		tProc = procinfo.InfoThreads(proceso, hebras)
		tProc.start()
		# Obtengo la informacion de las cpus lanzando una hebra
		tCpus = cpuinfo.InfoCPUS(num_cpus, info_cpus)
		tCpus.start()
		# Hago al proceso principal esperar a que terminen ambas hebras
		tCpus.join()
		tProc.join()
		# Lanzo una hebra para guardar la informacion obtenida en un archivo
		guardarTrace = log.SaveToFile(info_cpus, proceso, hebras, "/home/manu/pylog.txt")
		guardarTrace.start()
		# Lanzo una hebra para mostrar la informacion obtenida por pantalla
		mostrarInfo = PrintInfo(info_cpus, proceso, hebras)
		mostrarInfo.start()
		# Espero un tiempo antes de volver a recoger informacion
		time.sleep(tiempo)
		mostrarInfo.join()

if __name__ == "__main__":
	try:
		main(sys.argv)
	except KeyboardInterrupt:
		print "\nAdios!"
