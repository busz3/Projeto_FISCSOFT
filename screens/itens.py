import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import customtkinter as ctk
from tkinter import messagebox

from config.styles import COLORS, FONTS
from database.connection import Database


class ItensPage(ctk.CTkFrame):
    def __init__(self, master, on_voltar=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=COLORS["bg"])
        self.on_voltar = on_voltar

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
            width=340, height=38,
            border_width=0, fg_color=COLORS["white"],
            text_color=COLORS["text"], placeholder_text_color="#999999",
        )
        self.entry_busca.pack(side="left", padx=(12, 4), pady=2)
        ctk.CTkLabel(
            busca_container, text="\U0001f50d",
            font=ctk.CTkFont(size=14), text_color="#999999"
        ).pack(side="right", padx=(0, 10))

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
        cols.grid_columnconfigure(0, weight=1)
        cols.grid_columnconfigure(1, weight=3)
        cols.grid_columnconfigure(2, weight=2)
        cols.grid_columnconfigure(3, weight=1)
        cols.grid_columnconfigure(4, weight=2)
        cols.grid_columnconfigure(5, weight=1)
        cols.grid_columnconfigure(6, weight=1)

        colunas = ["ID", "Descrição do item", "Código Interno", "Categorias", "Semestre", "Qtd Prevista", "Status"]
        for i, col_text in enumerate(colunas):
            ctk.CTkLabel(
                cols, text=col_text,
                font=ctk.CTkFont(size=FONTS["size_small"], weight="bold"),
                text_color=COLORS["text_muted"]
            ).grid(row=0, column=i, sticky="w", padx=5)

        self.table_body = ctk.CTkScrollableFrame(
            self.table_frame, fg_color=COLORS["white"], corner_radius=0
        )
        self.table_body.pack(fill="both", expand=True)

        self.itens = self.carregar_do_banco()
        self.carregar_itens()

    def carregar_do_banco(self):
        db = Database()
        if db.conectar():
            resultados = db.executar(
                "SELECT id, nome, descricao, codigo_interno, categoria, semestre, quantidade_prevista, status "
                "FROM itens"
            )
            itens = []
            if resultados:
                for row in resultados.fetchall():
                    itens.append({
                        "id": row[0],
                        "nome": row[1] or row[2] or "-",
                        "descricao": row[2] or "-",
                        "codigo": row[3] or "-",
                        "categoria": row[4] or "-",
                        "semestre": row[5] or "-",
                        "quantidade_prevista": row[6] or 0,
                        "status": row[7] or "Ativo",
                    })
            db.desconectar()
            return itens
        return []

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
        data.grid_columnconfigure(0, weight=1)
        data.grid_columnconfigure(1, weight=3)
        data.grid_columnconfigure(2, weight=2)
        data.grid_columnconfigure(3, weight=1)
        data.grid_columnconfigure(4, weight=2)
        data.grid_columnconfigure(5, weight=1)
        data.grid_columnconfigure(6, weight=1)

        ctk.CTkLabel(
            data, text=str(item["id"]),
            font=ctk.CTkFont(size=FONTS["size_body"]), text_color=COLORS["text"], anchor="w"
        ).grid(row=0, column=0, sticky="w", padx=5)

        ctk.CTkLabel(
            data, text=item["nome"],
            font=ctk.CTkFont(size=FONTS["size_body"]), text_color=COLORS["text"], anchor="w"
        ).grid(row=0, column=1, sticky="w", padx=5)

        ctk.CTkLabel(
            data, text=item["codigo"],
            font=ctk.CTkFont(size=FONTS["size_body"]), text_color=COLORS["text_muted"], anchor="w"
        ).grid(row=0, column=2, sticky="w", padx=5)

        ctk.CTkLabel(
            data, text=item["categoria"],
            font=ctk.CTkFont(size=FONTS["size_body"]), text_color=COLORS["text"], anchor="w"
        ).grid(row=0, column=3, sticky="w", padx=5)

        ctk.CTkLabel(
            data, text=item["semestre"],
            font=ctk.CTkFont(size=FONTS["size_body"]), text_color=COLORS["text"], anchor="w"
        ).grid(row=0, column=4, sticky="w", padx=5)

        ctk.CTkLabel(
            data, text=str(item["quantidade_prevista"]),
            font=ctk.CTkFont(size=FONTS["size_body"]), text_color=COLORS["text"], anchor="w"
        ).grid(row=0, column=5, sticky="w", padx=5)

        status_container = ctk.CTkFrame(data, fg_color="transparent")
        status_container.grid(row=0, column=6, sticky="w")

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
            semestre = entries["Semestre"].get().strip()
            qtd_str = entries["Quantidade Prevista por Semestre"].get().strip()

            if not nome or not descricao:
                messagebox.showwarning("Aviso", "Nome do Item e Descrição são obrigatórios!", parent=modal)
                return

            try:
                qtd = int(qtd_str) if qtd_str else 0
            except ValueError:
                messagebox.showwarning("Aviso", "Quantidade deve ser um número!", parent=modal)
                return

            db = Database()
            if db.conectar():
                db.executar(
                    "INSERT INTO itens (nome, descricao, semestre, quantidade_prevista, status) VALUES (%s,%s,%s,%s,'Ativo')",
                    (nome, descricao, semestre, qtd)
                )
                db.commitar()
                db.desconectar()

            modal.destroy()
            self.itens = self.carregar_do_banco()
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
        if not busca:
            self.itens = self.carregar_do_banco()
        else:
            self.itens = [
                item for item in self.carregar_do_banco()
                if busca in item["nome"].lower()
                or busca in item["descricao"].lower()
                or busca in item["codigo"].lower()
                or busca in item["categoria"].lower()
                or busca in item["semestre"].lower()
            ]
        self.carregar_itens()
        self.total_label.configure(text=f"Total de itens: {len(self.itens)}")

    def limpar_filtros(self):
        self.entry_busca.delete(0, "end")
        self.itens = self.carregar_do_banco()
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
