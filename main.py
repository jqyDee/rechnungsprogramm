import fileinput
import logging
import os
import platform
import re
import shutil
import subprocess
import sys
import time
import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image

from fpdf import FPDF, XPos, YPos
import customtkinter
import yaml

#####################################################
#                                                   #
#                                                   #
#               Version Number 2.0.0                #
#                                                   #
#                                                   #
#####################################################
#           Copyright Matti Fischbach 2023          #
#####################################################

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")
default_font = ('Arial', 15, "normal")
small_heading = ('Arial', 18, "bold")
large_heading = ('Arial', 28, "bold")

try:
    search_img = customtkinter.CTkImage(light_image=Image.open('./system/components/images/search-md.png'),
                                        dark_image=Image.open('./system/components/images/search-md.png'),
                                        size=(15, 15))
except FileNotFoundError:
    logging.warning('./system/components/images/search-md.png cant be found, trying to rebuild at next startup')
    search_img = None
try:
    open_img = customtkinter.CTkImage(light_image=Image.open('./system/components/images/cursor-01.png'),
                                      dark_image=Image.open('./system/components/images/cursor-01.png'),
                                      size=(15, 15))
except FileNotFoundError:
    logging.warning('./system/components/images/cursor-01.png cant be found, trying to rebuild at next startup')
    open_img = None
try:
    edit_img = customtkinter.CTkImage(light_image=Image.open('./system/components/images/edit-05.png'),
                                      dark_image=Image.open('./system/components/images/edit-05.png'),
                                      size=(15, 15))
except FileNotFoundError:
    logging.warning('./system/components/images/edit-05.png cant be found, trying to rebuild at next startup')
    edit_img = None
try:
    trash_img = customtkinter.CTkImage(light_image=Image.open('./system/components/images/trash-03.png'),
                                       dark_image=Image.open('./system/components/images/trash-03.png'),
                                       size=(15, 15))
except FileNotFoundError:
    logging.warning('./system/components/images/trash-03.png cant be found, trying to rebuild at next startup')
    trash_img = None


class App(customtkinter.CTk):
    """Class creating the main window. Responsible for calling the class
       Sidebar and BottomNav at startup and calling the Interface classes."""

    # Default values for properties.yml
    version = '2.0.0'
    year = time.strftime('%Y')
    window_resizable = False
    window_width = 1300
    window_height = 750
    debug_mode = False
    behandlungsarten_limiter = True
    behandlungsarten_limit = 5
    rechnungen_location = f'{os.getcwd()}/rechnungen'
    stammdaten_location = f'{os.getcwd()}/stammdaten'
    backups_enabled = True
    backup_location = f'{os.getcwd()}/backups'

    # currently active interfaces - !!!MAYBE REDUNDANT!!!
    kg_interface = None
    hp_interface = None
    stammdaten_interface = None
    rechnung_loeschen_interface = None
    einstellungen_interface = None
    toplevel_window = None

    # currently active interface
    open_interface = None

    def __init__(self):
        super().__init__()

        self.configure(fg_color='gray16')
        self.protocol("WM_DELETE_WINDOW", lambda: self.on_shutdown())

        self.check_or_create_working_dirs()
        self.configure_main_window()

        self.sidebar = Sidebar(self)
        self.bottom_nav = BottomNav(self)

        self.mainloop()

    def check_or_create_working_dirs(self):
        """Runs at startup and checks the necessary Directories to run the Program. HAS TO BE MOVED TO BACKEND"""

        created_properties_yml = False

        # checking ./system/ or creating it
        if not os.path.exists('./system') or not os.path.exists('./system/properties.yml'):
            try:
                os.makedirs('./system')
            except FileExistsError:
                pass

            # creating properties.yml
            with open('system/properties.yml', 'w') as f:
                yaml.dump(
                    {'version': self.version, 'program_year': self.year, 'window_resizable': self.window_resizable,
                     'window_width': self.window_width, 'window_height': self.window_height,
                     'debug_mode': self.debug_mode, 'backup_location': self.backup_location,
                     'rechnungen_location': self.rechnungen_location,
                     'stammdaten_location': self.stammdaten_location,
                     'behandlungsarten_limiter': self.behandlungsarten_limiter,
                     'behandlungsarten_limit': self.behandlungsarten_limit,
                     'backups_enabled': self.backups_enabled}, f)

            created_properties_yml = True

        # extracting year out of ./system/properties.yml
        with open('./system/properties.yml', 'r') as f:
            properties_dict = yaml.safe_load(f)
            self.version = properties_dict['version']
            self.year = properties_dict['program_year']
            self.window_resizable = properties_dict['window_resizable']
            self.window_width = properties_dict['window_width']
            self.window_height = properties_dict['window_height']
            self.debug_mode = properties_dict['debug_mode']
            self.backup_location = properties_dict['backup_location']
            self.rechnungen_location = properties_dict['rechnungen_location']
            self.stammdaten_location = properties_dict['stammdaten_location']
            self.behandlungsarten_limiter = properties_dict['behandlungsarten_limiter']
            self.behandlungsarten_limit = properties_dict['behandlungsarten_limit']
            self.backups_enabled = properties_dict['backups_enabled']

        if self.debug_mode:
            logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
        else:
            logging.basicConfig(stream=sys.stderr, level=logging.INFO)

        logging.debug('App.check_or_create_working_dirs() called')
        if created_properties_yml:
            logging.info('created properties.yml file and dir')
        logging.info(f'read properties.yml file. \n'
                     f'version: {self.version};\n'
                     f'year: {self.year};\n'
                     f'resizable: {self.window_resizable}\n'
                     f'width: {self.window_width}\n'
                     f'height: {self.window_height}\n'
                     f'Debug: {self.debug_mode}\n'
                     f'behandlungsarten_limiter: {self.behandlungsarten_limiter}\n'
                     f'behandlungsarten_limit: {self.behandlungsarten_limit}\n'
                     f'rechnungen_location: {self.rechnungen_location}\n'
                     f'stammdaten_location: {self.stammdaten_location}\n'
                     f'backups_enabled: {self.backups_enabled}\n'
                     f'backup_location: {self.backup_location}')

        if not os.path.exists(f'{self.rechnungen_location}/rechnungen-{self.year}'):
            os.makedirs(f'{self.rechnungen_location}/rechnungen-{self.year}')
            logging.info(f'created rechnungen-{self.year} dir')

        if not os.path.exists(f'{self.stammdaten_location}/'):
            os.makedirs(f'{self.stammdaten_location}/')
            logging.info('created stammdaten dir')

        if not os.path.exists(f'{self.rechnungen_location}/rechnungen-csv'):
            os.makedirs(f'{self.rechnungen_location}/rechnungen-csv')
            logging.info('created ZusammenfassungRechnungen dir')

        if not os.path.exists(f'{self.backup_location}/'):
            os.makedirs(f'{self.backup_location}/')
            logging.info('created backups dir')

    def configure_main_window(self, title: str = 'Rechnungsprogramm'):
        """Configures the main window Dimensions, title, isResizeable, X-Y-Coordinates)"""

        logging.debug('App.configure_main_window() called')

        # configure main window
        self.title(f'{title}')
        if self.window_resizable:
            self.resizable(width=True, height=True)
        else:
            self.resizable(width=False, height=False)
        self.minsize(width=int(self.window_width), height=int(self.window_height))

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_cordinate = int((screen_width / 2) - (int(self.window_width) / 2))
        y_cordinate = int((screen_height / 2) - (int(self.window_height) / 2))

        self.geometry(f'{self.window_width}x{self.window_height}+{x_cordinate}+{y_cordinate}')

    def kg_rechnung(self, *args):
        """Calls the store_draft function and creates the interface to create a new KGRechnung by
           calling the class KGRechnungInterface.
                Param: *args = data out of rechnungen-*.csv or *-DRAFT-*.csv"""

        logging.debug('App.kg_rechnung() called')
        if not self.store_draft():
            return
        self.open_interface = 'kg'
        if self.kg_interface is None or not self.kg_interface.winfo_exists():
            self.clear_interfaces()
            self.kg_interface = KGRechnungInterface(self)
            try:
                if len(*args) != 0:
                    self.kg_interface.insert_data(*args)
            except TypeError:
                pass

    def hp_rechnung(self):
        """Calls the store_draft function and creates the interface to create a new HPRechnung by
           calling the class HPRechnungInterface"""

        logging.debug('App.hp_rechnung() called')
        if not self.store_draft():
            return
        self.open_interface = 'hp'
        if self.hp_interface is None or not self.hp_interface.winfo_exists():
            self.clear_interfaces()
            self.hp_interface = HPRechnungInterface(self)

    def stammdaten_(self):
        """Calls the store_draft function and creates the stammdaten Interface by
           calling the class StammdatenInterface"""

        logging.debug('App.stammdaten_() called')
        if not self.store_draft():
            return
        self.open_interface = 'st'
        if self.stammdaten_interface is None or not self.stammdaten_interface.winfo_exists():
            self.clear_interfaces()
            self.stammdaten_interface = StammdatenInterface(self)

    def rechnung_loeschen(self):
        """Calls the store_draft function and creates the Rechnung Löschen Interface by
           calling the class RechnungLoeschenInterface"""

        logging.debug('App.rechnung_loeschen() called')
        if not self.store_draft():
            return
        self.open_interface = 're'
        if self.rechnung_loeschen_interface is None or not self.rechnung_loeschen_interface.winfo_exists():
            self.clear_interfaces()
            self.rechnung_loeschen_interface = RechnungLoeschenInterface(self)

    def einstellungen(self):
        """Calls the store_draft function and creates the Einstellungen Interface by
           calling the class EinstellungenInterface"""

        logging.debug('App.rechnung_loeschen() called')
        if not self.store_draft():
            return
        self.open_interface = 'ei'
        if self.einstellungen_interface is None or not self.einstellungen_interface.winfo_exists():
            self.clear_interfaces()
            self.einstellungen_interface = EinstellungInterface(self)

    def updateyear_interface(self):
        """Creates the Update Year Interface by calling the class UpdateYearToplevelWindow"""

        logging.debug('App.updateyear_interface() called')

        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = UpdateYearToplevelWindow(self)

    def clear_interfaces(self):
        """Clears the Interfaces to prevent them from Layering on top of each other. Disables the Bottom nav
           Buttons and Warnings"""

        logging.debug('App.clear_interfaces() called')

        self.bottom_nav.bottom_nav_button.configure(state='disabled')
        self.bottom_nav.bottom_nav_button_2.configure(state='disabled')
        self.bottom_nav.bottom_nav_warning.configure(text='', fg_color='transparent')
        try:
            self.kg_interface.destroy()
            self.kg_interface = None
        except AttributeError:
            pass
        try:
            self.hp_interface.destroy()
            self.kg_interface = None
        except AttributeError:
            pass
        try:
            self.stammdaten_interface.destroy()
            self.stammdaten_interface = None
        except AttributeError:
            pass
        try:
            self.rechnung_loeschen_interface.destroy()
            self.rechnung_loeschen_interface = None
        except AttributeError:
            pass
        try:
            self.einstellungen_interface.destroy()
            self.einstellungen_interface = None
        except AttributeError:
            pass

    def on_shutdown(self):
        """Called when program is closing. Checks the integrity of necessary Directories and
           creates backup when enabled in properties.yml"""

        logging.debug('App.on_shutdown() called')

        self.check_or_create_working_dirs()

        if not Backend(self).create_backup():
            logging.info('No backup created')
        else:
            logging.info('Backup created')

        self.destroy()

    def store_draft(self) -> bool:
        """Calls store_draft in Backend with the Params:
                    open_interface: str = self.open_interface"""

        logging.debug('App.store_draft() called')

        return Backend(self).store_draft(self.open_interface)


class Sidebar(customtkinter.CTkFrame):
    """Creating the Sidebar frame and widgets"""

    def __init__(self, parent):
        super().__init__(parent)

        logging.info('class Sidebar() called')

        self.parent = parent
        self.year = self.parent.year

        self.configure(corner_radius=0)
        self.place(x=0, y=0, relwidth=0.2, relheight=1)

        self.create_widgets()
        self.create_layout()

    def create_widgets(self):
        """Creating the widgets of frame/class Sidebar"""

        logging.debug('Sidebar.create_widgets() called')

        # heading
        self.heading_1 = customtkinter.CTkLabel(self, text='Rechnungsprogramm',
                                                font=('Arial', 23, "bold"))
        self.heading_2 = customtkinter.CTkLabel(self, text=f'{self.year}', font=small_heading)

        # buttons
        self.button_1 = customtkinter.CTkButton(self, text='KG-Rechnung', command=lambda: self.parent.kg_rechnung())
        self.button_2 = customtkinter.CTkButton(self, text='HP-Rechnung', command=lambda: self.parent.hp_rechnung())
        self.button_3 = customtkinter.CTkButton(self, text='stammdaten', command=lambda: self.parent.stammdaten_())
        self.button_4 = customtkinter.CTkButton(self, text='rechnungen',
                                                command=lambda: self.parent.rechnung_loeschen())
        self.button_6 = customtkinter.CTkButton(self, text='clear screen',
                                                command=lambda: self.parent.clear_interfaces())
        self.button_5 = customtkinter.CTkButton(self, text='Einstellungen',
                                                command=lambda: self.parent.einstellungen())

    def create_layout(self):
        """Creating the layout of the widgets of the frame/class Sidebar """

        logging.debug('Sidebar.create_layout() called')

        # heading
        self.heading_1.pack(padx=0, pady=(20, 0), side='top', fill='x')
        self.heading_2.pack(padx=0, pady=(5, 0), side='top', fill='x')

        # buttons
        self.button_1.pack(padx=20, pady=(20, 0), side='top', fill='x')
        self.button_2.pack(padx=20, pady=(10, 0), side='top', fill='x')
        self.button_3.pack(padx=20, pady=(10, 0), side='top', fill='x')
        self.button_4.pack(padx=20, pady=(10, 0), side='top', fill='x')
        self.button_5.pack(padx=20, pady=(10, 20), side='bottom', fill='x')

        if self.parent.debug_mode:
            logging.debug('clear screen button packed')
            self.button_6.pack(padx=20, pady=(10, 0), side='bottom', fill='x')


class BottomNav(customtkinter.CTkFrame):
    """Creating the BottomNav frame and widgets"""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        logging.info('class BottomNav() called')

        self.configure(corner_radius=0)
        self.place(relx=0.2, rely=0.9, relwidth=0.8, relheight=0.1)

        # Creating widgets
        self.bottom_nav_warning = customtkinter.CTkLabel(self, text='')
        self.bottom_nav_button_2 = customtkinter.CTkButton(self, text='Entwurf speichern', state='disabled',
                                                           command=lambda: self.parent.store_draft())
        self.bottom_nav_button = customtkinter.CTkButton(self, text='speichern', state='disabled')

        # Creating layout
        self.bottom_nav_button.pack(side='right', fill=None, expand=False, padx=(20, 40))
        self.bottom_nav_button_2.pack(side='right', fill=None, expand=False, padx=20)
        self.bottom_nav_warning.pack(side='right', fill=None, expand=False, padx=20)


