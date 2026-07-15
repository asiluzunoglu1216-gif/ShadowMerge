<div align="center">

# 🕵️‍♂️ SHADOWMERGE STUDIO ULTIMATE

**« Askeri Düzey Şifreleme • Maksimum Sıkıştırma • Evrensel Veri Gizleme »**

[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078d7.svg?style=for-the-badge&logo=windows&logoColor=white)]()
[![License](https://img.shields.io/badge/Lisans-MIT-success.svg?style=for-the-badge)]()
[![Security](https://img.shields.io/badge/Security-XOR%20%2B%20ROTL-red.svg?style=for-the-badge)]()

*Dış kütüphanelere bağımlı olmayan, yerel (offline) ve tamamen ham byte manipülasyonu yapan üst düzey bir Steganografi ve Polyglot Derleyici motoru.*

<img src="https://raw.githubusercontent.com/tandpfun/skill-icons/main/icons/Python-Dark.svg" width="60">

</div>

<br>

> [!IMPORTANT]
> Bu araç, siber güvenlik araştırmaları, adli bilişim (forensics) testleri ve veri gizleme tekniklerinin (steganografi) sınırlarını keşfetmek amacıyla **eğitim odaklı** geliştirilmiştir. 

---

## 📑 İçindekiler
- [✨ Öne Çıkan Özellikler](#-öne-çıkan-özellikler)
- [🧠 Mimari ve Çalışma Mantığı](#-mimari-ve-çalışma-mantığı)
- [🚀 Kurulum ve Başlangıç](#-kurulum-ve-başlangıç)
- [🎮 Kullanım Rehberi](#-kullanım-rehberi)
- [⚙️ Bağımsız EXE (Kurulum) Oluşturma](#️-bağımsız-exe-kurulum-oluşturma)

---

## ✨ Öne Çıkan Özellikler

| Özellik | Açıklama |
| :--- | :--- |
| 🛡️ **Askeri Düzey Anti-Forensics** | Verileriniz XOR ve Bitwise Left Rotation (ROTL) ile şifrelenir. `Binwalk`, `HxD` veya `Foremost` gibi araçlar dosya içeriklerini okuyamaz. |
| 📦 **Sınırsız Evrensel Depo** | Tür (EXE, PDF, JPG, MP4, ZIP) ve boyut sınırı olmadan dilediğiniz sayıda dosyayı tek bir `.shadow` paketinde birleştirin. |
| 🗜️ **Maksimum Zlib Sıkıştırma** | Şifreleme öncesi Zlib `Level 9` ile verileriniz olabilecek en küçük boyuta getirilir. |
| 🖥️ **Kusursuz Arayüz & UX** | Karanlık tema (Dark Mode) destekli, Sürükle-Bırak yetenekli modern Tkinter/TkinterDnD2 arayüzü. |
| 🪟 **Windows Entegrasyonu** | Tek tuşla Windows Kayıt Defterine (Registry) eklenir. `.shadow` dosyaları uygulamanın kendi logosuyla (Tüy/Logo) görünür ve çift tıklama ile açılır. |
| ⚡ **C-Hızında Çözümleme** | Önceden hesaplanmış *Lookup Table (LUT)* ve bağımsız *TOC (İçindekiler)* mimarisi sayesinde GB'larca veriyi anında işler. |

---

## 🧠 Mimari ve Çalışma Mantığı

ShadowMerge Ultimate, verileri analiz araçlarından gizlemek için eşsiz bir **Binary (İkili)** dosya dizilimi kullanır:

<details>
<summary><b>🔍 Mimariyi Detaylı İncele (Tıkla)</b></summary>
<br>

1. **Ön Bellek (LUT) Üretimi:** Program başlar başlamaz 256-byte'lık bir şifreleme ve çözme tablosu oluşturur. Bu, şifreleme işleminin C-dili hızında yapılmasını sağlar.
2. **Sıkıştırma ve Şifreleme:** Eklenen her dosya önce `zlib` ile en yüksek oranda sıkıştırılır, ardından `XOR + ROTL` algoritması ile tamamen tanınmaz (obfuscated) hale getirilir.
3. **Ardışık Yazım ve TOC:** Şifrelenen tüm dosyalar art arda yazılır. En sona ise dosyaların gerçek isimlerini, orijinal boyutlarını ve şifreli boyutlarını barındıran **TOC (Table of Contents)** tablosu eklenir.
4. **SHDWULTM Mührü:** Dosyanın absolute sonuna (EOF) TOC boyutu ve 8 byte'lık sihirli mühür (`SHDWULTM`) yerleştirilir. Çözücü sekmesi dosyayı açarken sadece bu mührü okur ve tüm paket içeriğini RAM'i doldurmadan milisaniyeler içinde listeler.

</details>

---

## 🚀 Kurulum ve Başlangıç

### 🔧 Gereksinimler
- Python 3.8 veya daha üstü bir sürüm
- `tkinterdnd2` kütüphanesi (Sürükle-Bırak özelliği için şarttır)

### 📥 İndirme ve Çalıştırma

Aşağıdaki komutları kullanarak aracı anında çalıştırmaya başlayabilirsiniz:

```bash
# 1. Repoyu klonlayın
git clone https://github.com/asiluzunoglu1216-gif/ShadowMerge.git

# 2. Dizin içerisine girin
cd ShadowMerge

# 3. Gerekli kütüphaneyi kurun
pip install tkinterdnd2

# 4. Programı başlatın
python shadowmerge_ultimate.py
```

---

## 🎮 Kullanım Rehberi

Arayüz oldukça basit ve iki ana sekmeden oluşur:

### 🛠️ 1. Oluşturucu (Creator)
- Gizlemek istediğiniz dosyaları (örneğin birkaç fotoğraf, bir EXE dosyası ve özel belgelerinizi) ortadaki geniş siyah alana sürükleyip bırakın.
- Sağ alt köşedeki **"ShadowMerge Paketi Oluştur"** butonuna tıklayın.
- Arkanıza yaslanın! Sistem tüm dosyalarınızı şifreleyecek, sıkıştıracak ve tek bir `.shadow` dosyasına dönüştürecektir.

### 🔓 2. Çözücü (Extractor)
- Çözmek istediğiniz `.shadow` uzantılı paketi alana sürükleyin.
- İçindeki dosyalar anında orijinal adları ve boyutlarıyla listelenecektir.
- Listeden istediğiniz dosyayı seçip **"Seçili Dosyayı Bilgisayara İndir"** butonuna tıklayarak sıfır kayıpla veriyi geri alabilirsiniz.

> [!TIP]
> **Hızlı Kullanım:** Uygulama içindeki "Sisteme Entegre Et" butonunu kullanarak programı Windows'a tanıtabilirsiniz. Böylece bir daha arayüzü açmanıza gerek kalmaz; `.shadow` dosyasına çift tıkladığınızda program otomatik olarak Çözücü sekmesinde açılır! *(Bu işlem için programı Yönetici Olarak çalıştırmanız gerekebilir).*

---

## ⚙️ Bağımsız EXE (Kurulum) Oluşturma

Programı Python yüklü olmayan bilgisayarlara göndermek veya tam teşekküllü bir **Setup.exe** yapmak istiyorsanız:

1. Önce kod derleyici paketini yükleyin:
   ```bash
   pip install pyinstaller
   ```
2. Terminal üzerinden programı tek parça haline getirin:
   ```bash
   pyinstaller --noconsole --onefile --icon=logo.ico --add-data "C:\PythonYolunuz\tcl\tkdnd2.9.2;tkdnd" shadowmerge_ultimate.py
   ```
   *(Not: `tkdnd` kütüphanesinin bilgisayarınızdaki gerçek konumunu bulup yukarıdaki `C:\...` kısmına yazmayı unutmayın)*
3. Oluşan `dist/shadowmerge_ultimate.exe` dosyasını *Inno Setup* veya *NSIS* gibi araçlarla kolaylıkla bir kurulum sihirbazına (Installer) dönüştürebilirsiniz.

<br>

<div align="center">

**[ 🛡️ ShadowMerge Studio Ultimate - Tamamen Güvenli & Bağımsız ]**

</div>
