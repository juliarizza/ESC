// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

// set number of iterations
// iter = R1
@R1
D=M
@iter
M=D

// set sum to 0
// R2 = 0
@R2
M=0

// set D = R0
@R0
D=M

(LOOP)
  // for each iteration do iter - 1
  @iter
  M=M-1
  // if iter < 0 jump to end
  @END
  M;JLT

  // make sum = sum + D
  @R2
  M=D+M
  // restart loop
  @LOOP
  0;JMP

// prevent program to continue
(END)
  @END
  0;JMP