class KGRechnungInterface(customtkinter.CTkScrollableFrame):
    """Creating the KGRechnungInterface frame and widgets_part_1"""

    # Daten layout
    ################
    # 0  1  2  3
    # -----------
    # 1 (1) 2 (2)
    # 3 (3) 4 (4)
    # 5 (5) 6 (6)
    # 7 (7) 8 (8)
    # 9 (9) 10 (10)
    # -----------
    ################
    daten_layout = [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10)]

    # count for the Behandlungsarten
    row_count = 0

    def __init__(self, parent):
        super().__init__(parent)

        logging.info('class KGRechnungInterface() called')

        self.parent = parent
        self.parent.bottom_nav.bottom_nav_button.configure(command=lambda: self.kg_rechnung_erstellen_button_event())

        self.configure(fg_color='gray16', corner_radius=0)
        self.place(relx=0.2, y=0, relwidth=0.8, relheight=0.90)

        # tk variables
        self.frame_1_warning_var = tk.StringVar()

        self.create_widgets_part_1()
        self.create_layout_part_1()

    def create_widgets_part_1(self):
        """Creating the widgets_part_1 of frame/class KGRechnungInterface"""

        logging.debug('KGRechnungInterface.create_widgets_part_1() called')

        # heading section
        self.heading_1 = customtkinter.CTkLabel(self, text='Neue KG Rechnung', font=large_heading)

        # Separator
        self.separator_1 = tk.ttk.Separator(self, orient='horizontal')

        # kuerzel-rechnungsdatum section
        self.frame_1 = customtkinter.CTkFrame(self, fg_color='gray16')
        self.heading_2 = customtkinter.CTkLabel(self.frame_1, text='General', font=small_heading)
        self.kuerzel_label = customtkinter.CTkLabel(self.frame_1, text='Kürzel:')
        self.kuerzel_entry = customtkinter.CTkEntry(self.frame_1, validate='key', validatecommand=(self.register(
            self.kuerzel_entry_validation), '%P'))

        self.frame_1_warning = customtkinter.CTkLabel(self.frame_1, textvariable=self.frame_1_warning_var, text='')

        self.rechnungsdatum_label = customtkinter.CTkLabel(self.frame_1, text='Rechnungsdatum:')
        self.rechnungsdatum_entry = customtkinter.CTkEntry(self.frame_1)
        self.rechnungsdatum_entry.insert(0, f'{time.strftime("%d.%m.%y")}')

        # Separator
        self.separator_2 = tk.ttk.Separator(self, orient='horizontal')

    def create_layout_part_1(self):
        """Creating the layout_part_1 of frame/class KGRechnungInterface"""

        logging.debug('KGRechnungInterface.create_layout_part_1() called')

        # heading section
        self.heading_1.pack(side='top', fill='x', expand=False, pady=(20, 30), padx=20)

        # Separator
        self.separator_1.pack(fill='x', expand=False)

        # kuerzel-rechnungsdatum section
        self.frame_1.grid_columnconfigure(2, weight=1)
        self.frame_1.pack(fill='x', expand=False, pady=15, padx=20)
        self.heading_2.grid(row=0, column=0, padx=10, pady=4, columnspan=2, sticky='w')
        self.kuerzel_label.grid(row=1, column=0, padx=10, pady=4, sticky='w')
        self.kuerzel_entry.grid(row=1, column=1, sticky='w')

        self.frame_1_warning.grid(row=1, column=2, pady=4, sticky='ew')

        self.rechnungsdatum_label.grid(row=1, column=3, padx=10, pady=4)
        self.rechnungsdatum_entry.grid(row=1, column=4, padx=(0, 10), pady=4)

        # Separator
        self.separator_2.pack(fill='x', expand=False)

    def create_widgets_part_2(self):
        """Creating the widgets_part_2 of frame/class KGRechnungInterface"""

        logging.debug('KGRechnungInterface.create_widgets_part_2() called')

        # Daten Eingabe section
        self.frame_2 = customtkinter.CTkFrame(self, fg_color='gray16')
        self.heading_3 = customtkinter.CTkLabel(self.frame_2, text='Rechnungsdaten-Eingabe', font=small_heading)

        self.daten_labels = []
        self.daten_entrys = []
        for i in range(10):
            self.daten_labels.append(customtkinter.CTkLabel(self.frame_2, text=f'Datum {i + 1}:'))
        for i in range(10):
            self.daten_entrys.append(customtkinter.CTkEntry(self.frame_2))

        # Separator
        self.separator_3 = tk.ttk.Separator(self, orient='horizontal')

        # Behandlungsarten section
        self.frame_3 = customtkinter.CTkFrame(self, fg_color='gray16')
        self.heading_4 = customtkinter.CTkLabel(self.frame_3, text='Behandlungsarten', font=small_heading)
        self.behandlungsarten_labels_2d_array = []
        self.behandlungsarten_entrys_2d_array = []

        self.behandlungsarten_add_button = customtkinter.CTkButton(self.frame_3, text='Hinzufügen',
                                                                   command=lambda: self.behandlungsarten_add_event())
        self.behandlungsarten_delete_button = customtkinter.CTkButton(self.frame_3, text='Löschen',
                                                                      command=lambda:
                                                                      self.behandlungsarten_delete_button_event(),
                                                                      state='disabled')

    def create_layout_part_2(self):
        """Creating the layout_part_2 of frame/class KGRechnungInterface"""

        logging.debug('KGRechnungInterface.create_layout_part_2() called')

        # Daten Eingabe section
        self.frame_2.grid_columnconfigure(3, weight=1)

        self.frame_2.pack(fill='x', expand=False, pady=15, padx=20)
        self.heading_3.grid(row=0, column=0, padx=10, pady=4, columnspan=2, sticky='w')
        for index_1, i in enumerate(self.daten_layout):
            for index_2, a in enumerate(i):
                self.daten_labels[a - 1].grid(row=index_1 + 1, column=index_2 + index_2, padx=(10, 0), pady=4, sticky='w')
                self.daten_entrys[a - 1].grid(row=index_1 + 1, column=index_2 + index_2 + 1, padx=(0, 10), pady=4,
                                              sticky='w')

        # Separator
        self.separator_3.pack(fill='x', expand=False)

        # Behandlungsarten section

        self.frame_3.pack(fill='x', expand=False, pady=15, padx=20)
        self.heading_4.grid(row=0, column=0, padx=10, pady=4, columnspan=2, sticky='w')

        self.behandlungsarten_add_button.grid(row=1, column=0, padx=10, pady=(20, 30))
        self.behandlungsarten_delete_button.grid(row=1, column=1, padx=10, pady=(20, 30), sticky='w')

    def kuerzel_entry_validation(self, text_after_action: str) -> bool:
        """validating the changes made to kuerzel_entry widgets on keystroke.
           Params:
                text_after_action: str (text in the entry)"""

        logging.debug(f'KGRechnungInterface.kuerzel_entry_validation() called')

        def clear_kgrechnung_widgets():
            """unpacking and destroying the widgets_part_2"""

            logging.debug('KGRechnungInterface.kuerzel_entry_validation.clear_kgrechnung_widgets() called')

            self.parent.bottom_nav.bottom_nav_button.configure(state='disabled')
            self.parent.bottom_nav.bottom_nav_button_2.configure(state='disabled')
            self.parent.bottom_nav.bottom_nav_warning.configure(text='', fg_color='transparent')
            self.frame_1_warning_var.set('')

            try:
                self.separator_3.pack_forget()
                self.separator_3.destroy()
                self.frame_2.pack_forget()
                self.frame_2.destroy()
                self.frame_3.pack_forget()
                self.frame_3.destroy()
                self.daten_entrys.clear()
                self.behandlungsarten_entrys_2d_array.clear()
                self.row_count = 0
            except AttributeError:
                pass

        # checking if draft can and should be stored
        if not self.parent.store_draft():
            return False

        # entry can't be kuerzel (len() < 4). Letting change pass
        if len(text_after_action) < 4:
            logging.debug('kuerzel len < 4, letting change pass')
            if 'Success' in self.frame_1_warning_var.get():
                self.frame_1_warning_var.set('')
            clear_kgrechnung_widgets()
            return True

        # entry can't be kuerzel (len() > 4). Letting change pass
        elif len(text_after_action) > 4:
            logging.debug('kuerzel len > 4, not letting change pass')
            return False

        # entry could be kuerzel. checking if stammdatei from kuerzel exists
        elif len(text_after_action) == 4:
            logging.debug('kuerzel len == 4')

            if os.path.exists(f'{self.parent.stammdaten_location}/{text_after_action.upper()}.txt'):
                logging.info(f'stammdatei "{text_after_action}.txt" exists')
                with open(f'{self.parent.stammdaten_location}/{text_after_action}.txt', 'r') as f:
                    stammdaten = f.readlines()
                    for i, line in enumerate(stammdaten):
                        stammdaten[i] = line.replace('\n', '')

                self.frame_1_warning_var.set(f'Stammdatei gefunden!')
                self.frame_1_warning.configure(text_color='green')

                self.create_widgets_part_2()
                self.create_layout_part_2()
                self.parent.bottom_nav.bottom_nav_button.configure(state='normal')
                self.parent.bottom_nav.bottom_nav_button_2.configure(state='normal')

                return True

            else:
                logging.info(f'stammdatei "{text_after_action}.txt" doesnt exist')
                clear_kgrechnung_widgets()
                self.frame_1_warning_var.set(f'Stammdatei nicht gefunden!')
                self.frame_1_warning.configure(text_color='red')

                return True

    def behandlungsarten_add_event(self):
        """Adds 1 row to behandlungsarten. Exception: behandlungsarten_limiter is True and
           behdndlungsarten_limit is reached"""

        logging.debug(f'KGRechnungInterface.behandlungsarten_add_button_event() called')

        self.row_count += 1

        # checking if Exception is met
        if self.parent.behandlungsarten_limiter:
            if self.row_count == int(self.parent.behandlungsarten_limit):
                logging.info('max amount of "Behandlungsarten" reached')
                self.behandlungsarten_add_button.configure(state='disabled')

        self.behandlungsarten_labels_1d_array = []
        self.behandlungsarten_entrys_1d_array = []

        # creating widgets
        self.behandlungsarten_labels_1d_array.append(
            customtkinter.CTkLabel(self.frame_3, text=f'Behandlungsart {self.row_count}:'))
        self.behandlungsarten_entrys_1d_array.append(customtkinter.CTkEntry(self.frame_3, width=500))
        self.behandlungsarten_labels_1d_array.append(
            customtkinter.CTkLabel(self.frame_3, text='Einzelpreis:'))
        self.behandlungsarten_entrys_1d_array.append(customtkinter.CTkEntry(self.frame_3))

        self.behandlungsarten_labels_2d_array.append(self.behandlungsarten_labels_1d_array)
        self.behandlungsarten_entrys_2d_array.append(self.behandlungsarten_entrys_1d_array)

        # creating layout
        for index_1, i in enumerate(self.behandlungsarten_labels_2d_array):
            if index_1 == self.row_count - 1:
                for index_2, a in enumerate(i):
                    if index_2 == 0:
                        a.grid(row=int(self.row_count), column=int(index_2), padx=10, pady=4, sticky='w')
                    else:
                        a.grid(row=int(self.row_count), column=int(index_2 + 2), padx=10, pady=4)

        for index_1, i in enumerate(self.behandlungsarten_entrys_2d_array):
            if index_1 == self.row_count - 1:
                for index_2, a in enumerate(i):
                    if index_2 == 0:
                        a.grid(row=int(self.row_count), column=int(index_2 + 1), padx=10, pady=4)
                    else:
                        a.grid(row=int(self.row_count), column=int(index_2 + 3), padx=10, pady=4,
                               sticky='w')

        self.behandlungsarten_add_button.grid(row=self.row_count + 1, column=0, padx=10, pady=(20, 30))

        # repacking and configuring add and delete button
        self.behandlungsarten_delete_button.configure(state='normal')
        self.behandlungsarten_delete_button.grid(row=self.row_count + 1, column=1, padx=10, pady=(20, 30),
                                                 sticky='w')

    def behandlungsarten_delete_button_event(self):
        """Deletes 1 row of behandlungsarten. Exception: row_count is 0"""

        logging.debug(f'KGRechnungInterface.behandlungsarten_delete_button_event() called')

        self.row_count -= 1

        # checking if Exception is met
        if self.row_count == 0:
            logging.info('min amount of "Behandlungsarten" reached')
            self.behandlungsarten_delete_button.configure(state='disabled')

        # destroying widgets and unpacking
        for i in self.behandlungsarten_labels_2d_array[-1]:
            i.grid_forget()

        for i in self.behandlungsarten_entrys_2d_array[-1]:
            i.grid_forget()

        self.behandlungsarten_labels_2d_array.pop(-1)
        self.behandlungsarten_entrys_2d_array.pop(-1)

        # configuring add button
        self.behandlungsarten_add_button.configure(state='normal')

    def kg_rechnung_erstellen_button_event(self):
        """triggers the class Backend and the function of validate_kg_entrys of Backend.
           Checks the return value."""

        logging.debug('KGRechnungInterface.kg_rechnung_erstellen_button_event() called')

        # KG Rechnung erstellt
        if Backend(self, kuerzel=self.kuerzel_entry, rechnungsdatum=self.rechnungsdatum_entry,
                dates=self.daten_entrys,
                behandlungsarten=self.behandlungsarten_entrys_2d_array).validate_kg_entrys():

            self.kuerzel_entry.delete(0, tk.END)
            self.rechnungsdatum_entry.delete(0, tk.END)
            self.rechnungsdatum_entry.insert(0, f'{time.strftime("%d.%m.%y")}')
            self.parent.bottom_nav.bottom_nav_warning.configure(
                text=f'Rechnung erstellt und Daten gespeichert!', fg_color='green')
        # KG Rechnung nicht erstellt
        else:
            return False

    def insert_data(self, data: list):
        """Inserts the data given into the KGRechnungInterface.
                Params: data: list = data out of rechnungen-*.csv or *-DRAFT-*.csv"""

        logging.debug(f'KGRechnungInterface.insert_data() called')

        # inserts the given kuerzel and rechnungsdatum into the KGRechnungInterface
        self.kuerzel_entry.insert(0, data[0])
        self.rechnungsdatum_entry.delete(0, tk.END)
        self.rechnungsdatum_entry.insert(0, f'{data[1][4:6]}.{data[1][6:8]}.{data[1][8:10]}')

        # inserts the rechnungsdaten into the KGRechnungInterface
        for index, i in enumerate(data[8:18]):
            self.daten_entrys[index].insert(0, i)

        # checks the amount of given entrys of behandlungsarten
        row_count = int(len(data[18:]) / 2)

        # runs the behandlungsarten_add_event() for the amounf of behandlungsarten
        while True:
            if row_count != 0:
                self.behandlungsarten_add_event()
                row_count -= 1
                continue
            else:
                break

        # inserts the behandlungsart and einzelpreis into the created rows
        for index_1, i in enumerate(self.behandlungsarten_entrys_2d_array):
            for index_2, a in enumerate(i):
                if index_2 == 0:
                    a.insert(0, data[18 + index_1])
                else:
                    a.insert(0, data[18 + index_1 + int(len(data[18:]) / 2)])


