import fileinput
import logging
import os
import re
import sys
import time
import tkinter

import customtkinter
from fpdf import FPDF

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # checking dirs and creating missing ones
        if not os.path.exists("../System/version"):
            os.makedirs("../System/version")
            with open("../System/version/version.txt", "w") as f:
                f.write(str(time.strftime("%Y")))
            logging.info("Creating version file and dir")

        # getting version out of ./System/version/version.txt
        with open("../System/version/version.txt", "r") as f:
            f = f.readlines()
            for i, line in enumerate(f):
                f[i] = line.replace("\n", "")
            logging.info("Reading version file")

        self.version = str(f[0])
        logging.debug("Version: {0}".format(self.version))

        if not os.path.exists("./Rechnungen/Rechnungen{0}".format(self.version)):
            os.makedirs("./Rechnungen/Rechnungen{0}".format(self.version))
            logging.info("Creating Rechnungen{0} Ordner".format(self.version))

        if not os.path.exists("../Stammdaten"):
            os.makedirs("../Stammdaten")
            logging.info("Creating Stammdaten dir")

        if not os.path.exists("../Rechnungen/ZusammenfassungRechnungen"):
            os.makedirs("../Rechnungen/ZusammenfassungRechnungen")
            logging.info(("Creating ZusammenfassungRechnungen dir"))

        # configure window
        logging.debug("Configure bascic window")
        self.title("Rechnungsprogramm {0} - Mervi Kristina Fischbach".format(self.version))
        self.iconbitmap("./System/icon-blue.ico")
        # self.geometry("1123x580")
        self.resizable(width=False, height=False)
        self.minsize(width=1300, height=650)

        # configure grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # sidebar frame
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="ns")

        # sidebar configure grid layout
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        # sidebar label
        self.sidebar_label = customtkinter.CTkLabel(self.sidebar_frame, text="Rechnugsprogramm",
                                                    font=customtkinter.CTkFont(size=20, weight="bold"))
        self.sidebar_label.grid(row=0, column=0, padx=20, pady=(20, 0))
        self.sidebar_label_2 = customtkinter.CTkLabel(self.sidebar_frame, text=self.version,
                                                      font=customtkinter.CTkFont(size=18))
        self.sidebar_label_2.grid(row=1, column=0, padx=20, pady=(0, 20))

        # sidebar buttons
        self.sidebar_button_neue_rechnung = customtkinter.CTkButton(self.sidebar_frame, text="Neue Rechnung",
                                                                    command=self.sidebar_button_neue_rechnung_event)
        self.sidebar_button_neue_rechnung.grid(row=2, column=0, padx=20, pady=10)

        self.sidebar_button_stammdaten = customtkinter.CTkButton(self.sidebar_frame, text="Stammdaten",
                                                                 command=self.sidebar_button_stammdaten_event)
        self.sidebar_button_stammdaten.grid(row=3, column=0, padx=20, pady=10)

        self.sidebar_button_rechnung_loeschen = customtkinter.CTkButton(self.sidebar_frame, text="Rechnung Loeschen",
                                                                        command=self.sidebar_button_rechnung_loeschen_event)
        self.sidebar_button_rechnung_loeschen.grid(row=4, column=0, padx=20, pady=10)

        self.spacer_sidebar_1 = customtkinter.CTkLabel(self.sidebar_frame, text="")
        self.spacer_sidebar_1.grid(row=5, column=0, padx=0, pady=0, sticky="ns")

        self.sidebar_button_clear_screen = customtkinter.CTkButton(self.sidebar_frame, text="Clear Screen",
                                                                   command=self.clear_screen_event)
        self.sidebar_button_clear_screen.grid(row=6, column=0, padx=20, pady=10, sticky="s")
        self.sidebar_button_clear_screen.configure(state="disabled")

        self.sidebar_button_update_program = customtkinter.CTkButton(self.sidebar_frame, text="Upgdate Programmjahr",
                                                                     command=self.sidebar_button_update_version_event)
        self.sidebar_button_update_program.grid(row=7, column=0, padx=20, pady=10, sticky="s")

    # sidebar button events
    def sidebar_button_neue_rechnung_event(self):
        logging.info("Sidebar Button 'Neue Rechnungen' pressed")

        # clear screen
        self.clear_screen_event()

        # scrollable frame
        self.scrollable_main_frame_1 = customtkinter.CTkScrollableFrame(self, corner_radius=0)
        self.scrollable_main_frame_1.grid(row=0, column=1, padx=0, pady=0, sticky="nsew")

        # neue rechnung scrollable frame grid configure
        self.scrollable_main_frame_1.grid_columnconfigure(0, weight=1)

        self.neue_rechnung_label = customtkinter.CTkLabel(self.scrollable_main_frame_1, text="Neue Rechnung",
                                                          font=customtkinter.CTkFont(size=20, weight="bold",
                                                                                     underline=True))
        self.neue_rechnung_label.grid(row=0, column=0, padx=20, pady=(20, 40), sticky="ew")

        # main frame 1
        self.main_1 = customtkinter.CTkFrame(self.scrollable_main_frame_1, corner_radius=0)
        self.main_1.grid(row=1, column=0, padx=0, pady=0, sticky="ew")

        # main frame 1 grid configure
        self.main_1.columnconfigure(0, weight=1)

        # Kuerzel Eingabe
        self.kuerzel_frame = customtkinter.CTkFrame(self.main_1, corner_radius=0)
        self.kuerzel_frame.grid(row=0, column=0, padx=(10, 0), pady=5, sticky="ew")

        self.kuerzel_label = customtkinter.CTkLabel(self.kuerzel_frame, text="Kuerzel:")
        self.kuerzel_label.grid(row=0, column=0, padx=(42.5, 22.5), pady=10)
        self.kuerzel_entry = customtkinter.CTkEntry(self.kuerzel_frame, width=150, height=30,
                                                    font=customtkinter.CTkFont(size=15))
        self.kuerzel_entry.grid(row=0, column=1, padx=20, pady=10)
        self.kuerzel_entry.bind("<KeyRelease>", self.kuerzel_neue_rechnung_keystroke_check_event)

    def sidebar_button_stammdaten_event(self):
        logging.info("Sidebar Button 'Stammdaten' pressed")

        # clear screen
        self.clear_screen_event()

        # main frame
        self.scrollable_main_frame_2 = customtkinter.CTkScrollableFrame(self, corner_radius=0)
        self.scrollable_main_frame_2.grid(row=0, column=1, padx=0, pady=0, sticky="nsew")

        # stammdaten scrollable frame grid configure
        self.scrollable_main_frame_2.grid_columnconfigure(0, weight=1)

        self.stammdaten_label = customtkinter.CTkLabel(self.scrollable_main_frame_2, text="Stammdaten",
                                                       font=customtkinter.CTkFont(size=20, weight="bold",
                                                                                  underline=True))
        self.stammdaten_label.grid(row=0, column=0, padx=20, pady=(20, 40), sticky="ew")

        # main frame 2
        self.main_2 = customtkinter.CTkFrame(self.scrollable_main_frame_2, corner_radius=0)
        self.main_2.grid(row=2, column=0, padx=0, pady=0, sticky="ew")

        # main frame 2 grid configure
        self.main_2.columnconfigure(0, weight=1)

        # Kuerzel Eingabe
        self.kuerzel_frame = customtkinter.CTkFrame(self.main_2, corner_radius=0)
        self.kuerzel_frame.grid(row=0, column=0, padx=(10, 0), pady=5, sticky="ew")

        self.kuerzel_label = customtkinter.CTkLabel(self.kuerzel_frame, text="Kuerzel:")
        self.kuerzel_label.grid(row=0, column=0, padx=(42.5, 22.5), pady=10)
        self.kuerzel_entry = customtkinter.CTkEntry(self.kuerzel_frame, width=150, height=30,
                                                    font=customtkinter.CTkFont(size=15))
        self.kuerzel_entry.grid(row=0, column=1, padx=20, pady=10)
        self.kuerzel_entry.bind("<KeyRelease>", self.kuerzel_stammdaten_keystroke_check_event)

        # Stammdaten Anlegen
        self.stammdaten_anlegen_frame = customtkinter.CTkFrame(self.main_2, corner_radius=0)
        self.stammdaten_anlegen_frame.grid(row=1, column=0, padx=(10, 0), pady=5, sticky="ew")

        self.mann_frau_label = customtkinter.CTkLabel(self.stammdaten_anlegen_frame, text="Mann/Frau:")
        self.mann_frau_label.grid(row=0, column=0, padx=5, pady=10)
        self.mann_frau_entry = customtkinter.CTkEntry(self.stammdaten_anlegen_frame, width=150, height=30,
                                                      font=customtkinter.CTkFont(size=15))
        self.mann_frau_entry.grid(row=0, column=1, padx=5, pady=10)

        self.nachname_label = customtkinter.CTkLabel(self.stammdaten_anlegen_frame, text="Nachname:")
        self.nachname_label.grid(row=1, column=0, padx=5, pady=10)
        self.nachname_entry = customtkinter.CTkEntry(self.stammdaten_anlegen_frame, width=150, height=30,
                                                     font=customtkinter.CTkFont(size=15))
        self.nachname_entry.grid(row=1, column=1, padx=5, pady=10)

        self.vorname_label = customtkinter.CTkLabel(self.stammdaten_anlegen_frame, text="Vorname:")
        self.vorname_label.grid(row=2, column=0, padx=5, pady=10)
        self.vorname_entry = customtkinter.CTkEntry(self.stammdaten_anlegen_frame, width=150, height=30,
                                                    font=customtkinter.CTkFont(size=15))
        self.vorname_entry.grid(row=2, column=1, padx=5, pady=10)

        self.strasse_label = customtkinter.CTkLabel(self.stammdaten_anlegen_frame, text="Straße:")
        self.strasse_label.grid(row=3, column=0, padx=5, pady=10)
        self.strasse_entry = customtkinter.CTkEntry(self.stammdaten_anlegen_frame, width=150, height=30,
                                                    font=customtkinter.CTkFont(size=15))
        self.strasse_entry.grid(row=3, column=1, padx=5, pady=10)

        self.hausnummer_label = customtkinter.CTkLabel(self.stammdaten_anlegen_frame, text="Hausnummer:")
        self.hausnummer_label.grid(row=4, column=0, padx=5, pady=10)
        self.hausnummer_entry = customtkinter.CTkEntry(self.stammdaten_anlegen_frame, width=150, height=30,
                                                       font=customtkinter.CTkFont(size=15))
        self.hausnummer_entry.grid(row=4, column=1, padx=5, pady=10)

        self.plz_label = customtkinter.CTkLabel(self.stammdaten_anlegen_frame, text="PLZ:")
        self.plz_label.grid(row=5, column=0, padx=5, pady=10)
        self.plz_entry = customtkinter.CTkEntry(self.stammdaten_anlegen_frame, width=150, height=30,
                                                font=customtkinter.CTkFont(size=15))
        self.plz_entry.grid(row=5, column=1, padx=5, pady=10)

        self.ort_label = customtkinter.CTkLabel(self.stammdaten_anlegen_frame, text="Ort:")
        self.ort_label.grid(row=6, column=0, padx=5, pady=10)
        self.ort_entry = customtkinter.CTkEntry(self.stammdaten_anlegen_frame, width=150, height=30,
                                                font=customtkinter.CTkFont(size=15))
        self.ort_entry.grid(row=6, column=1, padx=5, pady=10)

        self.geburtsdatum_label = customtkinter.CTkLabel(self.stammdaten_anlegen_frame, text="Geburtsdatum:")
        self.geburtsdatum_label.grid(row=7, column=0, padx=5, pady=10)
        self.geburtsdatum_entry = customtkinter.CTkEntry(self.stammdaten_anlegen_frame, width=150, height=30,
                                                         font=customtkinter.CTkFont(size=15))
        self.geburtsdatum_entry.grid(row=7, column=1, padx=5, pady=10)

        self.kilometer_zu_fahren_label = customtkinter.CTkLabel(self.stammdaten_anlegen_frame,
                                                                text="Kilometer zu Fahren:")
        self.kilometer_zu_fahren_label.grid(row=8, column=0, padx=5, pady=10)
        self.kilometer_zu_fahren_entry = customtkinter.CTkEntry(self.stammdaten_anlegen_frame, width=150, height=30,
                                                                font=customtkinter.CTkFont(size=15))
        self.kilometer_zu_fahren_entry.grid(row=8, column=1, padx=5, pady=10)

        self.hausarzt_label = customtkinter.CTkLabel(self.stammdaten_anlegen_frame,
                                                     text="Hausarzt:")
        self.hausarzt_label.grid(row=9, column=0, padx=5, pady=10)
        self.hausarzt_entry = customtkinter.CTkEntry(self.stammdaten_anlegen_frame, width=150, height=30,
                                                     font=customtkinter.CTkFont(size=15))
        self.hausarzt_entry.grid(row=9, column=1, padx=5, pady=10)

        # Stammdaten abschicken

        self.stammdaten_abschicken_frame = customtkinter.CTkFrame(self.main_2,
                                                                  corner_radius=0)
        self.stammdaten_abschicken_frame.grid(row=2, column=0, padx=(10, 0), pady=5, sticky="ew")

        self.stammdaten_abschicken_button = customtkinter.CTkButton(self.stammdaten_abschicken_frame, text="Speichern",
                                                                    command=self.stammdaten_abschicken_button_event)
        self.stammdaten_abschicken_button.grid(row=0, column=0, padx=(5, 20), pady=5)

        self.stammdaten_error_msg = customtkinter.CTkLabel(self.stammdaten_abschicken_frame, text="")
        self.stammdaten_error_msg.grid(row=0, column=1, padx=5, pady=10)

    def sidebar_button_rechnung_loeschen_event(self):
        logging.info("Sidebar Button 'Rechnung Löschen' pressed")

        # clear screen
        self.clear_screen_event()

        # scrollable frame
        self.scrollable_main_frame_3 = customtkinter.CTkScrollableFrame(self, corner_radius=0)
        self.scrollable_main_frame_3.grid(row=0, column=1, padx=0, pady=0, sticky="nsew")

        # rechnung löschen scrollable frame grid configure
        self.scrollable_main_frame_3.grid_columnconfigure(0, weight=1)

        self.rechnung_loeschen_label = customtkinter.CTkLabel(self.scrollable_main_frame_3, text="Rechnung Loeschen",
                                                              font=customtkinter.CTkFont(size=20, weight="bold",
                                                                                         underline=True))
        self.rechnung_loeschen_label.grid(row=0, column=0, padx=20, pady=(20, 40), sticky="ew")

        # main frame
        self.main_3 = customtkinter.CTkFrame(self.scrollable_main_frame_3, corner_radius=0)
        self.main_3.grid(row=1, column=0, sticky="nsew")

        # main frame 3 grid configure
        self.main_3.columnconfigure(0, weight=1)

        # rechnungsnummer eingabe
        self.rechnungsnummer_frame = customtkinter.CTkFrame(self.main_3, corner_radius=0)
        self.rechnungsnummer_frame.grid(row=1, column=0, padx=(10, 0), pady=5, sticky="ew")

        self.rechnungsnummer_label = customtkinter.CTkLabel(self.rechnungsnummer_frame, text="Rechnungsnummer:")
        self.rechnungsnummer_label.grid(row=0, column=0, padx=(20, 0), pady=10)
        self.rechnungsnummer_entry = customtkinter.CTkEntry(self.rechnungsnummer_frame, width=150, height=30,
                                                            font=customtkinter.CTkFont(size=15))
        self.rechnungsnummer_entry.grid(row=0, column=1, padx=20, pady=10)

        self.jahr_updaten_error_msg = customtkinter.CTkLabel(self.rechnungsnummer_frame, text="")

        self.rechnung_loeschen_abschicken_button = customtkinter.CTkButton(self.rechnungsnummer_frame, text="Löschen",
                                                                           command=self.rechnung_loeschen_abschicken_button_event)
        self.rechnung_loeschen_abschicken_button.grid(row=1, column=1, padx=20, pady=5)

        self.rechnung_loeschen_bestaetigung_label = customtkinter.CTkLabel(self.rechnungsnummer_frame, text="Sicher?")
        self.rechnung_loeschen_bestaetigung_button = customtkinter.CTkButton(self.rechnungsnummer_frame,
                                                                             text="Bestätigen",
                                                                             command=self.rechnung_loeschen_bestaetigen_button_event)

    def sidebar_button_update_version_event(self):
        logging.info("Sidebar Button 'Update version' pressed")

        # clear screen
        self.clear_screen_event()

        # scrollable frame
        self.scrollable_main_frame_4 = customtkinter.CTkScrollableFrame(self, corner_radius=0)
        self.scrollable_main_frame_4.grid(row=0, column=1, padx=0, pady=0, sticky="nsew")

        # neue rechnung scrollable frame grid configure
        self.scrollable_main_frame_4.grid_columnconfigure(0, weight=1)

        self.update_version_label = customtkinter.CTkLabel(self.scrollable_main_frame_4, text="Neue Rechnung",
                                                          font=customtkinter.CTkFont(size=20, weight="bold",
                                                                                     underline=True))
        self.update_version_label.grid(row=0, column=0, padx=20, pady=(20, 40), sticky="ew")

        # main frame 4
        self.main_4 = customtkinter.CTkFrame(self.scrollable_main_frame_4, corner_radius=0)
        self.main_4.grid(row=1, column=0, padx=0, pady=0, sticky="ew")

        # main frame 4 grid configure
        self.main_4.columnconfigure(0, weight=1)

        # Jahr Eingabe
        self.jahr_updaten_frame = customtkinter.CTkFrame(self.main_4, corner_radius=0)
        self.jahr_updaten_frame.grid(row=0, column=0, padx=(10, 0), pady=5, sticky="ew")

        self.jahr_updaten_label = customtkinter.CTkLabel(self.jahr_updaten_frame, text="Jahr:")
        self.jahr_updaten_label.grid(row=0, column=0, padx=(42.5, 22.5), pady=10)
        self.jahr_updaten_entry = customtkinter.CTkEntry(self.jahr_updaten_frame, width=150, height=30,
                                                    font=customtkinter.CTkFont(size=15))
        self.jahr_updaten_entry.grid(row=0, column=1, padx=20, pady=10)

        self.jahr_updaten_error_msg = customtkinter.CTkLabel(self.jahr_updaten_frame, text="")

        self.jahr_updaten_button = customtkinter.CTkButton(self.jahr_updaten_frame, text="Updaten",
                                                                           command=self.jahr_updaten_button_event)
        self.jahr_updaten_button.grid(row=1, column=1, padx=20, pady=5)

        self.jahr_updaten_bestaetigung_label = customtkinter.CTkLabel(self.jahr_updaten_frame, text="Sicher?")
        self.jahr_updaten_bestaetigung_button = customtkinter.CTkButton(self.jahr_updaten_frame,
                                                                             text="Bestätigen",
                                                                             command=self.jahr_updaten_bestaetigen_button_event)

    # neue rechnung frame events
    def kuerzel_neue_rechnung_keystroke_check_event(self, t):
        logging.debug("Keystroke detected" + str(t))
        entry = self.kuerzel_entry.get().strip()

        if os.path.exists("./Stammdaten/" + entry + ".txt"):
            logging.info("stammdatei exists")
            with open("./Stammdaten/" + entry + ".txt", "r") as f:
                stammdaten = f.readlines()
                for i, line in enumerate(stammdaten):
                    stammdaten[i] = line.replace('\n', '')

            self.kuerzel_entry.delete(0, "end")
            self.kuerzel_entry.insert(0, stammdaten[0])
            self.neue_rechnung_interface()
            return True
        else:
            try:
                logging.error("Exception: stammdatei doesn't exist")
                logging.debug("clearing window")
                self.heutiges_datum_frame.grid_forget()
                self.heutiges_datum_frame.destroy()

                self.rechungsdaten_eingabe_frame.grid_forget()
                self.rechungsdaten_eingabe_frame.destroy()

                self.behandlungsart_frame.grid_forget()
                self.behandlungsart_frame.destroy()

                self.stammdaten_abschicken_button.grid_forget()
                self.stammdaten_abschicken_button.destroy()
            except:
                pass
            return False

    def radio_button_check_event(self):
        logging.info("radio button pressed")
        radio_on_off = self.radio_var.get()
        if radio_on_off == 1:
            logging.debug("radio-button: on")
            self.datum_eingabe_entry.delete(0, "end")
            self.datum_eingabe_entry.configure(state="disabled")
        elif radio_on_off == 0:
            logging.debug("radio-button: off")
            self.datum_eingabe_entry.configure(state="normal")

    def behandlungsarten_keystroke_check_event(self, t):
        self.behandlungsarten_error_1.grid_forget()
        global entry
        entry = self.behandlungsarten_anzahl_entry.get().strip()

        try:
            entry = int(entry)
        except:
            if entry == "":
                logging.debug("Exception: not '' -> clearing")
                self.behandlungsarten_entry_frame.grid_forget()
                try:
                    self.behandlungsart_1_label.grid_forget()
                    self.behandlungsart_1_entry.grid_forget()
                    self.behandlungskosten_1_label.grid_forget()
                    self.behandlungskosten_1_entry.grid_forget()
                    self.behandlungsart_2_label.grid_forget()
                    self.behandlungsart_2_entry.grid_forget()
                    self.behandlungskosten_2_label.grid_forget()
                    self.behandlungskosten_2_entry.grid_forget()
                    self.behandlungsart_3_label.grid_forget()
                    self.behandlungsart_3_entry.grid_forget()
                    self.behandlungskosten_3_label.grid_forget()
                    self.behandlungskosten_3_entry.grid_forget()
                    self.behandlungsart_4_label.grid_forget()
                    self.behandlungsart_4_entry.grid_forget()
                    self.behandlungskosten_4_label.grid_forget()
                    self.behandlungskosten_4_entry.grid_forget()
                    self.behandlungsart_5_label.grid_forget()
                    self.behandlungsart_5_entry.grid_forget()
                    self.behandlungskosten_5_label.grid_forget()
                    self.behandlungskosten_5_entry.grid_forget()
                except:
                    pass
                return
            elif not isinstance(entry, int):
                logging.debug("Exception: Only integer -> clearing")
                self.info_message("neue_rechnung", "Error: only integer/float -> (Zahlen mit Punkt als Komma)", "red")

                self.behandlungsarten_anzahl_entry.delete(0, "end")
                self.behandlungsarten_entry_frame.grid_forget()
                try:
                    self.behandlungsart_1_label.grid_forget()
                    self.behandlungsart_1_entry.grid_forget()
                    self.behandlungskosten_1_label.grid_forget()
                    self.behandlungskosten_1_entry.grid_forget()
                    self.behandlungsart_2_label.grid_forget()
                    self.behandlungsart_2_entry.grid_forget()
                    self.behandlungskosten_2_label.grid_forget()
                    self.behandlungskosten_2_entry.grid_forget()
                    self.behandlungsart_3_label.grid_forget()
                    self.behandlungsart_3_entry.grid_forget()
                    self.behandlungskosten_3_label.grid_forget()
                    self.behandlungskosten_3_entry.grid_forget()
                    self.behandlungsart_4_label.grid_forget()
                    self.behandlungsart_4_entry.grid_forget()
                    self.behandlungskosten_4_label.grid_forget()
                    self.behandlungskosten_4_entry.grid_forget()
                    self.behandlungsart_5_label.grid_forget()
                    self.behandlungsart_5_entry.grid_forget()
                    self.behandlungskosten_5_label.grid_forget()
                    self.behandlungskosten_5_entry.grid_forget()
                except:
                    pass
                return

        if entry > 5:
            logging.debug("Exception: entry > 5 -> entry = 5")
            self.info_message("neue_rechnung", "Error: max value 5", "red")

            self.behandlungsarten_anzahl_entry.delete(0, "end")
            self.behandlungsarten_anzahl_entry.insert("end", int(5))

        if entry >= 1:
            self.behandlungsarten_entry_frame.grid(row=4, column=0, pady=5, padx=(5, 0), sticky="nsew")
            self.behandlungsart_1_label.grid(row=0, column=0, padx=(5, 5), pady=10)
            self.behandlungsart_1_entry.grid(row=0, column=1, padx=(0, 5), pady=10)
            self.behandlungskosten_1_label.grid(row=0, column=2, padx=(15, 5), pady=10)
            self.behandlungskosten_1_entry.grid(row=0, column=3, padx=(0, 5), pady=10)
            if entry >= 2:
                self.behandlungsart_2_label.grid(row=1, column=0, padx=(5, 5), pady=10)
                self.behandlungsart_2_entry.grid(row=1, column=1, padx=(0, 5), pady=10)
                self.behandlungskosten_2_label.grid(row=1, column=2, padx=(15, 5), pady=10)
                self.behandlungskosten_2_entry.grid(row=1, column=3, padx=(0, 5), pady=10)
                if entry >= 3:
                    self.behandlungsart_3_label.grid(row=2, column=0, padx=(5, 5), pady=10)
                    self.behandlungsart_3_entry.grid(row=2, column=1, padx=(0, 5), pady=10)
                    self.behandlungskosten_3_label.grid(row=2, column=2, padx=(15, 5), pady=10)
                    self.behandlungskosten_3_entry.grid(row=2, column=3, padx=(0, 5), pady=10)
                    if entry >= 4:
                        self.behandlungsart_4_label.grid(row=3, column=0, padx=(5, 5), pady=10)
                        self.behandlungsart_4_entry.grid(row=3, column=1, padx=(0, 5), pady=10)
                        self.behandlungskosten_4_label.grid(row=3, column=2, padx=(15, 5), pady=10)
                        self.behandlungskosten_4_entry.grid(row=3, column=3, padx=(0, 5), pady=10)
                        if entry >= 5:
                            self.behandlungsart_5_label.grid(row=4, column=0, padx=(5, 5), pady=10)
                            self.behandlungsart_5_entry.grid(row=4, column=1, padx=(0, 5), pady=10)
                            self.behandlungskosten_5_label.grid(row=4, column=2, padx=(15, 5), pady=10)
                            self.behandlungskosten_5_entry.grid(row=4, column=3, padx=(0, 5), pady=10)

    def neue_rechnung_interface(self):
        logging.debug("configuring 'neue rechnungen' interface")
        # Heutiges Datum
        self.heutiges_datum_frame = customtkinter.CTkFrame(self.main_1, corner_radius=0)
        self.heutiges_datum_frame.grid(row=2, column=0, pady=5, padx=(10, 0), sticky="ew")
        self.radio_var = tkinter.IntVar(value=1)

        self.heutiges_datum_frame.grid_columnconfigure(2, weight=1)

        self.heutiges_datum_radio_button_label = customtkinter.CTkLabel(self.heutiges_datum_frame,
                                                                        text="Heutiges Datum (" + str(
                                                                            time.strftime("%d.%m.%y")) + "):")
        self.heutiges_datum_radio_button_label.grid(row=0, column=0, padx=(5, 0), pady=10)

        self.heutiges_datum_radio_button_1 = customtkinter.CTkRadioButton(master=self.heutiges_datum_frame, text="Ja",
                                                                          command=self.radio_button_check_event,
                                                                          variable=self.radio_var, value=1)
        self.heutiges_datum_radio_button_1.grid(row=0, column=1, padx=0, pady=5)
        self.heutiges_datum_radio_button_2 = customtkinter.CTkRadioButton(master=self.heutiges_datum_frame, text="Nein",
                                                                          command=self.radio_button_check_event,
                                                                          variable=self.radio_var, value=0,
                                                                          )
        self.heutiges_datum_radio_button_2.grid(row=0, column=2, padx=0, pady=5, sticky="w")

        self.datum_eingabe_label = customtkinter.CTkLabel(self.heutiges_datum_frame, text="Anderes Datum (mm.dd.yy):")
        self.datum_eingabe_label.grid(row=1, column=0, padx=5, pady=10)
        self.datum_eingabe_entry = customtkinter.CTkEntry(self.heutiges_datum_frame, width=150, height=30,
                                                          font=customtkinter.CTkFont(size=15))
        self.datum_eingabe_entry.grid(row=1, column=1, padx=30, pady=10)
        self.datum_eingabe_entry.configure(state="disabled")

        # Rechnungsdaten
        self.rechungsdaten_eingabe_frame = customtkinter.CTkFrame(self.main_1, corner_radius=0)
        self.rechungsdaten_eingabe_frame.grid(row=3, column=0, pady=5, padx=(10, 0), sticky="ew")

        self.rechnungsdaten_eingabe_label = customtkinter.CTkLabel(self.rechungsdaten_eingabe_frame,
                                                                   text="Rechnungsdaten-Eingabe")
        self.rechnungsdaten_eingabe_label.grid(row=0, column=0, padx=20, pady=(20, 0))

        self.rechnungsdaten_format_label = customtkinter.CTkLabel(self.rechungsdaten_eingabe_frame,
                                                                  text="Format: dd.mm.yy",
                                                                  font=customtkinter.CTkFont(size=13))
        self.rechnungsdaten_format_label.grid(row=1, column=0, padx=0, pady=0)

        #
        # Row 1
        #

        self.datum1_label = customtkinter.CTkLabel(self.rechungsdaten_eingabe_frame, text="Datum 1:").grid(row=2,
                                                                                                           column=0,
                                                                                                           padx=5,
                                                                                                           pady=10)
        self.datum1_entry = customtkinter.CTkEntry(self.rechungsdaten_eingabe_frame, width=150, height=30,
                                                   font=customtkinter.CTkFont(size=15))
        self.datum1_entry.grid(row=2, column=1, padx=0, pady=10)
        ###

        self.datum2_label = customtkinter.CTkLabel(self.rechungsdaten_eingabe_frame, text="Datum 2:").grid(row=2,
                                                                                                           column=2,
                                                                                                           padx=5,
                                                                                                           pady=10)
        self.datum2_entry = customtkinter.CTkEntry(self.rechungsdaten_eingabe_frame, width=150, height=30,
                                                   font=customtkinter.CTkFont(size=15))
        self.datum2_entry.grid(row=2, column=3, padx=0, pady=10)
        ###

        self.datum3_label = customtkinter.CTkLabel(self.rechungsdaten_eingabe_frame, text="Datum 3:").grid(row=2,
                                                                                                           column=4,
                                                                                                           padx=5,
                                                                                                           pady=10)
        self.datum3_entry = customtkinter.CTkEntry(self.rechungsdaten_eingabe_frame, width=150, height=30,
                                                   font=customtkinter.CTkFont(size=15))
        self.datum3_entry.grid(row=2, column=5, padx=0, pady=10)
        ###

        self.datum4_label = customtkinter.CTkLabel(self.rechungsdaten_eingabe_frame, text="Datum 4:").grid(row=2,
                                                                                                           column=6,
                                                                                                           padx=5,
                                                                                                           pady=10)
        self.datum4_entry = customtkinter.CTkEntry(self.rechungsdaten_eingabe_frame, width=150, height=30,
                                                   font=customtkinter.CTkFont(size=15))
        self.datum4_entry.grid(row=2, column=7, padx=(0, 5), pady=10)

        #
        # Row 2
        #

        self.datum5_label = customtkinter.CTkLabel(self.rechungsdaten_eingabe_frame, text="Datum 5:").grid(row=3,
                                                                                                           column=0,
                                                                                                           padx=5,
                                                                                                           pady=10)
        self.datum5_entry = customtkinter.CTkEntry(self.rechungsdaten_eingabe_frame, width=150, height=30,
                                                   font=customtkinter.CTkFont(size=15))
        self.datum5_entry.grid(row=3, column=1, padx=0, pady=10)
        ###

        self.datum6_label = customtkinter.CTkLabel(self.rechungsdaten_eingabe_frame, text="Datum 6:").grid(row=3,
                                                                                                           column=2,
                                                                                                           padx=5,
                                                                                                           pady=10)
        self.datum6_entry = customtkinter.CTkEntry(self.rechungsdaten_eingabe_frame, width=150, height=30,
                                                   font=customtkinter.CTkFont(size=15))
        self.datum6_entry.grid(row=3, column=3, padx=0, pady=10)
        ###

        self.datum7_label = customtkinter.CTkLabel(self.rechungsdaten_eingabe_frame, text="Datum 7:").grid(row=3,
                                                                                                           column=4,
                                                                                                           padx=5,
                                                                                                           pady=10)
        self.datum7_entry = customtkinter.CTkEntry(self.rechungsdaten_eingabe_frame, width=150, height=30,
                                                   font=customtkinter.CTkFont(size=15))
        self.datum7_entry.grid(row=3, column=5, padx=0, pady=10)
        ###

        self.datum8_label = customtkinter.CTkLabel(self.rechungsdaten_eingabe_frame, text="Datum 8:").grid(row=3,
                                                                                                           column=6,
                                                                                                           padx=5,
                                                                                                           pady=10)
        self.datum8_entry = customtkinter.CTkEntry(self.rechungsdaten_eingabe_frame, width=150, height=30,
                                                   font=customtkinter.CTkFont(size=15))
        self.datum8_entry.grid(row=3, column=7, padx=(0, 5), pady=10)

        #
        # Row 3
        #

        self.datum9_label = customtkinter.CTkLabel(self.rechungsdaten_eingabe_frame, text="Datum 9:").grid(row=4,
                                                                                                           column=0,
                                                                                                           padx=5,
                                                                                                           pady=10)
        self.datum9_entry = customtkinter.CTkEntry(self.rechungsdaten_eingabe_frame, width=150, height=30,
                                                   font=customtkinter.CTkFont(size=15))
        self.datum9_entry.grid(row=4, column=1, padx=(0, 5), pady=10)
        ###

        self.datum10_label = customtkinter.CTkLabel(self.rechungsdaten_eingabe_frame, text="Datum 10:").grid(row=4,
                                                                                                             column=2,
                                                                                                             padx=5,
                                                                                                             pady=10)
        self.datum10_entry = customtkinter.CTkEntry(self.rechungsdaten_eingabe_frame, width=150, height=30,
                                                    font=customtkinter.CTkFont(size=15))
        self.datum10_entry.grid(row=4, column=3, padx=(0, 5), pady=10)

        # behandlungsarten
        self.behandlungsart_frame = customtkinter.CTkFrame(self.main_1, corner_radius=0)
        self.behandlungsart_frame.grid(row=4, column=0, pady=5, padx=(10, 0), sticky="ew")

        self.behandlungsarten_main_label = customtkinter.CTkLabel(self.behandlungsart_frame, text="Behandlungsarten",
                                                                  font=customtkinter.CTkFont(size=15, underline=True))
        self.behandlungsarten_main_label.grid(row=0, column=0, padx=20, pady=(20, 0))

        self.behandlungsarten_anzahl_frame = customtkinter.CTkFrame(self.behandlungsart_frame, corner_radius=0)
        self.behandlungsarten_anzahl_frame.grid(row=1, column=0, padx=(5, 0), pady=5, sticky="nsew")

        self.behandlungsarten_anzahl_label = customtkinter.CTkLabel(self.behandlungsarten_anzahl_frame,
                                                                    text="Anzahl Behandlungsarten (max 5):")
        self.behandlungsarten_anzahl_label.grid(row=1, column=0, padx=(5, 5), pady=10)
        self.behandlungsarten_anzahl_entry = customtkinter.CTkEntry(self.behandlungsarten_anzahl_frame, width=150,
                                                                    height=30,
                                                                    font=customtkinter.CTkFont(size=15))
        self.behandlungsarten_anzahl_entry.grid(row=1, column=1, padx=(0, 5), pady=10)
        self.behandlungsarten_error_1 = customtkinter.CTkLabel(self.behandlungsarten_anzahl_frame, text="",
                                                               text_color="red")
        self.behandlungsarten_error_2 = customtkinter.CTkLabel(self.behandlungsarten_anzahl_frame, text="",
                                                               text_color="red")

        self.behandlungsarten_anzahl_entry.bind("<KeyRelease>", self.behandlungsarten_keystroke_check_event)

        # Behandlungsart 1
        self.behandlungsarten_entry_frame = customtkinter.CTkFrame(self.behandlungsart_frame, corner_radius=0)

        # Row 1
        self.behandlungsart_1_label = customtkinter.CTkLabel(self.behandlungsarten_entry_frame,
                                                             text="Behandlungsart 1:")
        self.behandlungsart_1_entry = customtkinter.CTkEntry(self.behandlungsarten_entry_frame, width=413,
                                                             height=30, font=customtkinter.CTkFont(size=15))
        self.behandlungskosten_1_label = customtkinter.CTkLabel(self.behandlungsarten_entry_frame,
                                                                text="Einzelpreis (Format: 00.00): ")
        self.behandlungskosten_1_entry = customtkinter.CTkEntry(self.behandlungsarten_entry_frame, width=150,
                                                                height=30, font=customtkinter.CTkFont(size=15))

        # Row 2
        self.behandlungsart_2_label = customtkinter.CTkLabel(self.behandlungsarten_entry_frame,
                                                             text="Behandlungsart 2:")
        self.behandlungsart_2_entry = customtkinter.CTkEntry(self.behandlungsarten_entry_frame, width=413,
                                                             height=30, font=customtkinter.CTkFont(size=15))
        self.behandlungskosten_2_label = customtkinter.CTkLabel(self.behandlungsarten_entry_frame,
                                                                text="Einzelpreis (Format: 00.00): ")
        self.behandlungskosten_2_entry = customtkinter.CTkEntry(self.behandlungsarten_entry_frame, width=150,
                                                                height=30, font=customtkinter.CTkFont(size=15))

        # Row 3
        self.behandlungsart_3_label = customtkinter.CTkLabel(self.behandlungsarten_entry_frame,
                                                             text="Behandlungsart 3:")
        self.behandlungsart_3_entry = customtkinter.CTkEntry(self.behandlungsarten_entry_frame, width=413,
                                                             height=30, font=customtkinter.CTkFont(size=15))
        self.behandlungskosten_3_label = customtkinter.CTkLabel(self.behandlungsarten_entry_frame,
                                                                text="Einzelpreis (Format: 00.00): ")
        self.behandlungskosten_3_entry = customtkinter.CTkEntry(self.behandlungsarten_entry_frame, width=150,
                                                                height=30, font=customtkinter.CTkFont(size=15))

        # Row 4
        self.behandlungsart_4_label = customtkinter.CTkLabel(self.behandlungsarten_entry_frame,
                                                             text="Behandlungsart 4:")
        self.behandlungsart_4_entry = customtkinter.CTkEntry(self.behandlungsarten_entry_frame, width=413,
                                                             height=30, font=customtkinter.CTkFont(size=15))
        self.behandlungskosten_4_label = customtkinter.CTkLabel(self.behandlungsarten_entry_frame,
                                                                text="Einzelpreis (Format: 00.00): ")
        self.behandlungskosten_4_entry = customtkinter.CTkEntry(self.behandlungsarten_entry_frame, width=150,
                                                                height=30, font=customtkinter.CTkFont(size=15))

        # Row 5
        self.behandlungsart_5_label = customtkinter.CTkLabel(self.behandlungsarten_entry_frame,
                                                             text="Behandlungsart 5:")
        self.behandlungsart_5_entry = customtkinter.CTkEntry(self.behandlungsarten_entry_frame, width=413,
                                                             height=30, font=customtkinter.CTkFont(size=15))
        self.behandlungskosten_5_label = customtkinter.CTkLabel(self.behandlungsarten_entry_frame,
                                                                text="Einzelpreis (Format: 00.00): ")
        self.behandlungskosten_5_entry = customtkinter.CTkEntry(self.behandlungsarten_entry_frame, width=150,
                                                                height=30, font=customtkinter.CTkFont(size=15))

        # Abschließen
        self.rechnung_abschicken_frame = customtkinter.CTkFrame(self.main_1, corner_radius=0)
        self.rechnung_abschicken_frame.grid(row=5, column=0, padx=(10, 0), pady=5, sticky="ew")

        self.rechnung_abschicken_button = customtkinter.CTkButton(self.rechnung_abschicken_frame, text="Speichern",
                                                                  command=self.neue_rechnung_abschicken_button_event)
        self.rechnung_abschicken_button.grid(row=0, column=0, padx=(5, 20), pady=5)

        self.rechnung_error_msg = customtkinter.CTkLabel(self.rechnung_abschicken_frame, text="")
        self.rechnung_error_msg.grid(row=0, column=1, padx=5, pady=10)

    def neue_rechnung_abschicken_button_event(self):
        logging.info("'Neue Rechnung': fetching data and calculating")
        logging.debug("'abschicken-button' disabled")

        self.info_message("neue_rechnung", "couldn't convert 'anzahl behandlungsdaten' into integer", "red")
        self.rechnung_abschicken_button.configure(state="disabled")
        entry = self.kuerzel_entry.get().strip()

        # Stammdaten abrufen
        logging.info("open/read 'Stammdaten' file")
        with open("./Stammdaten/" + entry + ".txt", 'r') as f:
            stammdaten = f.readlines()

        for i, line in enumerate(stammdaten):
            stammdaten[i] = line.replace('\n', '')

        # Heutiges/Anderes Datum
        logging.info("check radio-button 'Heutiges Datum'")
        heutiges_datum_on_off = self.radio_var.get()
        global heutiges_anderes_datum
        heutiges_anderes_datum = None

        if heutiges_datum_on_off == 0:
            heutiges_anderes_datum = self.datum_eingabe_entry.get().strip()
            heutiges_anderes_datum.replace("\n", "")
            logging.debug("use date out of entry")
        elif heutiges_datum_on_off == 1:
            heutiges_anderes_datum = time.strftime("%d.%m.%y")
            logging.debug("use todays date")

        # Rechnungsnummer
        rechnungsnummer = (stammdaten[0] + heutiges_anderes_datum.replace(".", ""))
        logging.info("Rechnungsnummer: " + str(rechnungsnummer))

        # fetch dates
        logging.info("fetching 'Datum' out of entrys")
        daten_liste = [self.datum1_entry.get().strip(),
                       self.datum2_entry.get().strip(),
                       self.datum3_entry.get().strip(),
                       self.datum4_entry.get().strip(),
                       self.datum5_entry.get().strip(),
                       self.datum6_entry.get().strip(),
                       self.datum7_entry.get().strip(),
                       self.datum8_entry.get().strip(),
                       self.datum9_entry.get().strip(),
                       self.datum10_entry.get().strip()]
        empty_dates = 0
        num = -1
        daten_liste_sorted = []
        for i in daten_liste:
            num += 1
            if i != "":
                daten_liste_sorted.append(daten_liste[num])
            elif i == "":
                empty_dates += 1

        datenanzahl = 10 - empty_dates
        while empty_dates > 0:
            daten_liste_sorted.append("")
            empty_dates -= 1

        # Behandlungsarten
        logging.info("fetching 'Behandlungsarten' out of entrys")
        anzahl_behandlungsarten = self.behandlungsarten_anzahl_entry.get().strip()

        try:
            anzahl_behandlungsarten = int(anzahl_behandlungsarten)
        except:
            logging.error("couldn't convert 'anzahl behandlungsdaten' into integer")

        behandlungsarten_kosten_liste = []
        behandlungsarten_bezeichnung_liste = []

        if anzahl_behandlungsarten is not None and anzahl_behandlungsarten != "" and isinstance(anzahl_behandlungsarten,
                                                                                                int):
            if anzahl_behandlungsarten >= 1:
                logging.debug("fetching 'Behandlungsarten 1'")
                behandlungsarten_bezeichnung_liste.append(self.behandlungsart_1_entry.get().strip())
                behandlungsarten_kosten_liste.append(self.behandlungskosten_1_entry.get().strip())
                if anzahl_behandlungsarten >= 2:
                    logging.debug("fetching 'Behandlungsarten 2'")
                    behandlungsarten_bezeichnung_liste.append(self.behandlungsart_2_entry.get().strip())
                    behandlungsarten_kosten_liste.append(self.behandlungskosten_2_entry.get().strip())
                    if anzahl_behandlungsarten >= 3:
                        logging.debug("fetching 'Behandlungsarten 3'")
                        behandlungsarten_bezeichnung_liste.append(
                            self.behandlungsart_3_entry.get().strip())
                        behandlungsarten_kosten_liste.append(self.behandlungskosten_3_entry.get().strip())
                        if anzahl_behandlungsarten >= 4:
                            logging.debug("fetching 'Behandlungsarten 4'")
                            behandlungsarten_bezeichnung_liste.append(
                                self.behandlungsart_4_entry.get().strip())
                            behandlungsarten_kosten_liste.append(
                                self.behandlungskosten_4_entry.get().strip())
                            if anzahl_behandlungsarten >= 5:
                                logging.debug("fetching 'Behandlungsarten 5'")
                                behandlungsarten_bezeichnung_liste.append(
                                    self.behandlungsart_5_entry.get().strip())
                                behandlungsarten_kosten_liste.append(
                                    self.behandlungskosten_5_entry.get().strip())

        logging.info("all fetched")

        '''print(rechnungsnummer, heutiges_anderes_datum, stammdaten, daten_liste, daten_liste_sorted, datenanzahl,
              behandlungsarten_bezeichnung_liste, behandlungsarten_kosten_liste)'''

        self.pdf_erstellen(rechnungsnummer, heutiges_anderes_datum, stammdaten, daten_liste_sorted, datenanzahl,
                           behandlungsarten_bezeichnung_liste, behandlungsarten_kosten_liste)

    def pdf_erstellen(self, rechnungsnummer, datum, stammdaten, daten_liste, datenzahl,
                      behandlungsarten_bezeichnung_liste,
                      behandlungsarten_kosten_liste):
        # Stammdaten convert
        kuerzel = stammdaten[0]
        mafr = stammdaten[1]
        nachname = stammdaten[2]
        vorname = stammdaten[3]
        strasse = stammdaten[4]
        hausnummer = stammdaten[5]
        plz = stammdaten[6]
        ort = stammdaten[7]
        geburtsdatum = stammdaten[8]
        kmzufahren = stammdaten[9]
        hausarzt = stammdaten[10]

        pdf = FPDF()
        # Header 1
        pdf.add_page()
        pdf.set_font("Arial", "B""U", 25)
        pdf.set_text_color(255, 0, 0)
        pdf.set_draw_color(255, 0, 0)
        pdf.cell(1)
        pdf.cell(0, 10, "Rechnung", border=1, ln=1, align="C")

        # Header 2
        pdf.set_font("Arial", "B", 15)
        pdf.set_text_color(255, 0, 0)
        pdf.cell(1)
        pdf.cell(0, 7, "Mervi Fischbach", ln=1, align="C")

        # Header 3
        pdf.set_font("Arial", "B", 15)
        pdf.set_text_color(255, 0, 0)
        pdf.cell(1)
        pdf.cell(0, 7, "Physiotherapeutin", ln=1, align="C")

        # Header 3
        pdf.set_font("Arial", "B", 13)
        pdf.set_text_color(255, 0, 0)
        pdf.cell(0, 3.5, "", ln=1, align="C")
        pdf.cell(1)
        pdf.cell(0, 6, "Schulgasse 9    86923 Finning", ln=1, align="C")

        # Abschnitt 1
        pdf.set_font("Arial", "", 12)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 4, "", ln=1, align="C")
        if mafr == "Mann":
            pdf.write(6.5, "Herr " + vorname + " " + nachname)
        elif mafr == "Frau":
            pdf.write(6.5, "Frau " + vorname + " " + nachname)
        pdf.cell(0, 5, "", ln=1, align="C")
        pdf.write(6.5, "" + strasse + " " + hausnummer)
        pdf.cell(0, 10, "", ln=1, align="C")
        pdf.set_font("Arial", "B", 12)
        pdf.write(6.5, "" + plz + " " + ort)

        # Abschnitt 2
        pdf.set_font("Arial", "B", 13)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 15, "", ln=1, align="C")
        pdf.write(6.5,
                  "Patient" + "                                              " + "Rechnungsnummer" + "                                        " + "Datum")
        pdf.set_font("Arial", "", 13)
        pdf.cell(0, 6, "", ln=1, align="C")
        pdf.write(6.5,
                  "" + kuerzel + "                                                     " + rechnungsnummer + "                                            " + str(
                      datum))

        # Abschnitt 3
        pdf.cell(0, 15, "", ln=1, align="C")
        pdf.set_font("Arial", "B", 12)
        pdf.write(6.5, "" + str(datenzahl) + " Behandlungstermine:\n")
        pdf.set_font("Arial", "", 12)
        pdf.write(6.5, "" + daten_liste[0] + "             " + daten_liste[1] + " \n")
        pdf.write(6.5, "" + daten_liste[2] + "             " + daten_liste[3] + " \n")
        pdf.write(6.5, "" + daten_liste[4] + "             " + daten_liste[5] + " \n")
        pdf.write(6.5, "" + daten_liste[6] + "             " + daten_liste[7] + " \n")
        pdf.write(6.5, "" + daten_liste[8] + "             " + daten_liste[9] + "\n")

        # Abschnitt 4
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, "", ln=1, align="C")
        if mafr == "Mann":
            pdf.write(6.5, "Sehr geehrter Herr " + nachname + ",\n")
            pdf.write(8, "hiermit erlaube ich mir, für meine Bemühungen folgendes Honorar zu berechnen:")
        elif mafr == "Frau":
            pdf.write(6.5, "Sehr geehrte Frau " + nachname + ",\n")
            pdf.write(8, "hiermit erlaube ich mir, für meine Bemühungen folgendes Honorar zu berechnen:")

        # Abschnitt 5
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 12, "", ln=1, align="C")
        pdf.write(6.5, "1      Anamnese + Befunderhebung;          ")
        pdf.set_font("Arial", "B", 12)
        pdf.write(6.5, "Einzelpreis: 00,00 Euro\n")

        # Behandlungsarten
        for i, data in enumerate(behandlungsarten_kosten_liste):
            try:
                data = int(data)
            except:
                try:
                    data = float(data)
                except:
                    logging.error("Error in 'Behandlungskosten': Nur float oder int")

                    self.info_message("neue_rechnung", "Error in 'Behandlungskosten': Nur float oder int", "red")
                    return None

        for i, data in enumerate(behandlungsarten_bezeichnung_liste):
            if data == "" or data is None:
                logging.error("Error in 'Behandlungskosten': Felder nicht gefüllt")

                self.info_message("neue_rechnung", "Error in 'Behandlungskosten': Felder nicht gefüllt", "red")
                return None

        global gesamtpreis
        gesamtpreis = 0
        for i, data in enumerate(behandlungsarten_kosten_liste):
            # Addition of 'Einzelpreise'
            gesamtpreis += datenzahl * float(data)

            # format 'Einzelpreis' to 2 decimals (2.3 -> 2.30)
            data = float(data)
            position_point = str(data).find(".") + 1
            decimals = str(data)[position_point:]
            if len(decimals) == 1:
                data = str(data) + "0"
            data = str(data).replace('.', ',')

            # write to PDF
            pdf.set_font("Arial", "", 12)
            pdf.write(6.5, "" + str(datenzahl) + "      " + str(behandlungsarten_bezeichnung_liste[i]) + ";          ")
            pdf.set_font("Arial", "B", 12)
            pdf.write(6.5, "Einzelpreis: " + str(data) + " Euro\n")

        # Abschnitt 6
        gesamtpreis = float(gesamtpreis)
        position_point = str(gesamtpreis).find(".") + 1
        decimals = str(gesamtpreis)[position_point:]
        if len(decimals) == 1:
            gesamtpreis = str(gesamtpreis) + "0"
        gesamtpreis = gesamtpreis.replace('.', ',')

        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 6, "", ln=1, align="C")
        pdf.write(6.5, "Ich bitte Sie, den Gesamtbetrag von " + str(
            gesamtpreis) + " Euro innerhalb von 14 Tagen unter Angabe der Rechnungsnummer auf unten stehendes Konto zu überweisen.")
        pdf.cell(0, 13, "", ln=1, align="C")
        pdf.set_font("Arial", "", 13)
        pdf.write(6.5, "Mit freundlichen Grüßen")
        pdf.cell(0, 20, "", ln=1, align="C")
        pdf.write(6.5, "Mervi Fischbach")

        # Abschnitt 7
        pdf.set_font("Arial", "B", 10)
        pdf.set_text_color(0, 0, 0)
        pdf.set_draw_color(0, 0, 0)
        pdf.cell(0, 10, "", ln=1, align="C")
        pdf.cell(1)
        pdf.cell(0, 3, "Bankverbindung", ln=1, align="C")
        pdf.cell(0, 3, "ING Diba", ln=1, align="C")
        pdf.cell(0, 3, "IBAN - DE 20 500 105 17 540 350 6861", ln=1, align="C")
        pdf.cell(0, 3, "BIC - INGDDEFFXXX", ln=1, align="C")
        pdf.set_font("Arial", "B", 8)
        pdf.cell(0, 3, "Steuer Nummer: 131-217-00314", ln=1, align="C")

        # Lines
        pdf.set_draw_color(0, 0, 0)
        pdf.line(10, 93, 200, 93)
        pdf.line(10, 73, 200, 73)
        pdf.line(10, 143, 200, 143)

        # Infos
        logging.debug("\n\nStammdaten:\nKürzel: " + str(kuerzel) + "\nMann/Frau; " + str(mafr) + "\nVorname: " + str(
            vorname) + "\nNachname: " + str(nachname) + "\nStrasse: " + str(strasse) + "\nHausnummer: " + str(
            hausnummer) + "\nPLZ: " + str(plz) + "\nOrt: " + str(ort) + "\nGeburtsdatum: " + str(
            geburtsdatum) + "\nKilometer zu fahren: " + str(kmzufahren) + "\nHausarzt: " + str(
            hausarzt) + "\n\nDaten:\n" + str(daten_liste[0]) + "; " + str(daten_liste[1]) + "\n" + str(
            daten_liste[2]) + "; " +
                      str(daten_liste[3]) + "\n" + str(daten_liste[4]) + "; " + str(daten_liste[5]) + "\n" + str(
            daten_liste[6]) + "; " +
                      str(daten_liste[7]) + "\n" + str(daten_liste[8]) + "; " + str(
            daten_liste[9]) + "\n\nBehandlungsarten-Bezeichnung: " +
                      str(behandlungsarten_bezeichnung_liste) + "\nBehandlungsarten-Einzelpreis: " + str(
            behandlungsarten_kosten_liste))

        # check Rechnung existance
        if os.path.exists("./Rechnungen/Rechnungen{0}/".format(self.version) + rechnungsnummer + ".pdf"):
            self.info_message("neue_rechnung", "Error: 'Rechnung' already exists", "red")
            return

        # store Data
        self.store_data(rechnungsnummer, datum, stammdaten, daten_liste, datenzahl,
                        behandlungsarten_bezeichnung_liste,
                        behandlungsarten_kosten_liste, gesamtpreis)

        # PDF Speichern
        pdf.ln(100)
        pdf.output("./Rechnungen/Rechnungen{0}/".format(self.version) + rechnungsnummer + ".pdf")
        logging.info("PDF successfully created")

    def store_data(self, rechnungsnummer, datum, stammdaten, daten_liste, datenzahl, behandlungsarten_bezeichnung_liste,
                   behandlungsarten_kosten_liste, gesamtpreis):
        logging.info("Storing data")

        try:
            km_insg = 2 * int(stammdaten[9]) * int(datenzahl)
        except:
            logging.error("Error: wahrscheinlich 'Stammdatei' korrupt")

            self.info_message("neue_rechnung", "Error: wahrscheinlich 'Stammdatei' korrupt", "red")
            return

        if os.path.exists("./Rechnungen/ZusammenfassungRechnungen/RechnungenInsgesamt{0}.txt".format(self.version)):
            open_file = open(
                "./Rechnungen/ZusammenfassungRechnungen/RechnungenInsgesamt{0}.txt".format(self.version),
                "a")
            open_file.write(
                "\n" + str(stammdaten[0]) + ";" + str(rechnungsnummer) + ";" + str(stammdaten[9]) + ";km;" + str(
                    km_insg) + ";km;" + str(
                    gesamtpreis) + ";Euro;" + str(daten_liste[0]) + ";" + str(daten_liste[1]) + ";" +
                str(daten_liste[2]) + ";" + str(daten_liste[3]) + ";" + str(daten_liste[4]) + ";" +
                str(daten_liste[5]) + ";" + str(daten_liste[6]) + ";" + str(daten_liste[7]) + ";" +
                str(daten_liste[8]) + ";" + str(daten_liste[9]) + ";" + str(
                    behandlungsarten_bezeichnung_liste) + ";" +
                str(behandlungsarten_kosten_liste))
            open_file.close()
        else:
            create_file = open(
                "./Rechnungen/ZusammenfassungRechnungen/RechnungenInsgesamt{0}.txt".format(self.version),
                "w")
            create_file.write(
                "\n" + str(stammdaten[0]) + ";" + str(rechnungsnummer) + ";" + str(stammdaten[9]) + ";km;" + str(
                    km_insg) + ";km;" + str(
                    gesamtpreis) + ";Euro;" + str(daten_liste[0]) + ";" + str(daten_liste[1]) + ";" +
                str(daten_liste[2]) + ";" + str(daten_liste[3]) + ";" + str(daten_liste[4]) + ";" +
                str(daten_liste[5]) + ";" + str(daten_liste[6]) + ";" + str(daten_liste[7]) + ";" +
                str(daten_liste[8]) + ";" + str(daten_liste[9]) + ";" + str(
                    behandlungsarten_bezeichnung_liste) + ";" +
                str(behandlungsarten_kosten_liste))
            create_file.close()

        logging.info("Data successfully Stored")

        self.info_message("neue_rechnung", "Saved successfully!", "green")

    # stammdaten frame events
    def kuerzel_stammdaten_keystroke_check_event(self, t):

        def insert_stammdaten_form(mannfrau, nachname, vorname, strasse, hausnummer, plz, ort, geburtsdatum, kmzufahren,
                                   hausarzt):
            self.mann_frau_entry.insert(0, mannfrau)
            self.nachname_entry.insert(0, nachname)
            self.vorname_entry.insert(0, vorname)
            self.strasse_entry.insert(0, strasse)
            self.hausnummer_entry.insert(0, hausnummer)
            self.plz_entry.insert(0, plz)
            self.ort_entry.insert(0, ort)
            self.geburtsdatum_entry.insert(0, geburtsdatum)
            self.kilometer_zu_fahren_entry.insert(0, kmzufahren)
            self.hausarzt_entry.insert(0, hausarzt)

        entry = self.kuerzel_entry.get().strip()
        if len(entry) == 4:

            if os.path.exists("./Stammdaten/" + entry + ".txt"):
                with open("./Stammdaten/" + entry + ".txt", 'r') as f:
                    f = f.readlines()
                    if len(f) != 11:
                        self.kuerzel_entry.configure(text_color="red")
                        return
                    for i, line in enumerate(f):
                        f[i] = line.replace("\n", "")

                self.clear_stammdaten_form()
                insert_stammdaten_form(f[1], f[2], f[3], f[4], f[5], f[6], f[7], f[8], f[9], f[10])
                self.info_message("stammdaten", "Loaded!", "green")
                self.kuerzel_entry.configure(text_color="green")
                return True

            elif not os.path.exists("./Stammdaten/" + entry + ".txt"):
                self.kuerzel_entry.configure(text_color="red")
                self.stammdaten_error_msg.grid_forget()

        else:
            self.kuerzel_entry.configure(text_color="white")
            self.stammdaten_error_msg.grid_forget()
            self.clear_stammdaten_form()
            return False

    def stammdaten_abschicken_button_event(self):
        with open('./Stammdaten/' + str(
                self.kuerzel_entry.get().strip()) + '.txt', 'w') as f:
            f.write(str(self.kuerzel_entry.get().strip()) + "\n")
            f.write(str(self.mann_frau_entry.get().strip()) + "\n")
            f.write(str(self.nachname_entry.get().strip()) + "\n")
            f.write(str(self.vorname_entry.get().strip()) + "\n")
            f.write(str(self.strasse_entry.get().strip()) + "\n")
            f.write(str(self.hausnummer_entry.get().strip()) + "\n")
            f.write(str(self.plz_entry.get().strip()) + "\n")
            f.write(str(self.ort_entry.get().strip()) + "\n")
            f.write(str(self.geburtsdatum_entry.get().strip()) + "\n")
            f.write(str(self.kilometer_zu_fahren_entry.get().strip()) + "\n")
            f.write(str(self.hausarzt_entry.get().strip()) + "\n")

        self.kuerzel_entry.configure(text_color="green")
        self.clear_stammdaten_form()
        self.info_message("stammdaten", "Saved!", "green")
        logging.info("'Stammdaten' saved successfully")

    def clear_stammdaten_form(self):
        self.mann_frau_entry.delete(0, "end")
        self.nachname_entry.delete(0, "end")
        self.vorname_entry.delete(0, "end")
        self.strasse_entry.delete(0, "end")
        self.hausnummer_entry.delete(0, "end")
        self.plz_entry.delete(0, "end")
        self.ort_entry.delete(0, "end")
        self.geburtsdatum_entry.delete(0, "end")
        self.kilometer_zu_fahren_entry.delete(0, "end")
        self.hausarzt_entry.delete(0, "end")

    # rechnung löschen frame events
    def rechnung_loeschen_abschicken_button_event(self):
        entry = self.rechnungsnummer_entry.get()

        if entry == "":
            self.info_message("rechnung_löschen", "Rechnungsnummer eingeben!", "red")
            return

        else:
            self.jahr_updaten_error_msg.grid_forget()

        self.rechnung_loeschen_bestaetigung_button.grid(row=2, column=1, padx=20, pady=5)
        self.rechnung_loeschen_bestaetigung_label.grid(row=2, column=0, padx=20, pady=5)

    def rechnung_loeschen_bestaetigen_button_event(self):
        entry = self.rechnungsnummer_entry.get()

        # checking if rechnung exists and entry is in RechnungenInsgesamt
        deleted_lines = 0
        rechnung_exists = os.path.exists("./Rechnungen/Rechnungen{0}/".format(self.version) + entry + ".pdf")

        for line in fileinput.input(
                "./Rechnungen/ZusammenfassungRechnungen/RechnungenInsgesamt{0}.txt".format(self.version),
                inplace=False):
            if entry in line:
                deleted_lines += 1
                continue

        # deleting
        if deleted_lines == 0 or not rechnung_exists:
            self.info_message("rechnung_löschen", "Rechnung nicht gefunden oder nicht in RechnungenInsgesamt", "red",
                              True)
            return

        elif deleted_lines == 1 and rechnung_exists:
            # deleting rechnung .pdf file
            os.remove("./Rechnungen/Rechnungen{0}/".format(self.version) + entry + ".pdf")

            # removing line out of RechnungenInsgesamt
            for line in fileinput.FileInput(
                    "./Rechnungen/ZusammenfassungRechnungen/RechnungenInsgesamt{0}.txt".format(self.version),
                    inplace=True):
                if entry in line:
                    print("", end="")
                    continue
                else:
                    print(line, end="")

            self.info_message("rechnung_löschen", "Successfully deleted", "green", True)
            self.rechnungsnummer_entry.delete(0, "end")
            return

        else:
            self.info_message("rechnung_löschen", "RechnungenInsgesamt****.txt ist korrupt", "red", True)
            return

    # update version

    def jahr_updaten_button_event(self):
        entry = self.jahr_updaten_entry.get()

        if entry == "":
            self.info_message("update_version", "Rechnungsnummer eingeben!", "red")
            return
        else:
            self.jahr_updaten_error_msg.grid_forget()

        self.jahr_updaten_bestaetigung_button.grid(row=2, column=1, padx=20, pady=5)
        self.jahr_updaten_bestaetigung_label.grid(row=2, column=0, padx=20, pady=5)

    def jahr_updaten_bestaetigen_button_event(self):
        entry = self.jahr_updaten_entry.get()

        if re.match(".*([2][0-9]{3})", entry) is None:
            self.info_message("update_version", "Nur Jahreszahlen erlaubt!", "red", True)
            return

        if os.path.exists("../System/version/version.txt"):
            with open("../System/version/version.txt", "w") as f:
                f.write(str(entry))
                self.info_message("update_version", "Updated!", "green", True)

                time.sleep(2)
                os.startfile("main.py")
                sys.exit()
        else:
            self.info_message("update_version", "Version file empty or not existing", "red", True)

    # main events
    def info_message(self, frame, error_msg, color, remove_elements=None):
        logging.info("Info message triggered")

        # determine which frame
        if frame == "neue_rechnung":
            self.behandlungsarten_error_1.configure(text=error_msg, text_color=color)
            self.behandlungsarten_error_1.grid(row=1, column=2, padx=(0, 5), pady=10)
            self.rechnung_abschicken_button.configure(state="enabled")
            logging.info("Error/Info: {0};{1};{2}".format(str(frame), str(error_msg), str(color)))

        if frame == "stammdaten":
            self.stammdaten_error_msg.configure(text=error_msg, text_color=color)
            self.stammdaten_error_msg.grid(row=0, column=1, padx=10, pady=10)
            logging.info("Error/Info: {0};{1};{2}".format(str(frame), str(error_msg), str(color)))

        if frame == "rechnung_löschen":
            self.jahr_updaten_error_msg.configure(text=error_msg, text_color=color)
            self.jahr_updaten_error_msg.grid(row=1, column=0, padx=20, pady=5)
            if remove_elements is True:
                self.rechnung_loeschen_bestaetigung_button.grid_forget()
                self.rechnung_loeschen_bestaetigung_label.grid_forget()
            logging.info("Error/Info: {0};{1};{2}".format(str(frame), str(error_msg), str(color)))

        if frame == "update_version":
            self.jahr_updaten_error_msg.configure(text=error_msg, text_color=color)
            self.jahr_updaten_error_msg.grid(row=1, column=0, padx=20, pady=5)
            if remove_elements is True:
                self.jahr_updaten_bestaetigung_label.grid_forget()
                self.jahr_updaten_bestaetigung_button.grid_forget()
            logging.info("Error/Info: {0};{1};{2}".format(str(frame), str(error_msg), str(color)))

    def clear_screen_event(self):
        logging.debug("Clear Screen Event")
        try:
            self.main_1.grid_forget()
            self.main_1.destroy()
            logging.info("screen cleared")
        except:
            try:
                self.main_2.grid_forget()
                self.main_2.destroy()
                logging.info("screen cleared")
            except:
                try:
                    self.main_3.grid_forget()
                    self.main_3.destroy()
                    logging.info("screen cleared")
                except:
                    try:
                        self.main_4.grid_forget()
                        self.main_4.destroy()
                        logging.info("screen cleared")
                    except:
                        logging.error("Exception: screen couldn't be cleaned")
                        pass


if __name__ == "__main__":
    app = App()
    app.mainloop()
