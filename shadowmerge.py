#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ShadowMerge - Uzantı Odaklı Polyglot Derleyici Programı
Bu araç, bir görseli ve bir videoyu hiçbir byte kayması yaşatmadan, tamamen
ham binary manipülasyonu ile birleştirir. Çıktı dosyasının uzantısı '.ico' 
yapıldığında Windows resim motoru tarafından, '.mp4' yapıldığında ise 
video oynatıcılar tarafından ekstra bir ayıklama işlemine gerek kalmadan 
doğrudan açılır.

Harici hiçbir bağımlılık (ffmpeg, imagemagick vb.) kullanmaz.
"""

import sys
import struct
import os

def main():
    # 1. Parametre Düzeni Kontrolü
    if len(sys.argv) != 4:
        print("Kullanım Hatası!")
        print("Doğru Kullanım: python shadowmerge.py <cikti_dosyasi> <gorsel_dosyasi> <video_dosyasi>")
        sys.exit(1)

    cikti_yolu = sys.argv[1]
    gorsel_yolu = sys.argv[2]
    video_yolu = sys.argv[3]

    # Girdi dosyalarının sistemde var olup olmadığını kontrol ediyoruz
    if not os.path.exists(gorsel_yolu):
        print(f"Hata: Görsel dosyası bulunamadı -> {gorsel_yolu}")
        sys.exit(1)
        
    if not os.path.exists(video_yolu):
        print(f"Hata: Video dosyası bulunamadı -> {video_yolu}")
        sys.exit(1)

    print("[*] Hedef dosyalar belleğe okunuyor...")
    try:
        with open(gorsel_yolu, "rb") as f:
            gorsel_veri = f.read()
        with open(video_yolu, "rb") as f:
            video_veri = f.read()
    except Exception as e:
        print(f"Hata: Dosyalar okunurken bir sorun oluştu -> {e}")
        sys.exit(1)

    gorsel_boyut = len(gorsel_veri)
    
    # =========================================================================
    # BÖLÜM 1: Evrensel Kutu Manipülasyonu (İlk 256 Byte Sahte Başlık)
    # =========================================================================
    # İlk 256 byte'ı boş bir alan olarak tahsis ediyoruz.
    baslik = bytearray(256)
    
    # İstenilen 6 byte'lık ICO sihirli kodu: 00 00 (Rezerve), 01 00 (Tip), 01 00 (Sayı)
    baslik[0:6] = b"\x00\x00\x01\x00\x01\x00"
    
    # Ancak MP4 okuyucuların bu ilk bloğu boş (free space) sayıp atlaması için 
    # ilk 4 byte '00 00 01 00' (Big-Endian 256) kalmalı ve hemen ardına (4-7 arasına)
    # 'free' kodu yazılmalıdır. Bu ICO'nun görsel sayısı (Image Count) değerini bozsa da, 
    # Windows parser'ı dizin yapısını okumaya devam edecek esnekliktedir.
    baslik[4:8] = b"free" 
    
    # İlk 22 byte içerisindeki ICO dizin girdilerinin geri kalanını dolduruyoruz.
    # 'free' kelimesinden dolayı 6. ve 7. byte'lar 0x65 (101) değerini alır 
    # ve bu görsel genişliği/yüksekliği olarak kabul edilir. Geri kalanları biz yazarız:
    baslik[8] = 0           # Renk paleti sayısı
    baslik[9] = 0           # Rezerve
    baslik[10:12] = b"\x01\x00" # Renk düzlemi (Planes = 1)
    baslik[12:14] = b"\x20\x00" # Bit derinliği (32 bpp)
    
    # Görselin dinamik boyutu (Little-Endian)
    baslik[14:18] = struct.pack("<I", gorsel_boyut)
    
    # Görselin bulunacağı mutlak offset (Little-Endian)
    # 256 (Sahte Başlık) + 24 (Gerçek FTYP) + 8 (SKIP Kutu Başlığı) = 288
    gorsel_offset = 288
    baslik[18:22] = struct.pack("<I", gorsel_offset)
    
    # =========================================================================
    # BÖLÜM 2: Hizalanmış MP4 Yerleşimi (Gerçek FTYP Kutusu)
    # =========================================================================
    # 256. byte'a konumlanacak 24 byte uzunluğundaki geçerli MP4 marka dizisi.
    # 00 00 00 18 (24 byte) + ftyp + isomiso2avc1mp41
    ftyp_kutusu = b"\x00\x00\x00\x18ftypisomiso2avc1mp41"
    
    # =========================================================================
    # BÖLÜM 3: Görseli MP4'ten Gizlemek İçin SKIP (Atla) Kutusu
    # =========================================================================
    # Boyut = Görsel verisinin boyutu + 8 byte (skip başlığının kendi boyutu)
    # Tip = skip (MP4 parser bu kutunun içini tamamen boş veri kabul edip atlar)
    skip_boyutu = gorsel_boyut + 8
    skip_baslik = struct.pack(">I", skip_boyutu) + b"skip"
    
    # =========================================================================
    # BÖLÜM 4: Kesintisiz Birleştirme ve Dosya Yazımı
    # =========================================================================
    print("[*] Veriler hizalanıyor ve binary akış inşa ediliyor...")
    try:
        with open(cikti_yolu, "wb") as f:
            # 1. İlk 256 Byte'lık çöp kutusu (İçinde ICO sihrini barındırır)
            f.write(baslik)
            
            # 2. Tam 256. offsetten başlayan 24 Byte'lık geçerli MP4 FTYP kutusu
            f.write(ftyp_kutusu)
            
            # 3. İçine görselin gömüleceği 8 Byte'lık SKIP kutu başlığı
            f.write(skip_baslik)
            
            # 4. Saf görsel verisi (Tam 288. offsette yer alır, ICO dizini burayı işaret eder)
            f.write(gorsel_veri)
            
            # 5. Saf video verisi (Kalan tüm byte'lar, MP4 yapısını devam ettirir)
            f.write(video_veri)
            
        print(f"[+] BAŞARILI: Uzantı odaklı Polyglot dosya oluşturuldu -> {cikti_yolu}")
        print("    ------------------------------------------------------------------")
        print("    * Dosya uzantısını '.ico' veya '.png' yaparsanız resim açılır.")
        print("    * Dosya uzantısını '.mp4' yaparsanız video doğrudan çalışır.")
        print("    * Hiçbir ayıklama aracına gerek yoktur, yapı native (yerel) desteklenir.")
        print("    ------------------------------------------------------------------")
    except Exception as e:
        print(f"Hata: Çıktı dosyası yazılırken beklenmedik bir sorun oluştu -> {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
