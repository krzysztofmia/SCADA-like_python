import pytest
from hydrosim import Zbiornik, Zawor, Pompa, Rura
from PyQt5.QtCore import QPointF

def test_zbiornik_init():
    z = Zbiornik(0, 0, nazwa="Test")
    assert z.aktualna_ilosc == 0.0
    assert z.poziom == 0.0
    assert z.pojemnosc == 100.0

@pytest.mark.parametrize(
    "poczatkowa, dodaj, wynik",
    [
        (0, 10, 10),
        (50, 20, 70),
        (90, 20, 100),   # nie moze przekroczyc pojemnosci
        (100, 10, 100),  # juz pelny
    ]
)
def test_dodaj_ciecz(poczatkowa, dodaj, wynik):
    z = Zbiornik(0, 0)
    z.aktualna_ilosc = poczatkowa
    z.aktualizuj_poziom()

    z.dodaj_ciecz(dodaj)

    assert z.aktualna_ilosc == wynik
    assert z.poziom == wynik / 100

@pytest.mark.parametrize(
    "poczatkowa, usun, wynik",
    [
        (100, 10, 90),
        (50, 20, 30),
        (10, 20, 0),   # nie moze zejsc ponizej 0
        (0, 10, 0),
    ]
)
def test_usun_ciecz(poczatkowa, usun, wynik):
    z = Zbiornik(0, 0)
    z.aktualna_ilosc = poczatkowa
    z.aktualizuj_poziom()

    z.usun_ciecz(usun)

    assert z.aktualna_ilosc == wynik
    assert z.poziom == wynik / 100

@pytest.mark.parametrize(
    "ilosc, pusty, pelny",
    [
        (0, True, False),
        (0.05, True, False),
        (50, False, False),
        (99.9, False, True),
        (100, False, True),
    ]
)
def test_stany_zbiornika(ilosc, pusty, pelny):
    z = Zbiornik(0, 0)
    z.aktualna_ilosc = ilosc
    z.aktualizuj_poziom()

    assert z.czy_pusty() == pusty
    assert z.czy_pelny() == pelny

@pytest.mark.parametrize(
    "akcja, wynik",
    [
        ("napelnij", 100),
        ("oproznij", 0),
    ]
)
def test_napelnij_oproznij(akcja, wynik):
    z = Zbiornik(0, 0)
    getattr(z, akcja)() # powoduje wywolanie z.napelnij oraz z.oproznij

    assert z.aktualna_ilosc == wynik
    assert z.poziom == wynik / 100

def test_zawor():
    z = Zawor(0, 0)
    assert z.stan_zaworu is False
    z.aktualizuj_stan_zaworu()
    assert z.stan_zaworu is True
    z.aktualizuj_stan_zaworu()
    assert z.stan_zaworu is False

def test_pompa():
    p = Pompa(0, 0)
    assert p.stan_pompy is False
    p.aktualizuj_stan_pompy()
    assert p.stan_pompy is True
    p.aktualizuj_stan_pompy()
    assert p.stan_pompy is False

def test_rura_przeplyw():
    r = Rura([(0, 0), (10, 10)])
    assert r.czy_plynie is False
    r.ustaw_przeplyw(True)
    assert r.czy_plynie is True
    r.ustaw_przeplyw(False)
    assert r.czy_plynie is False
