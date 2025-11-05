#!/usr/bin/env python3
"""
Script robusto para configurar o ambiente de desenvolvimento
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def get_project_root():
    """Retorna o diretório raiz do projeto"""
    return Path(__file__).parent.absolute()


def run_command(command, description, cwd=None):
    """Executa um comando e verifica se foi bem-sucedido"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True,
                                capture_output=True, text=True, cwd=cwd)
        print(f"✅ {description} - OK")
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FALHOU")
        if e.stderr:
            print(f"   Erro: {e.stderr.strip()}")
        return False


def install_packages(pip_cmd, packages):
    """Instala pacotes individualmente"""
    success_count = 0
    for package in packages:
        if run_command(f'{pip_cmd} install "{package}"', f"Instalando {package}"):
            success_count += 1
        else:
            print(f"⚠️  Falha ao instalar {package}, continuando...")

    return success_count


def main():
    print("🚀 CONFIGURAÇÃO DO AMBIENTE - VERSÃO ROBUSTA")
    print("=" * 60)

    project_root = get_project_root()
    print(f"📁 Diretório do projeto: {project_root}")

    # Verificar Python version
    python_version = platform.python_version()
    print(f"🐍 Python detectado: {python_version}")

    # Criar ambiente virtual (se não existir)
    venv_path = project_root / ".venv"
    if not venv_path.exists():
        print("📦 Criando ambiente virtual...")
        run_command(f'"{sys.executable}" -m venv "{venv_path}"',
                    "Criação do ambiente virtual")

    # Determinar comando do pip baseado no OS
    if platform.system() == "Windows":
        pip_cmd = f'"{venv_path}\\Scripts\\python.exe" -m pip'
        python_cmd = f'"{venv_path}\\Scripts\\python.exe"'
    else:
        pip_cmd = f'"{venv_path}/bin/python" -m pip'
        python_cmd = f'"{venv_path}/bin/python"'

    # Lista de pacotes essenciais (instalados individualmente)
    essential_packages = [
        "numpy==1.26.4",
        "XPlaneConnect==0.8.0",
        "matplotlib==3.8.0",
        "pyyaml==6.0.1",
        "pytest==7.4.3"
    ]

    # Instalar pacotes individualmente
    print("\n📥 INSTALANDO PACOTES ESSENCIAIS")
    print("-" * 40)

    success_count = install_packages(pip_cmd, essential_packages)

    print(f"\n📊 RESULTADO: {success_count}/{len(essential_packages)} pacotes instalados")

    # Verificar instalações críticas
    print("\n🔍 VERIFICANDO INSTALAÇÕES CRÍTICAS")
    print("-" * 40)

    critical_packages = ["numpy", "XPlaneConnect"]
    for package in critical_packages:
        check_cmd = f'{python_cmd} -c "import {package}; print(\\\"✅ {package} OK\\\")"'
        if run_command(check_cmd, f"Verificando {package}"):
            print(f"   ✅ {package} - FUNCIONANDO")
        else:
            print(f"   ❌ {package} - FALHOU")

    # Criar requirements.txt para uso futuro
    requirements_content = "\n".join(essential_packages)
    requirements_file = project_root / "requirements.txt"

    try:
        with open(requirements_file, 'w') as f:
            f.write(requirements_content)
        print(f"\n💾 requirements.txt criado em: {requirements_file}")
    except Exception as e:
        print(f"⚠️  Não foi possível criar requirements.txt: {e}")

    print("\n🎉 CONFIGURAÇÃO CONCLUÍDA!")
    print("=" * 60)
    print("📝 PRÓXIMOS PASSOS:")
    print("   1. Ative o ambiente virtual:")
    if platform.system() == "Windows":
        print(f'      "{venv_path}\\Scripts\\Activate.ps1"')
    else:
        print(f'      source "{venv_path}/bin/activate"')
    print("   2. Execute os testes básicos:")
    print('      python tests/test_basic_communication.py')
    print("\n🚀 Happy coding!")


if __name__ == "__main__":
    main()