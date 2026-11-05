import csv
import matplotlib
matplotlib.use("Agg")  # ekran yok, dosyaya çizsin
import matplotlib.pyplot as plt

zaman, enlem, boylam, irtifa = [], [], [], []
with open("ucus_kaydi.csv") as f:
    okuyucu = csv.DictReader(f)
    for satir in okuyucu:
        zaman.append(float(satir["zaman_s"]))
        enlem.append(float(satir["enlem"]))
        boylam.append(float(satir["boylam"]))
        irtifa.append(float(satir["irtifa_m"]))

fig, (ust, alt) = plt.subplots(2, 1, figsize=(7, 9))

ust.plot(zaman, irtifa)
ust.set_xlabel("Zaman (s)")
ust.set_ylabel("İrtifa (m)")
ust.set_title("İrtifa - Zaman")
ust.grid(True)

alt.plot(boylam, enlem)
alt.set_xlabel("Boylam")
alt.set_ylabel("Enlem")
alt.set_title("Uçuş yolu (üstten görünüm)")
alt.grid(True)

plt.tight_layout()
plt.savefig("grafik.png", dpi=120)
print("grafik.png olusturuldu")
