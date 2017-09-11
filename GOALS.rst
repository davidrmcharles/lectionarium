======================================================================
Goals for ``lectionarium``
======================================================================

* `Long-Term Goal`_
* `Short-Term Goal`_
* `Present Status`_
* `Next Steps`_

Long-Term Goal
======================================================================

In the long-term, I want to put the lectionary of the Ordinary Form on
the Internet in Latin.

Short-Term Goal
======================================================================

In the short-term, I'd be ecstatic if I could say:

.. code-block:: sh

    $ lectionarium.py

And today's readings would come out.

Present Status
======================================================================

Presently, I can say:

.. code-block:: sh

    $ bible.py ex 20:1-17

And the decalogue appears in a human-readable form::

    [20:1] Locutusque est Dominus cunctos sermones hos :  [20:2] Ego sum Dominus
    Deus tuus, qui eduxi te de terra Ægypti, de domo servitutis.  [20:3] Non
    habebis deos alienos coram me.  [20:4] Non facies tibi sculptile, neque omnem
    similitudinem quæ est in cælo desuper, et quæ in terra deorsum, nec eorum
    quæ sunt in aquis sub terra.  [20:5] Non adorabis ea, neque coles : ego sum
    Dominus Deus tuus fortis, zelotes, visitans iniquitatem patrum in filios, in
    tertiam et quartam generationem eorum qui oderunt me :  [20:6] et faciens
    misericordiam in millia his qui diligunt me, et custodiunt præcepta mea.
    [20:7] Non assumes nomen Domini Dei tui in vanum : nec enim habebit insontem
    Dominus eum qui assumpserit nomen Domini Dei sui frustra.  [20:8] Memento ut
    diem sabbati sanctifices.  [20:9] Sex diebus operaberis, et facies omnia opera
    tua.  [20:10] Septimo autem die sabbatum Domini Dei tui est : non facies omne
    opus in eo, tu, et filius tuus et filia tua, servus tuus et ancilla tua,
    jumentum tuum, et advena qui est intra portas tuas.  [20:11] Sex enim diebus
    fecit Dominus cælum et terram, et mare, et omnia quæ in eis sunt, et requievit
    in die septimo : idcirco benedixit Dominus diei sabbati, et sanctificavit eum.
    [20:12] Honora patrem tuum et matrem tuam, ut sis longævus super terram, quam
    Dominus Deus tuus dabit tibi.  [20:13] Non occides.  [20:14] Non mœchaberis.
    [20:15] Non furtum facies.  [20:16] Non loqueris contra proximum tuum falsum
    testimonium.  [20:17] Non concupisces domum proximi tui, nec desiderabis uxorem
    ejus, non servum, non ancillam, non bovem, non asinum, nec omnia quæ illius
    sunt.\


I got here in a bottom-up fashion by modeling the numerical portion of
the citation (``locs.py``), the book portion (``books.py``), and the
aggregation of the two (``citations.py``)

The text comes from `here
<http://vulsearch.sourceforge.net/index.html>`_ but goes through a
little massage (``preprocessclemtext.py``) prior to consumption by
``books.py``.

The high-level interface onto the whole thing is ``bible.py``.

Next Steps
======================================================================

The next step is to model the lectionary with all of its celebrations
in terms of these citations (``lectionarium.py``).  Then we will be
able to retrieve the readings associated with any known celebration.

Then, if we model the liturgical calendar (``calendarium.py``), we
will know the liturgical celebration associated with any given date
and the `Short-Term Goal`_ will be achieved.
