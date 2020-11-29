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

// Put your code here.

	@lastState  // Init lastState = 0
	M = 0
	
(LOOP)
	@state  // Init state = 0
	M = 0
	@KBD
	D = M
	@KbdNotPressed
	D;JEQ  //Set state to -1 if keyboard is pressed
	@state
	M = -1
	
	
	(KbdNotPressed)
	@lastState
	D = M
	@state
	D = D + M
	@LOOP
	D;JEQ  // Return to the begining of the loop if the current state is similar to the previous one
	
	
	@state
	D = M
	@lastState
	M = D  // Update lastState
	@SCREEN
	D = A
	@addr  // Init Pointer to current address
	M = D
	(FillLoop)
	@addr
	D = M
	@KBD
	D = A - D
	@LOOP
	D;JEQ  // Return to the begining of the loop if the filling the screen was completed
	
	@state
	D = M
	@addr
	A = M
	M = D  // Change the current pixel color
	
	@addr
	M = M + 1
	@FillLoop  // Continue to the next FillLoop iteration
	0;JMP
	
	
	
	
	
	
	
	
	