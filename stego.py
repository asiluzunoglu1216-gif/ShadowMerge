#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Stego - LSB Steganography Aracı
Bu program, bir görselin piksellerinin en önemsiz bitlerine (Least Significant Bit - LSB) 
veri gizleme ve bu veriyi geri çıkarma işlemi yapar.
Güvenlik filtrelerine takılmaması için doğrudan ham RGB piksel verisine müdahale eder.
"""

import sys
import struct
import os

try:
    from PIL import Image
except ImportError:
    print("Hata: Pillow kütüphanesi yüklü değil. Lütfen 'pip install Pillow' komutuyla yükleyin.")
    sys.exit(1)

def gizle(orijinal_resim, gizlenecek_dosya, cikti_resim):
    # Dosya varlık kontrolleri
    if not os.path.exists(orijinal_resim):
        print(f"Hata: {orijinal_resim} bulunamadı.")
        sys.exit(1)
    if not os.path.exists(gizlenecek_dosya):
        print(f"Hata: {gizlenecek_dosya} bulunamadı.")
        sys.exit(1)

    print("[*] Hedef dosyalar belleğe okunuyor...")
    try:
        with open(gizlenecek_dosya, 'rb') as f:
            veri = f.read()
    except Exception as e:
        print(f"Hata: Gizlenecek dosya okunamadı -> {e}")
        sys.exit(1)

    try:
        # Transparanlık vb. faktörleri sabitlemek ve standart LSB yapmak için RGB formatına dönüştürüyoruz
        img = Image.open(orijinal_resim).convert('RGB')
    except Exception as e:
        print(f"Hata: Resim açılamadı -> {e}")
        sys.exit(1)

    # İşlem hızını artırmak için tüm pikselleri düz bir bytearray'e çeviriyoruz
    pixels = bytearray(img.tobytes())
    veri_boyutu = len(veri)
    
    # Başa 8 byte (64 bit) uzunluğunda boyut bilgisi ekliyoruz (Big Endian)
    # Böylece program okurken kaç byte veri çıkarması gerektiğini bilecek
    baslik = struct.pack(">Q", veri_boyutu)
    tam_veri = baslik + veri
    toplam_bit = len(tam_veri) * 8

    # Kapasite kontrolü (Her renk kanalında (R,G,B) 1 bit taşıyoruz)
    if toplam_bit > len(pixels):
        max_kapasite = (len(pixels) // 8) - 8
        print("Hata: Resim bu dosyayı gizlemek için yeterince büyük değil!")
        print(f"Gerekli kapasite : {veri_boyutu} byte")
        print(f"Maksimum kapasite: {max_kapasite} byte")
        print("Çözüm: Daha yüksek çözünürlüklü bir resim kullanın.")
        sys.exit(1)

    print(f"[*] {veri_boyutu} byte boyutundaki veri, LSB yöntemiyle resme gömülüyor. Lütfen bekleyin...")
    
    # Veriyi bit bit resim kanallarına gömme işlemi
    for i in range(toplam_bit):
        byte_idx = i // 8
        bit_idx = 7 - (i % 8)
        bit = (tam_veri[byte_idx] >> bit_idx) & 1
        
        # Seçili piksel kanalının LSB'sini 0 yap (mask ~1) ve yeni biti ekle (| bit)
        pixels[i] = (pixels[i] & ~1) | bit

    print("[*] Gömme işlemi tamamlandı, yeni resim işleniyor...")
    try:
        yeni_img = Image.frombytes(img.mode, img.size, bytes(pixels))
        yeni_img.save(cikti_resim, format="PNG")
        print(f"[+] BAŞARILI: Veri '{cikti_resim}' adlı resme gizlendi.")
        print(f"    Artık bu PNG dosyasını normal bir resim gibi açıp görüntüleyebilirsiniz.")
    except Exception as e:
        print(f"Hata: Çıktı resmi kaydedilemedi -> {e}")
        sys.exit(1)


def coz(icinde_veri_olan_resim, cikartilacak_dosya):
    if not os.path.exists(icinde_veri_olan_resim):
        print(f"Hata: {icinde_veri_olan_resim} bulunamadı.")
        sys.exit(1)

    print("[*] Stego analizi için resim okunuyor...")
    try:
        img = Image.open(icinde_veri_olan_resim).convert('RGB')
    except Exception as e:
        print(f"Hata: Resim açılamadı -> {e}")
        sys.exit(1)

    pixels = bytearray(img.tobytes())
    
    # İlk olarak 64 bit'lik (8 byte) boyut başlığını okuyoruz
    baslik_bit = 64
    if len(pixels) < baslik_bit:
        print("Hata: Resim çok küçük, geçerli bir stego verisi barındıramaz.")
        sys.exit(1)

    veri_boyutu = 0
    for i in range(baslik_bit):
        bit = pixels[i] & 1
        veri_boyutu = (veri_boyutu << 1) | bit

    toplam_veri_biti = veri_boyutu * 8

    # Mantıksal doğrulama: Eğer başlıkta okunan boyut devasa ise, büyük ihtimalle 
    # bu resim tarafımızca oluşturulmuş bir stego resmi değildir.
    if (baslik_bit + toplam_veri_biti) > len(pixels) or veri_boyutu == 0:
        print("Hata: Çıkarılacak dosya boyutu tutarsız veya resim kapasitesini aşıyor.")
        print("Bu resimde bizim aracımızla gizlenmiş herhangi bir veri bulunmayabilir.")
        sys.exit(1)

    print(f"[*] {veri_boyutu} byte boyutunda gizli veri tespit edildi. Çıkarılıyor...")
    
    # Boş bir byte dizisi oluşturuyoruz
    cikti_verisi = bytearray(veri_boyutu)
    
    # Kalan piksellerdeki bitleri birleştirerek orijinal veriyi elde ediyoruz
    for i in range(toplam_veri_biti):
        piksel_idx = baslik_bit + i
        bit = pixels[piksel_idx] & 1
        
        byte_idx = i // 8
        bit_idx = 7 - (i % 8)
        
        if bit:
            cikti_verisi[byte_idx] |= (1 << bit_idx)

    print("[*] Steganography verisi başarıyla çıkartıldı. Dosyaya yazılıyor...")
    try:
        with open(cikartilacak_dosya, 'wb') as f:
            f.write(cikti_verisi)
        print(f"[+] BAŞARILI: Gizli veri '{cikartilacak_dosya}' dosyasına kaydedildi.")
    except Exception as e:
        print(f"Hata: Çıkarılan veri dosyaya yazılamadı -> {e}")
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        kullanim_yazdir()
        sys.exit(1)

    mod = sys.argv[1].lower()

    if mod == "gizle":
        if len(sys.argv) != 5:
            print("Kullanım Hatası!")
            print("Doğru Kullanım: python stego.py gizle <orijinal_resim.png> <gizlenecek_video.mp4> <cikti_resim.png>")
            sys.exit(1)
        gizle(sys.argv[2], sys.argv[3], sys.argv[4])
        
    elif mod == "coz":
        if len(sys.argv) != 4:
            print("Kullanım Hatası!")
            print("Doğru Kullanım: python stego.py coz <icinde_veri_olan_resim.png> <cikartilacak_video.mp4>")
            sys.exit(1)
        coz(sys.argv[2], sys.argv[3])
        
    else:
        print("Hata: Geçersiz Mod!")
        kullanim_yazdir()
        sys.exit(1)

def kullanim_yazdir():
    print("===============================================================")
    print("           Stego - Gelişmiş LSB Veri Gizleme Motoru           ")
    print("===============================================================")
    print("Modlar:")
    print("  gizle : İstediğiniz videoyu/dosyayı bir resmin içine gizler.")
    print("  coz   : Resmin içindeki gizli dosyayı sağ salim çıkartır.")
    print("")
    print("Örnek Kullanım:")
    print("  python stego.py gizle orijinal.png sirlar_odasi.mp4 masum_resim.png")
    print("  python stego.py coz masum_resim.png cikartilan_video.mp4")
    print("===============================================================")

if __name__ == "__main__":
    main()
