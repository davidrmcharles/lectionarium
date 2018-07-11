======================================================================
``README`` for ``lectionarium``
======================================================================

``lectionarium`` is a lectionary, in Latin, for Ordinary From of the
Mass and the source of `fideidepositum.org
<http://fideidepositum.org>`_.

Here are some things it can do:

* `View a Set of Lectionary Readings`_
* `View a Scripture Passage`_
* `Render the Whole Bible as HTML`_

View a Set of Lectionary Readings
======================================================================

To see today's readings, use script ``lectionary.sh``:

.. code-block:: text

    $ bin/lectionary.sh today
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

View a Scripture Passage
======================================================================

Under the hood is an entire Latin Bible whose text comes from `The
Clementine Vulgate project
<http://vulsearch.sourceforge.net/index.html>`_.  So, if instead you
just want to see just a single passage of Sacred Scripture, use script
``bible.sh``:

.. code-block:: text

    $ bin/bible.sh ex 20:1-17
    20:1 Locutusque est Dominus cunctos sermones hos: 20:2 Ego sum
    Dominus Deus tuus, qui eduxi te de terra Ægypti, de domo servitutis.
    20:3 Non habebis deos alienos coram me. 20:4 Non facies tibi
    . . . snip . . .

Render the Whole Bible as HTML
======================================================================

There is an ant target, ``bible``, to render the entire bible as HTML.

.. code-block:: text

    $ ant bible
