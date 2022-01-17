import tkinter as tk
import sqlalchemy.exc
from sqlalchemy import create_engine, Table, Integer, String, MetaData, Column


class App:
    def __init__(self):
        self.MainWin = tk.Tk()
        self.MainWin.title("Телефонная книга")
        self.MainWin.geometry("580x250+700+300")
        self.MainWin.resizable(False, False)
        self.MainWin.iconphoto(False, tk.PhotoImage(file="phone_icons.png"))

        self.FNameLbl = tk.Label(text="Имя", bg="Gray", width=10)
        self.SNameLbl = tk.Label(text="Фамилия", bg="Gray", width=10)
        self.PhoneLbl = tk.Label(text="Телефон", bg="Gray", width=10)

        self.FNameEntry = tk.Entry(self.MainWin, width=25, bd=4)
        self.SNameEntry = tk.Entry(self.MainWin, width=25, bd=4)
        self.PhoneEntry = tk.Entry(self.MainWin, width=15, bd=4)

        self.InsertBtn = tk.Button(self.MainWin, text="Добавить новый контакт", bd=2, command=self.add_contact)
        self.ReadBtn = tk.Button(self.MainWin, text="Показать контакты", bd=2, command=self.read_contacts)
        self.EditBtn = tk.Button(self.MainWin, text="Изменить запись", bd=2, command=self.edit_contact)
        self.DeleteBtn = tk.Button(self.MainWin, text="Удалить контакт", bd=2, command=self.delete_contact)

        self.ContactLtb = tk.Listbox(selectmode=tk.SINGLE, width=70, bd=5)
        self.WarningLbl = tk.Label(text="")

        self.FNameLbl.grid(row=0, column=0, sticky="we")
        self.SNameLbl.grid(row=0, column=1, sticky="we")
        self.PhoneLbl.grid(row=0, column=2, sticky="we")
        self.FNameEntry.grid(row=1, column=0)
        self.SNameEntry.grid(row=1, column=1)
        self.PhoneEntry.grid(row=1, column=2)
        self.InsertBtn.grid(row=0, column=3, rowspan=2, sticky="ns")
        self.ReadBtn.grid(row=2, column=3, rowspan=2, sticky="nswe")
        self.EditBtn.grid(row=4, column=3, rowspan=2, sticky="nswe")
        self.DeleteBtn.grid(row=6, column=3, rowspan=2, sticky="nswe")
        self.ContactLtb.grid(row=2, column=0, rowspan=6, columnspan=3)
        self.WarningLbl.grid(row=8, column=0, columnspan=4, sticky="we")

        self.meta = MetaData()
        self.engine = create_engine('sqlite:///PhoneContact.db')

        self.contacts = Table("Contacts", self.meta,
                              Column("id_contact", Integer, primary_key=True),
                              Column("FirstName", String(50)),
                              Column("SureName", String(50)),
                              Column("Phone", String(20))
                              )
        self.conn = self.engine.connect()

    def start(self):
        self.MainWin.mainloop()
        try:
            self.initialization_db()
        except sqlalchemy.exc.OperationalError:
            self.contacts = Table("Contacts", self.meta, autoload=True)

    def initialization_db(self):
        self.contacts.create(self.engine)

    def add_contact(self):
        if len(self.FNameEntry.get()) == 0 or len(self.SNameEntry.get()) == 0 or len(self.PhoneEntry.get()) == 0:
            self.WarningLbl.config(text="Заполните поля", font="Arial 8")
        else:
            first_name = str(self.FNameEntry.get())
            sure_name = str(self.SNameEntry.get())
            phone = str(self.PhoneEntry.get())
            ins_contact_query = self.contacts.insert().values(FirstName=first_name, SureName=sure_name, Phone=phone)
            self.FNameEntry.delete(0, tk.END)
            self.SNameEntry.delete(0, tk.END)
            self.PhoneEntry.delete(0, tk.END)
            self.conn.execute(ins_contact_query)
            self.read_contacts()
            self.WarningLbl.config(text="")

    def read_contacts(self):
        while self.ContactLtb.size() != 0:
            self.ContactLtb.delete(0)

        select_contact_query = self.contacts.select()
        result = self.conn.execute(select_contact_query)
        for row in result:
            self.ContactLtb.insert(row.id_contact, f"{row.FirstName}    -    {row.SureName}    -    {row.Phone}")

    def edit_contact(self):
        selection = self.ContactLtb.curselection()
        fname_new: str
        sname_new: str
        phone_new: str
        if len(self.FNameEntry.get()) == 0:
            fname_new = self.ContactLtb.get(selection[0]).split("    -    ")[0]
        else:
            fname_new = self.FNameEntry.get()

        if len(self.SNameEntry.get()) == 0:
            sname_new = self.ContactLtb.get(selection[0]).split("    -    ")[1]
        else:
            sname_new = self.SNameEntry.get()

        if len(self.PhoneEntry.get()) == 0:
            phone_new = self.ContactLtb.get(selection[0]).split("    -    ")[2]
        else:
            phone_new = self.PhoneEntry.get()

        upd_contact_query = self.contacts.update().where(
            self.contacts.c.FirstName == self.ContactLtb.get(selection[0]).split("    -    ")[0]).values(
                FirstName=fname_new,
                SureName=sname_new,
                Phone=phone_new
        )
        self.conn.execute(upd_contact_query)
        self.read_contacts()

    def delete_contact(self):
        selection = self.ContactLtb.curselection()
        delete_contact_query = self.contacts.delete().where(
            self.contacts.c.FirstName.like(self.ContactLtb.get(selection[0]).split("    -    ")[0]))
        self.conn.execute(delete_contact_query)
        self.read_contacts()
