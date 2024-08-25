import os
import subprocess
import shutil

def create_exe():
    # Путь к скрипту Python
    script_name = 'main.py'
    # Команда для PyInstaller
    command = ['pyinstaller', '--onefile', '--noconsole', script_name]

    # Запуск команды PyInstaller
    subprocess.run(command, check=True)

    # Папка с временными файлами, создаваемыми PyInstaller
    build_folder = 'build'
    dist_folder = 'dist'
    spec_file = script_name.replace('.py', '.spec')

    # Перемещение .exe файла в текущую директорию
    exe_file = os.path.join(dist_folder, script_name.replace('.py', '.exe'))
    if os.path.exists(exe_file):
        shutil.move(exe_file, os.path.join(os.getcwd(), script_name.replace('.py', '.exe')))

    # Удаление временных файлов и папок
    if os.path.exists(build_folder):
        shutil.rmtree(build_folder)
    if os.path.exists(dist_folder):
        shutil.rmtree(dist_folder)
    if os.path.exists(spec_file):
        os.remove(spec_file)

if __name__ == '__main__':
    create_exe()
