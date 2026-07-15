#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Stego Sınırsız - EOF Steganography Aracı
Bu program, hiçbir kapasite sınırı olmaksızın PNG dosyalarının IEND bitiş 
mührünün (AE 42 60 82) arkasına gizli verileri (video, ses vb.) ekler ve çıkartır.
Harici kütüphane gerektirmez (Pure Python).
"""

import sys
import struct
import os

def gizle(orijinal_png, video_dosyasi, cikti_png):
    if not os.path.exists(orijinal_png):
        print(f"Hata: Orijinal resim dosyası bulunamadı -> {orijinal_png}")
        sys.exit(1)
    if not os.path.exists(video_dosyasi):
        print(f"Hata: Gizlenecek video dosyası bulunamadı -> {video_dosyasi}")
        sys.exit(1)

    print("[*] Hedef dosyalar belleğe okunuyor...")
    try:
        with open(orijinal_png, "rb") as f:
            png_veri = f.read()
            
        with open(video_dosyasi, "rb") as f:
            video_veri = f.read()
    except Exception as e:
        print(f"Hata: Dosyalar okunurken bir sorun oluştu -> {e}")
        sys.exit(1)

    # IEND bloğu: IEND (49 45 4E 44) ve CRC (AE 42 60 82)
    # PNG'nin kesin bitiş mührünü arıyoruz. False positive'leri engellemek için rfind (sondan arama) kullanılır.
    iend_imzasi = b"\x49\x45\x4E\x44\xAE\x42\x60\x82"
    iend_index = png_veri.rfind(iend_imzasi)

    if iend_index == -1:
        print("Hata: Geçerli bir PNG bitiş mührü (IEND) bulunamadı. Lütfen geçerli ve bozulmamış bir PNG resmi kullanın.")
        sys.exit(1)

    # IEND bloğunun bittiği noktaya kadar olan orijinal veriyi saf bir şekilde alıyoruz
    png_gercek_veri = png_veri[:iend_index + len(iend_imzasi)]
    video_boyutu = len(video_veri)
    
    # 8 Byte uzunluğunda (unsigned long long) boyut bilgisi
    boyut_belirteci = struct.pack(">Q", video_boyutu)

    print(f"[*] {video_boyutu} byte boyutundaki video, PNG mührünün arkasına enjekte ediliyor...")
    
    # EOF (End of File) Steganography: Orijinal PNG + Gizli Video + 8 Byte Boyut
    cikti_veri = png_gercek_veri + video_veri + boyut_belirteci

    try:
        with open(cikti_png, "wb") as f:
            f.write(cikti_veri)
        print(f"[+] BAŞARILI! Sınırsız kapasiteli polyglot dosya oluşturuldu: {cikti_png}")
        print("    Oluşan dosya normal bir resim gibi açılacak, verileriniz güvende kalacaktır.")
    except Exception as e:
        print(f"Hata: Çıktı dosyası kaydedilemedi -> {e}")
        sys.exit(1)


def coz(cikti_png, cikartilan_video):
    if not os.path.exists(cikti_png):
        print(f"Hata: İşlenecek dosya bulunamadı -> {cikti_png}")
        sys.exit(1)

    print("[*] Stego dosyası baştan sona analiz ediliyor...")
    try:
        with open(cikti_png, "rb") as f:
            dosya_verisi = f.read()
    except Exception as e:
        print(f"Hata: Dosya okunurken sorun oluştu -> {e}")
        sys.exit(1)

    dosya_boyutu = len(dosya_verisi)
    
    if dosya_boyutu < 8:
        print("Hata: Dosya çok küçük, geçersiz format.")
        sys.exit(1)

    # En sondaki 8 byte boyut bilgisidir
    boyut_belirteci = dosya_verisi[-8:]
    video_boyutu = struct.unpack(">Q", boyut_belirteci)[0]

    # IEND imzası tespiti
    iend_imzasi = b"\x49\x45\x4E\x44\xAE\x42\x60\x82"
    iend_index = dosya_verisi.find(iend_imzasi)

    if iend_index == -1:
        print("Hata: Dosyada geçerli PNG mührü yok.")
        sys.exit(1)

    # PNG mührünün bittiği yer, gizli verinin başladığı noktadır
    png_bitis = iend_index + len(iend_imzasi)
    
    # Mantık Kontrolü: Belirtilen video boyutu ve dosya yapısı eşleşiyor mu?
    if (png_bitis + video_boyutu + 8) > dosya_boyutu:
        print("Hata: Dosyadan okunan boyut bilgisi geçersiz veya dosya içeriği bozuk.")
        print("Bu dosya bizim stego_sinirsiz motorumuzla oluşturulmamış olabilir.")
        sys.exit(1)

    print(f"[*] {video_boyutu} byte boyutundaki gizli veri (video), PNG mührünün ardından çıkartılıyor...")
    
    # Video verisini boyut ve başlangıç noktasına dayanarak ayıklama
    video_verisi = dosya_verisi[png_bitis : png_bitis + video_boyutu]

    try:
        with open(cikartilan_video, "wb") as f:
            f.write(video_verisi)
        print(f"[+] BAŞARILI! Gizli video dosyanın içinden sağ salim çıkartıldı: {cikartilan_video}")
    except Exception as e:
        print(f"Hata: Çıkarılan video kaydedilemedi -> {e}")
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        kullanim_yazdir()
        sys.exit(1)

    mod = sys.argv[1].lower()

    if mod == "gizle":
        if len(sys.argv) != 5:
            print("Kullanım Hatası!")
            print("Doğru Kullanım: python stego_sinirsiz.py gizle <orijinal.png> <video.mp4> <cikti.png>")
            sys.exit(1)
        gizle(sys.argv[2], sys.argv[3], sys.argv[4])
        
    elif mod == "coz":
        if len(sys.argv) != 4:
            print("Kullanım Hatası!")
            print("Doğru Kullanım: python stego_sinirsiz.py coz <cikti.png> <cikartilan_video.mp4>")
            sys.exit(1)
        coz(sys.argv[2], sys.argv[3])
        
    else:
        print("Hata: Geçersiz mod!")
        kullanim_yazdir()
        sys.exit(1)

def kullanim_yazdir():
    print("===============================================================")
    print("      Stego Sınırsız - EOF Polyglot Veri Gizleme Motoru        ")
    print("===============================================================")
    print("Modlar:")
    print("  gizle : İstediğiniz boyuttaki veriyi/videoyu resme katar.")
    print("  coz   : Katılan veriyi IEND sınırından ayırıp kurtarır.")
    print("")
    print("Örnekler:")
    print("  python stego_sinirsiz.py gizle orijinal.png dev_video.mp4 gizli.png")
    print("  python stego_sinirsiz.py coz gizli.png cikan_video.mp4")
    print("===============================================================")

if __name__ == "__main__":
    main()
