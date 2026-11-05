"""TEKNOFEST Sürü İHA - Proje 1: ArduPilot SITL üzerinde kare uçuş.

Çalıştırma: SITL ve MAVProxy açıkken  ->  python3 kare_ucus.py
MAVProxy, --out udp:127.0.0.1:14550 ile bu betiğe veri yönlendirir.
"""
import csv
import math
import time

from pymavlink import mavutil

BAGLANTI = "udp:127.0.0.1:14550"
IRTIFA = 10.0   # metre
KENAR = 20.0    # karenin kenar uzunluğu, metre


def mod_ayarla(iha, mod):
    iha.set_mode(mod)
    while iha.flightmode != mod:
        iha.recv_match(type="HEARTBEAT", blocking=True)


def konuma_git(iha, kuzey, dogu, asagi):
    """Kalkış noktasına göre yerel NED koordinatına git (asagi negatif = yukarı)."""
    iha.mav.set_position_target_local_ned_send(
        0, iha.target_system, iha.target_component,
        mavutil.mavlink.MAV_FRAME_LOCAL_NED,
        0b110111111000,  # yalnızca konum alanlarını kullan
        kuzey, dogu, asagi, 0, 0, 0, 0, 0, 0, 0, 0)


def kayit_al(iha, yazici, baslangic):
    """GLOBAL_POSITION_INT mesajını okuyup CSV'ye bir satır yazar, irtifayı döndürür."""
    msg = iha.recv_match(type="GLOBAL_POSITION_INT", blocking=True, timeout=1)
    if msg is None:
        return None
    irtifa = msg.relative_alt / 1000.0
    yazici.writerow([round(time.time() - baslangic, 2),
                     msg.lat / 1e7, msg.lon / 1e7, irtifa])
    return irtifa


def main():
    iha = mavutil.mavlink_connection(BAGLANTI)
    iha.wait_heartbeat()
    print("Bağlandı: sistem", iha.target_system)

    with open("ucus_kaydi.csv", "w", newline="") as f:
        yazici = csv.writer(f)
        yazici.writerow(["zaman_s", "enlem", "boylam", "irtifa_m"])
        baslangic = time.time()

        mod_ayarla(iha, "GUIDED")
        iha.arducopter_arm()
        iha.motors_armed_wait()
        print("Motorlar açık")

        iha.mav.command_long_send(
            iha.target_system, iha.target_component,
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, IRTIFA)

        # TODO 1: irtifa IRTIFA'nın %95'ine ulaşana kadar kayit_al() ile bekle.
        irtifa = 0.0
        while irtifa < IRTIFA * 0.95:
            sonuc = kayit_al(iha, yazici, baslangic)
            if sonuc is not None:
                irtifa = sonuc
        print("Kalkış tamam:", round(irtifa, 1), "m")


        # TODO 2: karenin 4 köşesini (kuzey, doğu) listesi olarak tanımla.
        koseler = [(KENAR, 0), (KENAR, KENAR), (0, KENAR), (0, 0)]
        # İpucu: ilk köşe (KENAR, 0) olabilir. Son köşe kalkış noktası (0, 0).
        

        for kuzey, dogu in koseler:
            konuma_git(iha, kuzey, dogu, -IRTIFA)
            # TODO 3: köşeye ulaşana kadar bekle ve bu sırada kayıt al.
            # İpucu: LOCAL_POSITION_NED mesajındaki x, y ile hedef arasındaki
            # mesafe 1 m'nin altına inince bir sonraki köşeye geç.
            while True:
                kayit_al(iha, yazici, baslangic)
                pos = iha.recv_match(type="LOCAL_POSITION_NED", blocking=True, timeout=1)
                if pos is None:
                    continue
                if math.hypot(pos.x - kuzey, pos.y - dogu) < 1.0:
                    break
            print("Köşeye ulaşıldı:", kuzey, dogu)

        mod_ayarla(iha, "LAND")
        # TODO 4: irtifa 0,3 m'nin altına inene kadar kayıt almaya devam et.
        irtifa = IRTIFA
        while irtifa > 0.3:
            sonuc = kayit_al(iha, yazici, baslangic)
            if sonuc is not None:
                irtifa = sonuc
        print("İniş tamam, kayıt: ucus_kaydi.csv")


if __name__ == "__main__":
    main()
