import matplotlib

matplotlib.use('TkAgg')

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk
)

from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import numpy as np
import sympy
import csv

from LSM import LSM
from style import Style
from scrollbar import CustomScrollbar

class App(Tk):

    def __init__(self):
        super().__init__()

        Style()

        self.geometry('1000x600')
        self.config(background='#F0F0F0')

        self.rowconfigure(3, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)           

        self.num_of_vars = StringVar()
        self.num_of_vars.trace_add('write', self.build_formula)

        ttk.Label(
            self, text='Количество неизвестных: ',
            background='#F0F0F0'
        ).grid(row=0, column=0, sticky=E)

        ttk.Spinbox(
            self, from_=1, to=10, width=2, 
            textvariable=self.num_of_vars
        ).grid(row=0, column=1, sticky=W)

        self.formula_box = Canvas(self, bg='#F0F0F0', height=30, highlightthickness=0)
        self.formula_box.grid(row=1, column=0, columnspan=2)

        self.xscrollbar = CustomScrollbar(self, orient=HORIZONTAL, command=self.formula_box.xview)
        self.xscrollbar.grid(row=2, column=0, columnspan=2, sticky=EW)
        self.formula_box.config(xscrollcommand=self.xscrollbar.set)

        self.formula = ttk.Frame(self.formula_box)
        self.formula_box.create_window(0, 0, window=self.formula, anchor=NW)

        self.table = ttk.Frame(self, borderwidth=1, relief=GROOVE)
        self.table.grid(row=3, column=0, columnspan=2, sticky=NSEW)

        self.table.rowconfigure(2, weight=1)
        self.table.columnconfigure(0, weight=1)
        self.table.columnconfigure(2, weight=1)

        btns = ttk.Frame(self)

        ttk.Button(btns, text='Загрузить', command=self.load_from_file).pack(side=TOP, pady=5)
        ttk.Button(btns, text='Построить', command=self.draw).pack(side=BOTTOM, pady=5)
                   
        btns.grid(row=3, column=2, padx=10, pady=10)

        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().grid(row=3, column=3, sticky=NSEW)

        self.text = ttk.Label(self, background='#F0F0F0', text=f'''RSS = ? 
                                                                 \rTSS = ?
                                                                 \rESS = ?
                                                                 \rR² = ? ''')
        self.text.grid(row=0, column=3, rowspan=3, sticky=NSEW)

        self.plot = self.figure.add_subplot()

        self.num_of_vars.set(2)
        self.build_table()

    def load_from_file(self):
        file = filedialog.askopenfile('r', filetypes=(('text files', '*.csv'),))

        if file is None:
            return

        self.X.delete('1.0', END)
        self.Y.delete('1.0', END)

        file.readline()
        csv_file = csv.reader(file)
        
        for line in csv_file:
            x, y = line
            self.X.insert(END, x + '\n')
            self.Y.insert(END, y + '\n')

        file.close()

    def build_formula(self, *args):
        n = int(self.num_of_vars.get())

        for widget in self.formula.winfo_children():
            widget.destroy()

        ttk.Label(self.formula, text='y=', background='#F0F0F0').pack(side=LEFT)
        for i in range(n):
            ttk.Entry(self.formula, width=3).pack(side=LEFT)
            ttk.Label(self.formula, text=f'b{i}' + '+' * (i < n - 1), background='#F0F0F0').pack(side=LEFT)

        self.formula.update_idletasks()
        self.formula_box.config(scrollregion=self.formula_box.bbox(ALL))

    def build_table(self):
        ttk.Label(self.table, text='X', background='#F0F0F0').grid(row=0, column=0)
        ttk.Separator(self.table, orient=VERTICAL).grid(row=0, column=1, sticky=NS)
        ttk.Label(self.table, text='Y', background='#F0F0F0').grid(row=0, column=2)

        ttk.Separator(self.table, orient=HORIZONTAL
        ).grid(row=1,column=0, columnspan=3, sticky=EW)

        self.X = Text(self.table)
        self.X.grid(row=2, column=0, sticky=NSEW)

        ttk.Separator(self.table, orient=VERTICAL).grid(row=2, column=1, sticky=NS)

        self.Y = Text(self.table)
        self.Y.grid(row=2, column=2, sticky=NSEW)
        
    def draw(self):

        def eval_eqn(eqn, in_dict):
            subs = {sympy.symbols(key): item for key, item in in_dict.items()}
            ans = sympy.simplify(eqn).evalf(subs=subs)

            return ans

        X = list(map(float, self.X.get('1.0', END).strip().split()))
        Y = list(map(float, self.Y.get('1.0', END).strip().split()))

        i = 0
        formula = ''
        
        arr = []

        for widget in self.formula.winfo_children():
            if type(widget) is ttk.Entry:
                column = []
                eqn = widget.get().lower()
                for x in X:
                    column.append(eval_eqn(eqn, {'x': x}))

                arr.append(column)

                if i > 0:
                    formula += '+'

                formula += f'({eqn})' + f'*b{i}'
                i += 1
                
        arr.append(Y)
        arr = np.array(arr).T

        coef = {f'b{i}': j for i, j in enumerate(LSM(arr))}
        
        print()
        for bi in coef:
            print(bi, float(coef[bi]))

        coef['x'] = 0

        self.plot.cla()
        self.plot.scatter(X, Y)

        x = np.linspace(min(X), max(X), 20)
        y = []

        for i in x:
            coef['x'] = i
            y.append(eval_eqn(formula, coef))

        self.plot.plot(x, y, color='red')

        RSS = 0
        TSS = 0

        m = np.mean(Y)

        for i in range(len(X)):
            coef['x'] = X[i]
            RSS += (Y[i] - eval_eqn(formula, coef)) ** 2
            TSS += (Y[i] - m) ** 2

        ESS = TSS - RSS
        RR = ESS / TSS

        self.text.config(text=f'''RSS = {round(RSS, 2)}
                                \rTSS = {round(TSS, 2)}
                                \rESS = {round(ESS, 2)}
                                \rR² = {round(RR, 2)}''')

        self.canvas.draw()        
    
    def run(self):
        self.mainloop()



        