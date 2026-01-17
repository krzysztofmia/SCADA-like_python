import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtCore import Qt, QTimer, QPointF
from PyQt5.QtGui import QPainter, QColor, QPen, QPainterPath, QBrush, QFont

# --- Klasa Rura ---

class Rura:
    def __init__(self, punkty, grubosc = 12, kolor = Qt.gray):
        # Konwersja listy krotek na obiekty QPointF
        self.punkty =[QPointF(float(p[0]), float(p[1])) for p in punkty]
        self.grubosc = grubosc
        self.kolor_rury = kolor
        self.kolor_cieczy = QColor(0, 180, 255) # Jasny niebieski
        self.czy_plynie = False

    def ustaw_przeplyw(self, plynie):
        self.czy_plynie = plynie
        
    def draw(self, painter):
        if len(self.punkty) <2:
            return
        
        path = QPainterPath()
        path.moveTo(self.punkty[0])
        for p in self.punkty[1:]:
            path.lineTo(p)

        # 1. Rysowanie obudowy rury
        pen_rura = QPen(self.kolor_rury, self.grubosc, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen_rura)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)

        # 2. Rysowanie cieczy w srodku (jesli plynie)
        if self.czy_plynie:
            pen_ciecz = QPen(self.kolor_cieczy, self.grubosc - 4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            painter.setPen(pen_ciecz)
            painter.drawPath(path)

# --- Klasa Zbiornik ---

class Zbiornik:
    def __init__(self, x, y, width = 100, height = 140, nazwa = " "):
        self.x = x ; self.y = y
        self.width = width; self.height = height
        self.nazwa = nazwa
        self.pojemnosc = 100.0
        self.aktualna_ilosc = 0.0
        self.poziom = 0.0 # Wartosc 0.0 - 1.0

    def dodaj_ciecz(self, ilosc):
        wolne = self.pojemnosc - self.aktualna_ilosc
        dodano = min(ilosc, wolne)
        self.aktualna_ilosc += dodano
        self.aktualizuj_poziom()
        return dodano
    
    def usun_ciecz(self, ilosc):
        usunieto = min(ilosc, self.aktualna_ilosc)
        self.aktualna_ilosc -= usunieto
        self.aktualizuj_poziom()
        return usunieto
    
    def aktualizuj_poziom(self):
        self.poziom = self.aktualna_ilosc / self.pojemnosc

    def czy_pusty(self): return self.aktualna_ilosc <= 0.1
    def czy_pelny(self): return self.aktualna_ilosc >= self.pojemnosc - 0.1

    def napelnij(self):
        self.aktualna_ilosc = 100
        self.aktualizuj_poziom()

    def oproznij(self):
        self.aktualna_ilosc = 0
        self.aktualizuj_poziom()

    # Punkty zaczepienia dla rur
    def punkt_gora_srodek(self): return (self.x +self.width/2, self.y)
    def punkt_dol_srodek(self): return (self.x +self.width/2, self.y + self.height)

    def draw(self, painter):
        # 1. Rysowanie cieczy
        if self.poziom > 0:
            h_cieczy = self.height * self.poziom
            y_start = self.y +self.height - h_cieczy
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(0, 120, 255, 200))
            painter.drawRect(int(self.x +3), int(y_start), int(self.width - 6), int(h_cieczy - 2))

        # 2. Rysowanie obrysu
        pen = QPen(Qt.white, 4)
        pen.setJoinStyle(Qt.MiterJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(int(self.x), int(self.y), int(self.width), int(self.height))

        # 3. Podpis
        painter.setPen(Qt.white)
        painter.drawText(int(self.x + 110), int(self.y + 30), self.nazwa)
        painter.drawText(int(self.x + 110), int(self.y + 50), "Poziom: " + str(round(self.aktualna_ilosc)) + "%")

# --- Klasa Zawor ---

class Zawor:
    def __init__(self, x, y, nazwa = " "):
        self.x = x; self.y = y
        self.nazwa = nazwa
        self.stan_zaworu = False
        
    def aktualizuj_stan_zaworu(self):
        self.stan_zaworu = not self.stan_zaworu

    # Punkty zaczepienia dla rur
    def punkt_lewy(self): return (self.x - 25, self.y)
    def punkt_prawy(self): return (self.x + 25, self.y)

    def draw(self, painter):
        # 1. Rysowanie obrysu
        pen = QPen(Qt.white, 4)
        pen.setJoinStyle(Qt.MiterJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)

        # Kolor zależny od stanu
        color = Qt.green if self.stan_zaworu else Qt.red
        painter.setBrush(QBrush(color))

        prawy_trojkat = [
            QPointF(self.x, self.y),
            QPointF(self.x + 25, self.y - 15),
            QPointF(self.x + 25, self.y + 15)
        ]
        lewy_trojkat = [
            QPointF(self.x, self.y),
            QPointF(self.x - 25, self.y - 15),
            QPointF(self.x - 25, self.y + 15)
        ]
        painter.drawPolygon(*prawy_trojkat)
        painter.drawPolygon(*lewy_trojkat)

        # 2. Rysowanie trzpienia
        pen = QPen(Qt.white, 2)
        painter.setPen(pen)
        painter.drawLine(self.x, self.y - 20, self.x, self.y - 40)

        # 3. Podpis
        painter.setPen(Qt.white)
        painter.drawText(int(self.x - 50), int(self.y + 40), self.nazwa)
        painter.drawText(int(self.x), int(self.y + 40), "OTWARTY" if self.stan_zaworu else "ZAMKNIETY")
        
        # --- Klasa Zawor ---

# --- Klasa Pompa ---

class Pompa:
    def __init__(self, x, y, nazwa = " "):
        self.x = x; self.y = y
        self.nazwa = nazwa
        self.stan_pompy = False
        
    def aktualizuj_stan_pompy(self):
        self.stan_pompy = not self.stan_pompy

    # Punkty zaczepienia dla rur
    def punkt_lewy(self): return (self.x - 25, self.y)
    def punkt_prawy(self): return (self.x + 25, self.y)

    def draw(self, painter):
        # 1. Rysowanie obrysu
        pen = QPen(Qt.white, 4)
        pen.setJoinStyle(Qt.MiterJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)

        # Kolor zależny od stanu
        color = Qt.green if self.stan_pompy else Qt.red
        painter.setBrush(QBrush(color))
        # Rysowanie okregu
        painter.drawEllipse(QPointF(self.x, self.y), 25, 25)
        # Rysowanie trojkata
        trojkat = [
            QPointF(self.x - 18, self.y),
            QPointF(self.x + 12, self.y - 15),
            QPointF(self.x + 12, self.y + 15)
        ]
        painter.drawPolygon(*trojkat)

        # 3. Podpis
        painter.setPen(Qt.white)
        painter.drawText(int(self.x - 50), int(self.y + 40), self.nazwa)
        painter.drawText(int(self.x + 5), int(self.y + 40), "AKTYWNA" if self.stan_pompy else "NIEAKTYWNA")

# --- Klasa SymulacjaKaskady ---

class SymulacjaKaskady(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HYDROSIMULATOR - SCADA-like python app/Pythonowa aplikacja przypominajaca systemy SCADA")
        self.setFixedSize(900, 600)
        self.setStyleSheet("background-color: #222;")

        # --- Konfiguracja Zbiornikow(schodkowo) ---
        self.z1 = Zbiornik(50, 50, nazwa = "Zbiornik 1")
        self.z1.aktualna_ilosc = 100.0; self.z1.aktualizuj_poziom() # Pelny
        self.z2 = Zbiornik(350, 200, nazwa = "Zbiornik 2")
        self.z3 = Zbiornik(650, 350, nazwa = "Zbiornik 3")
        self.z4 = Zbiornik(50, 350, nazwa = "Zbiornik 4")
        self.zbiorniki = [self.z1, self.z2, self.z3, self.z4]
        
        # Zawor:
        self.zawor = Zawor(250, 195, "Zawor 1")
        self.zawory = [self.zawor]

        # Pompa:
        self.pompa = Pompa(400, 450, "Pompa 1")
        self.pompy = [self.pompa]

        # --- Konfiguracja Rur ---
        # Rura 1: Z1(Dol) -> Zawor(Lewo) -> Zawor(Prawo) -> Z2(Gora)
        p_start = self.z1.punkt_dol_srodek()
        p_koniec = self.zawor.punkt_lewy()
        mid_y = (p_start[1] + p_koniec[1]) / 2

        self.rura1_1 = Rura([
            p_start, (p_start[0], mid_y), p_koniec
        ])

        p_start = self.zawor.punkt_prawy()
        p_koniec = self.z2.punkt_gora_srodek()
        mid_y = (p_start[1] + p_koniec[1]) / 2

        self.rura1_2 = Rura([
            p_start, (p_koniec[0], mid_y), p_koniec
        ])

        # Rura 2: Z2(Dol) -> Z3(Gora)
        p_start = self.z2.punkt_dol_srodek()
        p_koniec = self.z3.punkt_gora_srodek()
        mid_y2 = (p_start[1] + p_koniec[1]) / 2

        self.rura2 = Rura([
            p_start, (p_start[0], mid_y2), (p_koniec[0], mid_y2), p_koniec
        ])

        # Rura 3: Z3(Bok) -> Pompa(Prawo) -> Pompa(Lewo) -> Z4(Gora)
        p_start = (self.z3.x, self.z3.y + 100)
        p_koniec = self.pompa.punkt_prawy()

        self.rura3_1 = Rura([
            p_start, p_koniec
        ])

        p_start = self.pompa.punkt_lewy()
        p_koniec = self.z4.punkt_gora_srodek()

        self.rura3_2 = Rura([
            p_start, (250, p_start[1]), (250, p_koniec[1] - 5), (p_koniec[0], p_koniec[1] - 5), p_koniec
        ])

        self.rury = [self.rura1_1, self.rura1_2 , self.rura2, self.rura3_1, self.rura3_2]

        # --- Timer i Sterowanie ---
        self.timer = QTimer()
        self.timer.timeout.connect(self.logika_przeplywu)

        self.btn = QPushButton("Start/Stop", self)
        self.btn.setGeometry(625, 50, 200, 30)
        self.btn.setStyleSheet("background-color: red; color: #444;")
        self.btn.clicked.connect(self.przelacz_symulacje)

        self.stanZaworu = QPushButton("ON / OFF", self)
        self.stanZaworu.setGeometry(self.zawor.x - 50, self.zawor.y + 50, 100, 30)
        self.stanZaworu.setStyleSheet("background-color: red; color: #444;")
        self.stanZaworu.clicked.connect(self.zmien_stan_zaworu)

        self.stanZaworu2 = QPushButton("Zawor 1", self)
        self.stanZaworu2.setGeometry(625, 225, 100, 30)
        self.stanZaworu2.setStyleSheet("background-color: red; color: #444;")
        self.stanZaworu2.clicked.connect(self.zmien_stan_zaworu)

        self.stanPompy = QPushButton("ON / OFF", self)
        self.stanPompy.setGeometry(self.pompa.x - 50, self.pompa.y + 50, 100, 30)
        self.stanPompy.setStyleSheet("background-color: red; color: #444;")
        self.stanPompy.clicked.connect(self.zmien_stan_pompy)

        self.stanPompy2 = QPushButton("Pompa 1", self)
        self.stanPompy2.setGeometry(725, 225, 100, 30)
        self.stanPompy2.setStyleSheet("background-color: red; color: #444;")
        self.stanPompy2.clicked.connect(self.zmien_stan_pompy)

        self.napelnijZ1 = QPushButton("Napelnij Z1", self)
        self.napelnijZ1.setGeometry(625, 85, 100, 30)
        self.napelnijZ1.setStyleSheet("background-color: #444; color: white;")
        self.napelnijZ1.clicked.connect(lambda: self.napelnij_zbiornik(self.z1))

        self.oproznijZ1 = QPushButton("Oproznij Z1", self)
        self.oproznijZ1.setGeometry(725, 85, 100, 30)
        self.oproznijZ1.setStyleSheet("background-color: #444; color: white;")
        self.oproznijZ1.clicked.connect(lambda: self.oproznij_zbiornik(self.z1))

        self.napelnijZ2 = QPushButton("Napelnij Z2", self)
        self.napelnijZ2.setGeometry(625, 120, 100, 30)
        self.napelnijZ2.setStyleSheet("background-color: #444; color: white;")
        self.napelnijZ2.clicked.connect(lambda: self.napelnij_zbiornik(self.z2))

        self.oproznijZ2 = QPushButton("Oproznij Z2", self)
        self.oproznijZ2.setGeometry(725, 120, 100, 30)
        self.oproznijZ2.setStyleSheet("background-color: #444; color: white;")
        self.oproznijZ2.clicked.connect(lambda: self.oproznij_zbiornik(self.z2))

        self.napelnijZ3 = QPushButton("Napelnij Z3", self)
        self.napelnijZ3.setGeometry(625, 155, 100, 30)
        self.napelnijZ3.setStyleSheet("background-color: #444; color: white;")
        self.napelnijZ3.clicked.connect(lambda: self.napelnij_zbiornik(self.z3))

        self.oproznijZ3 = QPushButton("Oproznij Z3", self)
        self.oproznijZ3.setGeometry(725, 155, 100, 30)
        self.oproznijZ3.setStyleSheet("background-color: #444; color: white;")
        self.oproznijZ3.clicked.connect(lambda: self.oproznij_zbiornik(self.z3))

        self.napelnijZ4 = QPushButton("Napelnij Z4", self)
        self.napelnijZ4.setGeometry(625, 190, 100, 30)
        self.napelnijZ4.setStyleSheet("background-color: #444; color: white;")
        self.napelnijZ4.clicked.connect(lambda: self.napelnij_zbiornik(self.z4))

        self.oproznijZ4 = QPushButton("Oproznij Z4", self)
        self.oproznijZ4.setGeometry(725, 190, 100, 30)
        self.oproznijZ4.setStyleSheet("background-color: #444; color: white;")
        self.oproznijZ4.clicked.connect(lambda: self.oproznij_zbiornik(self.z4))

        self.przycisk_reset = QPushButton("Reset", self)
        self.przycisk_reset.setGeometry(625, 260, 200, 30)
        self.przycisk_reset.setStyleSheet("background-color: red; color: #444;")
        self.przycisk_reset.clicked.connect(self.reset)

        self.running = False
        self.flow_speed = 0.8

    def przelacz_symulacje(self):
        if self.running: 
            self.timer.stop()
            self.btn.setStyleSheet("background-color: red; color: black;")
        else: 
            self.timer.start(20)
            self.btn.setStyleSheet("background-color: green; color: white;")
        self.running = not self.running

    def logika_przeplywu(self):
        # 1. Przeplyw Z1 -> zawor -> Z2
        plynie_1_1 = False
        plynie_1_2 = False
        if not self.z1.czy_pusty() and not self.z2.czy_pelny():
            if self.zawor.stan_zaworu:
                ilosc = self.z1.usun_ciecz(self.flow_speed)
                self.z2.dodaj_ciecz(ilosc)
                plynie_1_2 = True
            plynie_1_1 = True
        self.rura1_1.ustaw_przeplyw(plynie_1_1)
        self.rura1_2.ustaw_przeplyw(plynie_1_2)

        # 2. Przeplyw Z2 -> Z3 ( Startuje dopiero gdy Z2 ma troche wody )
        plynie_2 = False
        if self.z2.aktualna_ilosc > 5.0 and not self.z3.czy_pelny():
            ilosc = self.z2.usun_ciecz(self.flow_speed)
            self.z3.dodaj_ciecz(ilosc)
            plynie_2 = True
        self.rura2.ustaw_przeplyw(plynie_2)

        # 3. Przeplyw Z3 -> pompa -> Z4
        plynie_3_1 = False
        plynie_3_2 = False
        if self.z3.aktualna_ilosc > 30.0 and not self.z4.czy_pelny():
            if self.pompa.stan_pompy:
                ilosc = self.z3.usun_ciecz(self.flow_speed)
                self.z4.dodaj_ciecz(ilosc)
                plynie_3_2 = True
            plynie_3_1 = True
        self.rura3_1.ustaw_przeplyw(plynie_3_1)
        self.rura3_2.ustaw_przeplyw(plynie_3_2)

        self.update()

    def zmien_stan_zaworu(self):
        self.zawor.aktualizuj_stan_zaworu()
        if self.zawor.stan_zaworu:
            self.stanZaworu.setStyleSheet("background-color: green; color: white;")
            self.stanZaworu2.setStyleSheet("background-color: green; color: white;")
        else:
            self.stanZaworu.setStyleSheet("background-color: red; color: black;")
            self.stanZaworu2.setStyleSheet("background-color: red; color: black;")
        self.update()

    def zmien_stan_pompy(self):
        self.pompa.aktualizuj_stan_pompy()
        if self.pompa.stan_pompy:
            self.stanPompy.setStyleSheet("background-color: green; color: white;")
            self.stanPompy2.setStyleSheet("background-color: green; color: white;")        
        else:
            self.stanPompy.setStyleSheet("background-color: red; color: black;")
            self.stanPompy2.setStyleSheet("background-color: red; color: black;")
        self.update()

    def napelnij_zbiornik(self, zb):
        zb.napelnij()
        self.update()

    def oproznij_zbiornik(self, zb):
        zb.oproznij()
        self.update()

    def reset(self):
        if self.running: 
            self.timer.stop()
            self.btn.setStyleSheet("background-color: red; color: black;")
        self.napelnij_zbiornik(self.z1)
        self.oproznij_zbiornik(self.z2)
        self.oproznij_zbiornik(self.z3)
        self.oproznij_zbiornik(self.z4)
        if self.zawor.stan_zaworu: 
            self.zmien_stan_zaworu()
        if self.pompa.stan_pompy: 
            self.zmien_stan_pompy()
        self.rura1_1.ustaw_przeplyw(False)
        self.rura1_2.ustaw_przeplyw(False)
        self.rura2.ustaw_przeplyw(False)
        self.rura3_1.ustaw_przeplyw(False)
        self.rura3_2.ustaw_przeplyw(False)

    def paintEvent(self, event,):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        # Rysowanie elementów
        # Najpierw rury (pod spodem), potem pozostale
        for r in self.rury: r.draw(p)
        for v in self.zawory: v.draw(p)
        for d in self.pompy: d.draw(p)
        for z in self.zbiorniki: z.draw(p)
        # Podpis panelu z przyciskami
        font = QFont("Arial", 12, QFont.Bold)
        p.setFont(font)
        p.drawText(622, 40, "PANEL STEROWANIA")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    okno = SymulacjaKaskady()
    okno.show()
    sys.exit(app.exec_())