class HPRechnungInterface(customtkinter.CTkScrollableFrame):
    """Creating the HPRechnungInterface frame and widgets_part_1"""

    row_count = 1

    def __init__(self, parent):
        super().__init__(parent)

        logging.info('class HPRechnungInterface() called')

        self.parent = parent
        self.parent.bottom_nav.bottom_nav_button.configure(command=lambda: print('Creating HP Rechnung'))

        self.configure(fg_color='gray16', corner_radius=0)

        self.place(relx=0.2, y=0, relwidth=0.8, relheight=0.90)

        # text variables
        self.frame_1_warning_var = tk.StringVar()

        self.create_widgets_part_1()
        self.create_layout_part_1()

    def create_widgets_part_1(self):
        """Creating the widgets_part_1 of frame/class HPRechnungInterface"""

        logging.debug('HPRechnungInterface.create_widgets_part_1() called')

        # heading section
        self.heading_1 = customtkinter.CTkLabel(self, text='Neue HP Rechnung', font=large_heading)

        # Separator
        self.separator_1 = tk.ttk.Separator(self, orient='horizontal')

        # kuerzel-rechnungsdatum section
        self.frame_1 = customtkinter.CTkFrame(self, fg_color='gray16')
        self.heading_2 = customtkinter.CTkLabel(self.frame_1,
                                                text='General', font=small_heading)
        self.kuerzel_label = customtkinter.CTkLabel(self.frame_1, text='Kürzel:')
        self.kuerzel_entry = customtkinter.CTkEntry(self.frame_1, validate='key', validatecommand=(
            self.register(self.kuerzel_entry_validation), '%P'))

        self.frame_1_warning = customtkinter.CTkLabel(self.frame_1, textvariable=self.frame_1_warning_var, text='')

        self.rechnungsdatum_label = customtkinter.CTkLabel(self.frame_1,
                                                           text='Rechnungsdatum:')
        self.rechnungsdatum_entry = customtkinter.CTkEntry(self.frame_1)
        self.rechnungsdatum_entry.insert(0, f'{time.strftime("%d.%m.%y")}')

        # Separator
        self.separator_2 = tk.ttk.Separator(self, orient='horizontal')

    def create_layout_part_1(self):
        """Creating the layout_part_1 of frame/class HPRechnungInterface"""

        logging.debug('HPRechnungInterface.create_layout_part_1() called')

        # heading section
        self.heading_1.pack(side='top', fill='x', expand=False, pady=(20, 30), padx=20)

        # Separator
        self.separator_1.pack(fill='x', expand=False)

        # kuerzel-rechnungsdatum section
        self.frame_1.grid_columnconfigure(2, weight=1)
        self.frame_1.pack(fill='x', expand=False, pady=(15, 15), padx=20)
        self.heading_2.grid(row=0, column=0, padx=10, pady=4, columnspan=2, sticky='w')
        self.kuerzel_label.grid(row=1, column=0, padx=10, pady=4, sticky='w')
        self.kuerzel_entry.grid(row=1, column=1, pady=4, sticky='w')

        self.frame_1_warning.grid(row=1, column=2, sticky='ew')

        self.rechnungsdatum_label.grid(row=1, column=3, padx=10, pady=4, )
        self.rechnungsdatum_entry.grid(row=1, column=4, padx=(0, 10), pady=4, )

        # Separator
        self.separator_2.pack(fill='x', expand=False)

    def create_widgets_part_2(self):
        """Creating the widgets_part_2 of frame/class HPRechnungInterface"""

        logging.debug(f'HPRechnungInterface.create_widgets_part_2() called')

        # Behandlungsarten section
        self.frame_2 = customtkinter.CTkFrame(self, fg_color='gray16')
        self.heading_3 = customtkinter.CTkLabel(self.frame_2, text='Behandlungsdaten', font=small_heading)

        # row frames
        self.row_frames = []

        # table buttons frame
        self.row_frames.append(customtkinter.CTkFrame(self.frame_2, corner_radius=0, fg_color='gray16'))

        # table buttons widgets
        self.behandlungsdaten_add_button = customtkinter.CTkButton(self.row_frames[0], text='Hinzufügen',
                                                                   command=lambda: self.behandlungsdaten_add_button_event())
        self.behandlungsdaten_delete_button = customtkinter.CTkButton(self.row_frames[0], text='Löschen',
                                                                      state='disabled',
                                                                      command=lambda: self.behandlungsdaten_delete_button_event())

        # row widgets
        self.rows_2d_array = []

        # table header row
        self.row_frames.append(customtkinter.CTkFrame(self.frame_2, corner_radius=0, fg_color='gray16'))
        self.rows_2d_array.append([customtkinter.CTkLabel(self.row_frames[1], text='Datum', width=80),
                                   tk.ttk.Separator(self.row_frames[1], orient='vertical'),
                                   customtkinter.CTkLabel(self.row_frames[1], text='Ziffer', width=60),
                                   tk.ttk.Separator(self.row_frames[1], orient='vertical'),
                                   customtkinter.CTkLabel(self.row_frames[1], text='Art der Behandlung'),
                                   tk.ttk.Separator(self.row_frames[1], orient='vertical'),
                                   customtkinter.CTkLabel(self.row_frames[1], text='Betrag in €', width=80),
                                   tk.ttk.Separator(self.row_frames[1], orient='horizontal')])

        # table row 1
        self.row_frames.append(customtkinter.CTkFrame(self.frame_2, corner_radius=0, fg_color='gray16'))
        self.rows_2d_array.append([customtkinter.CTkTextbox(self.row_frames[2], width=80, height=150),
                                   tk.ttk.Separator(self.row_frames[2], orient='vertical'),
                                   customtkinter.CTkTextbox(self.row_frames[2], width=60, height=150),
                                   tk.ttk.Separator(self.row_frames[2], orient='vertical'),
                                   customtkinter.CTkTextbox(self.row_frames[2], height=150),
                                   tk.ttk.Separator(self.row_frames[2], orient='vertical'),
                                   customtkinter.CTkTextbox(self.row_frames[2], width=80, height=150),
                                   tk.ttk.Separator(self.row_frames[2], orient='horizontal')])

        # Separator
        self.separator_3 = tk.ttk.Separator(self, orient='horizontal')

        # Diagnose section
        self.frame_3 = customtkinter.CTkFrame(self, corner_radius=0, fg_color='gray16')
        self.heading_4 = customtkinter.CTkLabel(self.frame_3, text='Diagnose', font=small_heading)
        self.diagnose_label = customtkinter.CTkLabel(self.frame_3, text='Diagnose:')
        self.diagnose_textbox = customtkinter.CTkTextbox(self.frame_3, height=60)

    def create_layout_part_2(self):
        """Creating the layout_part_2 of frame/class HPRechnungInterface"""

        logging.debug(f'HPRechnungInterface.create_layout_part_2() called')

        # Behandlungsarten section
        self.frame_2.pack(fill='x', expand=False, pady=(15, 15), padx=20)
        self.frame_2.grid_columnconfigure(0, weight=1)
        self.heading_3.grid(row=0, column=0, padx=10, pady=4, sticky='w')

        # packing table buttons
        self.behandlungsdaten_add_button.grid(row=0, column=0, padx=(0, 10), pady=(20, 30), sticky='w')
        self.behandlungsdaten_delete_button.grid(row=0, column=1, padx=10, pady=(20, 30), sticky='w')

        # pack the widgets into the frames
        for index_1, i in enumerate(self.rows_2d_array):
            for index_2, a in enumerate(i):
                if index_2 == 0:
                    a.grid(row=0, column=index_2, padx=0, pady=0)
                elif index_2 == 4:
                    a.grid(row=0, column=index_2, padx=0, pady=0, sticky='ew')
                elif index_2 == 6:
                    a.grid(row=0, column=index_2, padx=0, pady=0)
                elif (index_2 == 1 or index_2 == 3 or index_2 == 5) and index_2 == 0:
                    a.grid(row=0, column=index_2, padx=0, pady=(4, 0), sticky='ns')
                elif (index_2 == 1 or index_2 == 3 or index_2 == 5) and index_2 != 0:
                    a.grid(row=0, column=index_2, padx=0, pady=0, sticky='ns')
                elif index_2 == 2 or index_2 == 8:
                    a.grid(row=0, column=index_2, padx=0, pady=0)
                elif index_2 == 7 and index_1 == 0:
                    a.grid(row=1, column=0, padx=5, pady=0, columnspan=7, sticky='ew')

        # pack the frames onto HPRechnungInterface frame
        for index, i in enumerate(self.row_frames):
            if not index == 0:
                i.grid_columnconfigure(4, weight=1)
                i.grid(row=index + 1, column=0, padx=10, pady=0, sticky='ew')
            elif index == 1:
                i.grid_columnconfigure(4, weight=1)
                i.grid(row=index + 1, column=0, padx=10, pady=(4, 0), sticky='ew')
            else:
                i.grid(row=len(self.row_frames) + 1, column=0, padx=10, pady=0, sticky='ew')

        # Separator
        self.separator_3.pack(fill='x', expand=False)

        # Diagnose section
        self.frame_3.grid_columnconfigure(1, weight=1)
        self.frame_3.pack(fill='x', expand=False, pady=(15, 15), padx=20)
        self.heading_4.grid(row=0, column=0, padx=10, pady=4, columnspan=2, sticky='w')
        self.diagnose_textbox.grid(row=1, column=1, padx=10, pady=4, sticky='ew')

    def kuerzel_entry_validation(self, text_after_action):
        """validating the changes made to kuerzel_entry widgets on keystroke.
                   Params:
                        text_after_action: str (text in the entry)"""

        logging.debug(f'HPRechnungInterface.kuerzel_entry_validation() called')

        def clear_hprechnung_widgets():
            """unpacking and destroying the widgets_part_2 and widgets_part_3"""

            logging.debug('HPRechnungInterface.kuerzel_entry_validation.clear_kgrechnung_widgets() called')

            self.parent.bottom_nav.bottom_nav_button.configure(state='disabled')
            self.parent.bottom_nav.bottom_nav_button_2.configure(state='disabled')
            self.parent.bottom_nav.bottom_nav_warning.configure(text='', fg_color='transparent')
            self.frame_1_warning_var.set('')

            try:
                self.frame_2.destroy()
            except AttributeError:
                pass
            try:
                self.frame_3.destroy()
                self.separator_3.destroy()
            except AttributeError:
                pass

        # checking if draft can and should be stored
        if not self.parent.store_draft():
            return False

        # entry can't be kuerzel (len() < 4). Letting change pass
        if len(text_after_action) < 4:
            logging.debug('kuerzel len < 4, letting change pass')
            if 'Success' in self.frame_1_warning_var.get():
                self.frame_1_warning_var.set('')
            clear_hprechnung_widgets()
            return True

        # entry can't be kuerzel (len() > 4). Letting change pass
        elif len(text_after_action) > 4:
            logging.debug('kuerzel len > 4, not letting change pass')
            return False

        # entry could be kuerzel. checking if stammdatei from kuerzel exists
        elif len(text_after_action) == 4:
            logging.debug('kuerzel len == 4')

            if os.path.exists(f'{self.parent.stammdaten_location}/{text_after_action.upper()}.txt'):
                logging.info(f'stammdatei "{text_after_action}.txt" exists')
                with open(f'{self.parent.stammdaten_location}/{text_after_action}.txt', 'r') as f:
                    stammdaten = f.readlines()
                    for i, line in enumerate(stammdaten):
                        stammdaten[i] = line.replace('\n', '')

                self.frame_1_warning_var.set(f'Stammdatei gefunden!')
                self.frame_1_warning.configure(text_color='green')

                self.create_widgets_part_2()
                self.create_layout_part_2()
                self.parent.bottom_nav.bottom_nav_button.configure(state='normal')
                self.parent.bottom_nav.bottom_nav_button_2.configure(state='normal')
                return True

            else:
                logging.info(f'stammdatei "{text_after_action}.txt" doesnt exist')
                clear_hprechnung_widgets()
                self.frame_1_warning_var.set(f'Stammdatei nicht gefunden!')
                self.frame_1_warning.configure(text_color='red')
                return True

    def behandlungsdaten_add_button_event(self):
        """Adds 1 row to behandlungsdaten"""

        logging.debug(f'HPRechnungInterface.behandlungsdaten_add_button_event() called')

        self.row_count += 1

        # configuring delete button to normal
        self.behandlungsdaten_delete_button.configure(state='normal')

        # adds frame to row frames
        self.row_frames.append(customtkinter.CTkFrame(self.frame_2, corner_radius=0, fg_color='gray16'))

        # adds the widgets to row widgets
        self.rows_2d_array.append(
            [customtkinter.CTkTextbox(self.row_frames[len(self.row_frames) - 1], width=80, height=150),
             tk.ttk.Separator(self.row_frames[len(self.row_frames) - 1], orient='vertical'),
             customtkinter.CTkTextbox(self.row_frames[len(self.row_frames) - 1], width=60, height=150),
             tk.ttk.Separator(self.row_frames[len(self.row_frames) - 1], orient='vertical'),
             customtkinter.CTkTextbox(self.row_frames[len(self.row_frames) - 1], height=150),
             tk.ttk.Separator(self.row_frames[len(self.row_frames) - 1], orient='vertical'),
             customtkinter.CTkTextbox(self.row_frames[len(self.row_frames) - 1], width=80, height=150),
             tk.ttk.Separator(self.row_frames[len(self.row_frames) - 1], orient='horizontal')])

        # packing the widgets of the last row to the added frame
        for index_2, a in enumerate(self.rows_2d_array[-1]):
            if index_2 == 0:
                a.grid(row=1, column=index_2, padx=0, pady=0, sticky='w')
            elif index_2 == 4:
                a.grid(row=1, column=index_2, padx=0, pady=0, sticky='ew')
            elif index_2 == 6:
                a.grid(row=1, column=index_2, padx=0, pady=0, sticky='e')
            elif index_2 == 1 or index_2 == 3 or index_2 == 5:
                a.grid(row=1, column=index_2, padx=0, pady=0, sticky='ns')
            elif index_2 == 2 or index_2 == 8:
                a.grid(row=1, column=index_2, padx=0, pady=0)
            elif index_2 == 7 and not len(self.row_frames) == 3:
                a.grid(row=0, column=0, padx=5, pady=0, columnspan=7, sticky='ew')

        # repack the button frame
        self.row_frames[0].grid_forget()
        self.row_frames[0].grid(row=len(self.row_frames) + 1, column=0, padx=10, pady=0, sticky='ew')

        # packing the just created row
        self.row_frames[-1].grid_columnconfigure(4, weight=1)
        self.row_frames[-1].grid(row=len(self.row_frames), column=0, padx=10, pady=0, sticky='ew')

    def behandlungsdaten_delete_button_event(self):
        """Deletes 1 row to behandlungsdaten. Exception: row_count is 1"""

        logging.debug(f'HPRechnungInterface.behandlungsdaten_add_button_event() called')

        self.row_count -= 1

        # checking if Exception is met
        if self.row_count == 1:
            self.behandlungsdaten_delete_button.configure(state='disabled')

        # unpacking the row frame
        self.row_frames[-1].grid_forget()
        self.row_frames[-1].destroy()

        # removing row from row_frame
        self.row_frames.pop(-1)


