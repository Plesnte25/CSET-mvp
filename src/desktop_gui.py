import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from sku_mapper import SKUMapper


class MapperApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SKU Mapper")
        self.geometry("1000x650")
        self.mapper = SKUMapper()
        self.create_widgets()

    # ---------- UI Construction ----------
    def create_widgets(self):
        btn_load = tk.Button(self, text="Load Mapping File", command=self.load_mapping)
        btn_load.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.tree = ttk.Treeview(self, columns=("SKU", "MSKU"), show="headings", height=15)
        self.tree.heading("SKU", text="SKU")
        self.tree.heading("MSKU", text="MSKU")
        self.tree.grid(row=1, column=0, columnspan=5, sticky="nsew", padx=5, pady=5)

        tk.Label(self, text="SKU:").grid(row=2, column=0, sticky="e")
        self.entry_sku = tk.Entry(self)
        self.entry_sku.grid(row=2, column=1, sticky="w")

        tk.Label(self, text="MSKU:").grid(row=2, column=2, sticky="e")
        self.entry_msku = tk.Entry(self)
        self.entry_msku.grid(row=2, column=3, sticky="w")

        btn_add = tk.Button(self, text="Add Mapping", command=self.add_mapping)
        btn_add.grid(row=2, column=4, padx=5, pady=5, sticky="w")

        btn_proc = tk.Button(self, text="Process Sales Data", command=self.process_sales)
        btn_proc.grid(row=3, column=0, padx=5, pady=5, sticky="w")

        self.log = tk.Text(self, height=4)
        self.log.grid(row=4, column=0, columnspan=5, sticky="nsew", padx=5, pady=5)

        for i in range(5):
            self.grid_columnconfigure(i, weight=1)
        self.grid_rowconfigure(1, weight=1)

    # ---------- Callbacks ----------
    def load_mapping(self):
        path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv"), ("Excel", "*.xlsx *.xls")])
        if not path:
            return
        try:
            self.mapper.load_mappings(path)
            self.refresh_tree()
            messagebox.showinfo("Loaded", f"Loaded {len(self.mapper.mapping_dict)} mappings.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def add_mapping(self):
        sku = self.entry_sku.get().strip()
        msku = self.entry_msku.get().strip()
        if not self.mapper.validate_sku(sku):
            messagebox.showerror("Invalid SKU", "SKU format does not match [A-Z0-9_-]+")
            return
        self.mapper.add_combo([sku], msku)
        self.refresh_tree()
        self.entry_sku.delete(0, tk.END)
        self.entry_msku.delete(0, tk.END)

    def process_sales(self):
        path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv"), ("Excel", "*.xlsx *.xls")])
        if not path:
            return
        try:
            df, mapped, missing = self.mapper.process_sales(path)
            self.log.insert(tk.END, f"{mapped} mapped, {missing} missing\n")
            top = tk.Toplevel(self)
            top.title("Processed Preview")
            tree = ttk.Treeview(top, columns=list(df.columns), show="headings")
            for col in df.columns:
                tree.heading(col, text=col)
                tree.column(col, width=120, stretch=False)
            for _, row in df.head(100).iterrows():
                tree.insert("", tk.END, values=list(row))
            tree.pack(fill="both", expand=True)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------- Helpers ----------
    def refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        for sku, msku in self.mapper.mapping_dict.items():
            self.tree.insert("", tk.END, values=(sku, msku))


if __name__ == "__main__":
    MapperApp().mainloop()
