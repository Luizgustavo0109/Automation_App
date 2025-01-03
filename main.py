import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox, simpledialog
import webbrowser
import subprocess
import json
import os
import logging


logging.basicConfig(
    filename="automation_app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


CAMINHO_BOTOES = os.path.join(os.path.dirname(__file__), "buttons.json")

class AplicativoAutomacao:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplicativo de Automação")
        self.root.geometry("600x400")
        self.style = ttk.Style("superhero")
        self.botoes = {}
        self.botao_selecionado = None

        # Layout principal
        self.frame_principal = ttk.Frame(self.root, padding=10)
        self.frame_principal.pack(fill=BOTH, expand=True)

        # Título
        titulo = ttk.Label(
            self.frame_principal,
            text="AutoExec",
            font=("Aptostyle", 24, "bold")
        )
        titulo.pack(pady=10)

        # Botões fixos
        self.frame_botoes_fixos = ttk.Frame(self.frame_principal)
        self.frame_botoes_fixos.pack(pady=10)

        self.criar_botao(
            self.frame_botoes_fixos, "YouTube", self.abrir_youtube, 0, 0, PRIMARY
        )

        self.criar_botao(
            self.frame_botoes_fixos, "ChatGPT", self.abrir_chatgpt, 0, 1, SUCCESS
        )

        self.criar_botao(
            self.frame_botoes_fixos, "Word", self.abrir_word, 0, 2, INFO
        )

        # Botões personalizados
        self.frame_botoes_personalizados = ttk.Frame(self.frame_principal)
        self.frame_botoes_personalizados.pack(pady=10)

        # Botões inferiores
        self.frame_botoes_inferiores = ttk.Frame(self.frame_principal)
        self.frame_botoes_inferiores.pack(pady=10)

        self.frame_botoes_inferiores.grid_columnconfigure(0, weight=1)
        self.frame_botoes_inferiores.grid_columnconfigure(1, weight=1)
        self.frame_botoes_inferiores.grid_columnconfigure(2, weight=1)

        self.criar_botao(
            self.frame_botoes_inferiores, "Adicionar App", self.adicionar_aplicativo, 0, 0, SUCCESS
        )

        self.criar_botao(
            self.frame_botoes_inferiores, "Remover Todos", self.remover_todos_botoes, 0, 1, DANGER
        )

        self.criar_botao(
            self.frame_botoes_inferiores, "Remover", self.remover_botao_selecionado, 0, 2, WARNING
        )

        # Carregar botões salvos
        self.carregar_botoes()

    def criar_botao(self, frame, texto, comando, row, column, estilo):
        try:
            botao = ttk.Button(
                frame, text=texto, command=comando, style=f"{estilo}", width=20, bootstyle=estilo
            )
            botao.grid(row=row, column=column, padx=5, pady=5)
            logging.info(f"Botão '{texto}' criado com sucesso.")
        except Exception as e:
            logging.error(f"Erro ao criar botão '{texto}': {e}")

    def abrir_youtube(self):
        webbrowser.open("https://www.youtube.com")
        logging.info("YouTube aberto.")

    def abrir_chatgpt(self):
        webbrowser.open("https://chat.openai.com")
        logging.info("ChatGPT aberto.")

    def abrir_word(self):
        caminho_word = r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE"
        try:
            subprocess.Popen([caminho_word])
            logging.info("Microsoft Word aberto.")
        except FileNotFoundError:
            logging.error(f"Microsoft Word não encontrado no caminho: {caminho_word}.")
            messagebox.showerror("Erro", f"Microsoft Word não encontrado.")
        except Exception as e:
            logging.error(f"Erro ao abrir o Word: {e}")
            messagebox.showerror("Erro", f"Falha ao iniciar o Word: {e}")

    def adicionar_aplicativo(self):
        try:
            caminho_arquivo = filedialog.askopenfilename(title="Selecione um Aplicativo")
            if caminho_arquivo:
                nome_app = simpledialog.askstring("Nome do Aplicativo", "Digite o nome do aplicativo:")
                if not nome_app:
                    nome_app = os.path.basename(caminho_arquivo)
                self.botoes[nome_app] = caminho_arquivo
                self.criar_botao_personalizado(nome_app, caminho_arquivo)
                self.salvar_botoes()
                logging.info(f"Aplicativo '{nome_app}' adicionado com sucesso.")
        except Exception as e:
            logging.error(f"Erro ao adicionar aplicativo: {e}")

    def criar_botao_personalizado(self, nome, caminho):
        contador_botoes = len(self.frame_botoes_personalizados.winfo_children())
        row, col = divmod(contador_botoes, 3)

        frame_botao = ttk.Frame(self.frame_botoes_personalizados)
        frame_botao.grid(row=row, column=col, padx=5, pady=5)

        botao_app = ttk.Button(
            frame_botao, text=nome, width=20, bootstyle="primary"
        )
        botao_app.pack(pady=5)

        botao_app.bind("<Button-1>", lambda e, btn=botao_app: self.selecionar_botao(btn))
        botao_app.bind("<Double-1>", lambda e, path=caminho: self.abrir_aplicativo(path))

    def selecionar_botao(self, botao):
        if self.botao_selecionado:
            self.botao_selecionado.config(bootstyle="primary")
        self.botao_selecionado = botao
        self.botao_selecionado.config(bootstyle="success")
        logging.info(f"Botão '{self.botao_selecionado.cget('text')}' selecionado.")

    def abrir_aplicativo(self, caminho):
        try:
            subprocess.Popen(caminho)
            logging.info(f"Aplicativo '{caminho}' aberto.")
        except Exception as e:
            logging.error(f"Erro ao abrir o aplicativo '{caminho}': {e}")
            messagebox.showerror("Erro", f"Falha ao iniciar o aplicativo: {e}")

    def remover_botao_selecionado(self):
        if not self.botao_selecionado:
            messagebox.showinfo("Informação", "Nenhum botão foi selecionado para remoção.")
            return

        texto_botao = self.botao_selecionado.cget('text')
        if texto_botao in self.botoes:
            for widget in self.frame_botoes_personalizados.winfo_children():
                if widget.winfo_children()[0] == self.botao_selecionado:
                    widget.destroy()
                    break

            del self.botoes[texto_botao]
            self.salvar_botoes()
            self.botao_selecionado = None
            messagebox.showinfo("Sucesso", f"O botão '{texto_botao}' foi removido.")
            logging.info(f"Botão '{texto_botao}' removido.")
        else:
            messagebox.showwarning("Aviso", f"O botão '{texto_botao}' não foi encontrado.")
            logging.warning(f"Tentativa de remover um botão inexistente: '{texto_botao}'.")

    def remover_todos_botoes(self):
        for widget in self.frame_botoes_personalizados.winfo_children():
            widget.destroy()
        self.botoes = {}
        self.botao_selecionado = None
        self.salvar_botoes()
        logging.info("Todos os botões personalizados foram removidos.")

    def salvar_botoes(self):
        try:
            with open(CAMINHO_BOTOES, "w") as arquivo:
                json.dump(self.botoes, arquivo)
            logging.info("Botões salvos com sucesso.")
        except Exception as e:
            logging.error(f"Erro ao salvar botões: {e}")

    def carregar_botoes(self):
        if os.path.exists(CAMINHO_BOTOES):
            try:
                with open(CAMINHO_BOTOES, "r") as arquivo:
                    self.botoes = json.load(arquivo)
                for nome, caminho in self.botoes.items():
                    self.criar_botao_personalizado(nome, caminho)
                logging.info("Botões carregados com sucesso.")
            except Exception as e:
                logging.error(f"Erro ao carregar botões: {e}")

if __name__ == "__main__":
    root = ttk.Window(themename="superhero")
    app = AplicativoAutomacao(root)
    root.mainloop()