class StammdatenInterface(customtkinter.CTkFrame):
    """Creating the StammdatenInterface frame and widgets_part_1 and
       updating the list for the first time"""

    # Entrys for new Stammdatei
    stammdaten_label_names = ['Kürzel', 'Mann/Frau', 'Nachname', 'Vorname', 'Straße', 'Hausnummer', 'Postleitzahl',
                              'Stadt', 'Geburtsdatum', 'Kilometer', 'Hausarzt', 'Email', 'KG/HP']

    def __init__(self, parent):
        super().__init__(parent)

        logging.info('class StammdatenInterface() called')

        self.parent = parent
        self.parent.bottom_nav.bottom_nav_button.configure(command=lambda: self.create_stammdatei_event())

        self.configure(fg_color='gray16', corner_radius=0)

        self.place(relx=0.2, y=0, relwidth=0.8, relheight=0.90)

        self.create_widgets_part_1()
        self.create_layout_part_1()
        self.aktualisieren_event()

    def create_widgets_part_1(self):
        """Creating the widgets_part_1 of frame/class StammdatenInterface"""

        logging.debug('StammdatenInterface.create_widgets_part_1() called')

        # heading section
        self.heading_1 = customtkinter.CTkLabel(self, text='stammdaten Bearbeiten', font=large_heading)

        # Separator
        self.separator_1 = tk.ttk.Separator(self, orient='horizontal')

        # Filter section
        self.frame_1 = customtkinter.CTkFrame(self, fg_color='gray16')
        self.heading_2 = customtkinter.CTkLabel(self.frame_1, text='Filter', font=small_heading)
        self.search_label = customtkinter.CTkLabel(self.frame_1, text='Suche:')
        self.search_entry = customtkinter.CTkEntry(self.frame_1)
        self.search_entry.bind('<Return>', self.aktualisieren_event)
        self.segmented_button_1 = customtkinter.CTkSegmentedButton(self.frame_1, values=['Alle', 'KG', 'HP'],
                                                                   command=lambda x: self.aktualisieren_event(x))
        self.segmented_button_1.set('Alle')
        self.aktualisieren_button = customtkinter.CTkButton(self.frame_1, width=20, text='suchen',
                                                            image=search_img,
                                                            command=lambda: self.aktualisieren_event())

        # Separator
        self.separator_2 = tk.ttk.Separator(self, orient='horizontal')

    def create_layout_part_1(self):
        """Creating the layout_part_1 of frame/class StammdatenInterface"""

        logging.debug('StammdatenInterface.create_layout_part_1() called')

        # heading section
        self.heading_1.pack(side='top', fill='x', expand=False, pady=(20, 30), padx=20)

        # Separator
        self.separator_1.pack(fill='x', expand=False)

        # Filter section
        self.frame_1.grid_columnconfigure(3, weight=1)
        self.frame_1.pack(fill='x', expand=False, pady=(15, 15), padx=20)
        self.heading_2.grid(row=0, column=0, padx=10, pady=4, columnspan=2, sticky='w')
        self.search_label.grid(row=1, column=0, padx=10, pady=4, sticky='w')
        self.search_entry.grid(row=1, column=1, sticky='w')
        self.segmented_button_1.grid(row=1, column=2, pady=4, padx=10)
        self.aktualisieren_button.grid(row=1, column=4)

        # Separator
        self.separator_2.pack(fill='x', expand=False)

    def create_widgets_part_2(self):
        """Creating the widgets_part_2 of frame/class StammdatenInterface
           -> being called by aktualisieren_event"""

        logging.debug('StammdatenInterface.create_widgets_part_2() called')

        self.frame_2 = customtkinter.CTkScrollableFrame(self, corner_radius=0)

        self.row_frames = []

        # header row
        self.row_frames.append(customtkinter.CTkFrame(self.frame_2, corner_radius=0))
        self.heading_3 = customtkinter.CTkLabel(self.row_frames[0], text='Dateiname', width=120)
        self.separator_3 = tk.ttk.Separator(self.row_frames[0], orient='vertical')
        self.date_added_label = customtkinter.CTkLabel(self.row_frames[0], text='Erstellungsdatum', width=120)
        self.separator_4 = tk.ttk.Separator(self.row_frames[0], orient='vertical')
        self.date_modified_label = customtkinter.CTkLabel(self.row_frames[0], text='Änderungsdatum', width=120)
        self.separator_5 = tk.ttk.Separator(self.row_frames[0], orient='horizontal')
        self.new_stammdatei_button = customtkinter.CTkButton(self.row_frames[0], width=20, text='Neue erstellen',
                                                             command=lambda: self.new_stammdatei_button_event())

        # creating widgets for every file in dir
        self.rows_2d_array = []
        for index, i in enumerate(self.files_in_dir):
            if index % 2 != 0:
                self.row_frames.append(customtkinter.CTkFrame(self.frame_2, corner_radius=0, fg_color='gray25'))
            else:
                self.row_frames.append(customtkinter.CTkFrame(self.frame_2, corner_radius=0))

            row_1d_array = [customtkinter.CTkLabel(self.row_frames[index + 1], width=120,
                                                   text=str(i).replace('.pdf', '')),
                            tk.ttk.Separator(self.row_frames[index + 1], orient='vertical'),
                            customtkinter.CTkLabel(self.row_frames[index + 1], width=120,
                                                   text=str(time.strftime("%d.%m.%y at %H:%M",
                                                                          time.strptime(
                                                                              time.ctime(os.path.getctime(
                                                                                  f'{self.parent.stammdaten_location}/{i}')))))),
                            tk.ttk.Separator(self.row_frames[index + 1], orient='vertical'),
                            customtkinter.CTkLabel(self.row_frames[index + 1], width=120,
                                                   text=str(time.strftime("%d.%m.%y at %H:%M",
                                                                          time.strptime(
                                                                              time.ctime(os.path.getmtime(
                                                                                  f'{self.parent.stammdaten_location}/{i}')))))),
                            customtkinter.CTkLabel(self.row_frames[index + 1], text=''),
                            customtkinter.CTkButton(self.row_frames[index + 1], width=20,
                                                    text='öffnen', image=open_img),
                            customtkinter.CTkButton(self.row_frames[index + 1], width=20,
                                                    text='bearbeiten', image=edit_img),
                            customtkinter.CTkButton(self.row_frames[index + 1], width=20,
                                                    text='löschen', image=trash_img)]

            self.rows_2d_array.append(row_1d_array)

    def create_layout_part_2(self):
        """Creating the layout_part_2 of frame/class StammdatenInterface
           -> being called by aktualisieren_event"""

        logging.debug('StammdatenInterface.create_layout_part_2() called')

        self.frame_2.pack(side='top', fill='both', expand=True, pady=20, padx=20)
        self.frame_2.grid_columnconfigure(0, weight=1)

        # header row widgets
        self.heading_3.grid(row=0, column=0, ipadx=20, ipady=6)
        self.separator_3.grid(row=0, column=1, padx=0, pady=0, rowspan=2, sticky='ns')
        self.date_added_label.grid(row=0, column=2, ipadx=20, ipady=6)
        self.separator_4.grid(row=0, column=3, padx=0, pady=0, rowspan=2, sticky='ns')
        self.date_modified_label.grid(row=0, column=4, ipadx=20, ipady=6)
        self.separator_5.grid(row=1, column=0, padx=0, pady=0, columnspan=9, sticky='ew')
        self.new_stammdatei_button.grid(row=0, column=5, padx=(5, 20), pady=6,
                                        sticky='e')

        # creating layout for created widgets of file in dir
        for index_1, i in enumerate(self.rows_2d_array):
            for index_2, a in enumerate(i):
                if index_2 == 1 or index_2 == 3:
                    a.grid(row=0, column=index_2, padx=0, pady=0, rowspan=2, sticky='ns')
                elif index_2 == 5:
                    a.grid(row=0, column=index_2, ipadx=20, ipady=6, sticky='ew')
                elif index_2 == 6:
                    if self.parent.debug_mode:
                        a.grid(row=0, column=index_2, padx=5, pady=6)
                        a.configure(command=lambda row=index_1: self.open_stammdatei_button_event(
                            row))
                elif index_2 == 7:
                    if self.parent.debug_mode:
                        a.grid(row=0, column=index_2, padx=5, pady=6)
                        a.configure(command=lambda row=index_1: self.edit_stammdatei_button_event(
                            row))
                    else:
                        a.grid(row=0, column=index_2, padx=(5, 20), pady=6)
                        a.configure(command=lambda row=index_1: self.edit_stammdatei_button_event(
                            row))
                elif index_2 == 8:
                    if self.parent.debug_mode:
                        a.grid(row=0, column=index_2, padx=(5, 20), pady=6)
                        a.configure(command=lambda row=index_1: self.delete_stammdatei_button_event(
                            row))
                else:
                    a.grid(row=0, column=index_2, ipadx=20, ipady=6)

        # creating the layout of the row_frames
        for index, i in enumerate(self.row_frames):
            i.grid_columnconfigure(5, weight=1)
            i.grid(row=index, column=0, columnspan=9, sticky='nsew')

    def create_widgets_part_3(self):
        """Creating the widgets_part_3 of frame/class StammdatenInterface
           -> being called when new stammdatei button is pressed"""

        logging.debug('StammdatenInterface.create_widgets_part_3() called')

        self.parent.bottom_nav.bottom_nav_button.configure(state='normal')

        self.frame_3 = customtkinter.CTkFrame(self.parent, fg_color='gray16', corner_radius=0)

        # heading section
        self.heading_4 = customtkinter.CTkLabel(self.frame_3, text='Neue Stammdatei', font=large_heading)

        # Separator
        self.separator_6 = tk.ttk.Separator(self.frame_3, orient='horizontal')

        # placeholder section
        self.frame_4 = customtkinter.CTkFrame(self.frame_3, fg_color='gray16')
        self.heading_5 = customtkinter.CTkLabel(self.frame_4, text='', font=small_heading)
        self.search_label = customtkinter.CTkLabel(self.frame_4, text='')
        self.close_button = customtkinter.CTkButton(self.frame_4, width=20, text='Schließen',
                                                    command=lambda: self.clear_widgets_part_3())

        # Separator
        self.separator_2 = tk.ttk.Separator(self.frame_3, orient='horizontal')

        # stammdatei section
        self.frame_5 = customtkinter.CTkFrame(self.frame_3, corner_radius=0)

        self.stammdaten_labels = []
        self.stammdaten_entrys = []
        for index, i in enumerate(self.stammdaten_label_names):
            self.stammdaten_labels.append(customtkinter.CTkLabel(self.frame_5, text=f'{i}:'))
            self.stammdaten_entrys.append(customtkinter.CTkEntry(self.frame_5))
            if index == 0:
                self.stammdaten_entrys[index].focus_set()
            if index == 11:
                self.stammdaten_entrys[index].configure(width=300)

    def create_layout_part_3(self):
        """Creating the layout_part_3 of frame/class StammdatenInterface
           -> being called when new stammdatei button is pressed"""

        logging.debug('StammdatenInterface.create_layout_part_3() called')

        self.frame_3.place(relx=0.2, y=0, relwidth=0.8, relheight=0.90)

        # heading section
        self.heading_4.pack(side='top', fill='x', expand=False, pady=(20, 30), padx=20)

        # Separator
        self.separator_6.pack(fill='x', expand=False)

        # placeholder section
        self.frame_4.grid_columnconfigure(2, weight=1)
        self.frame_4.pack(fill='x', expand=False, pady=(15, 15), padx=20)
        self.heading_5.grid(row=0, column=0, padx=10, pady=4, columnspan=2, sticky='w')
        self.search_label.grid(row=1, column=0, padx=10, pady=4, sticky='w')
        self.close_button.grid(row=1, column=4, sticky='w')
        self.separator_2.pack(side='top', fill='x', expand=False)

        # stammdatei section
        self.frame_5.grid_columnconfigure(5, weight=1)
        self.frame_5.pack(side='top', fill='both', expand=True, pady=20, padx=20)

        for index, i in enumerate(self.stammdaten_label_names):
            if index < 6:
                self.stammdaten_entrys[index].grid(row=index, column=1, padx=(10, 10), pady=(8, 0))
                self.stammdaten_labels[index].grid(row=index, column=0, padx=(20, 10), pady=(8, 0), sticky='w')
            else:
                self.stammdaten_labels[index].grid(row=index - 6, column=2, padx=(40, 10), pady=(8, 0), sticky='w')
                self.stammdaten_entrys[index].grid(row=index - 6, column=3, padx=(10, 10), pady=(8, 0), sticky='w')

    def clear_widgets_part_3(self):
        """Clears the frame to create a new stammdatei
           -> being called when close button is pressed"""

        logging.debug('StammdatenInterface.clear_widgets_part_3() called')

        self.parent.bottom_nav.bottom_nav_button.configure(state='disabled')

        self.frame_3.place_forget()
        self.frame_3.destroy()
        self.aktualisieren_event()

    def aktualisieren_event(self, *args):
        """is responsible to fetch and prepare the name of the files in dir.
           Updates the widgets and layout part_2"""

        logging.debug('StammdatenInterface.aktualisieren_event() called')

        def destroy_frame():
            """destroys the widgets and layout part_2"""

            logging.debug('StammdatenInterface.aktualisieren_event.destroy_frame() called')

            try:
                self.frame_2.pack_forget()
                self.frame_2.destroy()
            except AttributeError:
                pass

        def create_frame():
            """runs the create widgets and layout part_2 functions"""

            logging.debug('StammdatenInterface.aktualisieren_event.create_frame() called')

            self.create_widgets_part_2()
            self.create_layout_part_2()
            self.parent.focus_set()

        # fetches names of files in dir
        self.files_in_dir = []
        self.files_in_dir_unsorted = os.listdir(f'{self.parent.stammdaten_location}/')

        # checks if file meets filter criteria
        for index, i in enumerate(self.files_in_dir_unsorted):
            if i == '.DS_Store':
                continue
            if self.segmented_button_1.get() == 'Alle':
                with open(f'{self.parent.stammdaten_location}/{i}', 'r') as f:
                    f = f.readlines()
                    for a in f:
                        if self.search_entry.get() in a or self.search_entry.get() in i:
                            self.files_in_dir.append(i)
                            break
            elif self.segmented_button_1.get() == 'KG':
                with open(f'{self.parent.stammdaten_location}/{i}', 'r') as f:
                    f = f.readlines()
                    for a in f:
                        try:
                            if f[12].replace('\n', '') == 'KG' and (
                                    self.search_entry.get() in a or self.search_entry.get() in i):
                                self.files_in_dir.append(i)
                                break
                        except IndexError:
                            pass
            elif self.segmented_button_1.get() == 'HP':
                with open(f'{self.parent.stammdaten_location}/{i}', 'r') as f:
                    f = f.readlines()
                    for a in f:
                        try:
                            if f[12].replace('\n', '') == 'HP' and (
                                    self.search_entry.get() in a or self.search_entry.get() in i):
                                self.files_in_dir.append(i)
                                break
                        except IndexError:
                            pass

        # sorts the filenames alphabetically
        self.files_in_dir.sort()

        destroy_frame()
        create_frame()

    def open_stammdatei_button_event(self, row):
        """being called when open button of specific file is pressed and
           opens the respective file."""

        logging.debug(f'StammdatenInterface.open_stammdatei_button_event() called, row={row}')

        Backend(self).open_file(f'{self.parent.stammdaten_location}/{self.files_in_dir[row]}')

    def edit_stammdatei_button_event(self, row):
        """being called when edit button of specific file is pressed. Runs create
           widgets and layout part_3 and inserts saved values into entries."""

        logging.debug(f'StammdatenInterface.edit_stammdatei_button_event() called, row={row}')

        self.create_widgets_part_3()
        self.create_layout_part_3()

        # inserts the values in the entries
        filepath = f'{self.parent.stammdaten_location}/{self.files_in_dir[row]}'
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                f = f.readlines()
                for i in range(13):
                    try:
                        self.stammdaten_entrys[i].insert(0, f[i].replace('\n', ''))
                    except IndexError:
                        logging.info(f'stammdatei {self.files_in_dir[row]} corrupt')
                        break

    def delete_stammdatei_button_event(self, row):
        """being called when delete button of specific file is pressed and
           deletes the respective file. After it calls the aktualisieren event."""

        logging.debug(f'StammdatenInterface.delete_stammdaeti_button_event() called, row={row}')

        filepath = f'{self.parent.stammdaten_location}/{self.files_in_dir[row]}'

        Backend(self).clean_remove(filepath, self.files_in_dir[row])

        self.aktualisieren_event()

    def new_stammdatei_button_event(self):
        """being called when new stammdatei button is pressed and calls function to
           create widgets and layout part_3."""

        logging.debug(f'StammdatenInterface.new_stammdatei_button_event() called')

        self.create_widgets_part_3()
        self.create_layout_part_3()

    def create_stammdatei_event(self):
        """being called when save button is pressed. Passes the data from entries
           to Backend and validates them"""

        if Backend(self, stammdaten=self.stammdaten_entrys).validate_stammdaten_entrys():
            self.clear_widgets_part_3()


