import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, simpledialog, ttk
import subprocess
import os
import re
import platform

class AssemblyIDE:
    def __init__(self, master):
        self.master = master
        master.title("Assembly Language IDE")
        master.geometry("1000x800")

        # Create menu bar
        self.menu_bar = tk.Menu(master)
        master.config(menu=self.menu_bar)

        # File menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New", command=self.new_file)
        self.file_menu.add_command(label="Open", command=self.open_file)
        self.file_menu.add_command(label="Save", command=self.save_file)
        self.file_menu.add_command(label="Save As", command=self.save_file_as)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=master.quit)

        # Run menu
        self.run_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Run", menu=self.run_menu)
        self.run_menu.add_command(label="Assemble", command=self.assemble_code)
        self.run_menu.add_command(label="Run", command=self.run_code)

        # Tools menu
        self.tools_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Tools", menu=self.tools_menu)
        self.tools_menu.add_command(label="Generate Project", command=self.generate_project)
        self.tools_menu.add_command(label="Code Snippets", command=self.show_code_snippets)
        self.tools_menu.add_command(label="Assembly Reference", command=self.show_assembly_reference)

        # Code editor with line numbers
        self.line_numbers = tk.Text(master, width=4, padx=3, pady=3, 
                                    fg='darkgrey', background='lightgrey', 
                                    state='disabled', wrap='none')
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        self.code_editor = scrolledtext.ScrolledText(master, wrap=tk.WORD)
        self.code_editor.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        # Bind events for line numbering
        self.code_editor.bind('<Any-KeyRelease>', self.update_line_numbers)
        self.code_editor.bind('<MouseWheel>', self.update_line_numbers)

        # Output console
        self.output_console = scrolledtext.ScrolledText(master, height=10, state='disabled')
        self.output_console.pack(side=tk.BOTTOM, fill=tk.X)

        # Current file path
        self.current_file = None

        # Syntax highlighting
        self.syntax_highlighting()

    def syntax_highlighting(self):
        """Apply syntax highlighting to the code editor"""
        # Define syntax highlighting patterns
        self.code_editor.tag_configure('register', foreground='blue')
        self.code_editor.tag_configure('instruction', foreground='green')
        self.code_editor.tag_configure('directive', foreground='purple')
        self.code_editor.tag_configure('comment', foreground='grey', font=('TkDefaultFont', 10, 'italic'))

        # Common x86 assembly registers, instructions, and directives
        registers = r'\b(eax|ebx|ecx|edx|esi|edi|esp|ebp|eip|ax|bx|cx|dx)\b'
        instructions = r'\b(mov|add|sub|mul|div|inc|dec|push|pop|call|ret|jmp|cmp|je|jne|jg|jl)\b'
        directives = r'\b(section|global|extern|db|dw|dd|resb|resw|resd)\b'
        comments = r';.*$'

        # Function to apply highlighting
        def highlight():
            # Remove existing tags
            for tag in ['register', 'instruction', 'directive', 'comment']:
                self.code_editor.tag_remove(tag, '1.0', tk.END)
            
            # Apply highlighting
            content = self.code_editor.get('1.0', tk.END)
            
            # Highlight registers
            for match in re.finditer(registers, content, re.MULTILINE | re.IGNORECASE):
                start = f'1.0 + {match.start()}c'
                end = f'1.0 + {match.end()}c'
                self.code_editor.tag_add('register', start, end)
            
            # Highlight instructions
            for match in re.finditer(instructions, content, re.MULTILINE | re.IGNORECASE):
                start = f'1.0 + {match.start()}c'
                end = f'1.0 + {match.end()}c'
                self.code_editor.tag_add('instruction', start, end)
            
            # Highlight directives
            for match in re.finditer(directives, content, re.MULTILINE | re.IGNORECASE):
                start = f'1.0 + {match.start()}c'
                end = f'1.0 + {match.end()}c'
                self.code_editor.tag_add('directive', start, end)
            
            # Highlight comments
            for match in re.finditer(comments, content, re.MULTILINE):
                start = f'1.0 + {match.start()}c'
                end = f'1.0 + {match.end()}c'
                self.code_editor.tag_add('comment', start, end)
        
        # Bind highlighting to key events
        self.code_editor.bind('<KeyRelease>', lambda e: highlight())

    def update_line_numbers(self, event=None):
        """Update line numbers in the line number column"""
        # Get the current content of the code editor
        content = self.code_editor.get('1.0', tk.END)
        
        # Count the number of lines
        lines = content.count('\n')
        
        # Clear existing line numbers
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', tk.END)
        
        # Add line numbers
        for i in range(1, lines + 2):
            self.line_numbers.insert(tk.END, f'{i}\n')
        
        # Disable editing of line numbers
        self.line_numbers.config(state='disabled')

    def new_file(self):
        """Create a new file"""
        # Clear the current editor content
        self.code_editor.delete('1.0', tk.END)
        self.current_file = None
        self.master.title("Assembly Language IDE - New File")

    def open_file(self):
        """Open an existing file"""
        file_path = filedialog.askopenfilename(
            defaultextension=".asm",
            filetypes=[("Assembly Files", "*.asm"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    # Clear existing content
                    self.code_editor.delete('1.0', tk.END)
                    # Insert file content
                    self.code_editor.insert(tk.END, file.read())
                
                # Update current file path
                self.current_file = file_path
                self.master.title(f"Assembly Language IDE - {os.path.basename(file_path)}")
                
                # Update line numbers
                self.update_line_numbers()
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {e}")

    def save_file(self):
        """Save the current file"""
        if self.current_file:
            try:
                with open(self.current_file, 'w') as file:
                    file.write(self.code_editor.get('1.0', tk.END))
                messagebox.showinfo("Save", "File saved successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")
        else:
            self.save_file_as()

    def save_file_as(self):
        """Save the file with a new name"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".asm",
            filetypes=[("Assembly Files", "*.asm"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as file:
                    file.write(self.code_editor.get('1.0', tk.END))
                
                # Update current file path
                self.current_file = file_path
                self.master.title(f"Assembly Language IDE - {os.path.basename(file_path)}")
                
                messagebox.showinfo("Save", "File saved successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")

    def assemble_code(self):
        """Assemble the current code"""
        # Check if file is saved
        if not self.current_file:
            self.save_file_as()
        
        if not self.current_file:
            return
        
        # Clear previous output
        self.output_console.config(state='normal')
        self.output_console.delete('1.0', tk.END)
        
        # Determine the OS and assembler
        system = platform.system()
        
        try:
            if system == "Windows":
                # For Windows, use NASM
                subprocess.run(["nasm", "-f", "win32", self.current_file], 
                               check=True, capture_output=True, text=True)
                output_obj = self.current_file.replace('.asm', '.obj')
                output_exe = self.current_file.replace('.asm', '.exe')
                
                # Link the object file
                subprocess.run(["link", "/subsystem:console", "/out:" + output_exe, output_obj], 
                               check=True, capture_output=True, text=True)
                
                self.output_console.insert(tk.END, f"Assembled successfully: {output_exe}")
            
            elif system == "Linux":
                # For Linux, use NASM and ld
                output_obj = self.current_file.replace('.asm', '.o')
                output_exe = self.current_file.replace('.asm', '')
                
                # Assemble
                result = subprocess.run(["nasm", "-f", "elf32", "-g", "-F", "dwarf", 
                                         self.current_file, "-o", output_obj], 
                                        capture_output=True, text=True)
                
                if result.returncode != 0:
                    self.output_console.insert(tk.END, f"Assembly Error:\n{result.stderr}")
                    return
                
                # Link
                result = subprocess.run(["ld", "-m", "elf_i386", "-o", output_exe, output_obj], 
                                        capture_output=True, text=True)
                
                if result.returncode != 0:
                    self.output_console.insert(tk.END, f"Linking Error:\n{result.stderr}")
                    return
                
                self.output_console.insert(tk.END, f"Assembled successfully: {output_exe}")
            
            elif system == "Darwin":  # macOS
                # For macOS, use NASM and ld
                output_obj = self.current_file.replace('.asm', '.o')
                output_exe = self.current_file.replace('.asm', '')
                
                # Assemble
                result = subprocess.run(["nasm", "-f", "macho", "-g", 
                                         self.current_file, "-o", output_obj], 
                                        capture_output=True, text=True)
                
                if result.returncode != 0:
                    self.output_console.insert(tk.END, f"Assembly Error:\n{result.stderr}")
                    return
                
                # Link
                result = subprocess.run(["ld", "-macosx_version_min", "10.7.0", 
                                         "-lSystem", "-o", output_exe, output_obj], 
                                        capture_output=True, text=True)
                
                if result.returncode != 0:
                    self.output_console.insert(tk.END, f"Linking Error:\n{result.stderr}")
                    return
                
                self.output_console.insert(tk.END, f"Assembled successfully: {output_exe}")
            
            else:
                self.output_console.insert(tk.END, f"Unsupported operating system: {system}")
        
        except subprocess.CalledProcessError as e:
            self.output_console.insert(tk.END, f"Error: {e}\n{e.stderr}")
        except FileNotFoundError:
            self.output_console.insert(tk.END, "Error: NASM or linker not found. Please install NASM.")
        except Exception as e:
            self.output_console.insert(tk.END, f"Unexpected error: {e}")
        
        # Disable console editing
        self.output_console.config(state='disabled')

    def run_code(self):
        """Run the assembled executable"""
        # Check if file is saved and assembled
        if not self.current_file:
            messagebox.showwarning("Warning", "Please save and assemble the file first")
            return
        
        # Clear previous output
        self.output_console.config(state='normal')
        self.output_console.delete('1.0', tk.END)
        
        try:
            system = platform.system()
            
            if system == "Windows":
                executable = self.current_file.replace('.asm', '.exe')
            else:
                executable = self.current_file.replace('.asm', '')
            
            # Run the executable
            result = subprocess.run([executable], 
                                    capture_output=True, text=True, check=True)
            
            # Display output
            self.output_console.insert(tk.END, "Program Output:\n")
            self.output_console.insert(tk.END, result.stdout)
            
            if result.stderr:
                self.output_console.insert(tk.END, "\nError Output:\n")
                self.output_console.insert(tk.END, result.stderr)
        
        except subprocess.CalledProcessError as e:
            self.output_console.insert(tk.END, f"Runtime Error:\n{e.stderr}")
        except FileNotFoundError:
            self.output_console.insert(tk.END, "Error: Executable not found. Assemble the code first.")
        except Exception as e:
            self.output_console.insert(tk.END, f"Unexpected error: {e}")
        
        # Disable console editing
        self.output_console.config(state='disabled')

    def generate_project(self):
        """Generate a new assembly project structure"""
        # Ask for project name
        project_name = simpledialog.askstring("New Project", "Enter project name:")
        
        if not project_name:
            return
        
        try:
            # Create project directory
            os.makedirs(project_name, exist_ok=True)
            
            # Create subdirectories
            os.makedirs(os.path.join(project_name, 'src'), exist_ok=True)
            os.makedirs(os.path.join(project_name, 'include'), exist_ok=True)
            os.makedirs(os.path.join(project_name, 'build'), exist_ok=True)
            
            # Create initial files
            # Main source file
            with open(os.path.join(project_name, 'src', 'main.asm'), 'w') as f:
                f.write(self.get_project_template(project_name))
            
            # Makefile
            with open(os.path.join(project_name, 'Makefile'), 'w') as f:
                f.write(self.get_makefile_template(project_name))
            
            # README
            with open(os.path.join(project_name, 'README.md'), 'w') as f:
                f.write(f"# {project_name}\n\nAssembly Language Project\n")
            
            messagebox.showinfo("Project Generated", 
                                f"Project '{project_name}' created successfully!\n"
                                f"Location: {os.path.abspath(project_name)}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Could not generate project: {e}")

    def get_project_template(self, project_name):
        """Generate a basic project template"""
        return f'''; {project_name} - Main Source File
section .data
    project_name db '{project_name}', 0
    welcome_msg db 'Welcome to {project_name} project!', 0ah, 0
    msg_len equ $ - welcome_msg

section .text
    global _start

_start:
    ; Write welcome message
    mov eax, 4          ; syscall number for write
    mov ebx, 1          ; file descriptor (1 = stdout)
    mov ecx, welcome_msg; message to write
    mov edx, msg_len    ; message length
    int 0x80            ; call kernel

    ; Exit program
    mov eax, 1          ; syscall number for exit
    xor ebx, ebx        ; exit status 0
    int 0x80            ; call kernel
'''

    def get_makefile_template(self, project_name):
        """Generate a basic Makefile"""
        return f'''# Makefile for {project_name}

# Assembler and linker
NASM = nasm
LD = ld

# Flags
NASM_FLAGS = -f elf32
LD_FLAGS = -m elf_i386

# Directories
SRC_DIR = src
BUILD_DIR = build

# Source and output files
SRC_FILE = $(SRC_DIR)/main.asm
OBJ_FILE = $(BUILD_DIR)/main.o
EXEC_FILE = $(BUILD_DIR)/{project_name}

# Default target
all: $(EXEC_FILE)

# Compile assembly to object file
$(BUILD_DIR)/%.o: $(SRC_DIR)/%.asm
	@mkdir -p $(BUILD_DIR)
	$(NASM) $(NASM_FLAGS) -o $@ $<

# Link object file to executable
$(EXEC_FILE): $(OBJ_FILE)
	$(LD) $(LD_FLAGS) -o $@ $<

# Clean build files
clean:
	rm -rf $(BUILD_DIR)

# Phony targets
.PHONY: all clean
'''

    def show_code_snippets(self):
        """Display a window with common assembly code snippets"""
        snippet_window = tk.Toplevel(self.master)
        snippet_window.title("Assembly Code Snippets")
        snippet_window.geometry("600x400")

        # Create a text widget to display snippets
        snippets_text = tk.Text(snippet_window, wrap=tk.WORD)
        snippets_text.pack(expand=True, fill=tk.BOTH)

        # Add snippets
        snippets = [
            ("Hello World", '''section .data
    msg db 'Hello, World!', 0ah
    msg_len equ $ - msg

section .text
    global _start

_start:
    ; Write message
    mov eax, 4          ; syscall: write
    mov ebx, 1          ; file descriptor (stdout)
    mov ecx, msg        ; message to write
    mov edx, msg_len    ; message length
    int 0x80            ; call kernel

    ; Exit program
    mov eax, 1          ; syscall: exit
    xor ebx, ebx        ; exit status 0
    int 0x80'''),

            ("Function Call Example", '''section .text
    global _start

; Function to add two numbers
add_numbers:
    ; Input: 
    ;   First number in eax
    ;   Second number in ebx
    ; Output: 
    ;   Sum in eax
    add eax, ebx
    ret

_start:
    ; Example of calling add_numbers function
    mov eax, 5      ; First number
    mov ebx, 7      ; Second number
    call add_numbers
    ; Now eax contains 12

    ; Exit program
    mov eax, 1
    xor ebx, ebx
    int 0x80'''),

            ("Array Manipulation", '''section .data
    array dd 10, 20, 30, 40, 50   ; Array of 5 integers
    array_len equ 5

section .text
    global _start

_start:
    ; Find sum of array elements
    mov ecx, array_len  ; Loop counter
    mov esi, 0          ; Array index
    mov eax, 0          ; Sum accumulator

sum_loop:
    add eax, [array + esi * 4]  ; Add current array element
    inc esi             ; Move to next index
    loop sum_loop       ; Decrement ecx and continue if not zero

    ; Exit program
    mov eax, 1
    xor ebx, ebx
    int 0x80''')
        ]

        # Insert snippets into text widget
        for title, snippet in snippets:
            snippets_text.insert(tk.END, f"{title}:\n", 'title')
            snippets_text.insert(tk.END, snippet + "\n\n")

        # Configure tags for formatting
        snippets_text.tag_configure('title', font=('TkDefaultFont', 10, 'bold'))
        snippets_text.config(state=tk.DISABLED)

        # Add a button to copy selected snippet
        def copy_snippet():
            try:
                selected_text = snippets_text.get(tk.SEL_FIRST, tk.SEL_LAST)
                snippet_window.clipboard_clear()
                snippet_window.clipboard_append(selected_text)
            except tk.TclError:
                messagebox.showwarning("Copy", "No text selected")

        copy_button = tk.Button(snippet_window, text="Copy Selected", command=copy_snippet)
        copy_button.pack(side=tk.BOTTOM)

    def show_assembly_reference(self):
        """Display a comprehensive assembly language reference"""
        reference_window = tk.Toplevel(self.master)
        reference_window.title("x86 Assembly Reference")
        reference_window.geometry("800x600")

        # Create notebook (tabbed interface)
        notebook = ttk.Notebook(reference_window)
        notebook.pack(expand=True, fill=tk.BOTH)

        # Reference sections
        reference_sections = [
            ("Registers", 
             "x86 Registers Overview:\n\n"
             "General Purpose Registers:\n"
             "- EAX: Accumulator (often used for return values)\n"
             "- EBX: Base register\n"
             "- ECX: Counter (often used in loops)\n"
             "- EDX: Data register\n\n"
             "Segment Registers:\n"
             "- CS: Code Segment\n"
             "- DS: Data Segment\n"
             "- SS: Stack Segment\n"
             "- ES: Extra Segment\n\n"
             "Special Registers:\n"
             "- ESP: Stack Pointer\n"
             "- EBP: Base Pointer\n"
             "- ESI: Source Index\n"
             "- EDI: Destination Index\n"
             "- EIP: Instruction Pointer"),

            ("Instructions", 
             "Common x86 Instructions:\n\n"
             "Data Movement:\n"
             "- MOV: Move data between registers or memory\n"
             "  Example: mov eax, 42\n"
             "  Example: mov ebx, [address]\n\n"
             "Arithmetic:\n"
             "- ADD: Add two values\n"
             "  Example: add eax, ebx\n"
             "- SUB: Subtract two values\n"
             "  Example: sub ecx, edx\n"
             "- MUL: Multiply\n"
             "- DIV: Divide\n\n"
             "Control Flow:\n"
             "- JMP: Unconditional jump\n"
             "- CMP: Compare values\n"
             "- JE: Jump if equal\n"
             "- JNE: Jump if not equal\n"
             "- JG: Jump if greater\n"
             "- JL: Jump if less"),

            ("System Calls", 
             "Common Linux System Calls:\n\n"
             "- Write: Syscall 4\n"
             "  Parameters:\n"
             "  - EAX: 4\n"
             "  - EBX: File descriptor\n"
             "  - ECX: Buffer address\n"
             "  - EDX: Buffer length\n\n"
             "- Exit: Syscall 1\n"
             "  Parameters:\n"
             "  - EAX: 1\n"
             "  - EBX: Exit status\n\n"
             "Basic System Call Example:\n"
             "  mov eax, 4      ; Write syscall\n"
             "  mov ebx, 1      ; Stdout\n"
             "  mov ecx, msg    ; Message\n"
             "  mov edx, len    ; Length\n"
             "  int 0x80        ; Invoke syscall")
        ]

        # Create tabs
        for title, content in reference_sections:
            frame = tk.Frame(notebook)
            text_widget = tk.Text(frame, wrap=tk.WORD)
            text_widget.pack(expand=True, fill=tk.BOTH)
            text_widget.insert(tk.END, content)
            text_widget.config(state=tk.DISABLED)
            notebook.add(frame, text=title)

def main():
    root = tk.Tk()
    ide = AssemblyIDE(root)
    root.mainloop()

if __name__ == "__main__":
    main()