Rubik's Cube
=============

:date: 2014-04-01
:tags: puzzles, rubik
:category: play
:slug: rubik-notation
:summary: Notation used in posts on Rubik's Cube

About
-----
Quite probably the best known puzzle in the world - cube consisting
of 3x3x3 matrix of colored cubes, that can be rotated per layer.

Notation used
-------------
Choose the front face - the one facing you. Then the letters denote:


.. image:: {static}/images/rubik-files/rubik-rotations.svg
   :height: 300px
   :align: center
   :alt: Slice rotations

.. image:: {static}/images/rubik-files/rubik-3d.svg
   :height: 300px
   :align: center
   :alt: Whole cube rotations

F
    rotate the front face of the cube clock-wise
B
    rotate the rear (back) face of the cube counter-clockwise (clockwise if you would make it front)
R
    rotate the right face of the cube upward (clockwise if you would make it front front)
L
    rotate the left face of the cube downward (i.e. also clockwise)
U
    rotate the top (upper) face of the cube to the left (i.e. clockwise)
D
    rotate the bottom (down) face of the cube to the right (i.e. clockwise)
|M_R|
    rotate the middle slice of the cube upward (clockwise, as R turn)
|M_D|
    rotate the middle slice to the right (clockwise, as D turn)
|M_F|
    rotate the unseen middle slice clockwise (the slice between front and rear faces)
|G_R|
    rotate the whole cube upward (clockwise, as R turn)
|G_F|
    rotate the whole cube clockwise (as F turn)
|G_D|
    rotate the whole cube to the right (as D turn)

The primed letter means change of direction to counterclockwise:
F', B', R', L', U', D', |M'_R|, |M'_D|, |M'_F|, |G'_R|, |G'_F|, |G'_D|.


.. |M_R| replace:: M\ :sub:`R`

.. |M_F| replace:: M\ :sub:`F`

.. |M_D| replace:: M\ :sub:`D`

.. |G_R| replace:: G\ :sub:`R`

.. |G_F| replace:: G\ :sub:`F`

.. |G_D| replace:: G\ :sub:`D`

.. |M'_R| replace:: M'\ :sub:`R`

.. |M'_F| replace:: M'\ :sub:`F`

.. |M'_D| replace:: M'\ :sub:`D`

.. |G'_R| replace:: G'\ :sub:`R`

.. |G'_F| replace:: G'\ :sub:`F`

.. |G'_D| replace:: G'\ :sub:`D`
