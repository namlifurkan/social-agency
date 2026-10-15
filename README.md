# Social Agency

Claude ile carousel, story reel ve film reel üreten sosyal medya masası. Müşteriler `clients/`
altında: şimdilik `okul` (okul.com.tr) ve `okulup` (OkulUp).

## Bir kerelik kurulum (Windows)

1. **Araçları kur.** Başlat menüsünden *Terminal*'i (PowerShell) aç, satırları tek tek çalıştır:
   ```powershell
   winget install Git.Git
   winget install Python.Python.3.12
   winget install Gyan.FFmpeg
   winget install yt-dlp.yt-dlp
   winget install ImageMagick.ImageMagick
   winget install Google.Chrome
   ```
   Bitince Terminal'i kapatıp yeniden aç.
2. **Repoyu indir.** Claude uygulaması repo indiremiyor. [GitHub Desktop](https://desktop.github.com)
   ile *File → Clone repository* → `namlifurkan/social-agency` seç ya da Terminal'de:
   ```powershell
   git clone https://github.com/namlifurkan/social-agency.git
   ```
3. **Claude desktop uygulamasını aç** → üstte **Code** sekmesi → Environment: **Local** →
   **Select folder** → indirdiğin `social-agency` klasörünü seç.
4. **Kurulum görüşmesini başlat:** `/client-setup okul` ya da `/client-setup okulup` yaz.

   Claude şunları sorar: ElevenLabs API anahtarın, hangi hesaplara paylaşım yapılacağı, reel'in
   nasıl biteceği ("LINK IN BIO" mı, başka bir şey mi) ve seslendirici sesin. Sesi birlikte
   tasarlarsınız, örnekleri dinleyip seçersin.

   API anahtarını sohbete yapıştırma: Claude sana uygulamanın içindeki **Terminal**'i
   (`` Ctrl+` ``) açtırıp anahtarı oradan eklemeni söyler.

Mac'te aynı adımlar, sadece 1. adım `brew install git python ffmpeg yt-dlp imagemagick` olur.

## Her gün

Ne istediğini düz cümleyle yaz:

- "okul için bursluluk sınavları hakkında bir carousel yap"
- "okulup için yemek menüsü özelliğini anlatan bir reel yap"
- "okulup için şu konuda 3 post fikri ver"

Hiçbir şey kendiliğinden paylaşılmaz; dosyalar önce sana gelir.

## Desktop uygulamasında işine yarayacaklar

- **Dosya ekle:** Logo, fotoğraf, ses kaydı ya da örnek bir post görselini sohbet kutusuna sürükle
  ("bu görseldeki gibi bir carousel yap").
- **Sonucu gör:** Sohbetteki görsel ya da video yoluna tıkla, uygulamanın içinde açılır. Sağ
  tıkla dosyanın klasörünü açabilirsin.
- **`/` yaz:** Kullanabileceğin komutlar listelenir: `/client-setup`, `/social-studio`,
  `/story-reel`, `/film-reel`.
- **Mod seçimi:** Prompt kutusunun altından. **Manual** her adımda onay ister; **Accept edits**
  dosya değişikliklerini sormadan yapar, uzun reel işlerinde daha rahattır.
- **Aynı anda birden fazla iş:** Sol kenar çubuğundan yeni bir oturum aç; biri reel yaparken
  diğeri carousel yapabilir.

## Yeni müşteri

`/client-setup <müşteri-adı>` yaz. Logo, renkler, fontlar, ton ve ses aynı görüşmede ayarlanır.
Sitesinin linkini verirsen logo, renk ve fontları oradan çıkarmaya çalışır.

## Vault

`vault/` ekibin ortak hafızası: alınan kararlar, öğrenilen dersler, çözülen sorunlar. Claude
kendisi not yazar; istersen klasörü [Obsidian](https://obsidian.md) ile açıp okuyabilirsin.