class RechnungLoeschenInterface(customtkinter.CTkFrame):
    """Creating the RechnungLoeschenInterface frame and widgets_part_1 and
       updating the list for the first time"""

    def __init__(self, parent):
        super().__init__(parent)

        logging.info('class KGRechnungInterface() called')

        self.parent = parent
        self.parent.bottom_nav.bottom_nav_button.configure()

        self.configure(fg_color='gray16', corner_radius=0)

        self.place(relx=0.2, y=0, relwidth=0.8, relheight=0.90)

        self.create_widgets_part_1()
        self.create_layout_part_1()
        self.aktualisieren_event()

    def create_widgets_part_1(self):
        """Creating the widgets_part_1 of frame/class RechnungLoeschenInterface"""

        logging.debug('RechnungLoeschenInterface.create_widgets_part_1() called')

        # heading section
        self.heading_1 = customtkinter.CTkLabel(self, text='rechnungen Bearbeiten', font=large_heading)

        # Separator
        self.separator_1 = tk.ttk.Separator(self, orient='horizontal')

        # Filter
        self.frame_1 = customtkinter.CTkFrame(self, fg_color='gray16')
        self.heading_2 = customtkinter.CTkLabel(self.frame_1,
                                                text='Filter', font=small_heading)
        self.search_label = customtkinter.CTkLabel(self.frame_1, text='Suche:')
        self.search_entry = customtkinter.CTkEntry(self.frame_1)

        self.segmented_button_1 = customtkinter.CTkSegmentedButton(self.frame_1,
                                                                   values=['Alle', 'KG', 'HP', 'Entwürfe'],
                                                                   command=lambda x: self.aktualisieren_event(x))
        self.segmented_button_1.set('Alle')
        self.aktualisieren_button = customtkinter.CTkButton(self.frame_1, width=20, text='suchen',
                                                            image=search_img,
                                                            command=lambda: self.aktualisieren_event())

        # Separator
        self.separator_2 = tk.ttk.Separator(self, orient='horizontal')

    def create_layout_part_1(self):
        """Creating the layout_part_1 of frame/class RechnungLoeschenInterface"""

        logging.debug('RechnungLoeschenInterface.create_layout_part_1() called')

        # heading section
        self.heading_1.pack(side='top', fill='x', expand=False, pady=(20, 30), padx=20)

        # Separator
        self.separator_1.pack(fill='x', expand=False)

        # Filter section
        self.frame_1.grid_columnconfigure(3, weight=1)
        self.frame_1.pack(fill='x', expand=False, pady=(15, 15), padx=20)
        self.heading_2.grid(row=0, column=0, padx=10, pady=4, columnspan=2, sticky='w')
        self.search_label.grid(row=1, column=0, padx=10, pady=4, sticky='w')
        self.search_entry.grid(row=1, column=1, sticky='w')
        self.segmented_button_1.grid(row=1, column=2, pady=4, padx=10)
        self.aktualisieren_button.grid(row=1, column=4)

        # Separator
        self.separator_2.pack(fill='x', expand=False)

    def create_widgets_part_2(self, basepath):
        """Creating the widgets_part_2 of frame/class RechnungLoeschenInterface
           -> being called by aktualisieren_event"""

        logging.debug('StammdatenInterface.create_widgets_part_2() called')

        self.frame_2 = customtkinter.CTkScrollableFrame(self, corner_radius=0)

        self.row_frames = []

        # header row
        self.row_frames.append(customtkinter.CTkFrame(self.frame_2, corner_radius=0))
        self.heading_3 = customtkinter.CTkLabel(self.row_frames[0], text='Dateiname', width=160)
        self.separator_3 = tk.ttk.Separator(self.row_frames[0], orient='vertical')
        self.date_added_label = customtkinter.CTkLabel(self.row_frames[0], text='Erstellungsdatum', width=120)
        self.separator_4 = tk.ttk.Separator(self.row_frames[0], orient='vertical')
        self.date_modified_label = customtkinter.CTkLabel(self.row_frames[0], text='Änderungsdatum', width=120)
        self.separator_5 = tk.ttk.Separator(self.row_frames[0], orient='horizontal')

        # creating widgets for every file in dir
        self.rows_2d_array = []
        for index, i in enumerate(self.files_in_dir):
            if index % 2 != 0:
                self.row_frames.append(customtkinter.CTkFrame(self.frame_2, corner_radius=0, fg_color='gray25'))
            else:
                self.row_frames.append(customtkinter.CTkFrame(self.frame_2, corner_radius=0))

            row_1d_array = [customtkinter.CTkLabel(self.row_frames[index + 1], width=160,
                                                   text=str(i).replace('.pdf', '')),
                            tk.ttk.Separator(self.row_frames[index + 1], orient='vertical'),
                            customtkinter.CTkLabel(self.row_frames[index + 1], width=120,
                                                   text=str(time.strftime("%d.%m.%y at %H:%M",
                                                                          time.strptime(
                                                                              time.ctime(os.path.getctime(
                                                                                  f'{basepath}'
                                                                                  f'{i}')))))),
                            tk.ttk.Separator(self.row_frames[index + 1], orient='vertical'),
                            customtkinter.CTkLabel(self.row_frames[index + 1], width=120,
                                                   text=str(time.strftime("%d.%m.%y at %H:%M",
                                                                          time.strptime(
                                                                              time.ctime(os.path.getmtime(
                                                                                  f'{basepath}'
                                                                                  f'{i}')))))),
                            customtkinter.CTkLabel(self.row_frames[index + 1], text=''),
                            customtkinter.CTkButton(self.row_frames[index + 1], width=20,
                                                    text='öffnen', image=open_img),
                            customtkinter.CTkButton(self.row_frames[index + 1], width=20,
                                                    text='bearbeiten', image=edit_img),
                            customtkinter.CTkButton(self.row_frames[index + 1], width=20,
                                                    text='löschen', image=trash_img)]

            self.rows_2d_array.append(row_1d_array)

    def create_layout_part_2(self, basepath, draft):
        """Creating the layout_part_2 of frame/class RechnungLoeschenInterface
           -> being called by aktualisieren_event"""

        logging.debug('StammdatenInterface.create_layout_part_2() called')

        self.frame_2.pack(side='top', fill='both', expand=True, pady=20, padx=20)
        self.frame_2.grid_columnconfigure(0, weight=1)

        # header row widgets
        self.heading_3.grid(row=0, column=0, ipadx=20, ipady=6, sticky='w')
        self.separator_3.grid(row=0, column=1, padx=0, pady=0, rowspan=2, sticky='ns')
        self.date_added_label.grid(row=0, column=2, ipadx=20, ipady=6)
        self.separator_4.grid(row=0, column=3, padx=0, pady=0, rowspan=2, sticky='ns')
        self.date_modified_label.grid(row=0, column=4, ipadx=20, ipady=6)
        self.separator_5.grid(row=1, column=0, padx=0, pady=0, columnspan=9, sticky='ew')

        # creating layout for created widgets of file in dir
        for index_1, i in enumerate(self.rows_2d_array):
            for index_2, a in enumerate(i):
                if index_2 == 1 or index_2 == 3:
                    a.grid(row=0, column=index_2, padx=0, pady=0, rowspan=2, sticky='ns')
                elif index_2 == 5:
                    a.grid(row=0, column=index_2, ipadx=20, ipady=6, sticky='ew')
                elif index_2 == 6:
                    if not draft or self.parent.debug_mode:
                        a.grid(row=0, column=index_2, padx=5, pady=6)
                        a.configure(command=lambda row=index_1: self.open_rechnung_button_event(
                            row, basepath))
                    else:
                        continue
                elif index_2 == 7:
                    a.grid(row=0, column=index_2, padx=5, pady=6)
                    a.configure(command=lambda row=index_1: self.edit_rechnung_button_event(
                        row, basepath, draft))
                elif index_2 == 8:
                    a.grid(row=0, column=index_2, padx=(5, 20), pady=6)
                    a.configure(command=lambda row=index_1: self.delete_rechnung_button_event(
                        row, basepath))
                else:
                    a.grid(row=0, column=index_2, ipadx=20, ipady=6, sticky='w')

        # creating the layout of the row_frames
        for index, i in enumerate(self.row_frames):
            i.grid_columnconfigure(5, weight=1)
            i.grid(row=index, column=0, columnspan=9, sticky='nsew')

    def aktualisieren_event(self, *args):
        """is responsible to fetch and prepare the name of the files in dir.
           Updates the widgets and layout part_2"""

        logging.debug('StammdatenInterface.aktualisieren_event() called')

        def destroy_frame():
            """destroys the widgets and layout part_2"""

            logging.debug('StammdatenInterface.aktualisieren_event.destroy_frame() called')

            try:
                self.frame_2.pack_forget()
                self.frame_2.destroy()
            except AttributeError:
                pass

        def create_frame():
            """runs the create widgets and layout part_2 functions"""

            logging.debug('StammdatenInterface.aktualisieren_event.create_frame() called')

            self.create_widgets_part_2(basepath)
            self.create_layout_part_2(basepath, draft)
            self.parent.focus_set()

        # checks in what directory to search
        self.files_in_dir = []
        if self.segmented_button_1.get() == 'Entwürfe':
            basepath = f'{self.parent.rechnungen_location}/drafts/'
            draft = True
        else:
            basepath = f'{self.parent.rechnungen_location}/rechnungen-{self.parent.year}/'
            draft = False

        if not os.path.exists(basepath):
            os.makedirs(basepath)

        # fetches names of files in dir
        self.files_in_dir_unsorted = os.listdir(basepath)

        # checks if file meets filter criteria
        for index, i in enumerate(self.files_in_dir_unsorted):
            if i == '.DS_Store':
                continue
            if self.segmented_button_1.get() == 'Alle':
                if self.search_entry.get().upper() in i:
                    self.files_in_dir.append(i)
            elif self.segmented_button_1.get() == 'KG':
                if self.search_entry.get().upper() in i and not i[:-4][-1:] == 'H':
                    self.files_in_dir.append(i)
            elif self.segmented_button_1.get() == 'HP':
                if self.search_entry.get().upper() in i and i[:-4][-1:] == 'H':
                    self.files_in_dir.append(i)
            elif self.segmented_button_1.get() == 'Entwürfe':
                self.files_in_dir = self.files_in_dir_unsorted

        destroy_frame()
        create_frame()

    def open_rechnung_button_event(self, row, basepath):
        """being called when open button of specific file is pressed and
           opens the respective file."""

        logging.debug(f'RechnungLoeschenInterface.open_rechnung_button_event() called, row={row}')

        Backend(self).open_file(
            f'{basepath}{self.files_in_dir[row]}')

    def edit_rechnung_button_event(self, row, basepath, draft):
        """being called when edit button of specific file is pressed. Switches to
        KGRechnungInterface and passes values."""

        logging.debug(f'RechnungLoeschenInterface.edit_rechnung_button_event() called, row={row}')

        filepath = f'{basepath}{self.files_in_dir[row]}'
        row_count = 0
        data = []

        # checks if file is a draft
        if draft:
            with open(filepath,
                      newline='') as f:
                csvfile = csv.reader(f, delimiter=';')
                for index, row_1 in enumerate(csvfile):
                    if index == 0:
                        data.extend(row_1)
        else:
            if not os.path.exists(filepath):
                logging.debug(f'Rechnung {self.files_in_dir_unsorted[row]} cant be found. Trying to recreate!')
            else:
                logging.debug(f'Rechnung {self.files_in_dir_unsorted[row]} found.')

            if not os.path.exists(f'{self.parent.rechnungen_location}/rechnungen-csv/rechnungen-{self.parent.year}.csv'):
                with open(f'{self.parent.rechnungen_location}/rechnungen-csv/rechnungen-{self.parent.year}.csv', 'w'):
                    pass
                logging.error(
                    f'rechnungen-csv Error: rechnungen-{self.parent.year}.csv just created. Error in filestructure!')
                return messagebox.showerror('rechnungen-csv Error',
                                            f'rechnungen-{self.parent.year}.csv wurde nun erstellt. Fehler in der Ablage Struktur!')

            with open(f'{self.parent.rechnungen_location}/rechnungen-csv/rechnungen-{self.parent.year}.csv',
                      newline='') as f:
                csvfile = csv.reader(f, delimiter=';')
                for row_1 in csvfile:
                    if self.files_in_dir[row].replace('.pdf', '') in row_1:
                        row_count += 1
                        data.extend(row_1)

            if row_count > 1:
                logging.error(
                    f'rechnungen-csv Error: rechnungen-{self.parent.year}.csv corruopt. Multiple times Rechnung {self.files_in_dir[row]}!')
                return messagebox.showerror('rechnungen-csv Error',
                                            f'rechnungen-{self.parent.year}.csv korrupt. Mehrfach {self.files_in_dir[row]} gefunden!')

        # checks if stammdatei exists
        if not os.path.exists(f'{self.parent.stammdaten_location}/{data[0]}.txt'):
                logging.error(
                    f'stammdatei Error: stammdatei {data[0]}.txt not found, create it again to edit this rechnung!')
                return messagebox.showerror('stammdatei Error', f'Stammdatei {data[0]}.txt nicht gefunden. Erneut '
                                                                f'erstellen um Rechnung zu bearbeiten!')

        self.parent.kg_rechnung(data)

    def delete_rechnung_button_event(self, row, basepath):
        """being called when delete button of specific file is pressed and
           deletes the respective file. After it calls the aktualisieren event."""

        logging.debug(f'RechnungLoeschenInterface.delete_rechnung() called, row={row}')

        filepath = f'{self.parent.rechnungen_location}/rechnungen-{self.parent.year}/{self.files_in_dir[row]}'

        Backend(self).clean_remove(filepath, self.files_in_dir[row])

        self.aktualisieren_event()


class EinstellungInterface(customtkinter.CTkScrollableFrame):
    def __init__(self, parent):
        super().__init__(parent)

        logging.info('class EinstellungInterface() called')

        self.parent = parent

        self.configure(fg_color='gray16', corner_radius=0)

        self.place(relx=0.2, y=0, relwidth=0.8, relheight=0.90)

        self.parent.bottom_nav.bottom_nav_button.configure()

        # textvariables
        self.frame_1_warning_var = tk.StringVar()
        self.frame_1_switch_var = tk.StringVar(value='off')
        if self.parent.debug_mode:
            self.frame_3_switch_var_1 = tk.StringVar(value='on')
        else:
            self.frame_3_switch_var_1 = tk.StringVar(value='off')
        if self.parent.behandlungsarten_limiter:
            self.frame_3_switch_var_2 = tk.StringVar(value='on')
        else:
            self.frame_3_switch_var_2 = tk.StringVar(value='off')
        if self.parent.backups_enabled:
            self.frame_3_switch_var_3 = tk.StringVar(value='on')
        else:
            self.frame_3_switch_var_3 = tk.StringVar(value='off')

        self.frame_3_behandlungsarten_limit = tk.StringVar(value=f'{self.parent.behandlungsarten_limit}')
        self.frame_3_rechnungen_location_var = tk.StringVar(value=f'{self.parent.rechnungen_location}/')
        self.frame_3_stammdaten_location_var = tk.StringVar(value=f'{self.parent.stammdaten_location}/')
        self.frame_3_backup_folder_location_var = tk.StringVar(value=f'{self.parent.backup_location}/')

        self.create_widgets_part_1()
        self.create_layout_part_1()

    def create_widgets_part_1(self):
        logging.debug('EinstellungInterface.create_widgets_part_1() called')

        # 'KG Rechnung' / 'heading_1' section
        self.heading_1 = customtkinter.CTkLabel(self, text='Einstellungen', font=large_heading)

        # Separator
        self.separator_1 = tk.ttk.Separator(self, orient='horizontal')

        # 'kuerzel-rechnungsdatum' section
        self.frame_1 = customtkinter.CTkFrame(self, fg_color='gray16')
        self.heading_2 = customtkinter.CTkLabel(self.frame_1, text='General', font=small_heading)
        self.change_year_label = customtkinter.CTkLabel(self.frame_1, text='Programmjahr ändern')
        self.change_year_button = customtkinter.CTkButton(self.frame_1, text='Ändern',
                                                          command=lambda: self.parent.updateyear_interface())
        self.show_dev_options_label = customtkinter.CTkLabel(self.frame_1, text='Erweiterte Optionen anzeigen')
        self.advanced_options_switch = customtkinter.CTkSwitch(self.frame_1, text='', variable=self.frame_1_switch_var,
                                                               onvalue='on', offvalue='off',
                                                               command=lambda: self.advanced_options_switch_event())

        # Separator
        self.separator_2 = tk.ttk.Separator(self, orient='horizontal')

        # About section
        self.frame_2 = customtkinter.CTkFrame(self, fg_color='gray16')
        self.heading_3 = customtkinter.CTkLabel(self.frame_2, text='About', font=small_heading)
        self.about_text_label = customtkinter.CTkLabel(self.frame_2, text=f'Rechnungsprogramm\n\n'
                                                                          f'Version Number {self.parent.version}\n\n'
                                                                          f'Copyright 2023 | Matti Fischbach')

        # Separator
        self.separator_3 = tk.ttk.Separator(self, orient='horizontal')

    def create_layout_part_1(self):
        logging.debug('EinstellungInterface.create_layout_part_1() called')

        # 'KG Rechnung' / 'heading_1' section
        self.heading_1.pack(side='top', fill='x', expand=False, pady=(20, 30), padx=20)

        # Separator
        self.separator_1.pack(fill='x', expand=False)

        # 'kuerzel-rechnungsdatum' section
        self.frame_1.grid_columnconfigure(2, weight=1)
        self.frame_1.pack(fill='x', expand=False, pady=(15, 15), padx=20)
        self.heading_2.grid(row=0, column=0, padx=10, pady=4, columnspan=2, sticky='w')
        self.change_year_label.grid(row=1, column=0, padx=10, pady=4, sticky='w')
        self.change_year_button.grid(row=1, column=1, padx=10, pady=4, sticky='w')
        self.show_dev_options_label.grid(row=1, column=2, padx=10, pady=4, sticky='e')
        self.advanced_options_switch.grid(row=1, column=3, padx=10, pady=4, sticky='e')

        # Separator
        self.separator_2.pack(fill='x', expand=False)

        # About section
        self.frame_2.grid_columnconfigure(0, weight=1)
        self.frame_2.pack(fill='x', expand=False, pady=(15, 15), padx=20)
        self.heading_3.grid(row=0, column=0, padx=10, pady=4, sticky='w')
        self.about_text_label.grid(row=1, column=0, padx=10, pady=4, sticky='ew')

        # Separator
        self.separator_3.pack(fill='x', expand=False)

    def create_widgets_part_2(self):
        logging.debug('EinstellungInterface.create_widgets_part_2() called')

        self.frame_3 = customtkinter.CTkFrame(self, fg_color='gray16')

        self.heading_4 = customtkinter.CTkLabel(self.frame_3, text='Advanced', font=small_heading)

        # Debug section
        self.debug_mode_label = customtkinter.CTkLabel(self.frame_3, text='Debug Mode:')
        self.debug_mode_switch = customtkinter.CTkSwitch(self.frame_3, text='', variable=self.frame_3_switch_var_1,
                                                         onvalue='on', offvalue='off',
                                                         command=lambda: self.edit_dirs('debug_mode'))

        # Behandlungsarten limit(-er) section
        self.disable_behandlungsarten_limit_label = customtkinter.CTkLabel(self.frame_3,
                                                                           text=f'Behandlungsarten Limiter')
        self.disable_behandlungsarten_limit_switch = customtkinter.CTkSwitch(self.frame_3, text='',
                                                                             variable=self.frame_3_switch_var_2,
                                                                             onvalue='on', offvalue='off',
                                                                             command=lambda: self.edit_dirs(
                                                                                 'behandlungsarten_limiter'))
        self.behandlungsarten_limit_label = customtkinter.CTkLabel(self.frame_3, text='Limit =')
        self.behandlungsarten_limit_entry = customtkinter.CTkEntry(self.frame_3, width=30,
                                                                   textvariable=self.frame_3_behandlungsarten_limit,
                                                                   validate='key', validatecommand=(
                self.register(self.behandlungsarten_limit_validation), '%P'))
        if self.frame_3_switch_var_2.get() == 'off':
            self.behandlungsarten_limit_entry.configure(state='disabled', fg_color='gray16')

        # Separator
        self.separator_4 = tk.ttk.Separator(self.frame_3, orient='horizontal')

        # rechnungen location section
        self.rechnungen_location_label = customtkinter.CTkLabel(self.frame_3,
                                                                text='rechnungen folder location:')
        self.rechnungen_location_entry = customtkinter.CTkEntry(self.frame_3,
                                                                textvariable=self.frame_3_rechnungen_location_var,
                                                                state='disabled', fg_color='gray16')
        self.rechnungen_location_button = customtkinter.CTkButton(self.frame_3, text='öffnen',
                                                                  command=lambda: self.edit_dirs('rechnungen_location'))

        # stammdaten location section
        self.stammdaten_location_label = customtkinter.CTkLabel(self.frame_3,
                                                                text='stammdaten folder location:')
        self.stammdaten_location_entry = customtkinter.CTkEntry(self.frame_3,
                                                                textvariable=self.frame_3_stammdaten_location_var,
                                                                state='disabled', fg_color='gray16')
        self.stammdaten_location_button = customtkinter.CTkButton(self.frame_3, text='öffnen',
                                                                  command=lambda: self.edit_dirs('stammdaten_location'))

        # Backups enabled and location section
        self.backups_enabled_label = customtkinter.CTkLabel(self.frame_3, text='Backups erstellen?')
        self.backups_enabled_switch = customtkinter.CTkSwitch(self.frame_3, text='', variable=self.frame_3_switch_var_3,
                                                              onvalue='on', offvalue='off',
                                                              command=lambda: self.edit_dirs('backups_enabled'))
        self.backup_location_label = customtkinter.CTkLabel(self.frame_3, text='Backup folder location:')
        self.backup_location_entry = customtkinter.CTkEntry(self.frame_3,
                                                            textvariable=self.frame_3_backup_folder_location_var,
                                                            state='disabled', fg_color='gray16')
        self.backup_location_button = customtkinter.CTkButton(self.frame_3, text='öffnen',
                                                              command=lambda: self.edit_dirs('backups_location'))

        # Separator
        self.separator_5 = tk.ttk.Separator(self.frame_3, orient='horizontal')

    def create_layout_part_2(self):
        logging.debug('EinstellungInterface.create_layout_part_2() called')

        self.frame_3.grid_columnconfigure(1, weight=1)
        self.frame_3.pack(fill='x', expand=False, pady=(15, 15), padx=20)
        self.heading_4.grid(row=0, column=0, padx=10, pady=4, columnspan=2, sticky='w')

        self.debug_mode_label.grid(row=1, column=0, padx=10, pady=4, sticky='w')
        self.debug_mode_switch.grid(row=1, column=1, padx=10, pady=4, sticky='w')

        self.disable_behandlungsarten_limit_label.grid(row=2, column=0, padx=10, pady=(4, 20), sticky='w')
        self.disable_behandlungsarten_limit_switch.grid(row=2, column=1, padx=10, pady=(4, 20), sticky='w')
        self.behandlungsarten_limit_label.grid(row=2, column=1, padx=(100, 10), pady=(4, 20), sticky='w')
        self.behandlungsarten_limit_entry.grid(row=2, column=1, padx=150, pady=(4, 20), sticky='w')

        # Separator
        self.separator_4.grid(row=3, column=0, columnspan=10, pady=20, sticky='ew')

        self.rechnungen_location_label.grid(row=4, column=0, padx=10, pady=4, sticky='w')
        self.rechnungen_location_entry.grid(row=4, column=1, padx=10, pady=4, sticky='ew')
        self.rechnungen_location_entry.focus_set()
        self.rechnungen_location_button.grid(row=4, column=2, padx=10, pady=4, sticky='w')

        self.stammdaten_location_label.grid(row=5, column=0, padx=10, pady=4, sticky='w')
        self.stammdaten_location_entry.grid(row=5, column=1, padx=10, pady=4, sticky='ew')
        self.stammdaten_location_button.grid(row=5, column=2, padx=10, pady=4, sticky='w')

        self.backups_enabled_label.grid(row=6, column=0, padx=10, pady=(20, 4), sticky='w')
        self.backups_enabled_switch.grid(row=6, column=1, padx=10, pady=(20, 4), sticky='w')
        self.backup_location_label.grid(row=7, column=0, padx=10, pady=4, sticky='w')
        self.backup_location_entry.grid(row=7, column=1, padx=10, pady=4, sticky='ew')
        self.backup_location_button.grid(row=7, column=2, padx=10, pady=4, sticky='w')

        # Separator
        self.separator_5.grid(row=8, column=0, columnspan=10, pady=20, sticky='ew')

    def advanced_options_switch_event(self):
        logging.debug('EinstellungInterface.advanced_options_switch_event() called')

        if self.frame_1_switch_var.get() == 'on':
            self.create_widgets_part_2()
            self.create_layout_part_2()
        elif self.frame_1_switch_var.get() == 'off':
            self.frame_3.destroy()

    def edit_dirs(self, kind):
        logging.debug('EinstellungInterface.open_dir() called')

        Backend(self).change_properties(kind)

    def behandlungsarten_limit_validation(self, text_after_action):
        if not text_after_action == '':
            try:
                int(text_after_action)
            except ValueError:
                print('not int')
                return False
            Backend(self).change_properties('behandlungsarten_limit', text_after_action)
            return True
        else:
            Backend(self).change_properties('behandlungsarten_limit', text_after_action)
            return True


