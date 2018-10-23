# Monitor de Hebras MHSM

La aplicación MHSM es el trabajo realizado como proyecto fin de carrera (Ingeniería Informática - 2010) por el alumno Manuel Soler Moreno de la Universidad de Almería en colaboración con los profesores D. Juan Fº Sanjuan Estrada y D. Leocadio G. Casado.

## ¿Qué es MHSM?
El principal objetivo del MHSM es ayudar al desarrollador de aplicaciones en sistemas multicore a realizar un seguimiento de las hebras de su aplicación, a la vez que le permite contemplar el estado del sistema, siendo posible realizar este seguimiento, de forma mas detallada, una vez que el programa ha finalizado su ejecución. Todo esto será posible a través de una aplicación muy sencilla de utilizar, de tal forma que el programador se centrará en el funcionamiento de su aplicación y no en como hacer funcionar el monitor.

Las principales características que ofrece MHSM son:

* Seguimiento simultáneo de las distintas hebras, de una o varias aplicaciones.
* Posibilidad de almacenar toda la información de las monitorizaciones realizadas.
* Posibilidad de mejorar la precisión de la información, modificando el tiempo de muestreo de la herramienta.
* Visualización de monitorizaciones almacenadas, permitiendo la navegación por los registros con total libertad, y en arquitecturas diferentes al monitorizado.
* Posibilidad de etiquetar eventos en los registros por medio de comentarios.
* Barra de navegación resaltando los registros con eventos.
* Generación de hasta 4 tipos de gráficas totalmente configurables, a partir de una base de datos donde se almacena las monitorizaciones previas.
* Posibilidad de exportar las gráficas a distintos formatos (xls, eps).

Para realizar todo esto, MHSM se compone de tres bloques fundamentales:
* Monitor de aplicaciones
* Visualizador offline
* Generador de gráficas

![Arquitectura MHSM](http://mhsm.msolm.es/_images/arquitectura.png "Arquitectura MHSM")

