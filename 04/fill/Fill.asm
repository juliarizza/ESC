// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed.
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// set the max number of iterations
@8192
D=A
@max
M=D

// reset D and iterations count
(START)
@0
D=A
@iter
M=D-1 // iteration starts at -1 because loop starts adding 1

(LOOP)
  @iter
  M=M+1 // iter = iter + 1

  // if iter = max, reset iterations
  D=M // D = iter
  @max
  D=M-D // D = max - iter
  @START
  D;JEQ // D = 0 ? yes => jump to START

  // read the keyboard value
  @KBD
  D=M

  // jump to DRAWBLACK if a key is pressed
  @DRAWBLACK
  D;JNE // D != 0

  // if D = 0 continue and draw white
  @iter
  D=M // get the iteration number
  @SCREEN
  A=A+D // get the word position for the iteration
  M=0 // write 0 to that word
  @LOOP
  0;JMP // go to the next iteration

  (DRAWBLACK)
  @iter
  D=M // get the iteration number
  @SCREEN
  A=A+D //get the word position for the iteration
  M=-1 // write 1 to all the 16 bits of that word
  @LOOP
  0;JMP // go to the next iteration
