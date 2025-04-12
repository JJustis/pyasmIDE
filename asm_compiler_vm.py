
"""
Assembly Compiler and Virtual Machine
-------------------------------------
This module provides a basic assembly compiler and virtual machine.
"""
import re
from enum import Enum, auto
from typing import Dict, List, Tuple, Optional, Union, Callable


class Instruction(Enum):
    """Enum representing the supported assembly instructions."""
    PUSH = auto()    # Push value onto stack
    POP = auto()     # Pop value from stack
    ADD = auto()     # Add top two values on stack
    SUB = auto()     # Subtract top value from second top value
    MUL = auto()     # Multiply top two values on stack
    DIV = auto()     # Divide second top value by top value
    STORE = auto()   # Store value in memory
    LOAD = auto()    # Load value from memory
    JMP = auto()     # Jump to address
    JZ = auto()      # Jump if zero
    JNZ = auto()     # Jump if not zero
    CALL = auto()    # Call subroutine
    RET = auto()     # Return from subroutine
    PRINT = auto()   # Print value
    HALT = auto()    # Halt execution


class AssemblyCompiler:
    """A simple assembly language compiler."""
    
    def __init__(self):
        self.instruction_map = {
            'PUSH': Instruction.PUSH,
            'POP': Instruction.POP,
            'ADD': Instruction.ADD,
            'SUB': Instruction.SUB,
            'MUL': Instruction.MUL,
            'DIV': Instruction.DIV,
            'STORE': Instruction.STORE,
            'LOAD': Instruction.LOAD,
            'JMP': Instruction.JMP,
            'JZ': Instruction.JZ,
            'JNZ': Instruction.JNZ,
            'CALL': Instruction.CALL,
            'RET': Instruction.RET,
            'PRINT': Instruction.PRINT,
            'HALT': Instruction.HALT,
        }
        self.labels: Dict[str, int] = {}
        self.instructions: List[Tuple[Instruction, Optional[int]]] = []
        
    def parse_line(self, line: str) -> Optional[Tuple[Instruction, Optional[int]]]:
        """Parse a single line of assembly code."""
        # Remove comments
        line = re.sub(r';.*$', '', line).strip()
        if not line:
            return None
            
        # Check for label definition
        label_match = re.match(r'(\w+):', line)
        if label_match:
            label = label_match.group(1)
            self.labels[label] = len(self.instructions)
            return None
            
        # Parse instruction
        parts = line.split()
        instruction_name = parts[0].upper()
        
        if instruction_name not in self.instruction_map:
            raise ValueError(f"Unknown instruction: {instruction_name}")
            
        instruction = self.instruction_map[instruction_name]
        operand = None
        
        # Parse operand if present
        if len(parts) > 1:
            operand_str = parts[1]
            # Check if operand is a label reference
            if operand_str.isalpha():
                # We'll resolve this in the second pass
                operand = operand_str
            else:
                try:
                    operand = int(operand_str)
                except ValueError:
                    raise ValueError(f"Invalid operand: {operand_str}")
                    
        return instruction, operand
        
    def compile(self, source: str) -> List[Tuple[Instruction, Optional[int]]]:
        """Compile assembly source code to bytecode."""
        lines = source.splitlines()
        
        # First pass: collect instructions and labels
        self.instructions = []
        self.labels = {}
        
        for line in lines:
            result = self.parse_line(line)
            if result:
                self.instructions.append(result)
                
        # Second pass: resolve label references
        for i, (instr, operand) in enumerate(self.instructions):
            if isinstance(operand, str):
                if operand in self.labels:
                    self.instructions[i] = (instr, self.labels[operand])
                else:
                    raise ValueError(f"Undefined label: {operand}")
                    
        return self.instructions


