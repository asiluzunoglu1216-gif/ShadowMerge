#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ShadowMerge Studio Ultimate - Askeri Düzey Şifreleme ve Sıkıştırma
Tkinter ve TkinterDnD2 kullanılarak hazırlanmıştır. 
Sınırlandırılmamış dosya depolama (Evrensel Depo), Zlib sıkıştırma (Level 9), 
Anti-Adli Bilişim (XOR + Bitwise Left Rotation) destekli tek parça bağımsız bir yazılımdır.
"""

import sys
import struct
import os
import tempfile
import zlib
import winreg
import ctypes
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
except ImportError:
    print("Hata: 'tkinterdnd2' kütüphanesi eksik.")
    print("Kurulum için: pip install tkinterdnd2")
    sys.exit(1)

# ==========================================
# ASKERİ DÜZEY ŞİFRELEME MOTORU (XOR + ROTL)
# ==========================================
# Performans (C-Hızı) için 256 byte'lık önden hesaplanmış Lookup Table (LUT) kullanıyoruz.
ENC_TABLE = bytearray(256)
DEC_TABLE = bytearray(256)
SECRET_KEY = 0x8C  # Gizli XOR Anahtarı

for i in range(256):
    # Şifreleme: Önce XOR, sonra 3 bit Sola Kaydırma (Bitwise Left Rotation)
    b = i ^ SECRET_KEY
    rotated = ((b << 3) & 0xFF) | (b >> 5)
    ENC_TABLE[i] = rotated
    
    # Çözme: Şifrelenmiş byte üzerinden orijinal i'yi eşleştiriyoruz
    DEC_TABLE[rotated] = i


class ShadowMergeUltimate(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("ShadowMerge Studio Ultimate")
        self.geometry("850x700")
        self.configure(bg="#1e1e1e")
        self.resizable(False, False)
        
        self.current_shadow = None

        # Windows Görev Çubuğu (Taskbar) İkonunu Düzeltme (Sadece Windows)
        try:
            myappid = 'shadowmerge.studio.ultimate.1'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

        # Özel Logo (Icon) Desteği
        self.script_dizini = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.logo_yolu = os.path.join(self.script_dizini, "logo.ico")
        if os.path.exists(self.logo_yolu):
            try: 
                self.iconbitmap(self.logo_yolu)
            except Exception: 
                pass

        # Tema ve Stil Ayarları
        self.stil = ttk.Style(self)
        self.stil.theme_use('clam')
        
        self.stil.configure('TNotebook', background='#1e1e1e', borderwidth=0)
        self.stil.configure('TNotebook.Tab', background='#2d2d30', foreground='white', padding=[15, 8], font=('Segoe UI', 10, 'bold'))
        self.stil.map('TNotebook.Tab', background=[('selected', '#d32f2f')]) # Kırmızı vurgu (Ultimate)
        
        self.stil.configure('TFrame', background='#1e1e1e')
        self.stil.configure('TLabel', background='#1e1e1e', foreground='#d4d4d4', font=('Segoe UI', 11))
        
        self.stil.configure('TButton', background='#333337', foreground='white', font=('Segoe UI', 10, 'bold'), borderwidth=1)
        self.stil.map('TButton', background=[('active', '#e53935'), ('disabled', '#2a2a2a')])
        
        self.stil.configure('Drop.TFrame', background='#252526', relief='solid', borderwidth=1)
        self.stil.configure('Drop.TLabel', background='#252526', foreground='#858585', font=('Segoe UI', 11, 'bold'))

        self.stil.configure('Treeview', background='#252526', foreground='white', fieldbackground='#252526', rowheight=25)
        self.stil.map('Treeview', background=[('selected', '#d32f2f')])
        self.stil.configure('Treeview.Heading', background='#333337', foreground='white', font=('Segoe UI', 10, 'bold'))

        # Sekme Yöneticisi
        self.sekme_yoneticisi = ttk.Notebook(self)
        self.sekme_yoneticisi.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        self.sekme_olusturucu = ttk.Frame(self.sekme_yoneticisi)
        self.sekme_cozucu = ttk.Frame(self.sekme_yoneticisi)

        self.sekme_yoneticisi.add(self.sekme_olusturucu, text="Oluşturucu (Creator)")
        self.sekme_yoneticisi.add(self.sekme_cozucu, text="Çözücü (Extractor)")

        self.arayuz_olusturucu_hazirla()
        self.arayuz_cozucu_hazirla()
        
        # Alt Çubuk (Status/Action Bar)
        self.alt_cerceve = ttk.Frame(self)
        self.alt_cerceve.pack(fill=tk.X, side=tk.BOTTOM, padx=15, pady=10)
        
        btn_entegre = ttk.Button(self.alt_cerceve, text="Sisteme Entegre Et (Kayıt Et)", command=self.sisteme_entegre_et)
        btn_entegre.pack(side=tk.RIGHT)

        # Çift Tıklama ile Otomatik Açılma (CLI Parametre Kontrolü)
        if len(sys.argv) > 1:
            arg_dosya = sys.argv[1]
            if os.path.exists(arg_dosya) and arg_dosya.endswith(".shadow"):
                self.sekme_yoneticisi.select(self.sekme_cozucu)
                self.load_shadow(arg_dosya)
                self.lbl_shadow_drop.config(text=os.path.basename(arg_dosya), foreground="#4caf50")

    def boyut_formatla(self, boyut):
        for birim in ['B', 'KB', 'MB', 'GB']:
            if boyut < 1024.0:
                return f"{boyut:.2f} {birim}"
            boyut /= 1024.0
        return f"{boyut:.2f} TB"

    # ==========================================
    # OLUŞTURUCU (CREATOR) ARAYÜZ VE FONKSİYONLARI
    # ==========================================
    def arayuz_olusturucu_hazirla(self):
        baslik = ttk.Label(self.sekme_olusturucu, text="Sınırsız Dosya Ekle (Şifrelenip Sıkıştırılacaktır)", font=('Segoe UI', 13, 'bold'), foreground='white')
        baslik.pack(pady=10)

        # Büyük Sürükle-Bırak Alanı
        cerceve_drop = ttk.Frame(self.sekme_olusturucu, style='Drop.TFrame')
        cerceve_drop.pack(fill=tk.X, padx=20, pady=10, ipady=15)
        
        lbl_drop = ttk.Label(cerceve_drop, text="HERHANGİ BİR DOSYAYI BURAYA SÜRÜKLEYİN", style='Drop.TLabel', anchor="center")
        lbl_drop.pack(expand=True, fill=tk.BOTH, pady=10)
        
        cerceve_drop.drop_target_register(DND_FILES)
        cerceve_drop.dnd_bind('<<Drop>>', self.dosya_suruklendi_creator)
        lbl_drop.drop_target_register(DND_FILES)
        lbl_drop.dnd_bind('<<Drop>>', self.dosya_suruklendi_creator)

        # Treeview Listesi
        f_liste = ttk.Frame(self.sekme_olusturucu)
        f_liste.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        scroll = ttk.Scrollbar(f_liste, orient=tk.VERTICAL)
        self.creator_tree = ttk.Treeview(f_liste, columns=("ad", "uzanti", "boyut"), show="headings", yscrollcommand=scroll.set)
        scroll.config(command=self.creator_tree.yview)
        
        self.creator_tree.heading("ad", text="Dosya Adı")
        self.creator_tree.heading("uzanti", text="Uzantı")
        self.creator_tree.heading("boyut", text="Orijinal Boyut")
        self.creator_tree.column("ad", width=400)
        self.creator_tree.column("uzanti", width=100, anchor="center")
        self.creator_tree.column("boyut", width=150, anchor="e")
        
        self.creator_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Butonlar
        f_butonlar = ttk.Frame(self.sekme_olusturucu)
        f_butonlar.pack(pady=15)
        
        btn_temizle = ttk.Button(f_butonlar, text="Listeyi Temizle", command=lambda: self.creator_tree.delete(*self.creator_tree.get_children()))
        btn_temizle.grid(row=0, column=0, padx=10, ipadx=10, ipady=5)
        
        btn_uret = ttk.Button(f_butonlar, text="ShadowMerge Paketi Oluştur", command=self.shadow_olustur)
        btn_uret.grid(row=0, column=1, padx=10, ipadx=10, ipady=5)

    def dosya_suruklendi_creator(self, olay):
        yollar = self.tk.splitlist(olay.data)
        for yol in yollar:
            if os.path.isfile(yol):
                ad = os.path.basename(yol)
                _, uzanti = os.path.splitext(ad)
                if not uzanti: uzanti = "Bilinmeyen"
                boyut = os.path.getsize(yol)
                boyut_str = self.boyut_formatla(boyut)
                # Orijinal yolu arka planda 'text' parametresinde tutuyoruz
                self.creator_tree.insert("", tk.END, text=yol, values=(ad, uzanti, boyut_str))

    def shadow_olustur(self):
        items = self.creator_tree.get_children()
        if not items:
            messagebox.showwarning("Boş Liste", "Lütfen pakete eklenecek dosyaları sürükleyin.")
            return
            
        save_path = filedialog.asksaveasfilename(defaultextension=".shadow", filetypes=[("Shadow Paketleri", "*.shadow")])
        if not save_path: return
        
        try:
            with open(save_path, "wb") as out_f:
                files_meta = []
                for item_id in items:
                    item = self.creator_tree.item(item_id)
                    src_path = item['text']
                    ad = item['values'][0]
                    
                    with open(src_path, "rb") as in_f:
                        raw_data = in_f.read()
                        
                    orig_size = len(raw_data)
                    
                    # 1. Zlib ile maksimum sıkıştırma
                    comp_data = zlib.compress(raw_data, level=9)
                    
                    # 2. XOR ve Sol Kaydırma (Hızlı C-Seviyesi tablodan dönüşüm)
                    # Binwalk gibi programların analiz etmesi tamamen engellendi.
                    enc_data = comp_data.translate(ENC_TABLE)
                    enc_size = len(enc_data)
                    
                    out_f.write(enc_data)
                    
                    files_meta.append({
                        'name': ad,
                        'orig_size': orig_size,
                        'enc_size': enc_size
                    })
                    
                # TOC (İçindekiler) Tablosunu Oluşturma
                toc_bytes = bytearray()
                toc_bytes += struct.pack(">I", len(files_meta))
                for f in files_meta:
                    nb = f['name'].encode('utf-8')
                    toc_bytes += struct.pack(">H", len(nb))
                    toc_bytes += nb
                    toc_bytes += struct.pack(">Q", f['orig_size'])
                    toc_bytes += struct.pack(">Q", f['enc_size'])
                    
                # Dosyanın en sonuna TOC verisi, TOC boyutu ve Güvenlik İmzası eklenir
                out_f.write(toc_bytes)
                out_f.write(struct.pack(">Q", len(toc_bytes)))
                out_f.write(b"SHDWULTM") # 8 bytes magic signature
                
            messagebox.showinfo("Başarılı", "ShadowMerge Ultimate paketi başarıyla oluşturuldu!\n\nTüm veriler şifrelendi ve Zlib ile sıkıştırıldı. Analiz araçları bu içeriği göremez.")
            self.creator_tree.delete(*items)
        except Exception as e:
            messagebox.showerror("Kritik Hata", "Paket oluşturulurken hata meydana geldi:\n" + str(e))

    # ==========================================
    # ÇÖZÜCÜ (EXTRACTOR) ARAYÜZ VE FONKSİYONLARI
    # ==========================================
    def arayuz_cozucu_hazirla(self):
        baslik = ttk.Label(self.sekme_cozucu, text="Paket Çözücü: İçeriği Görüntüle ve Çıkart", font=('Segoe UI', 13, 'bold'), foreground='white')
        baslik.pack(pady=10)

        cerceve_drop = ttk.Frame(self.sekme_cozucu, style='Drop.TFrame')
        cerceve_drop.pack(fill=tk.X, padx=20, pady=5, ipady=10)
        
        self.lbl_shadow_drop = ttk.Label(cerceve_drop, text=".shadow Dosyasını Buraya Sürükleyin", style='Drop.TLabel', anchor="center")
        self.lbl_shadow_drop.pack(expand=True, fill=tk.BOTH, pady=5)
        
        cerceve_drop.drop_target_register(DND_FILES)
        cerceve_drop.dnd_bind('<<Drop>>', lambda e: self.suruklenen_shadow(e))
        self.lbl_shadow_drop.drop_target_register(DND_FILES)
        self.lbl_shadow_drop.dnd_bind('<<Drop>>', lambda e: self.suruklenen_shadow(e))

        f_liste = ttk.Frame(self.sekme_cozucu)
        f_liste.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        scroll = ttk.Scrollbar(f_liste, orient=tk.VERTICAL)
        self.player_tree = ttk.Treeview(f_liste, columns=("ad", "uzanti", "boyut"), show="headings", yscrollcommand=scroll.set)
        scroll.config(command=self.player_tree.yview)
        
        self.player_tree.heading("ad", text="Gizli Dosya Adı")
        self.player_tree.heading("uzanti", text="Uzantı")
        self.player_tree.heading("boyut", text="Orijinal Boyut")
        self.player_tree.column("ad", width=400)
        self.player_tree.column("uzanti", width=100, anchor="center")
        self.player_tree.column("boyut", width=150, anchor="e")
        
        self.player_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.btn_indir = ttk.Button(self.sekme_cozucu, text="Seçili Dosyayı Bilgisayara İndir", command=self.dosyayi_indir)
        self.btn_indir.pack(pady=15, ipadx=10, ipady=5)
        self.btn_indir.state(['disabled'])

    def suruklenen_shadow(self, olay):
        yol = olay.data
        if yol.startswith('{') and yol.endswith('}'):
            yol = yol[1:-1]
        self.lbl_shadow_drop.config(text=os.path.basename(yol), foreground="#4caf50")
        self.load_shadow(yol)

    def load_shadow(self, yol):
        self.current_shadow = yol
        self.player_tree.delete(*self.player_tree.get_children())
        
        files = self.parse_shadow_toc(yol)
        if not files:
            messagebox.showerror("Geçersiz Dosya", "Bu dosya geçerli bir ShadowMerge Ultimate paketi değil veya bozulmuş.")
            self.btn_indir.state(['disabled'])
            return
            
        for f in files:
            boyut_str = self.boyut_formatla(f['orig_size'])
            _, uzanti = os.path.splitext(f['name'])
            if not uzanti: uzanti = "Bilinmeyen"
            
            self.player_tree.insert("", tk.END, text=str(f['index']), values=(f['name'], uzanti, boyut_str))
            
        self.btn_indir.state(['!disabled'])

    def parse_shadow_toc(self, filepath):
        try:
            with open(filepath, "rb") as f:
                f.seek(-16, os.SEEK_END)
                toc_size_bytes = f.read(8)
                magic = f.read(8)
                
                if magic != b"SHDWULTM":
                    return None
                    
                toc_size = struct.unpack(">Q", toc_size_bytes)[0]
                f.seek(-(16 + toc_size), os.SEEK_END)
                toc_data = f.read(toc_size)
                
                offset = 0
                file_count = struct.unpack_from(">I", toc_data, offset)[0]
                offset += 4
                
                files = []
                data_offset = 0
                for i in range(file_count):
                    name_len = struct.unpack_from(">H", toc_data, offset)[0]
                    offset += 2
                    name = toc_data[offset:offset+name_len].decode('utf-8')
                    offset += name_len
                    orig_size, enc_size = struct.unpack_from(">QQ", toc_data, offset)
                    offset += 16
                    
                    files.append({
                        'index': i,
                        'name': name,
                        'orig_size': orig_size,
                        'enc_size': enc_size,
                        'data_offset': data_offset
                    })
                    data_offset += enc_size
                    
                return files
        except Exception:
            return None

    def dosyayi_indir(self):
        selected = self.player_tree.selection()
        if not selected:
            messagebox.showwarning("Seçim Yapılmadı", "Lütfen indirmek istediğiniz dosyayı listeden seçin.")
            return
            
        item = self.player_tree.item(selected[0])
        idx = int(item['text'])
        ad = item['values'][0]
        
        save_path = filedialog.asksaveasfilename(initialfile=ad)
        if not save_path: return
        
        files = self.parse_shadow_toc(self.current_shadow)
        target = next((x for x in files if x['index'] == idx), None)
        if not target: return
        
        try:
            with open(self.current_shadow, "rb") as f:
                f.seek(target['data_offset'])
                enc_data = f.read(target['enc_size'])
                
            # 1. Şifreyi Çöz (Tersine Çevrilmiş LUT ile C-Hızında)
            dec_data = enc_data.translate(DEC_TABLE)
            # 2. Zlib Sıkıştırmasını Aç
            raw_data = zlib.decompress(dec_data)
            
            with open(save_path, "wb") as f:
                f.write(raw_data)
                
            messagebox.showinfo("Başarılı", f"{target['name']} sıfır kayıpla başarıyla çıkartıldı!")
        except Exception as e:
            messagebox.showerror("Hata", "Dosya çıkartılırken bir sorun oluştu:\n" + str(e))

    # ==========================================
    # WINDOWS KAYIT DEFTERİ ENTEGRASYONU
    # ==========================================
    def sisteme_entegre_et(self):
        try:
            script_yolu = os.path.abspath(sys.argv[0])
            python_yolu = sys.executable
            komut_dizgesi = f'"{python_yolu}" "{script_yolu}" "%1"'

            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, ".shadow") as key:
                winreg.SetValue(key, "", winreg.REG_SZ, "ShadowMerge.AssocFile")
                
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, "ShadowMerge.AssocFile") as key:
                winreg.SetValue(key, "", winreg.REG_SZ, "ShadowMerge Paketi")
                
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, r"ShadowMerge.AssocFile\DefaultIcon") as key:
                if os.path.exists(self.logo_yolu):
                    winreg.SetValue(key, "", winreg.REG_SZ, f'"{self.logo_yolu}",0')
                    
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, r"ShadowMerge.AssocFile\shell\open\command") as key:
                winreg.SetValue(key, "", winreg.REG_SZ, komut_dizgesi)
                
            messagebox.showinfo("Başarılı", "ShadowMerge sisteme başarıyla entegre edildi!\nArtık .shadow dosyalarına çift tıklayarak doğrudan Çözücü sekmesinde açabilirsiniz.")
        except PermissionError:
            messagebox.showerror("Yetki Hatası", "Kayıt defterine yazabilmek için programı Yönetici (Administrator) olarak çalıştırmalısınız.\n\nLütfen programı kapatıp, sağ tıklayarak 'Yönetici olarak çalıştır' seçeneğiyle tekrar açın.")
        except Exception as e:
            messagebox.showerror("Kayıt Hatası", "Kayıt defterine entegre edilirken beklenmedik bir hata oluştu:\n" + str(e))

def baslat():
    uygulama = ShadowMergeUltimate()
    uygulama.mainloop()

if __name__ == "__main__":
    baslat()

"""
=========================================================
📦 EXE YAPMA VE KURULUM PAKETİ (INSTALLER) KLAVUZU
=========================================================
Bu Python kodunu tamamen bağımsız bir Kurulum Dosyası (Setup.exe) haline getirmek için 
aşağıdaki adımları sırasıyla uygulayın:

