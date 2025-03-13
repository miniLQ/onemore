from loguru import logger
import os

# get the path of the current file
current_file_path = os.path.abspath(__file__)
# get the directory of the current file
current_dir = os.path.dirname(current_file_path)
# get the parent directory of the current directory
tools_dir = os.path.dirname(current_dir)

# path to the directory where the gnu-tools
gnu_tools_dir = os.path.join(tools_dir, 'gnu-tools')

gdb64_path = os.path.join(gnu_tools_dir, 'bin', 'gdb.exe')
nm64_path = os.path.join(gnu_tools_dir, 'bin', 'aarch64-linux-gnu-nm.exe')
objdump64_path = os.path.join(gnu_tools_dir, 'bin', 'llvm-objdump.exe')