class VirtualMachine:
    """A simple stack-based virtual machine."""
    
    def __init__(self, memory_size: int = 1024):
        self.stack: List[int] = []
        self.memory: List[int] = [0] * memory_size
        self.call_stack: List[int] = []
        self.program: List[Tuple[Instruction, Optional[int]]] = []
        self.ip: int = 0  # Instruction pointer
        self.running: bool = False
        
    def load_program(self, program: List[Tuple[Instruction, Optional[int]]]):
        """Load a program into the VM."""
        self.program = program
        self.ip = 0
        self.stack = []
        self.call_stack = []
        
    def execute_instruction(self) -> bool:
        """Execute the current instruction and return whether to continue."""
        if self.ip >= len(self.program):
            return False
            
        instruction, operand = self.program[self.ip]
        self.ip += 1
        
        if instruction == Instruction.PUSH:
            if operand is None:
                raise ValueError("PUSH instruction requires an operand")
            self.stack.append(operand)
            
        elif instruction == Instruction.POP:
            if not self.stack:
                raise ValueError("Stack underflow")
            self.stack.pop()
            
        elif instruction == Instruction.ADD:
            if len(self.stack) < 2:
                raise ValueError("Stack underflow")
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a + b)
            
        elif instruction == Instruction.SUB:
            if len(self.stack) < 2:
                raise ValueError("Stack underflow")
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a - b)
            
        elif instruction == Instruction.MUL:
            if len(self.stack) < 2:
                raise ValueError("Stack underflow")
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a * b)
            
        elif instruction == Instruction.DIV:
            if len(self.stack) < 2:
                raise ValueError("Stack underflow")
            b = self.stack.pop()
            if b == 0:
                raise ValueError("Division by zero")
            a = self.stack.pop()
            self.stack.append(a // b)  # Integer division
            
        elif instruction == Instruction.STORE:
            if len(self.stack) < 2:
                raise ValueError("Stack underflow")
            value = self.stack.pop()
            address = self.stack.pop()
            if address < 0 or address >= len(self.memory):
                raise ValueError(f"Memory address out of bounds: {address}")
            self.memory[address] = value
            
        elif instruction == Instruction.LOAD:
            if not self.stack:
                raise ValueError("Stack underflow")
            address = self.stack.pop()
            if address < 0 or address >= len(self.memory):
                raise ValueError(f"Memory address out of bounds: {address}")
            self.stack.append(self.memory[address])
            
        elif instruction == Instruction.JMP:
            if operand is None:
                raise ValueError("JMP instruction requires an operand")
            self.ip = operand
            
        elif instruction == Instruction.JZ:
            if not self.stack:
                raise ValueError("Stack underflow")
            value = self.stack.pop()
            if value == 0 and operand is not None:
                self.ip = operand
                
        elif instruction == Instruction.JNZ:
            if not self.stack:
                raise ValueError("Stack underflow")
            value = self.stack.pop()
            if value != 0 and operand is not None:
                self.ip = operand
                
        elif instruction == Instruction.CALL:
            if operand is None:
                raise ValueError("CALL instruction requires an operand")
            self.call_stack.append(self.ip)
            self.ip = operand
            
        elif instruction == Instruction.RET:
            if not self.call_stack:
                raise ValueError("Call stack underflow")
            self.ip = self.call_stack.pop()
            
        elif instruction == Instruction.PRINT:
            if not self.stack:
                raise ValueError("Stack underflow")
            print(self.stack.pop())
            
        elif instruction == Instruction.HALT:
            return False
            
        return True
        
    def run(self):
        """Run the loaded program."""
        self.running = True
        
        try:
            while self.running and self.execute_instruction():
                pass
        except Exception as e:
            print(f"Runtime error: {e}")
            
        self.running = False


class LanguageModel:
    """Base class for implementing a custom language model."""
    
    def __init__(self):
        self.compiler = AssemblyCompiler()
        self.vm = VirtualMachine()
        
    def compile_and_run(self, source: str):
        """Compile and run the provided source code."""
        program = self.compiler.compile(source)
        self.vm.load_program(program)
        self.vm.run()
        
    def translate_to_asm(self, source: str) -> str:
        """
        Translate your custom language to assembly.
        Override this method in your subclass.
        """
        raise NotImplementedError("Subclasses must implement translate_to_asm")
        
    def run(self, source: str):
        """Run code written in your custom language."""
        asm_code = self.translate_to_asm(source)
        self.compile_and_run(asm_code)
