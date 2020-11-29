//C_PUSH constant 111
@111
D=M
@SP
A=M
M=D
@SP
M=M+1
//C_PUSH constant 333
@333
D=M
@SP
A=M
M=D
@SP
M=M+1
//C_PUSH constant 888
@888
D=M
@SP
A=M
M=D
@SP
M=M+1
//C_POP static 8
@C:\temp\nand2tetris\projects\07\MemoryAccess\StaticTest\StaticTest.asm.8
D=M
@SP
M=M-1
A=M
D=M
//C_POP static 3
@C:\temp\nand2tetris\projects\07\MemoryAccess\StaticTest\StaticTest.asm.3
D=M
@SP
M=M-1
A=M
D=M
//C_POP static 1
@C:\temp\nand2tetris\projects\07\MemoryAccess\StaticTest\StaticTest.asm.1
D=M
@SP
M=M-1
A=M
D=M
//C_PUSH static 3
@C:\temp\nand2tetris\projects\07\MemoryAccess\StaticTest\StaticTest.asm.3
D=M
@SP
A=M
M=D
@SP
M=M+1
//C_PUSH static 1
@C:\temp\nand2tetris\projects\07\MemoryAccess\StaticTest\StaticTest.asm.1
D=M
@SP
A=M
M=D
@SP
M=M+1
//sub
@SP
M=M-1
A=M
D=M
A=A-1
M=M-D
//C_PUSH static 8
@C:\temp\nand2tetris\projects\07\MemoryAccess\StaticTest\StaticTest.asm.8
D=M
@SP
A=M
M=D
@SP
M=M+1
//add
@SP
M=M-1
A=M
D=M
A=A-1
M=M+D