class UpdateYearToplevelWindow(customtkinter.CTkToplevel):
    window_width = 300
    window_height = 150

    def __init__(self, parent):
        super().__init__(parent)

        logging.info('class UpdateYearToplevelWindow() called')

        self.parent = parent

        # textvariable
        self.entry_var = tk.StringVar()
        self.label_var = tk.StringVar()

        self.wm_transient(parent)
        self.grab_set()

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_cordinate = int((screen_width / 2) - (int(self.window_width) / 2))
        y_cordinate = int((screen_height / 2) - (int(self.window_height) / 2))
        self.title('Programmjahr ändern')
        self.resizable(False, False)
        self.geometry(f'{self.window_width}x{self.window_height}+{x_cordinate}+{y_cordinate}')

        self.label = customtkinter.CTkLabel(self, text="Neues Programmjahr:")
        self.label.pack(padx=20, pady=4)

        self.entry = customtkinter.CTkEntry(self, textvariable=self.entry_var)
        self.entry.bind('<Return>', self.update_button_event)
        self.entry.pack(padx=20, pady=4)

        self.button = customtkinter.CTkButton(self, text='Ändern', command=lambda: self.update_button_event())
        self.button.pack(padx=20, pady=4)

        self.label_2 = customtkinter.CTkLabel(self, text='', textvariable=self.label_var, text_color='red')
        self.label_2.pack(padx=20, pady=(4, 20))

    def update_button_event(self, *args):
        logging.debug('UpdateYearToplevelWindow.update_button_event() called')

        if re.match('^[12][0-9]{3}$', self.entry_var.get()):
            logging.debug('valid year entry')

            self.parent.year = self.entry_var.get()
            self.parent.sidebar.heading_2.configure(text=f'{self.parent.year}')
            tk.messagebox.showinfo('Success', 'Änderungen wurden übernommen!')
            logging.info(f'changed year to {self.parent.year}')
            with open('./system/properties.yml', 'r') as a:
                properties_dict = yaml.safe_load(a)
                properties_dict['program_year'] = self.parent.year
            with open('./system/properties.yml', 'w') as f:
                yaml.dump(properties_dict, f)
            self.destroy()
        else:
            logging.warning('year must be format YYYY')
            self.label_var.set('Format Datum -> YYYY / 2023')


