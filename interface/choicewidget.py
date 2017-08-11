from tkinter import Frame, Label, Button
from tkinter.ttk import Treeview, Scrollbar

from util import pkw


class TkChoice(Frame):

    def __init__(self, master, arg, data, callbacks):
        super().__init__(master)
        title, colnames, widths = arg
        self.data = None
        self.tw = None

        Label(self, text=title).pack(**pkw)

        self._build_treeview(data, colnames, widths, callbacks)
        self._build_buttonframe(callbacks)

    def _build_treeview(self, data, colnames, widths, callbacks):
        self.tw = Treeview(self, columns=[str(i) for i in range(len(colnames)-1)])
        self._configure_treeview(data, colnames, widths)
        self._add_scrollbar_to_treeview()

        self.tw.bind("<<TreeviewSelect>>", self.setdata)
        self.tw.bind("<Double-Button-1>", callbacks["step"])
        self.tw.pack(**pkw)

    def _configure_treeview(self, data, colnames, widths):
        for col, name in enumerate(colnames):
            self.tw.heading(f"#{col}", text=name)
        for col, cw in enumerate(widths):
            self.tw.column(f"#{col}", width=cw)
        for row in data:
            self.tw.insert("", "end", text=row[0], values=row[1:])

    def _add_scrollbar_to_treeview(self):
        vsb = Scrollbar(self, orient="vertical", command=self.tw.yview)
        hsb = Scrollbar(self, orient="horizontal", command=self.tw.xview)
        self.tw.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    def _build_buttonframe(self, callbacks):
        f = Frame(self)
        Button(f, text="Vissza", command=callbacks["back"]).pack(side="left", **pkw)
        Button(f, text="Mégsem", command=callbacks["cancel"]).pack(side="left", **pkw)
        Button(f, text="Új...", command=callbacks["new"]).pack(side="left", **pkw)
        self.nextb = Button(f, text="Tovább", command=callbacks["step"], state="disabled")
        self.nextb.pack(side="left", **pkw)
        f.pack(**pkw)

    def setdata(self, event):
        sel = event.widget.selection(items="#0")
        self.data = event.widget.item(sel)["text"]
        self.nextb.configure(state="active")
