Solving the Rubik's Cube
=========================

:date: 2014-04-03
:tags: puzzles, rubick
:category: play
:slug: rubik-solve
:summary: Algorithm for solving Rubik's Cube.

See `notation <{filename}rubik-notation.rst>`_.

Cross of the first layer
------------------------

Moves cube FD -> FU

F->F, D->U
  F\ |^2|


F->U, D->F
  D R F' R'
  or
  F' |M'_D| F |M_D|


Corners of the first layer
--------------------------

Moves cube FDL -> FUL

F->F, D->L, L->U
  L D L'


F->U, D->F, L->L
  F' U' F


F->L, D->U, L->F
  ( F' R' ) D\ |^2| ( R F )


Second layer
------------

Moves cube FD

F->F, D->L
  ( D L D' L' ) ( D' F' D F )


F->F, D->R
  ( D' R' D R ) ( D F D' F' )


Placing side cubes of third layer
---------------------------------

Moves cube FU -> LU
  (U F R ) U (R' U' F' )


Cross of the third layer
------------------------

Rotating cube UR

Rotate UR and UB
  ( R |M_D| )\ |^4| U ( R |M_D| )\ |^4|


Rotate UR and UF
  ( R |M_D| )\ |^4| U' ( R |M_D| )\ |^4|


Rotate UR and UL
  ( R |M_D| )\ |^4| U\ |^2| ( R |M_D| )\ |^4|


Placing corner cubes of third layer
-----------------------------------

Moves cubes FLU, FLR, RUB, cube ULB is not moving

Shift by one position clockwise
  ( R' F' L' F ) (R F' L F )


Shift by one position counter-clockwise
  ( F' L' F R' ) ( F' L F R )


Final placement
---------------

Rotate the cube FUR

[ ( R F' R' F )\ |^2| ]\ |^n| {U | U' | U\ |^2| } [ ( R F' R' F )\ |^2| ]\ |^n|

+ ``n`` - rotates FUR by ``n/3`` clockwise
+ U - rotates FUR and RUB
+ U' - rotates FUR and FUL
+ U\ |^2| - rotates FUR and LUB

.. |^n| replace:: \ :sup:`n`

.. |^4| replace:: \ :sup:`4`

.. |^2| replace:: \ :sup:`2`

.. |M_D| replace:: M\ :sub:`D`

.. |M'_D| replace:: M'\ :sub:`D`

