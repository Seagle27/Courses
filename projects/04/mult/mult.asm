// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

// Put your code here.

	@R0
	D = M
	@num0  // num0 = R0
	M = D

	@R1
	D = M
	@num1  // num1 = R1 
	M = D
	
	@R2  // sum = 0
	M = 0
	
	@i  // i=0
	M = 0
	
(LOOP)
	@i  // if (num0 - i) == 0: GOTO END
	D = M
	@num0
	D = M - D
	@END
	D;JEQ
	@num1
	D = M
	@R2  // sum = sum + R1
	M = M + D
	@i
	M = M + 1
	@LOOP  // GOTO LOOP  
	0;JMP
(END)
	@END
	0;JMP
	
	
	