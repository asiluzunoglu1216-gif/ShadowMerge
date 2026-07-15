#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ShadowMerge Studio - Tamamen Yerel ve Bağımsız Polyglot Arayüzü (Entegre Sürüm)
Tkinter ve TkinterDnD2 kullanılarak hazırlanmıştır. 
Özel logo desteği, komut satırı tetiklemesi ve Windows Kayıt Defteri entegrasyonuna sahiptir.
"""

import sys
import struct
import os
import tempfile
import base64
import winreg
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
except ImportError:
    print("Hata: 'tkinterdnd2' kütüphanesi eksik.")
    print("Kurulum için: pip install tkinterdnd2")
    sys.exit(1)

class ShadowMergeStudio(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("ShadowMerge Studio")
        self.geometry("750x680")
        self.configure(bg="#1e1e1e")
        self.resizable(False, False)

        # 1. Özel Logo (Icon) Desteği
        self.script_dizini = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.logo_yolu = os.path.join(self.script_dizini, "logo.ico")
        if os.path.exists(self.logo_yolu):
            try:
                self.iconbitmap(self.logo_yolu)
            except Exception:
                pass

        # Değişkenler
        self.png_yolu = tk.StringVar()
        self.mp4_yolu = tk.StringVar()
        self.zip_yolu = tk.StringVar()
        self.shadow_yolu = tk.StringVar()

        # Tema ve Stil Ayarları
        self.stil = ttk.Style(self)
        self.stil.theme_use('clam')
        
        self.stil.configure('TNotebook', background='#1e1e1e', borderwidth=0)
        self.stil.configure('TNotebook.Tab', background='#2d2d30', foreground='white', padding=[15, 8], font=('Segoe UI', 10, 'bold'))
        self.stil.map('TNotebook.Tab', background=[('selected', '#007acc')])
        
        self.stil.configure('TFrame', background='#1e1e1e')
        self.stil.configure('TLabel', background='#1e1e1e', foreground='#d4d4d4', font=('Segoe UI', 11))
        
        self.stil.configure('TButton', background='#333337', foreground='white', font=('Segoe UI', 10, 'bold'), borderwidth=1)
        self.stil.map('TButton', background=[('active', '#3e3e42'), ('disabled', '#2a2a2a')])
        
        self.stil.configure('Drop.TFrame', background='#252526', relief='solid', borderwidth=1)
        self.stil.configure('Drop.TLabel', background='#252526', foreground='#858585', font=('Segoe UI', 10, 'italic'))

        # Sekme Yöneticisi
        self.sekme_yoneticisi = ttk.Notebook(self)
        self.sekme_yoneticisi.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        self.sekme_olusturucu = ttk.Frame(self.sekme_yoneticisi)
        self.sekme_cozucu = ttk.Frame(self.sekme_yoneticisi)

        self.sekme_yoneticisi.add(self.sekme_olusturucu, text="Oluşturucu (Creator)")
        self.sekme_yoneticisi.add(self.sekme_cozucu, text="Oynatıcı / Çözücü (Player)")

        self.arayuz_olusturucu_hazirla()
        self.arayuz_cozucu_hazirla()
        
        # Alt Çubuk (Status/Action Bar)
        self.alt_cerceve = ttk.Frame(self)
        self.alt_cerceve.pack(fill=tk.X, side=tk.BOTTOM, padx=15, pady=10)
        
        btn_entegre = ttk.Button(self.alt_cerceve, text="Sisteme Entegre Et (Kayıt Et)", command=self.sisteme_entegre_et)
        btn_entegre.pack(side=tk.RIGHT)

        # 2. Çift Tıklama ile Otomatik Açılma (CLI Parametre Kontrolü)
        if len(sys.argv) > 1:
            arg_dosya = sys.argv[1]
            if os.path.exists(arg_dosya) and arg_dosya.endswith(".shadow"):
                self.sekme_yoneticisi.select(self.sekme_cozucu)
                self.shadow_yolu.set(arg_dosya)
                self.lbl_shadow_drop.config(text=os.path.basename(arg_dosya), foreground="#4caf50", font=('Segoe UI', 10, 'bold'))
                self.butonlari_guncelle(arg_dosya)

    def surukle_birak_alani(self, ebeveyn, metin, degisken, callback=None):
        cerceve = ttk.Frame(ebeveyn, style='Drop.TFrame')
        etiket = ttk.Label(cerceve, text=metin, style='Drop.TLabel', anchor="center")
        etiket.pack(expand=True, fill=tk.BOTH, padx=10, pady=20)
        
        cerceve.drop_target_register(DND_FILES)
        cerceve.dnd_bind('<<Drop>>', lambda e: self.dosya_suruklendi(e, degisken, etiket, callback))
        etiket.drop_target_register(DND_FILES)
        etiket.dnd_bind('<<Drop>>', lambda e: self.dosya_suruklendi(e, degisken, etiket, callback))
        
        buton = ttk.Button(ebeveyn, text="Dosya Seç", command=lambda: self.dosya_sec(degisken, etiket, callback))
        return cerceve, buton, etiket

    def dosya_suruklendi(self, olay, degisken, etiket, callback):
        yol = olay.data
        if yol.startswith('{') and yol.endswith('}'):
            yol = yol[1:-1]
        degisken.set(yol)
        etiket.config(text=os.path.basename(yol), foreground="#4caf50", font=('Segoe UI', 10, 'bold'))
        if callback:
            callback(yol)

    def dosya_sec(self, degisken, etiket, callback):
        yol = filedialog.askopenfilename()
        if yol:
            degisken.set(yol)
            etiket.config(text=os.path.basename(yol), foreground="#4caf50", font=('Segoe UI', 10, 'bold'))
            if callback:
                callback(yol)

    def arayuz_olusturucu_hazirla(self):
        baslik = ttk.Label(self.sekme_olusturucu, text="Oluşturucu: PNG (Zorunlu), MP4 ve ZIP (Opsiyonel)", font=('Segoe UI', 13, 'bold'), foreground='white')
        baslik.pack(pady=15)

        f_png, b_png, _ = self.surukle_birak_alani(self.sekme_olusturucu, "PNG Görselini Buraya Sürükleyin (Zorunlu)", self.png_yolu)
        f_png.pack(fill=tk.X, padx=30, pady=5)
        b_png.pack(pady=2)

        f_mp4, b_mp4, _ = self.surukle_birak_alani(self.sekme_olusturucu, "MP4 Videosunu Buraya Sürükleyin (İsteğe Bağlı)", self.mp4_yolu)
        f_mp4.pack(fill=tk.X, padx=30, pady=5)
        b_mp4.pack(pady=2)

        f_zip, b_zip, _ = self.surukle_birak_alani(self.sekme_olusturucu, "ZIP Arşivini Buraya Sürükleyin (İsteğe Bağlı)", self.zip_yolu)
        f_zip.pack(fill=tk.X, padx=30, pady=5)
        b_zip.pack(pady=2)

        uret_butonu = ttk.Button(self.sekme_olusturucu, text="ShadowMerge Dosyası Oluştur", command=self.shadow_olustur)
        uret_butonu.pack(pady=20, ipadx=10, ipady=5)

    def arayuz_cozucu_hazirla(self):
        baslik = ttk.Label(self.sekme_cozucu, text=".shadow Uzantılı Paketi Çöz ve Oynat", font=('Segoe UI', 13, 'bold'), foreground='white')
        baslik.pack(pady=30)

        f_shd, b_shd, self.lbl_shadow_drop = self.surukle_birak_alani(self.sekme_cozucu, "Oluşturulan .shadow Dosyasını Buraya Sürükleyin", self.shadow_yolu, callback=self.butonlari_guncelle)
        f_shd.pack(fill=tk.X, padx=30, pady=10)
        b_shd.pack(pady=5)

        kontrol_cercevesi = ttk.Frame(self.sekme_cozucu)
        kontrol_cercevesi.pack(pady=40)

        self.btn_foto = ttk.Button(kontrol_cercevesi, text="Fotoğrafı Göster", command=self.fotografi_goster)
        self.btn_foto.grid(row=0, column=0, padx=15, ipadx=10, ipady=10)

        self.btn_video = ttk.Button(kontrol_cercevesi, text="Videoyu Oynat", command=self.videoyu_oynat)
        self.btn_video.grid(row=0, column=1, padx=15, ipadx=10, ipady=10)

        self.btn_zip = ttk.Button(kontrol_cercevesi, text="ZIP Arşivini Çıkar", command=self.arsivi_cikar)
        self.btn_zip.grid(row=0, column=2, padx=15, ipadx=10, ipady=10)
        
        self.butonlari_kapat()

    def butonlari_kapat(self):
        self.btn_foto.state(['disabled'])
        self.btn_video.state(['disabled'])
        self.btn_zip.state(['disabled'])

    def butonlari_guncelle(self, yol):
        try:
            with open(yol, "rb") as f:
                baslik = f.read(24)
                if len(baslik) == 24:
                    png_boyut, mp4_boyut, zip_boyut = struct.unpack(">QQQ", baslik)
                    
                    self.btn_foto.state(['!disabled']) if png_boyut > 0 else self.btn_foto.state(['disabled'])
                    self.btn_video.state(['!disabled']) if mp4_boyut > 0 else self.btn_video.state(['disabled'])
                    self.btn_zip.state(['!disabled']) if zip_boyut > 0 else self.btn_zip.state(['disabled'])
                else:
                    self.butonlari_kapat()
        except Exception:
            self.butonlari_kapat()

    def shadow_olustur(self):
        p_yol = self.png_yolu.get()
        m_yol = self.mp4_yolu.get()
        z_yol = self.zip_yolu.get()

        if not p_yol or not os.path.exists(p_yol):
            messagebox.showwarning("Eksik Dosya", "Paketin kapak resmi olması için en azından bir PNG Görseli seçmek zorundasınız.")
            return

        try:
            with open(p_yol, "rb") as f: png_veri = f.read()
            
            mp4_veri = b""
            if m_yol and os.path.exists(m_yol):
                with open(m_yol, "rb") as f: mp4_veri = f.read()
                
            zip_veri = b""
            if z_yol and os.path.exists(z_yol):
                with open(z_yol, "rb") as f: zip_veri = f.read()

            baslik = struct.pack(">QQQ", len(png_veri), len(mp4_veri), len(zip_veri))
            saf_paket = baslik + png_veri + mp4_veri + zip_veri

            kayit_yolu = filedialog.asksaveasfilename(defaultextension=".shadow", filetypes=[("Shadow Paketleri", "*.shadow")])
            if not kayit_yolu: return

            with open(kayit_yolu, "wb") as f:
                f.write(saf_paket)

            messagebox.showinfo("İşlem Başarılı", "ShadowMerge dosyası başarıyla oluşturuldu!\nPaket kullanıma hazır.")
        except Exception as e:
            messagebox.showerror("Kritik Hata", "Dosya birleştirilirken bir sorun oluştu:\n" + str(e))

    def verileri_ayristir(self):
        s_yol = self.shadow_yolu.get()
        if not s_yol or not os.path.exists(s_yol):
            messagebox.showwarning("Hata", "Lütfen geçerli bir .shadow dosyası yükleyin.")
            return None, None, None

        try:
            with open(s_yol, "rb") as f:
                baslik = f.read(24)
                if len(baslik) < 24:
                    messagebox.showerror("Hata", "Dosya boyutu çok küçük veya format hatalı.")
                    return None, None, None
                
                boyut_png, boyut_mp4, boyut_zip = struct.unpack(">QQQ", baslik)
                
                png_veri = f.read(boyut_png) if boyut_png > 0 else b""
                mp4_veri = f.read(boyut_mp4) if boyut_mp4 > 0 else b""
                zip_veri = f.read(boyut_zip) if boyut_zip > 0 else b""
                
                return png_veri, mp4_veri, zip_veri
        except Exception as e:
            messagebox.showerror("Okuma Hatası", "Paket ayrıştırılırken hata oluştu:\n" + str(e))
            return None, None, None

    def fotografi_goster(self):
        png_veri, _, _ = self.verileri_ayristir()
        if not png_veri:
            messagebox.showwarning("Uyarı", "Bu pakette kapak görseli bulunmamaktadır.")
            return

        try:
            pencere = tk.Toplevel(self)
            pencere.title("ShadowMerge - Görsel Önizleme")
            pencere.configure(bg="#1e1e1e")
            if os.path.exists(self.logo_yolu):
                try: pencere.iconbitmap(self.logo_yolu)
                except Exception: pass
            
            b64_kodlu_veri = base64.b64encode(png_veri)
            resim_objesi = tk.PhotoImage(data=b64_kodlu_veri)
            
            etiket = tk.Label(pencere, image=resim_objesi, bg="#1e1e1e")
            etiket.image = resim_objesi
            etiket.pack(padx=20, pady=20)
        except Exception as e:
            messagebox.showerror("Hata", "Görsel yüklenemedi. Dosya PNG formatında olmayabilir.\n" + str(e))

    def videoyu_oynat(self):
        _, mp4_veri, _ = self.verileri_ayristir()
        if not mp4_veri:
            messagebox.showwarning("Uyarı", "Bu pakette gizli video bulunmamaktadır.")
            return

        try:
            gecici_yol = os.path.join(tempfile.gettempdir(), "shadow_gecici_video.mp4")
            with open(gecici_yol, "wb") as f:
                f.write(mp4_veri)
            
            os.startfile(gecici_yol)
        except Exception as e:
            messagebox.showerror("Hata", "Video oynatılamadı:\n" + str(e))

    def arsivi_cikar(self):
        _, _, zip_veri = self.verileri_ayristir()
        if not zip_veri:
            messagebox.showwarning("Uyarı", "Bu pakette gizli arşiv bulunmamaktadır.")
            return

        try:
            masaustu_hedef = r"C:\Users\Asil10tr\Desktop\cikartilan_arsiv.zip"
            with open(masaustu_hedef, "wb") as f:
                f.write(zip_veri)
            
            messagebox.showinfo("Başarılı", "ZIP Arşivi başarıyla masaüstüne çıkarıldı!\nDosya: " + masaustu_hedef)
        except Exception as e:
            messagebox.showerror("Hata", "Arşiv çıkarılamadı:\n" + str(e))

    def sisteme_entegre_et(self):
        try:
            script_yolu = os.path.abspath(sys.argv[0])
            python_yolu = sys.executable
            
            # python.exe script.py "%1"
            komut_dizgesi = f'"{python_yolu}" "{script_yolu}" "%1"'

            # .shadow uzantısını tanıtma
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, ".shadow") as key:
                winreg.SetValue(key, "", winreg.REG_SZ, "ShadowMerge.AssocFile")
                
            # Sınıf anahtarını oluşturma
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, "ShadowMerge.AssocFile") as key:
                winreg.SetValue(key, "", winreg.REG_SZ, "ShadowMerge Paketi")
                
            # Simge (DefaultIcon) ayarlama
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, r"ShadowMerge.AssocFile\DefaultIcon") as key:
                if os.path.exists(self.logo_yolu):
                    winreg.SetValue(key, "", winreg.REG_SZ, f'"{self.logo_yolu}",0')
                    
            # Açma komutunu (shell\open\command) ayarlama
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, r"ShadowMerge.AssocFile\shell\open\command") as key:
                winreg.SetValue(key, "", winreg.REG_SZ, komut_dizgesi)
                
            messagebox.showinfo("Başarılı", "ShadowMerge sisteme başarıyla entegre edildi!\nArtık .shadow dosyalarına çift tıklayarak doğrudan Player sekmesinde açabilirsiniz.")
        except PermissionError:
            messagebox.showerror("Yetki Hatası", "Kayıt defterine yazabilmek için programı Yönetici (Administrator) olarak çalıştırmalısınız.\n\nLütfen programı kapatıp, sağ tıklayarak 'Yönetici olarak çalıştır' seçeneğiyle tekrar açın.")
        except Exception as e:
            messagebox.showerror("Kayıt Hatası", "Kayıt defterine entegre edilirken beklenmedik bir hata oluştu:\n" + str(e))


def baslat():
    uygulama = ShadowMergeStudio()
    uygulama.mainloop()

if __name__ == "__main__":
    baslat()
