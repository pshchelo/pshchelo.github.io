Solving 2x2 Rubik's cube
==========================

:date: 2020-12-13
:tags: puzzles, rubik
:category: play
:slug: rubik2-solve
:summary: Algorithm for solving 2x2 Rubik's Cube.


Base combinations
-----------------

1. Swap FRU <-> FRD  - ``R U R' U'`` (with rotation)

   Repeat, and cubes are back to previous places but rotated.
   Repeat 6 times changes nothing, everything comes back to original places

2. Swap FRU <-> FLU - ``U R U' L' U R' U' L U`` (with some rotation)

   The D layer stays unchanged, the BRU and BLU rotate too.


Base algorithm
--------------

1. Build one layer, it becomes D-layer for now,
   should be easy enough w/o any explicit algorithm.
2. Use combo 2 to place the cubes of U layer in the correct places,
   disregarding their rotation for now.
3. Turn the cube upside down, the already built D-layer becomes U-layer.
4. Start rotating the now D-layer using combo 1 x2 or x4 - do not worry that
   U-layer becomes undone.
5. **w/o rotating the whole cube**, use `D` or `D'` to place the next
   incorrectly rotated cube of D layer to position FRD.
6. Repeat step 4 and 5.
7. Apart from some U or D rotation it should come together eventually when
   rotating the last incorrect D-layer cube.

`Source <https://www.youtube.com/watch?v=AJCW5xTjmTk>`_.