class Backend:
    def __init__(self, parent, **kwargs):
        logging.info('class Backend() called')
        self.kwargs = kwargs
        self.parent = parent
        self.datenanzahl = 0

    def validate_kg_entrys(self):
        logging.debug('Backend.validate_kg_entrys() called')

        self.parent.parent.bottom_nav.bottom_nav_warning.configure(text='')

        # validate kuerzel + getting stammdaten
        if len(self.kwargs.get('kuerzel').get()) == 4:
            if os.path.exists(f'{self.parent.parent.stammdaten_location}/{self.kwargs.get("kuerzel").get()}.txt'):
                with open(f'{self.parent.parent.stammdaten_location}/{self.kwargs.get("kuerzel").get()}.txt', 'r') as f:
                    self.stammdaten = f.readlines()
                    for i, line in enumerate(self.stammdaten):
                        self.stammdaten[i] = line.replace('\n', '')
            else:
                logging.warning(f'kuerzel not found, check code and check kuerzel')
                messagebox.showwarning('Kürzel Warning', 'Kürzel/Stammdatei nicht gefunden. Versuche es erneut!')
                self.parent.parent.bottom_nav.bottom_nav_warning.configure(
                    text=f'Kürzel/Stammdatei nicht gefunden. Versuche es erneut!', fg_color='red')
                return False
        logging.debug(f'stammdaten: {self.stammdaten}')

        # validate rechnungsdatum
        if re.match("(^0[1-9]|[12][0-9]|3[01]).(0[1-9]|1[0-2]).(\d{2}$)", self.kwargs.get('rechnungsdatum').get()):
            self.rechnungsdatum = self.kwargs.get('rechnungsdatum').get()
        else:
            self.parent.rechnungsdatum_entry.select_range(0, tk.END)
            self.parent.rechnungsdatum_entry.set_focus()
            logging.info('rechnungsdatum not formatted correctly: mm.dd.yy')
            self.parent.parent.bottom_nav.bottom_nav_warning.configure(
                text=f'Rechnungsdatum nicht richtig formatiert: dd.mm.yy', fg_color='red')
            return False
        logging.debug(f'rechnungsdatum: {self.rechnungsdatum}')

        # validate dates
        self.dates = []
        empty_dates = []
        for index, i in enumerate(self.kwargs.get('dates')):
            if re.match("(^0[1-9]|[12][0-9]|3[01]).(0[1-9]|1[0-2]).(\d{2}$)", i.get()):
                self.dates.append(str(i.get()))
                self.datenanzahl += 1
            elif i.get() == '':
                logging.debug(f'date {index} no value')
                empty_dates.append(str(i.get()))
            else:
                logging.debug(f'date {index + 1} not formatted correctly, exiting')
                i.select_range(0, tk.END)
                self.parent.parent.bottom_nav.bottom_nav_warning.configure(text=f'Datum {index + 1} '
                                                                                       f'nicht richtig formatiert: dd.mm.yy',
                                                                                  fg_color='red')
                return False
        if self.datenanzahl == 0:
            if not messagebox.askyesno('Do you want to continue?',
                                       'Keine Behandlungsdaten eingetragen! Trotzdem fortsetzen?'):
                logging.debug(f'no dates and dont wanting to continue, exiting')
                self.parent.parent.bottom_nav.bottom_nav_warning.configure(text=f'Rechnung wurde nicht erstellt',
                                                                                  fg_color='orange')
                return False
        self.dates.extend(empty_dates)
        logging.debug(f'datenanzahl: {self.datenanzahl}')
        logging.debug(f'dates: {self.dates}')

        # validate behandlungsdaten
        self.behandlungsarten = []
        self.einzelpreise = []
        for index_1, i in enumerate(self.kwargs.get('behandlungsarten')):
            for index_2, a in enumerate(i):
                if index_2 == 0:
                    if not a.get() == '':
                        self.behandlungsarten.append(a.get())
                    else:
                        logging.debug(f'Behandlungsart {index_1 + 1} has no value, exiting')
                        a.set_focus()
                        self.parent.parent.bottom_nav.bottom_nav_warning.configure(
                            text=f'Behandlungsart {index_1 + 1} braucht eine Eingabe!',
                            fg_color='red')
                        return False
                elif index_2 == 1:
                    if not a.get() == '':
                        try:
                            self.einzelpreise.append(float(a.get()))
                        except ValueError:
                            logging.debug(f'Einzelpreis {index_1 + 1} not convertable to float, exiting')
                            a.select_range(0, tk.END)
                            self.parent.parent.bottom_nav.bottom_nav_warning.configure(
                                text=f'Einzelpreis {index_1 + 1} keine Zahl: {a.get()} -> z.B. 3.40',
                                fg_color='red')
                            return False
                    else:
                        logging.debug(f'Einzelpreis {index_1 + 1} has no value, exiting')
                        a.set_focus()
                        self.parent.parent.bottom_nav.bottom_nav_warning.configure(
                            text=f'Einzelpreis {index_1 + 1} brauch eine Eingabe!',
                            fg_color='red')
                        return False
        logging.debug(f'behandlungsarten: {self.behandlungsarten}')
        logging.debug(f'einzelpreise: {self.einzelpreise}')

        # validate Stammdatei
        for index, i in enumerate(self.stammdaten):
            if index == 9:
                try:
                    float(i)
                except ValueError:
                    logging.debug(f'Stammdatei/Kilometer zu Fahren has non float convertible value, exiting')
                    self.parent.parent.bottom_nav.bottom_nav_warning.configure(
                        text=f'Stammdatei - Kilometer keine Zahl: -> z.B. 3.40 oder 10; Ändern unter stammdaten!',
                        fg_color='red')
                    return False
            if i == '':
                if index == 8:
                    pass
                else:
                    logging.debug(f'Stammdatei has no value in line {index + 1}, exiting')
                    self.parent.parent.bottom_nav.bottom_nav_warning.configure(
                        text=f'Stammdatei hat keinen Wert in Linie {index + 1}. Stammdatei überprüfen!',
                        fg_color='red')
                    return False
            logging.debug(f'Stammdatei[{index}]: {i}')

        self.parent.parent.bottom_nav.bottom_nav_warning.configure(fg_color='transparent')

        if not self.store_kg_data():
            self.parent.parent.bottom_nav.bottom_nav_warning.configure(
                text=f'Rechnung wurde nicht überschrieben!',
                fg_color='orange')
            return False
        else:
            if self.create_kg_pdf():
                return True

    def store_kg_data(self):
        logging.debug('Backend.store_kg_data() called')

        # validate Rechnungsnummer
        self.rechnungsnummer = f'{self.stammdaten[0]}{self.rechnungsdatum.replace(".", "")}'
        logging.debug(f'rechnungsnummer: {self.rechnungsnummer}')

        # calculating km total
        km_insg = 2 * float(self.stammdaten[9]) * float(self.datenanzahl)
        logging.debug(f'km insgesamt: {km_insg}')

        # calculating gesamtpreis
        self.gesamtpreis = 0
        for i, data in enumerate(self.einzelpreise):
            # Addition of 'Einzelpreise'
            self.gesamtpreis += self.datenanzahl * float(data)
        logging.debug(f'gesamtpreis: {self.gesamtpreis}')

        rechnungsdaten = [self.stammdaten[0], self.rechnungsnummer, self.stammdaten[9], 'km', km_insg, 'km',
                          self.gesamtpreis, '€']
        rechnungsdaten.extend(self.dates)
        rechnungsdaten.extend(self.behandlungsarten)
        rechnungsdaten.extend(self.einzelpreise)

        if not self.clean_remove(
                f'{self.parent.parent.rechnungen_location}/rechnungen-{self.parent.parent.year}/{self.rechnungsnummer}.pdf',
                f'{self.rechnungsnummer}.pdf'):
            return False
        else:
            with open(
                    f'{self.parent.parent.rechnungen_location}/rechnungen-csv/rechnungen-{self.parent.parent.year}.csv',
                    'a',
                    newline='') as f:
                csvfile = csv.writer(f, delimiter=';')
                csvfile.writerow(rechnungsdaten)
                logging.info('wrote new line in RechnungenInsgesamt')
            return True

    def create_kg_pdf(self):
        logging.debug('Backend.create_kg_pdf() called')

        filepath = KgRechnung(self, self.stammdaten, self.rechnungsnummer, self.rechnungsdatum, self.gesamtpreis, self.dates,
                              self.datenanzahl, self.behandlungsarten, self.einzelpreise).create_pages()

        # PDF Öffnen
        self.open_file(filepath)

        return True

    def validate_stammdaten_entrys(self):
        logging.debug('Backend.validate_stammdaten_entrys() called')
        self.stammdaten = self.kwargs.get('stammdaten')

        self.parent.parent.bottom_nav.bottom_nav_warning.configure(text='')

        if len(self.stammdaten[0].get()) != 4:
            self.stammdaten[0].select_range(0, tk.END)
            self.stammdaten[0].focus_set()
            return self.parent.parent.bottom_nav.bottom_nav_warning.configure(
                text=f'Kuerzel mehr/weniger als 4 Buchstaben!', fg_color='red')

        if self.stammdaten[1].get() != 'Mann' and self.stammdaten[1].get() != 'Frau':
            self.stammdaten[1].select_range(0, tk.END)
            self.stammdaten[1].focus_set()
            return self.parent.parent.bottom_nav.bottom_nav_warning.configure(
                text=f'Mann/Frau muss "Mann" oder "Frau" sein', fg_color='red')

        try:
            float(self.stammdaten[9].get())
        except ValueError:
            self.stammdaten[9].select_range(0, tk.END)
            self.stammdaten[9].focus_set()
            return self.parent.parent.bottom_nav.bottom_nav_warning.configure(
                text=f'Kilometer zu fahren muss int oder float sein!', fg_color='red')

        if not self.stammdaten[12].get() == 'HP' and not self.stammdaten[12].get() == 'KG':
            self.stammdaten[12].select_range(0, tk.END)
            self.stammdaten[12].focus_set()
            return self.parent.parent.bottom_nav.bottom_nav_warning.configure(
                text=f'Nicht HP oder KG eingegeben!', fg_color='red')

        self.parent.parent.bottom_nav.bottom_nav_warning.configure(fg_color='transparent')

        if not self.store_stammdaten_data():
            self.parent.parent.bottom_nav.bottom_nav_warning.configure(
                text=f'Stammdatei wurde nicht überschrieben!',
                fg_color='orange')
            return False
        else:
            self.parent.parent.bottom_nav.bottom_nav_warning.configure(
                text=f'Stammdatei wurde über-/geschrieben!',
                fg_color='green')
            return True

    def store_stammdaten_data(self):
        logging.debug('Backend.store_stammdaten_data() called')

        if os.path.exists(f'{self.parent.parent.stammdaten_location}/{self.stammdaten[0].get()}.txt'):
            if not messagebox.askyesno('Do you want to continue?',
                                       f'Stammdatei zu {self.stammdaten[0].get()} exisitiert bereits und wird beim '
                                       f'fortsetzen überschrieben! Trotzdem forstetzen?'):
                logging.debug('Stammdatei wird nicht überschrireben, exiting')
                return False
            else:
                logging.debug('Stammdatei wird überschrieben')
                with open(f'{self.parent.parent.stammdaten_location}/{self.stammdaten[0].get()}.txt', 'w') as f:
                    for index, i in enumerate(self.stammdaten):
                        if index != 12:
                            f.write(f'{i.get()}\n')
                        else:
                            f.write(f'{i.get()}')
                return True
        else:
            with open(f'{self.parent.parent.stammdaten_location}/{self.stammdaten[0].get()}.txt', 'w') as f:
                for index, i in enumerate(self.stammdaten):
                    if index != 12:
                        f.write(f'{i.get()}\n')
                    else:
                        f.write(f'{i.get()}')
            return True

    def store_draft(self, interface):
        if interface is None or self.parent.debug_mode:
            return True
        if interface == 'kg':
            try:
                data = [self.parent.kg_interface.kuerzel_entry, self.parent.kg_interface.rechnungsdatum_entry,
                        self.parent.kg_interface.daten_entrys, self.parent.kg_interface.behandlungsarten_entrys_2d_array]
            except AttributeError:
                return True

            found = False
            for i in data[2]:
                if i.get() != '':
                    found = True
            for i in data[3]:
                for a in i:
                    if a.get() != '':
                        found = True
            if not found:
                return True

            rechnungsdaten = [data[0].get(), f'{data[0].get()}{data[1].get().replace(".", "")}', 'km', 'km', 'km', 'km',
                              'Euro', 'Euro', ]
            for i in data[2]:
                rechnungsdaten.append(i.get())
            behandlungsarten = []
            einzelpreise = []
            for i in data[3]:
                behandlungsarten.append(i[0].get())
                einzelpreise.append(i[1].get())
            rechnungsdaten.extend(behandlungsarten)
            rechnungsdaten.extend(einzelpreise)
        else:
            return True

        # check if draft exist and check value
        if os.path.exists(f'{self.parent.rechnungen_location}/drafts/{rechnungsdaten[1]}DRAFT.csv'):
            data = []
            with open(f'{self.parent.rechnungen_location}/drafts/{rechnungsdaten[1]}DRAFT.csv', newline='') as f:
                csvfile = csv.reader(f, delimiter=';')
                for index, row_1 in enumerate(csvfile):
                    if index == 0:
                        data.extend(row_1)
            if data == rechnungsdaten:
                return True

        # check if rechnung to rechnungsnummer exists
        if os.path.exists(f'{self.parent.rechnungen_location}/rechnungen-{self.parent.year}/{rechnungsdaten[1].upper()}.pdf'):
            return True

        # ask if draft should be safed
        draft_yesno = messagebox.askyesnocancel('Do you want to continue?', 'Soll ein Entwurf gespeicher werden?')
        if draft_yesno:
            if not os.path.exists(f'{self.parent.rechnungen_location}/drafts/'):
                os.mkdir(f'{self.parent.rechnungen_location}/drafts/')
            with open(f'{self.parent.rechnungen_location}/drafts/{rechnungsdaten[1].upper()}DRAFT.csv', 'w',
                      newline='') as f:
                csvfile = csv.writer(f, delimiter=';')
                csvfile.writerow(rechnungsdaten)
                logging.info('created draft')
            return True
        elif draft_yesno is False:
            return True
        elif draft_yesno is None:
            return False

    def clean_remove(self, filepath, file):
        logging.debug('Backend.clean_remove() called')

        if os.path.exists(filepath):
            if not messagebox.askyesno('Do you want to continue?',
                                       f'Beim fortfahren wird die Rechnung {file} '
                                       f'gelöscht/überschrieben!'):
                logging.debug('Rechnung wird nicht gelöscht, exiting')
                return False
            else:
                logging.debug('Rechnung wird gelöscht')
                if os.path.exists(
                        f'{self.parent.parent.rechnungen_location}/rechnungen-csv/rechnungen-{self.parent.parent.year}.csv'):
                    with fileinput.FileInput(
                            f'{self.parent.parent.rechnungen_location}/rechnungen-csv/rechnungen-{self.parent.parent.year}.csv',
                            inplace=True) as a:
                        for line in a:
                            if file.replace('.pdf', '') in line:
                                print('', end='')
                                logging.debug('deleted line in RechnungenInsgesamt')
                                continue
                            else:
                                print(line, end='')
                else:
                    with open(
                            f'{self.parent.parent.rechnungen_location}/rechnungen-csv/rechnungen-{self.parent.parent.year}.csv',
                            'w'):
                        pass
                os.remove(filepath)
        else:
            if os.path.exists(
                    f'{self.parent.parent.rechnungen_location}/rechnungen-csv/rechnungen-{self.parent.parent.year}.csv'):
                with fileinput.FileInput(
                        f'{self.parent.parent.rechnungen_location}/rechnungen-csv/rechnungen-{self.parent.parent.year}.csv',
                        inplace=True) as a:
                    for line in a:
                        if file.replace('.pdf', '') in line:
                            print('', end='')
                            logging.info('deleted line in RechnungenInsgesamt')
                            continue
                        else:
                            print(line, end='')
            else:
                with open(
                        f'{self.parent.parent.rechnungen_location}/rechnungen-csv/rechnungen-{self.parent.parent.year}.csv',
                        'w'):
                    pass
            logging.info("File didn't exist. Cleared RechnungenInsgesamt!")

        draft_files = os.listdir(f'{self.parent.parent.rechnungen_location}/drafts/')
        file_without_extension = os.path.splitext(file)[0]
        for i in draft_files:
            if file_without_extension.lower() in i.lower():
                os.remove(f'{self.parent.parent.rechnungen_location}/drafts/{i}')
        return True

    def change_properties(self, kind, *args):
        if kind == 'stammdaten_location':
            dirpath = tk.filedialog.askdirectory(title='stammdaten Filepath', initialdir='./', )
            if dirpath == '':
                return
            else:
                try:
                    for i in os.listdir(self.parent.parent.stammdaten_location):
                        shutil.move(f'{self.parent.parent.stammdaten_location}/{i}', dirpath)
                    os.removedirs(self.parent.parent.stammdaten_location)
                except FileNotFoundError:
                    logging.error('stammdaten location not existing')

                self.parent.parent.stammdaten_location = dirpath
                if os.path.exists('./system/properties.yml'):
                    with open('./system/properties.yml', 'r') as a:
                        properties_dict = yaml.safe_load(a)
                        properties_dict['stammdaten_location'] = self.parent.parent.stammdaten_location
                    with open('./system/properties.yml', 'w') as f:
                        yaml.dump(properties_dict, f)
                    self.parent.frame_3_stammdaten_location_var.set(f'{self.parent.parent.stammdaten_location}/')
                else:
                    self.parent.parent.check_or_create_working_dirs()
                return logging.info('stammdaten location changed successfully')
        elif kind == 'rechnungen_location':
            dirpath = tk.filedialog.askdirectory(title='rechnungen Filepath', initialdir='./', )
            if dirpath == '':
                return
            else:
                try:
                    for i in os.listdir(self.parent.parent.rechnungen_location):
                        try:
                            shutil.move(f'{self.parent.parent.rechnungen_location}/{i}', dirpath)
                            os.removedirs(self.parent.parent.rechnungen_location)
                        except shutil.Error:
                            logging.info('dir already exists and files wont be moved')
                except FileNotFoundError:
                    logging.error('rechnungen location not existing')

                self.parent.parent.rechnungen_location = dirpath
                if os.path.exists('./system/properties.yml'):
                    with open('./system/properties.yml', 'r') as a:
                        properties_dict = yaml.safe_load(a)
                        properties_dict['rechnungen_location'] = self.parent.parent.rechnungen_location
                    with open('./system/properties.yml', 'w') as f:
                        yaml.dump(properties_dict, f)
                    self.parent.frame_3_rechnungen_location_var.set(f'{self.parent.parent.rechnungen_location}/')
                else:
                    self.parent.parent.check_or_create_working_dirs()
                return logging.info('rechnungen location changed successfully')
        elif kind == 'backups_location':
            dirpath = tk.filedialog.askdirectory(title='Backups Filepath', initialdir='./', )
            if dirpath == '':
                return
            else:
                try:
                    for i in os.listdir(self.parent.parent.backup_location):
                        shutil.move(f'{self.parent.parent.backup_location}/{i}', dirpath)
                    os.removedirs(self.parent.parent.backup_location)
                except FileNotFoundError:
                    logging.error('backup location not existing')

                self.parent.parent.backup_location = dirpath
                if os.path.exists('./system/properties.yml'):
                    with open('./system/properties.yml', 'r') as a:
                        properties_dict = yaml.safe_load(a)
                        properties_dict['backup_location'] = self.parent.parent.backup_location
                    with open('./system/properties.yml', 'w') as f:
                        yaml.dump(properties_dict, f)
                    self.parent.frame_3_backup_folder_location_var.set(f'{self.parent.parent.backup_location}/')
                else:
                    self.parent.parent.check_or_create_working_dirs()
                return logging.info('backups location changed successfully')
        elif kind == 'debug_mode':
            if self.parent.frame_3_switch_var_1.get() == 'off':
                self.parent.parent.debug_mode = False
            else:
                self.parent.parent.debug_mode = True

            if os.path.exists('./system/properties.yml'):
                with open('./system/properties.yml', 'r') as a:
                    properties_dict = yaml.safe_load(a)
                    properties_dict['debug_mode'] = self.parent.parent.debug_mode
                with open('./system/properties.yml', 'w') as f:
                    yaml.dump(properties_dict, f)
            else:
                self.parent.parent.check_or_create_working_dirs()

            return messagebox.showinfo('Änderungen gespeichert',
                                       'Programm muss neu gestartet werden um Änderungen zu sehen!')
        elif kind == 'behandlungsarten_limiter':
            if self.parent.frame_3_switch_var_2.get() == 'off':
                self.parent.parent.behandlungsarten_limiter = False
                self.parent.behandlungsarten_limit_entry.configure(state='disabled', fg_color='gray16')
            else:
                self.parent.parent.behandlungsarten_limiter = True
                self.parent.behandlungsarten_limit_entry.configure(state='normal', fg_color='#343638')

            if os.path.exists('./system/properties.yml'):
                with open('./system/properties.yml', 'r') as a:
                    properties_dict = yaml.safe_load(a)
                    properties_dict['behandlungsarten_limiter'] = self.parent.parent.behandlungsarten_limiter
                with open('./system/properties.yml', 'w') as f:
                    yaml.dump(properties_dict, f)
            else:
                self.parent.parent.check_or_create_working_dirs()
        elif kind == 'behandlungsarten_limit':
            self.parent.parent.behandlungsarten_limit = int(*args[0])
            if os.path.exists('./system/properties.yml'):
                with open('./system/properties.yml', 'r') as a:
                    properties_dict = yaml.safe_load(a)
                    properties_dict['behandlungsarten_limit'] = self.parent.parent.behandlungsarten_limit
                with open('./system/properties.yml', 'w') as f:
                    yaml.dump(properties_dict, f)
            else:
                self.parent.parent.check_or_create_working_dirs()
        elif kind == 'backups_enabled':
            if self.parent.frame_3_switch_var_3.get() == 'off':
                self.parent.parent.backups_enabled = False
            else:
                self.parent.parent.backups_enabled = True

            if os.path.exists('./system/properties.yml'):
                with open('./system/properties.yml', 'r') as a:
                    properties_dict = yaml.safe_load(a)
                    properties_dict['backups_enabled'] = self.parent.parent.backups_enabled
                with open('./system/properties.yml', 'w') as f:
                    yaml.dump(properties_dict, f)
            else:
                self.parent.parent.check_or_create_working_dirs()

    def create_backup(self):
        logging.debug('Backend.create_backup() called')

        if self.parent.backups_enabled:
            current_date_time = time.strftime('%Y-%m-%d--%H-%M-%S')
            if not os.path.exists(self.parent.backup_location):
                os.makedirs(self.parent.backup_location)
                logging.info(f'created {self.parent.backup_location}')
            shutil.make_archive(f'{self.parent.backup_location}/backup-rechnungen--{current_date_time}', 'zip',
                                f'{self.parent.rechnungen_location}/')
            return True
        else:
            return False

    def open_file(self, filepath):
        logging.debug('Backend.open_rechnung() called')

        if platform.system() == 'Darwin':  # macOS
            subprocess.call(('open', filepath))
            logging.info('macOS: opened file')
        elif platform.system() == 'Windows':  # Windows
            subprocess.Popen(filepath, shell=True)
            logging.info('Windows: opened file')
        else:  # linux variants
            subprocess.call(('xdg-open', filepath))
            logging.info('linux: opened file')


