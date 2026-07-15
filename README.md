```markdown
# 🚀 ShadowMerge Studio Ultimate

ShadowMerge Studio Ultimate; Windows işletim sistemlerinde dosya boyutu, format ve işletim sistemi filtreleme sınırlarını ortadan kaldıran, **Askeri Düzey Şifreleme** ve **Zlib (Level 9) Sıkıştırma** entegrasyonlu, sürükle-bırak destekli gelişmiş bir adli bilişim karşıtı (anti-forensics) veri gizleme ve paketleme istasyonudur.

Bu yazılım; klasik steganografi veya polyglot yöntemlerinin ötesine geçerek, yerel Windows dosya ilişkisi (File Association) mimarisiyle entegre çalışır.

---

## 🌟 Öne Çıkan Özellikler

*   **📦 Evrensel Depolama (Sınırsız Dosya Desteği):** PNG, MP4, ZIP, EXE, PDF gibi dosya formatı ve adet sınırlamalarını tamamen ortadan kaldırır. İstediğiniz sayıda ve türde dosyayı tek bir pakette birleştirir.
*   **🛡️ Askeri Düzey "Anti-Adli Bilişim" Şifrelemesi:** Dosyalar birleştirilmeden önce C hızında çalışan özel bir Lookup Table (LUT) üzerinden **XOR + Bitwise Left Rotation (3-bit bit kaydırma)** işlemlerine tabi tutulur. Bu sayede `Binwalk`, `Foremost` veya `HxD` gibi analiz araçları dosya imzalarını (Magic Bytes) tamamen çorba olarak görür ve içerik tespit edemez.
*   **🗜️ Zlib Sıkıştırma Katmanı (Küçük Dosya Boyutu):** Eklenen tüm veriler şifreleme öncesinde en yüksek seviyede (`Level 9`) sıkıştırılarak depolanır. Oluşan `.shadow` paketinin diskte minimum yer kaplamasını sağlar.
*   **📋 Seçimli Dosya Kurtarma (Treeview Listesi):** Paket çözüldüğünde içerideki tüm gizli dosyaları orijinal isim, uzantı ve boyutlarıyla listeler. İstediğiniz dosyayı seçip bilgisayarınıza sıfır kayıpla indirebilirsiniz.
*   **🪟 Windows Entegrasyonu & Çift Tıklama Desteği:** Tek tıkla Windows Kayıt Defteri'ne (`Registry`) kendini kaydeder. Tüm `.shadow` dosyalarının simgesini `logo.ico` yapar ve çift tıkladığınızda otomatik olarak programın çözücü ekranında açılmasını sağlar.

---

## ⚙️ Teknik Çalışma Mantığı

Program, verileri eklerken ve çözerken aşağıdaki özel binary akış şemasını (Custom Packaging Structure) kullanır:


```

[ GİZLENMİŞ DOSYA VERİLERİ (Sıkıştırılmış + Şifrelenmiş) ]
👇
[ TOC (İçindekiler Tablosu): Dosya Adları, Boyutları ve Adresleri ]
👇
[ TOC Boyut Bilgisi (8 Byte Big-Endian Unsigned Long Long) ]
👇
[ Sihirli Güvenlik İmzası (8 Byte: SHDWULTM) ]

```

---

## 🛠️ Kurulum ve Gereksinimler

Programın çalışması için bilgisayarınızda **Python 3.10 veya üzeri (Tercihen 3.12 / 3.13)** kurulu olmalıdır.

### 1. Gerekli Kütüphaneleri Yükleyin
Sürükle-bırak motorunun (TkinterDnD2) aktif olması için terminale (CMD) şu komutları girin:
```bash
pip install tkinterdnd2

```

### 2. Programı Çalıştırın

```bash
python shadowmerge_ultimate.py

```

---

## 📦 Bağımsız EXE ve Kurulum Dosyası (Setup.exe) Yapma

Yazılımı Python kurulu olmayan bilgisayarlarda da çalıştırmak ve kurmak için bağımsız bir `.exe` dosyasına dönüştürebilirsiniz.

### 1. Derleme Adımı (PyInstaller)

Terminali açın ve projenin bulunduğu klasörde şu komutu çalıştırın (Klasörde `logo.ico` dosyasının olduğundan emin olun):

```bash
pyinstaller --noconsole --onefile --icon=logo.ico shadowmerge_ultimate.py

```

> **Önemli:** Eğer sürükle-bırak kütüphanesinin paket içine gömülmesinde sorun yaşarsanız komuta `--add-data` parametresini ekleyerek `tkdnd` klasörünüzün yolunu belirtin.

### 2. Kurulum Sihirbazı (Inno Setup)

* `dist` klasöründe oluşan `shadowmerge_ultimate.exe` dosyasını alın.
* **Inno Setup** kullanarak bu `.exe` dosyasını ve `logo.ico` simgenizi içeren profesyonel bir `Setup.exe` kurulum sihirbazı oluşturun.

---

## 🧑‍💻 Kullanım Kılavuzu

### Paket Oluşturma (Creator)

1. `Oluşturucu` sekmesine gelin.
2. İstediğiniz dosyaları büyük sürükle-bırak alanına bırakın.
3. **ShadowMerge Paketi Oluştur** butonuna basarak `.shadow` uzantılı dosyanızı kaydedin.

### Paket Çözme ve İndirme (Extractor)

1. Oluşturduğunuz `.shadow` dosyasını `Çözücü` sekmesine sürükleyin (veya sisteme entegre ettiyseniz dosyaya çift tıklayın).
2. Listelenen gizli dosyalardan kurtarmak istediğinizi seçin.
3. **Seçili Dosyayı Bilgisayara İndir** butonuna basarak istediğiniz yere kaydedin.

```

```