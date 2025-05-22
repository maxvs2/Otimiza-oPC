import os
import shutil
import tkinter as tk
from tkinter import messagebox
import getpass
from datetime import datetime
import subprocess
import winshell  # Biblioteca para esvaziar lixeira
import psutil    # Biblioteca para uso da CPU e memória
import GPUtil    # Biblioteca para uso da GPU

def limpar_pasta(caminho, log):
    removidos = 0
    if not os.path.exists(caminho):
        log.append(f"Pasta não encontrada: {caminho}")
        return 0
    for arquivo in os.listdir(caminho):
        caminho_completo = os.path.join(caminho, arquivo)
        try:
            if os.path.isfile(caminho_completo) or os.path.islink(caminho_completo):
                os.remove(caminho_completo)
                log.append(f"Arquivo removido: {caminho_completo}")
                removidos += 1
            elif os.path.isdir(caminho_completo):
                shutil.rmtree(caminho_completo, ignore_errors=True)
                log.append(f"Pasta removida: {caminho_completo}")
                removidos += 1
        except Exception as e:
            log.append(f"Erro ao remover {caminho_completo}: {e}")
    return removidos

def limpar_logs(log):
    caminhos_logs = [
        f"C:/Users/{getpass.getuser()}/AppData/Local",
        "C:/Windows/Logs",
        "C:/ProgramData"
    ]
    total = 0
    for base in caminhos_logs:
        for raiz, _, arquivos in os.walk(base):
            for arquivo in arquivos:
                if arquivo.endswith(".log"):
                    try:
                        caminho = os.path.join(raiz, arquivo)
                        os.remove(caminho)
                        log.append(f".log removido: {caminho}")
                        total += 1
                    except:
                        pass
    return total

def otimizar_disco(log):
    try:
        output = subprocess.check_output("defrag C: /O", shell=True, text=True)
        log.append("Otimização de disco concluída:\n" + output)
        return True
    except Exception as e:
        log.append(f"Erro na otimização: {e}")
        return False

def agendar_limpeza(log):
    try:
        script = os.path.realpath(__file__)
        comando = f'schtasks /Create /SC WEEKLY /D SUN /TN "LimpadorSemanal" /TR "\"{script}\"" /RL HIGHEST /F'
        os.system(comando)
        log.append("Tarefa agendada com sucesso.")
        return True
    except Exception as e:
        log.append(f"Erro ao agendar tarefa: {e}")
        return False

def esvaziar_lixeira(log):
    try:
        winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
        log.append("Lixeira esvaziada com sucesso.")
        return True
    except Exception as e:
        log.append(f"Erro ao esvaziar lixeira: {e}")
        return False

def salvar_relatorio(logs):
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    nome = f"relatorio_limpeza_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
    caminho = os.path.join(desktop, nome)
    with open(caminho, "w", encoding="utf-8") as f:
        for linha in logs:
            f.write(linha + "\n")
    return caminho

def executar_limpeza():
    usuario = getpass.getuser()
    caminhos = []

    if var_temp.get():
        caminhos += [os.getenv("TEMP"), f"C:/Users/{usuario}/AppData/Local/Temp"]
    if var_win_temp.get():
        caminhos.append("C:/Windows/Temp")
    if var_prefetch.get():
        caminhos.append("C:/Windows/Prefetch")
    if var_recent.get():
        caminhos.append(f"C:/Users/{usuario}/AppData/Roaming/Microsoft/Windows/Recent")

    log = []
    total_removido = 0
    for caminho in caminhos:
        log.append(f"\n--- Limpando: {caminho} ---")
        total_removido += limpar_pasta(caminho, log)

    if var_lixeira.get():
        esvaziar_lixeira(log)

    if var_logs.get():
        total_removido += limpar_logs(log)

    if var_defrag.get():
        otimizar_disco(log)

    if var_agendar.get():
        agendar_limpeza(log)

    caminho_relatorio = salvar_relatorio(log)
    messagebox.showinfo("Finalizado", f"Limpeza concluída. Relatório salvo em:\n{caminho_relatorio}")

def mostrar_monitoramento():
    try:
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        info = f"CPU: {cpu}%\nMemória usada: {mem.percent}%"

        gpus = GPUtil.getGPUs()
        if gpus:
            for gpu in gpus:
                info += f"\n\nGPU: {gpu.name}\nUso da GPU: {gpu.load * 100:.1f}%\nMemória da GPU: {gpu.memoryUsed}/{gpu.memoryTotal} MB"
        else:
            info += "\n\nGPU: Nenhuma GPU detectada."
    except Exception as e:
        info = f"Erro ao obter dados de monitoramento:\n{e}"

    messagebox.showinfo("Monitoramento do Sistema", info)

# Interface Gráfica
janela = tk.Tk()
janela.title("Otimizador de Sistema Windows")
janela.geometry("500x550")

tk.Label(janela, text="Selecione as opções de limpeza:", font=("Arial", 14)).pack(pady=10)

var_temp = tk.BooleanVar(value=True)
var_win_temp = tk.BooleanVar(value=True)
var_prefetch = tk.BooleanVar(value=False)
var_recent = tk.BooleanVar(value=False)
var_lixeira = tk.BooleanVar(value=True)
var_logs = tk.BooleanVar(value=True)
var_defrag = tk.BooleanVar(value=False)
var_agendar = tk.BooleanVar(value=False)

tk.Checkbutton(janela, text="Limpar TEMP do usuário", variable=var_temp).pack(anchor='w', padx=20)
tk.Checkbutton(janela, text="Limpar C:/Windows/Temp", variable=var_win_temp).pack(anchor='w', padx=20)
tk.Checkbutton(janela, text="Limpar Prefetch", variable=var_prefetch).pack(anchor='w', padx=20)
tk.Checkbutton(janela, text="Limpar arquivos Recentes", variable=var_recent).pack(anchor='w', padx=20)
tk.Checkbutton(janela, text="Esvaziar Lixeira", variable=var_lixeira).pack(anchor='w', padx=20)
tk.Checkbutton(janela, text="Remover arquivos .log", variable=var_logs).pack(anchor='w', padx=20)
tk.Checkbutton(janela, text="Otimizar disco (HD)", variable=var_defrag).pack(anchor='w', padx=20)
tk.Checkbutton(janela, text="Agendar limpeza semanal", variable=var_agendar).pack(anchor='w', padx=20)

tk.Button(janela, text="Executar Limpeza", bg="green", fg="white", font=("Arial", 12), command=executar_limpeza).pack(pady=10)
tk.Button(janela, text="Monitorar Sistema", bg="blue", fg="white", font=("Arial", 11), command=mostrar_monitoramento).pack(pady=5)

janela.mainloop()