class PDF(FPDF):
    def __init__(self, rechnungsnummer):
        super().__init__()
        self.rechnungsnummer = rechnungsnummer

    def header(self):
        self.set_top_margin(10)
        # Logo
        try:
            self.image(x=15, y=10, name='./system/components/images/logo.png', w=18, alt_text='Logo')
        except FileNotFoundError:
            pass
        self.set_font('helvetica', 'B', 14)
        self.cell(0, new_x=XPos.LMARGIN, new_y=YPos.TMARGIN)
        self.ln(2.5)
        self.cell(25)
        self.cell(0, txt='Mervi Fischbach', align='L')
        # self.cell(0, txt='Test', align='R')
        self.ln()
        self.cell(25)
        self.set_font('helvetica', 'B', 12)
        self.set_text_color(150)
        self.cell(0, txt='Heilpraktikerin &', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.cell(25)
        self.cell(0, txt='Physiotherapeutin')
        self.ln(23)

    # Page footer
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # helvetica italic 8
        self.set_font('helvetica', 'B', 8)
        self.cell(0, 5, 'Bankverbindung ING Diba', align='C')
        self.ln(3)
        self.cell(0, 5, 'IBAN: DE20 5001 0517 5403 5068 61', align='C')
        self.ln(3)
        self.cell(0, 5, 'BIC: INGDDEFFXXX', align='C')
        self.ln(3)
        self.set_font('helvetica', '', 6)
        self.cell(1, 5, f'Rechnungsnummer: {self.rechnungsnummer}', align='L')
        self.cell(0, 5, 'Steuer Nummer: 131-217-00314 - Ust. Befreit nach §4 UStG', align='C')
        # Page number
        self.cell(0, 5, 'Seite ' + str(self.page_no()) + ' von {nb}', align='R')


class KgRechnung(PDF):
    normal_font_size = 11
    honorar_font_size = 10
    rechnungsempfaenger_offset = 4

    def __init__(self, parent, stammdaten: list, rechnungsnummer: str, rechnungsdatum: str, gesamtpreis: int,
                 rechnungsdaten: list, rechnungsdaten_anzahl: int, behandlungsarten: list,
                 einzelpreise: list):
        super().__init__(rechnungsnummer)
        self.parent = parent

        self.prepare_data(stammdaten, rechnungsnummer, rechnungsdatum, gesamtpreis, rechnungsdaten,
                          rechnungsdaten_anzahl, behandlungsarten, einzelpreise)

    def prepare_data(self, stammdaten, rechnungsnummer, rechnungsdatum, gesamtpreis, rechnungsdaten,
                     rechnungsdaten_anzahl, behandlungsarten, einzelpreise):

        self.TABLE_DATA_1 = [['Patientenkürzel', 'Rechnungsnummer', 'Rechnungsdatum']]

        self.TABLE_DATA_2 = []

        self.TABLE_DATA_3 = [['Anzahl', 'Art der Behandlung', 'Einzelpreis', 'Gesamtpreis', ''],
                             ['1', 'Anamnese und Befunderhebung', '0,00', '0,00', '\u00a0']]

        self.TABLE_DATA_4 = [['', '', '', '']]

        self.kuerzel = stammdaten[0]
        self.mafr = stammdaten[1]
        self.nachname = stammdaten[2]
        self.vorname = stammdaten[3]
        self.strasse = stammdaten[4]
        self.hausnummer = stammdaten[5]
        self.plz = stammdaten[6]
        self.ort = stammdaten[7]
        self.geburtsdatum = stammdaten[8]

        self.TABLE_DATA_1.append([self.kuerzel, rechnungsnummer, rechnungsdatum])

        for i in range(int(len(rechnungsdaten) / 2)):
            array_1d = []
            for a in range(2):
                array_1d.append(rechnungsdaten.pop(-1))
            array_1d.reverse()
            self.TABLE_DATA_2.insert(0, array_1d)

        self.rechnungsdaten_anzahl = rechnungsdaten_anzahl
        if behandlungsarten:
            for index, i in enumerate(behandlungsarten):
                self.TABLE_DATA_3.append([str(self.rechnungsdaten_anzahl), i,
                                          f'{round(float(einzelpreise[index]), 2):.2f}'.replace('.', ','),
                                          f'{round(float(einzelpreise[index]) * rechnungsdaten_anzahl, 2):.2f}'.replace(
                                              '.', ','),
                                          '\u00a0'])

        self.gesamtpreis = f'{round(float(gesamtpreis), 2):.2f}'.replace('.', ',')
        self.TABLE_DATA_4.insert(0, ['', 'Gesamtbetrag:', self.gesamtpreis, '\u00a0'])

    def create_pages(self):
        self.add_page()

        self.set_font("helvetica", size=7)
        self.cell(self.rechnungsempfaenger_offset)
        self.write(txt='Mervi Fischbach - Schulgasse 9 - 86923 Finning')
        self.ln(3)

        self.set_font("helvetica", size=self.normal_font_size)
        self.cell(self.rechnungsempfaenger_offset)
        if self.mafr == 'Mann':
            self.write(txt='Herr\n')
        elif self.mafr == 'Frau':
            self.write(txt='Frau\n')
        self.cell(self.rechnungsempfaenger_offset)
        self.write(txt=f'{self.vorname} {self.nachname}\n')
        self.cell(self.rechnungsempfaenger_offset)
        self.write(txt=f'{self.strasse} {self.hausnummer}\n')
        self.cell(self.rechnungsempfaenger_offset)
        self.write(txt=f'{self.plz} {self.ort}\n')
        self.ln(27)

        self.cell(190, 0, border=1, center=True)
        self.set_font("helvetica", size=self.normal_font_size)
        with self.table(borders_layout='NONE', line_height=1.5 * self.font_size,
                        text_align=('LEFT', 'CENTER', 'RIGHT')) as table:
            for data_row in self.TABLE_DATA_1:
                row = table.row()
                for datum in data_row:
                    row.cell(datum)
        self.cell(190, 0, border=1, center=True)
        self.ln(5)

        self.set_font("helvetica", style='B', size=self.normal_font_size)
        if self.mafr == 'Mann':
            self.cell(25, txt='Patient:', align='L')
        elif self.mafr == 'Frau':
            self.cell(25, txt='Patientin:', align='L')
        self.set_font("helvetica", style='', size=self.normal_font_size)
        self.cell(40, txt=f'{self.vorname} {self.nachname}, geb. {self.geburtsdatum}')
        self.ln(7)

        self.set_font("helvetica", style='B', size=self.normal_font_size)
        self.write(txt=f'{self.rechnungsdaten_anzahl} Behandlungstermine:')
        self.set_font("helvetica", style='', size=self.normal_font_size)
        self.ln(5)
        with self.table(width=80, line_height=1.7 * self.font_size, align='LEFT', borders_layout='NONE',
                        first_row_as_headings=False) as table:
            for data_row in self.TABLE_DATA_2:
                row = table.row()
                for datum in data_row:
                    row.cell(datum)
        self.ln(10)

        self.set_font("helvetica", size=self.normal_font_size)
        if self.mafr == 'Mann':
            self.write(txt=f'Sehr geehrter Herr {self.nachname},\n\n'
                           'hiermit erlaube ich mir, für meine Bemühungen folgendes Honorar zu berechnen:')
        if self.mafr == 'Frau':
            self.write(txt=f'Sehr geehrte Frau {self.nachname},\n\n'
                           'hiermit erlaube ich mir, für meine Bemühungen folgendes Honorar zu berechnen:')
        self.ln(7)
        self.set_font("helvetica", size=self.honorar_font_size)

        with self.table(cell_fill_color=230, cell_fill_mode="ROWS",
                        line_height=1.7 * self.font_size,
                        text_align=('CENTER', 'LEFT', 'RIGHT', 'RIGHT', 'LEFT'),
                        col_widths=(9, 70, 12, 14, 3)) as table:
            for data_row in self.TABLE_DATA_3:
                row = table.row()
                for index, datum in enumerate(data_row):
                    if index == 4:
                        self.set_font("symbol", size=self.honorar_font_size + 1)
                        row.cell(datum)
                        self.set_font("helvetica", style='', size=self.honorar_font_size)
                    else:
                        row.cell(datum)

        self.cell(190, 0, border=1, center=True)
        with self.table(borders_layout='NONE', col_widths=(9, 70, 12, 14, 3), line_height=1.7 * self.font_size,
                        text_align=('CENTER', 'RIGHT', 'RIGHT', 'RIGHT', 'LEFT'),
                        cell_fill_color=180, cell_fill_mode="NONE", first_row_as_headings=False) as table:
            for data_row in self.TABLE_DATA_4:
                row = table.row()
                for index_2, datum in enumerate(data_row):
                    if index_2 == 1:
                        self.set_font("helvetica", style='B', size=self.honorar_font_size)
                        row.cell(datum, colspan=2)
                        self.set_font("helvetica", style='', size=self.honorar_font_size)
                    elif index_2 == 3:
                        self.set_font("symbol", '', size=self.honorar_font_size + 1)
                        row.cell(datum)
                        self.set_font("helvetica", style='', size=self.honorar_font_size)
                    else:
                        self.set_font("helvetica", style='B', size=self.honorar_font_size)
                        row.cell(datum)
                        self.set_font("helvetica", style='', size=self.honorar_font_size)

        self.ln(0)
        self.set_font("helvetica", size=self.normal_font_size)
        self.write(6.5, txt=f'Ich bitte Sie, den Gesamtbetrag von {self.gesamtpreis} ')
        self.set_font("symbol", size=self.normal_font_size + 1)
        self.write(6.5, txt='\u00a0 ')
        self.set_font("helvetica", size=self.normal_font_size)
        self.write(6.5,
                   txt='innerhalb von 14 Tagen unter Angabe der Rechnungsnummer auf unten stehendes Konto zu überweisen.')
        self.ln(13)
        self.write(txt='Mit freundlichen Grüßen')
        self.ln(10)
        self.write(txt='Mervi Fischbach')

        export_filepath = f'{self.parent.parent.parent.rechnungen_location}/rechnungen-{self.parent.parent.parent.year}/{self.rechnungsnummer}.pdf'
        # export_filepath = './kgrechnung.pdf'
        self.output(export_filepath)
        return export_filepath


class HpRechnung(PDF):
    normal_font_size = 11
    honorar_font_size = 10
    rechnungsempfaenger_offset = 4

    def __init__(self, parent, stammdaten: list, rechnungsnummer: str, rechnungsdatum: str, gesamtpreis: float,
                 rechnungsdaten: list, diagnose: str):
        super().__init__(rechnungsnummer)
        self.parent = parent

        self.prepare_data(stammdaten, rechnungsnummer, rechnungsdatum, gesamtpreis, rechnungsdaten, diagnose)
        self.create_pages()

    def prepare_data(self, stammdaten, rechnungsnummer, rechnungsdatum, gesamtpreis, rechnungsdaten,
                     diagnose):

        self.TABLE_DATA_1 = [['Patientenkürzel', 'Rechnungsnummer', 'Rechnungsdatum']]

        self.TABLE_DATA_2 = [['Datum', 'Ziffer', 'Art der Behandlung', 'Betrag', '']]

        self.TABLE_DATA_3 = [['', '', '', '', '']]

        self.kuerzel = stammdaten[0]
        self.mafr = stammdaten[1]
        self.nachname = stammdaten[2]
        self.vorname = stammdaten[3]
        self.strasse = stammdaten[4]
        self.hausnummer = stammdaten[5]
        self.plz = stammdaten[6]
        self.ort = stammdaten[7]
        self.geburtsdatum = stammdaten[8]

        self.TABLE_DATA_1.append([self.kuerzel, rechnungsnummer, rechnungsdatum])

        for index, i in enumerate(rechnungsdaten):
            print(i)
            i.append('\u00a0')
            self.TABLE_DATA_2.append(i)

        self.gesamtpreis = f'{round(float(gesamtpreis), 2):.2f}'.replace('.', ',')
        self.TABLE_DATA_3.insert(0, ['', '', 'Gesamtbetrag:', self.gesamtpreis, '\u00a0'])

        self.diagnose = diagnose

        print(self.TABLE_DATA_1)
        print(self.TABLE_DATA_2)
        print(self.TABLE_DATA_3)

    def create_pages(self):
        self.add_page()
        self.set_margin(25)
        self.set_top_margin(10)
        self.set_left_margin(10)
        self.set_right_margin(10)

        self.set_font("helvetica", size=7)
        self.cell(self.rechnungsempfaenger_offset)
        self.write(txt='Mervi Fischbach - Schulgasse 9 - 86923 Finning')
        self.ln(3)

        self.set_font("helvetica", size=self.normal_font_size)
        self.cell(self.rechnungsempfaenger_offset)
        if self.mafr == 'Mann':
            self.write(txt='Herr\n')
        elif self.mafr == 'Frau':
            self.write(txt='Frau\n')
        self.cell(self.rechnungsempfaenger_offset)
        self.write(txt=f'{self.vorname} {self.nachname}\n')
        self.cell(self.rechnungsempfaenger_offset)
        self.write(txt=f'{self.strasse} {self.hausnummer}\n')
        self.cell(self.rechnungsempfaenger_offset)
        self.write(txt=f'{self.plz} {self.ort}\n')
        self.ln(27)

        self.cell(190, 0, border=1, center=True)
        self.set_font("helvetica", size=self.normal_font_size)
        with self.table(borders_layout='NONE', line_height=1.5 * self.font_size,
                        text_align=('LEFT', 'CENTER', 'RIGHT')) as table:
            for data_row in self.TABLE_DATA_1:
                row = table.row()
                for datum in data_row:
                    row.cell(datum)
        self.cell(190, 0, border=1, center=True)
        self.ln(5)

        self.set_font("helvetica", style='B', size=self.normal_font_size)
        if self.mafr == 'Mann':
            self.cell(25, txt='Patient:', align='L')
        elif self.mafr == 'Frau':
            self.cell(25, txt='Patientin:', align='L')
        self.set_font("helvetica", style='', size=self.normal_font_size)
        self.cell(40, txt=f'{self.vorname} {self.nachname}, geb. {self.geburtsdatum}')

        self.ln(7)
        self.set_font("helvetica", style='B', size=self.normal_font_size)
        self.cell(25, txt='Diagnose:', align='L')
        self.set_font("helvetica", style='', size=self.normal_font_size)
        self.multi_cell(160, txt=f'{self.diagnose}')

        # checking if page break is triggered by first table
        with self.offset_rendering() as dummy:
            dummy.ln(15)
            if self.mafr == 'Mann':
                dummy.write(txt=f'Sehr geehrter Herr {self.nachname},\n\n'
                               'hiermit erlaube ich mir, für meine Bemühungen folgendes Honorar zu berechnen:')
            if self.mafr == 'Frau':
                dummy.write(txt=f'Sehr geehrte Frau {self.nachname},\n\n'
                               'hiermit erlaube ich mir, für meine Bemühungen folgendes Honorar zu berechnen:')
            dummy.ln(7)
            dummy.set_font("helvetica", size=self.honorar_font_size)

            with dummy.table(cell_fill_color=230, cell_fill_mode="ROWS", borders_layout='SINGLE_TOP_LINE',
                             line_height=1.7 * self.font_size,
                             text_align=('CENTER', 'RIGHT', 'LEFT', 'RIGHT', 'LEFT'),
                             col_widths=(10, 8, 70, 10, 3)) as table:
                for data_row in self.TABLE_DATA_2:
                    row = table.row()
                    for index, datum in enumerate(data_row):
                        if index == 4:
                            dummy.set_font("symbol", size=self.honorar_font_size + 1)
                            row.cell(datum)
                            dummy.set_font("helvetica", style='', size=self.honorar_font_size)
                        else:
                            row.cell(datum)
            dummy.cell(190, 0, border=1, center=True)

            # check if page break is triggered by table2
            if dummy.page_no() == 1:
                with dummy.table(borders_layout='NONE', col_widths=(10, 8, 70, 10, 3), line_height=1.7 * self.font_size,
                                 text_align=('CENTER', 'LEFT', 'RIGHT', 'RIGHT', 'LEFT'),
                                 cell_fill_color=180, cell_fill_mode="NONE", first_row_as_headings=False) as table:
                    for data_row in self.TABLE_DATA_3:
                        row = table.row()
                        for index, datum in enumerate(data_row):
                            if index == 4:
                                dummy.set_font("symbol", '', size=self.honorar_font_size + 1)
                                row.cell(datum)
                                dummy.set_font("helvetica", style='', size=self.honorar_font_size)
                            else:
                                dummy.set_font("helvetica", style='B', size=self.honorar_font_size)
                                row.cell(datum)
                                dummy.set_font("helvetica", style='', size=self.honorar_font_size)

                # triggered by table 2
                if dummy.page_no() != 1:
                    linebreak_length = 25
                else:
                    linebreak_length = 15

            # triggered by table 1
            else:
                linebreak_length = 15

        # rendering the tables
        self.ln(linebreak_length)
        if self.mafr == 'Mann':
            self.write(txt=f'Sehr geehrter Herr {self.nachname},\n\n'
                            'hiermit erlaube ich mir, für meine Bemühungen folgendes Honorar zu berechnen:')
        if self.mafr == 'Frau':
            self.write(txt=f'Sehr geehrte Frau {self.nachname},\n\n'
                            'hiermit erlaube ich mir, für meine Bemühungen folgendes Honorar zu berechnen:')
        self.ln(7)
        self.set_font("helvetica", size=self.honorar_font_size)

        with self.table(cell_fill_color=230, cell_fill_mode="ROWS",
                         line_height=1.7 * self.font_size,
                         text_align=('CENTER', 'CENTER', 'LEFT', 'RIGHT', 'LEFT'),
                         col_widths=(10, 8, 70, 10, 3)) as table:
            for data_row in self.TABLE_DATA_2:
                row = table.row()
                for index, datum in enumerate(data_row):
                    if index == 4:
                        self.set_font("symbol", size=self.honorar_font_size + 1)
                        row.cell(datum)
                        self.set_font("helvetica", style='', size=self.honorar_font_size)
                    else:
                        row.cell(datum)
        self.cell(190, 0, border=1, center=True)

        with self.table(borders_layout='NONE', col_widths=(10, 8, 70, 10, 3), line_height=1.7 * self.font_size,
                         text_align=('CENTER', 'LEFT', 'RIGHT', 'RIGHT', 'LEFT'),
                         cell_fill_color=180, cell_fill_mode="NONE", first_row_as_headings=False) as table:
            for data_row in self.TABLE_DATA_3:
                row = table.row()
                for index, datum in enumerate(data_row):
                    if index == 4:
                        self.set_font("symbol", '', size=self.honorar_font_size + 1)
                        row.cell(datum)
                        self.set_font("helvetica", style='', size=self.honorar_font_size)
                    else:
                        self.set_font("helvetica", style='B', size=self.honorar_font_size)
                        row.cell(datum)
                        self.set_font("helvetica", style='', size=self.honorar_font_size)

        # rendering finished
        self.ln(3)

        with self.offset_rendering() as dummy:
            page_number_before = dummy.page_no()
            dummy.write(6.5, txt=f'Ich bitte Sie, den Gesamtbetrag von {self.gesamtpreis} ')
            dummy.set_font("symbol", size=self.normal_font_size + 1)
            dummy.write(6.5, txt='\u00a0 ')
            dummy.set_font("helvetica", size=self.normal_font_size)
            dummy.write(6.5,
                       txt='innerhalb von 14 Tagen unter Angabe der Rechnungsnummer auf unten stehendes Konto zu überweisen.')
            dummy.ln(13)
            dummy.write(txt='Mit freundlichen Grüßen')
            dummy.ln(10)
            dummy.write(txt='Mervi Fischbach')
            page_number_after = dummy.page_no()

        if page_number_before is not page_number_after:
            self.add_page()

        self.write(6.5, txt=f'Ich bitte Sie, den Gesamtbetrag von {self.gesamtpreis} ')
        self.set_font("symbol", size=self.normal_font_size + 1)
        self.write(6.5, txt='\u00a0 ')
        self.set_font("helvetica", size=self.normal_font_size)
        self.write(6.5,
                    txt='innerhalb von 14 Tagen unter Angabe der Rechnungsnummer auf unten stehendes Konto zu überweisen.')
        self.ln(13)
        self.write(txt='Mit freundlichen Grüßen')
        self.ln(10)
        self.write(txt='Mervi Fischbach')

        # export_filepath = f'{self.parent.parent.parent.rechnungen_location}/rechnungen-{self.parent.parent.parent.year}/{self.rechnungsnummer}H.pdf'
        export_filepath = './--sample-files/hprechnung2.pdf'
        self.output(export_filepath)
        return export_filepath


if __name__ == "__main__":
    app = App()
    # HpRechnung(1, ['FIMA', 'Mann', 'Fischbach', 'Matti', 'Schulgasse', '9', '86923', 'Finning', '29.11.2004', '10',
    #                'Dr. Moser', 'matti.fischbach@web.de', 'KG'], 'FIMA232323', '23.23.23', 20,
    #            [['23.23.23\n ', '100.0\n100.1', 'Allgemeine Untersuchung\nAllgemeine Untersuchung\nAllgemeine Untersuchung\nAllgemeine Untersuchung\nAllgemeine Untersuchung\nAllgemeine Untersuchung\n', '12000,50\n12000,50'],
    #             ['23.23.23\n ', '100.0\n100.1', 'Allgemeine Untersuchung\nAllgemeine Untersuchung\nAllgemeine Untersuchung\nAllgemeine Untersuchung\nAllgemeine Untersuchung\nAllgemeine Untersuchung\nAllgemeine Untersuchung\n', '12000,50\n12000,50'],
    #             ['23.23.23\n ', '100.0\n100.1', 'Allgemeine Untersuchung\nAllgemeine Untersuchung\nAllgemeine Untersuchung\nAllgemeine Untersuchung\nAllgemeine Untersuchung\n', '12000,50\n12000,50']]
    #            , 'Hallo was geht ab Freunde ich schriebe jetzt hier einen langen text um zu schauen ob sich der text wrapped')

