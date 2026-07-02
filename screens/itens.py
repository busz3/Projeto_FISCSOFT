import sys
import re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import customtkinter as ctk
from tkinter import messagebox, filedialog

import pandas as pd

from config.styles import COLORS, FONTS

ABA = "TCCM-GERAL"


class ItensPage(ctk.CTkFrame):
    def __init__(self, master, on_voltar=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=COLORS["bg"])
        self.on_voltar = on_voltar
        self.arquivo_atual = None

        self.build_header()
        self.build_filter_bar()
        self.build_table()
        self.build_footer()

    def build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(30, 20))

        ctk.CTkLabel(
            header,
            text="Itens do Tccm",
            font=ctk.CTkFont(size=FONTS["size_title"], weight="bold"),
            text_color=COLORS["primary"],
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Visualize e gerencie os itens cadastrados no sistema",
            font=ctk.CTkFont(size=FONTS["size_subtitle"]),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w", pady=(4, 0))

    def build_filter_bar(self):
        container = ctk.CTkFrame(
            self, fg_color=COLORS["white"], corner_radius=8,
            border_width=1, border_color=COLORS["border"]
        )
        container.pack(fill="x", padx=30, pady=(0, 20))

        inner = ctk.CTkFrame(container, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=14)

        ctk.CTkLabel(
            inner, text="Filtro",
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            text_color=COLORS["text_muted"]
        ).pack(anchor="w", pady=(0, 8))

        row = ctk.CTkFrame(inner, fg_color="transparent")
        row.pack(fill="x")

        busca_container = ctk.CTkFrame(
            row, fg_color=COLORS["white"], border_width=1,
            border_color=COLORS["border"], corner_radius=6
        )
        busca_container.pack(side="left", padx=(0, 10))

        self.entry_busca = ctk.CTkEntry(
            busca_container,
            placeholder_text="Buscar item...",
            width=300, height=38,
            border_width=0, fg_color=COLORS["white"],
            text_color=COLORS["text"], placeholder_text_color="#999999",
        )
        self.entry_busca.pack(side="left", padx=(12, 4), pady=2)
        ctk.CTkLabel(
            busca_container, text="\U0001f50d",
            font=ctk.CTkFont(size=14), text_color="#999999"
        ).pack(side="right", padx=(0, 10))

        semestre_container = ctk.CTkFrame(
            row, fg_color=COLORS["white"], border_width=1,
            border_color=COLORS["border"], corner_radius=6
        )
        semestre_container.pack(side="left", padx=(0, 10))

        ctk.CTkLabel(
            semestre_container, text="Semestre:",
            font=ctk.CTkFont(size=FONTS["size_body"]),
            text_color=COLORS["text_muted"]
        ).pack(side="left", padx=(10, 4), pady=2)

        self.combo_semestre = ctk.CTkComboBox(
            semestre_container,
            values=["Todos"],
            width=130, height=34,
            border_width=1, border_color=COLORS["border"],
            fg_color=COLORS["white"], text_color=COLORS["text"],
            button_color=COLORS["primary"], button_hover_color=COLORS["primary_hover"],
            dropdown_fg_color=COLORS["white"],
            font=ctk.CTkFont(size=FONTS["size_body"]),
        )
        self.combo_semestre.pack(side="left", padx=(0, 8), pady=4)
        self.combo_semestre.set("Todos")

        btn_frame = ctk.CTkFrame(row, fg_color="transparent")
        btn_frame.pack(side="left", padx=(5, 0))

        ctk.CTkButton(
            btn_frame,
            text="\u2630  Aplicar Filtro",
            height=38, corner_radius=6,
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            text_color="white", border_width=0,
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            command=self.pesquisar,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_frame,
            text="\U0001f504  Limpar",
            height=38, corner_radius=6,
            fg_color=COLORS["white"], hover_color="#F0F0F0",
            text_color=COLORS["text"],
            border_width=1, border_color=COLORS["border"],
            font=ctk.CTkFont(size=FONTS["size_body"]),
            command=self.limpar_filtros,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_frame,
            text="\U0001f4e5  Importar Excel",
            height=38, corner_radius=6,
            fg_color=COLORS["white"], hover_color="#F0F0F0",
            text_color=COLORS["text"],
            border_width=1, border_color=COLORS["border"],
            font=ctk.CTkFont(size=FONTS["size_body"]),
            command=self.importar_excel,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_frame,
            text="+  Novo Item",
            height=38, corner_radius=6,
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            text_color="white", border_width=0,
            font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            command=self.novo_item,
        ).pack(side="left")

    def build_table(self):
        self.table_frame = ctk.CTkFrame(
            self, fg_color=COLORS["white"], corner_radius=8,
            border_width=1, border_color=COLORS["border"]
        )
        self.table_frame.pack(fill="both", expand=True, padx=30, pady=(0, 10))

        header = ctk.CTkFrame(
            self.table_frame, fg_color="#FAFAFA",
            height=44, corner_radius=0
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        cols = ctk.CTkFrame(header, fg_color="transparent")
        cols.pack(side="left", fill="x", expand=True, padx=(20, 20))

        colunas = ["ID", "Descrição do item", "Categorias", "Semestre", "Qtd Prevista", "Status"]
        larguras = [50, 350, 120, 100, 90, 80]
        for i, (col_text, larg) in enumerate(zip(colunas, larguras)):
            ctk.CTkLabel(
                cols, text=col_text, width=larg,
                font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                text_color=COLORS["text_muted"], anchor="w"
            ).grid(row=0, column=i, sticky="w", padx=5)

        self.table_body = ctk.CTkScrollableFrame(
            self.table_frame, fg_color=COLORS["white"], corner_radius=0
        )
        self.table_body.pack(fill="both", expand=True)

        self.itens = self.carregar_do_excel()
        self._todos_os_itens = self.itens[:]
        self.semestres_disponiveis = self._extrair_semestres()
        self.combo_semestre.configure(values=["Todos"] + [f"{s} meses" for s in self.semestres_disponiveis])
        self.carregar_itens()

    def _parsear_prazo(self, texto):
        """Extrai lista de (quantidade, semestre) de uma string de prazo de entrega."""
        if pd.isna(texto) or not str(texto).strip():
            return []
        pattern = re.compile(
            r'(\d+(?:[.,]\d+)?)\s*(?:Kg|kg|un|unidade[s]?|caixa[s]?|litro[s]?)?\s*em\s*at[ée]\s*(\d+)\s*m[eê]s'
        )
        return [(qtd, int(meses)) for qtd, meses in pattern.findall(str(texto))]

    def carregar_do_excel(self):
        if not self.arquivo_atual:
            return []
        try:
            ext = Path(self.arquivo_atual).suffix.lower()
            engine = "odf" if ext == ".ods" else "openpyxl" if ext == ".xlsx" else None
            if not engine:
                messagebox.showerror("Erro", f"Formato não suportado: {ext}")
                return []
            df = pd.read_excel(self.arquivo_atual, engine=engine, sheet_name=ABA)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao ler o arquivo:\n{e}")
            return []

        itens = []
        for _, row in df.iterrows():
            prazos = self._parsear_prazo(row.get("PRAZO DE ENTREGA", ""))
            primeiro_prazo = prazos[0] if prazos else ("-", "-")
            qtd_prevista = primeiro_prazo[0]
            semestre = f"{primeiro_prazo[1]} meses" if primeiro_prazo[1] != "-" else "-"

            itens.append({
                "id": int(row.get("Nº", 0)) if pd.notna(row.get("Nº")) else 0,
                "descricao": str(row.get("DESCRIÇÃO", "")) or "-",
                "categoria": str(row.get("TIPO DE MATERIAL", "")) or "-",
                "semestre": semestre,
                "quantidade_prevista": qtd_prevista,
                "status": "Ativo",
                "prazos": prazos,
            })
        return itens

    def _extrair_semestres(self):
        semestres = set()
        for item in self.itens:
            for _, meses in item.get("prazos", []):
                semestres.add(meses)
        return sorted(semestres)

    def importar_excel(self):
        caminho = filedialog.askopenfilename(
            title="Selecionar arquivo Excel",
            filetypes=[
                ("Planilhas", "*.ods *.xlsx *.xls"),
                ("Todos os arquivos", "*.*")
            ]
        )
        if not caminho:
            return

        self.arquivo_atual = caminho
        self.itens = self.carregar_do_excel()
        self._todos_os_itens = self.itens[:]
        self.semestres_disponiveis = self._extrair_semestres()
        self.combo_semestre.configure(values=["Todos"] + [f"{s} meses" for s in self.semestres_disponiveis])
        self.carregar_itens()
        self.total_label.configure(text=f"Total de itens: {len(self.itens)}")

        nome_arquivo = Path(caminho).name
        messagebox.showinfo("Sucesso", f"Arquivo '{nome_arquivo}' carregado com {len(self.itens)} itens.")

    def carregar_itens(self):
        for widget in self.table_body.winfo_children():
            widget.destroy()

        for item in self.itens:
            self.adicionar_linha(item)

    def adicionar_linha(self, item):
        linha = ctk.CTkFrame(self.table_body, fg_color="transparent", height=48)
        linha.pack(fill="x")
        linha.pack_propagate(False)

        ctk.CTkFrame(
            self.table_body, fg_color="#F0F0F0", height=1
        ).pack(fill="x")

        data = ctk.CTkFrame(linha, fg_color="transparent")
        data.pack(side="left", fill="x", expand=True, padx=(20, 20))

        ctk.CTkLabel(
            data, text=str(item["id"]), width=50,
            font=ctk.CTkFont(size=FONTS["size_body"]), text_color=COLORS["text"], anchor="w"
        ).pack(side="left", padx=5)

        desc_trim = item["descricao"][:50] + ("..." if len(item["descricao"]) > 50 else "")
        desc_label = ctk.CTkLabel(
            data, text=desc_trim, width=350,
            font=ctk.CTkFont(size=FONTS["size_body"]), text_color=COLORS["text"], anchor="w",
            cursor="hand2"
        )
        desc_label.pack(side="left", padx=5)
        desc_label.bind("<Button-1>", lambda e, d=item["descricao"]: self._mostrar_descricao(d))

        ctk.CTkLabel(
            data, text=item["categoria"], width=120,
            font=ctk.CTkFont(size=FONTS["size_body"]), text_color=COLORS["text"], anchor="w"
        ).pack(side="left", padx=5)

        ctk.CTkLabel(
            data, text=item["semestre"], width=100,
            font=ctk.CTkFont(size=FONTS["size_body"]), text_color=COLORS["text"], anchor="w"
        ).pack(side="left", padx=5)

        ctk.CTkLabel(
            data, text=str(item["quantidade_prevista"]), width=90,
            font=ctk.CTkFont(size=FONTS["size_body"]), text_color=COLORS["text"], anchor="w"
        ).pack(side="left", padx=5)

        status_container = ctk.CTkFrame(data, fg_color="transparent", width=80)
        status_container.pack(side="left", padx=5)
        status_container.pack_propagate(False)

        cor = COLORS["primary"] if item["status"] == "Ativo" else COLORS["danger"] if item["status"] == "Inativo" else "#E65100"
        bolinha = ctk.CTkFrame(
            status_container, fg_color=cor,
            width=8, height=8, corner_radius=4
        )
        bolinha.pack(side="left", padx=(0, 6))
        bolinha.pack_propagate(False)
        ctk.CTkLabel(
            status_container, text=item["status"],
            font=ctk.CTkFont(size=FONTS["size_body"]), text_color=COLORS["text"]
        ).pack(side="left")

    def _mostrar_descricao(self, descricao):
        modal = ctk.CTkToplevel(self)
        modal.title("Descrição do Item")
        modal.geometry("500x200")
        modal.configure(fg_color=COLORS["white"])
        modal.transient(self)
        modal.grab_set()

        ctk.CTkLabel(
            modal, text="Descrição Completa",
            font=ctk.CTkFont(size=FONTS["size_subtitle"], weight="bold"),
            text_color=COLORS["primary"]
        ).pack(pady=(15, 10))

        ctk.CTkLabel(
            modal, text=descricao, wraplength=450,
            font=ctk.CTkFont(size=FONTS["size_body"]), text_color=COLORS["text"]
        ).pack(padx=20, pady=10)

        ctk.CTkButton(
            modal, text="Fechar", height=34, width=100,
            fg_color=COLORS["border"], hover_color="#C0C0C0",
            text_color=COLORS["text"],
            font=ctk.CTkFont(size=FONTS["size_body"]),
            command=modal.destroy
        ).pack(pady=(10, 15))

    def build_footer(self):
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=30, pady=(5, 15))

        self.total_label = ctk.CTkLabel(
            footer,
            text=f"Total de itens: {len(self.itens)}",
            font=ctk.CTkFont(size=FONTS["size_body"]),
            text_color=COLORS["text_muted"]
        )
        self.total_label.pack(side="left")

        voltar_container = ctk.CTkFrame(footer, fg_color="transparent")
        voltar_container.pack(side="right", expand=True)

        ctk.CTkButton(
            voltar_container,
            text="Voltar",
            height=38, width=200, corner_radius=6,
            fg_color=COLORS["border"], hover_color="#C0C0C0",
            text_color=COLORS["text"],
            font=ctk.CTkFont(size=FONTS["size_body"]),
            command=self.voltar,
        ).pack()

    def voltar(self):
        if self.on_voltar:
            self.on_voltar()
        else:
            self.master.destroy()

    def novo_item(self):
        self.abrir_formulario()

    def abrir_formulario(self):
        modal = ctk.CTkToplevel(self)
        modal.title("Novo Item")
        modal.geometry("450x520")
        modal.configure(fg_color=COLORS["white"])
        modal.transient(self)
        modal.grab_set()

        ctk.CTkLabel(
            modal, text="Cadastrar Novo Item",
            font=ctk.CTkFont(size=FONTS["size_title"], weight="bold"),
            text_color=COLORS["primary"]
        ).pack(pady=(20, 15))

        frame = ctk.CTkFrame(modal, fg_color="transparent")
        frame.pack(padx=30, fill="x")

        campos = ["Nome do Item", "Descrição", "Semestre", "Quantidade Prevista por Semestre"]
        entries = {}

        for label in campos:
            ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
                          text_color=COLORS["text"], anchor="w").pack(fill="x", pady=(8, 2))
            entry = ctk.CTkEntry(frame, height=36, corner_radius=6,
                                  fg_color=COLORS["white"], border_width=1, border_color=COLORS["border"])
            entry.pack(fill="x")
            entries[label] = entry

        def salvar():
            nome = entries["Nome do Item"].get().strip()
            descricao = entries["Descrição"].get().strip()

            if not nome or not descricao:
                messagebox.showwarning("Aviso", "Nome do Item e Descrição são obrigatórios!", parent=modal)
                return

            modal.destroy()
            self.itens = self.carregar_do_excel()
            self._todos_os_itens = self.itens[:]
            self.semestres_disponiveis = self._extrair_semestres()
            self.combo_semestre.configure(values=["Todos"] + [f"{s} meses" for s in self.semestres_disponiveis])
            self.carregar_itens()
            self.total_label.configure(text=f"Total de itens: {len(self.itens)}")

        ctk.CTkButton(
            frame, text="Salvar", height=40, corner_radius=6,
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            text_color="white", font=ctk.CTkFont(size=FONTS["size_body"], weight="bold"),
            command=salvar
        ).pack(fill="x", pady=(20, 5))

        ctk.CTkButton(
            frame, text="Cancelar", height=34, corner_radius=6,
            fg_color="transparent", text_color=COLORS["text_muted"],
            hover_color="#F0F0F0", font=ctk.CTkFont(size=FONTS["size_body"]),
            command=modal.destroy
        ).pack(fill="x")

    def pesquisar(self):
        busca = self.entry_busca.get().strip().lower()
        semestre_sel = self.combo_semestre.get()

        self.itens = [
            item for item in self._todos_os_itens
            if (not busca or busca in item["descricao"].lower()
                or busca in item["categoria"].lower()
                or busca in str(item["id"]))
            and (semestre_sel == "Todos" or item["semestre"] == semestre_sel)
        ]
        self.carregar_itens()
        self.total_label.configure(text=f"Total de itens: {len(self.itens)}")

    def limpar_filtros(self):
        self.entry_busca.delete(0, "end")
        self.combo_semestre.set("Todos")
        self.itens = self._todos_os_itens[:]
        self.carregar_itens()
        self.total_label.configure(text=f"Total de itens: {len(self.itens)}")


if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.title("FISCSOFT - Itens")
    app.geometry("1200x700")
    app.configure(fg_color=COLORS["bg"])

    ItensPage(app).pack(fill="both", expand=True)
    app.mainloop()