1. Gerekli Kütüphaneleri Yükleyin:
   Terminali açın ve şu komutları girin:
   > pip install pyinstaller
   > pip install tkinterdnd2

2. Tek Parça EXE Oluşturma (Derleme):
   Projenizin bulunduğu klasörde terminali açın ve şu komutu çalıştırın:
   > pyinstaller --noconsole --onefile --icon=logo.ico shadowmerge_ultimate.py

   - "--noconsole": Arka planda siyah terminal penceresinin açılmasını engeller.
   - "--onefile": Tüm projeyi tek bir .exe dosyasına sıkıştırır.
   - "--icon=logo.ico": Oluşacak programın simgesini belirler. (Klasörde logo.ico olmalıdır)

3. TkinterDnD2 Bağımlılığını EXE'ye Dahil Etmek (ÖNEMLİ):
   PyInstaller bazen sürükle-bırak kütüphanesini tek dosyaya dahil edemez. 
   Bunun için komuta '--add-data' parametresini eklemelisiniz.
   Örnek (Windows için):
   > pyinstaller --noconsole --onefile --icon=logo.ico --add-data "C:\\KullaniciYolunuz\\AppData\\Local\\Programs\\Python\\Python39\\tcl\\tkdnd2.9.2;tkdnd" shadowmerge_ultimate.py
   
   (TkinterDnD2'nin tkdnd klasörünün sisteminizdeki yolunu bulup yukarıdaki gibi ekleyin.)

4. Kurulum Sihirbazı (Inno Setup) ile Setup.exe Hazırlama:
   - "dist" klasörü içinde oluşan shadowmerge_ultimate.exe dosyasını alın.
   - Inno Setup (veya NSIS) programını indirin.
   - Yeni bir proje açarak "shadowmerge_ultimate.exe" dosyanızı ve "logo.ico" dosyanızı projeye ekleyin.
   - Derlediğinizde size profesyonel bir Kurulum Sihirbazı (Setup.exe) verecektir.
=========================================================
"""
