//C_PUSH constant 3030
@3030
D=M
@SP
A=M
M=D
@SP
M=M+1
//C_POP pointer 0
@THAT
D=A
@SP
M=M-1
A=M
D=M
//C_PUSH constant 3040
@3040
D=M
@SP
A=M
M=D
@SP
M=M+1
//C_POP pointer 1
@THAT
D=A
@SP
M=M-1
A=M
D=M
//C_PUSH constant 32
@32
D=M
@SP
A=M
M=D
@SP
M=M+1
//C_POP this 2
@THIS
D=M
@2
A=A+D
D=M
@SP
M=M-1
A=M
D=M
//C_PUSH constant 46
@46
D=M
@SP
A=M
M=D
@SP
M=M+1
//C_POP that 6
@THAT
D=M
@6
A=A+D
D=M
@SP
M=M-1
A=M
D=M
//C_PUSH pointer 0
@THAT
D=A
@SP
A=M
M=D
@SP
M=M+1
//C_PUSH pointer 1
@THAT
D=A
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
//C_PUSH this 2
@THIS
D=M
@2
A=A+D
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
//C_PUSH that 6
@THAT
D=M
@6
A=A+D
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
