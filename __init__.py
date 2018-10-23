"""
En esta pagina obtendra toda la informacion acerca del codigo de la
aplicacion Monitor de Hebras.

Package Organization 
==================== 

El paquete MonitorHebras contine los siguientes subpaquetes y modulos:

G{packagetree} 

The user interfaces are provided by the `gui` and `cli` modules. 
The `apidoc` module defines the basic data types used to record 
information about Python objects.  The programmatic interface to 
epydoc is provided by `docbuilder`.  Docstring markup parsing is 
handled by the `markup` package, and output generation is handled by 
the `docwriter` package.  See the submodule list for more 
information about the submodules and subpackages. 
 
@author: `Manuel Soler Moreno <manusoler@gmail.com>`__ 
@requires: Python 2.6 
@version: 1.0.0 
@see: `The epydoc webpage <http://epydoc.sourceforge.net>`__ 
@see: `The epytext markup language 
      manual <http://epydoc.sourceforge.net/epytext.html>`__ 
 
@todo: Create a better default top_page than trees.html. 
@todo: Fix trees.html to work when documenting non-top-level 
      modules/packages 
@todo: Implement @include 
@todo: Optimize epytext 
@todo: More doctests 
@todo: When introspecting, limit how much introspection you do (eg, 
       don't construct docs for imported modules' vars if it's 
       not necessary) 
 
@bug: UserDict.* is interpreted as imported .. why?? 
  
@license: GPL
@copyright: (c) 2009 Manuel Soler Moreno

@newfield contributor: Contributor, Contributors (Alphabetical Order) 
@contributor: `Glyph Lefkowitz  <mailto:glyph@twistedmatrix.com>`__ 
@contributor: `Edward Loper  <mailto:edloper@gradient.cis.upenn.edu>`__ 
@contributor: `Bruce Mitchener  <mailto:bruce@cubik.org>`__ 
@contributor: `Jeff O'Halloran  <mailto:jeff@ohalloran.ca>`__ 
@contributor: `Simon Pamies  <mailto:spamies@bipbap.de>`__ 
@contributor: `Christian Reis  <mailto:kiko@async.com.br>`__ 
@contributor: `Daniele Varrazzo  <mailto:daniele.varrazzo@gmail.com>`__ 
@contributor: `Jonathan Guyer <mailto:guyer@nist.gov>`__ 

"""
