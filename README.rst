======================================================================
lectionarium
======================================================================

``lectionarium`` is a Latin lectionary for the Ordinary Form of the
Mass in the Roman Rite implemented in Python.

The Latin text comes from the vulsearch project: http://vulsearch.sourceforge.net/index.html

Two scripts, ``lectionary.sh`` and ``bible.sh`` provide a command-line
interface.

To see today's readings, use ``lectionary.sh``:

.. code-block:: none

    $ ./lectionary.sh today
    ================================================================================
    Readings for Friday (Cycle A, I)
    ================================================================================

    Romans 9:1-9:5

    9:1 Veritatem dico in Christo, non mentior: testimonium mihi perhibente
    conscientia mea in Spiritu Sancto: 9:2 quoniam tristitia mihi magna
    est, et continuus dolor cordi meo. 9:3 Optabam enim ego ipse anathema
    . . . snip . . .

You may also see the readings for a particular date or for the mass
with a particular name.

If instead you just want to see a passage of Sacred Scripture, use
``bible.sh``:

.. code-block:: none

    $ ./bible.sh ex 20:1-17
    20:1 Locutusque est Dominus cunctos sermones hos: 20:2 Ego sum
    Dominus Deus tuus, qui eduxi te de terra Ægypti, de domo servitutis.
    20:3 Non habebis deos alienos coram me. 20:4 Non facies tibi
    . . . snip . . .

That's all at the moment!
