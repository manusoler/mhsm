TODO
----------------
* Refinar todo el codigo y refactorizar bien el codigo
* Cerrar la aplicacion mientras se esta monitorizando
* Mostrar ventana información de cada CPU
* Guardar el tiempo de monitorizacion
* Monitorizacion en forma remota (SSH?)???

BUGS
---------------
./monitor.py:19: GtkWarning: file /build/buildd/gtk+2.0-2.18.3/gtk/gtktreeview.c: line 4891 (gtk_tree_view_bin_expose): assertion `has_next' failed.
There is a disparity between the internal view of the GtkTreeView,
and the GtkTreeModel.  This generally means that the model has changed
without letting the view know.  Any display from now on is likely to
be incorrect.

./monitor.py:19: GtkWarning: gtk_list_store_get_value: assertion `VALID_ITER (iter, list_store)' failed
  gtk.main()
./monitor.py:19: Warning: g_object_set_property: assertion `G_IS_VALUE (value)' failed
  gtk.main()
./monitor.py:19: Warning: g_value_unset: assertion `G_IS_VALUE (value)' failed
  gtk.main()
Fallo de segmentación

