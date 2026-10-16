# Ramazandan.com — Haber Portalı + CMS

Türkçe haber portalı: public site, yönetim paneli (CMS), medya sistemi, SEO altyapısı,
reklam yönetimi ve arama. Tek sunucuda, dış servis bağımlılığı olmadan çalışır.

## Teknoloji

| Katman | Seçim | Neden |
|---|---|---|
| Framework | Next.js 16 (App Router) + TypeScript strict | RSC ile minimum istemci JS, ISR, yerleşik metadata/SEO API'si |
| Veritabanı | SQLite (WAL) + FTS5 | Haber sitesi okuma ağırlıklı; sıfır işletme maliyeti, ek servis yok |
| ORM | Drizzle ORM + better-sqlite3 | Saf TypeScript; Prisma'nın engine binary'si paylaşımlı hostingde sorun çıkarıyor |
| Arama | SQLite FTS5 + Türkçe karakter katlama | Ek arama servisi (Elastic/Meili) gerekmez |
| Görsel | sharp (upload anında WebP/AVIF varyant) | Runtime image optimizer kapalı → paylaşımlı hostingde CPU/RAM korunur |
| Oturum | DB tabanlı session + httpOnly çerez + bcryptjs | Harici auth paketi yok, tam kontrol, native derleme riski yok |
| Editör | TipTap → HTML, sunucuda `sanitize-html` | XSS'e karşı tek merkezi savunma hattı |
| Stil | Tailwind CSS v4 + CSS değişkenli tasarım token'ları | Tek kaynak tema |

## Hızlı başlangıç

```bash
npm install
cp .env.example .env     # SESSION_SECRET ve CRON_TOKEN değerlerini doldurun
npm run db:migrate
npm run db:seed          # örnek içerik (yalnızca geliştirme)
npm run dev              # http://localhost:3100
```

Seed **yalnızca geliştirme içindir** ve üretim ortamında çalışmayı reddeder.

### Demo modundan çıkış (canlıya alma)

```bash
npm run go-live
```

Bu komut örnek haber/galeri/etiket/görselleri ve demo giriş hesaplarını siler
(kategoriler, kurumsal sayfalar, menüler ve ayarlar korunur), ardından ekip
hesaplarını oluşturup şifreleri **bir kez** ekrana yazar. Ünvan, biyografi ve
profil fotoğrafı bilerek boş bırakılır; her kullanıcı bunları panelde
**Profilim** ekranından doldurur.

Hesap güvenliği: şifreler `crypto.randomBytes` ile üretilir ve yalnızca bcrypt
(cost 12) özeti saklanır; 5 hatalı denemede hesap 15 dk kilitlenir; IP bazlı
rate limit vardır; şifre değişiminde diğer tüm oturumlar kapatılır.

## Komutlar

| Komut | Açıklama |
|---|---|
| `npm run dev` | Geliştirme sunucusu (3100) |
| `npm run build` / `npm start` | Üretim derlemesi / sunucu |
| `npm run typecheck` | TypeScript kontrolü |
| `npm run lint` | ESLint |
| `npm test` | Birim testleri (vitest) |
| `npm run smoke` | Ayakta olan sunucuya uçtan uca HTTP testi (`SMOKE_EMAIL`/`SMOKE_PASSWORD` ister) |
| `npm run db:generate` | Şema değişikliğinden SQL migration üretir |
| `npm run db:migrate` | Migration'ları uygular + FTS tablosunu kurar |
| `npm run db:seed` | Örnek içerik yükler (mevcut içeriği siler) |
| `npm run db:reset` | Veritabanı + yüklenen görselleri sıfırlar (dev) |
| `npm run brand:assets` | Logo/favicon/OG görsellerini yeniden üretir |
| `npm run go-live` | Demo içeriği siler, ekip hesaplarını oluşturur (canlıya alma) |
| `npm run cleanup` | Oturum/denetim temizliği, yedek, VACUUM (cron) |

## Mimari

```
src/
  app/
    (site)/          public site: ana sayfa, /[kategori], /[kategori]/[slug], arama,
                     galeri, video, yazar, etiket, kurumsal sayfalar
    admin/giris      yönetim girişi (kabuk dışında)
    admin/(panel)/   yönetim paneli: dashboard, haberler, kategoriler, etiketler,
                     yazarlar, medya, galeriler, sayfalar, menüler, reklamlar,
                     yönlendirmeler, kullanıcılar, ayarlar
    api/             auth, admin CRUD, upload, view sayacı, cron
    sitemap*.xml, rss.xml, robots.ts
  components/        news / layout / ui / ads / admin
  lib/
    db/              schema, bağlantı, FTS arama
    auth/            session, password, rbac, csrf, rate-limit
    queries/         okuma sorguları (public)
    services/        yazma iş mantığı (slug, etiket, indeks, yönlendirme)
    media/           sharp pipeline + storage adapter
    seo/             metadata, JSON-LD, sitemap/RSS üretimi
    validation/      Zod şemaları (istemci + sunucu ortak)
  proxy.ts           yönlendirmeler, 404 doğruluğu, admin koruması, CSRF çerezi
                     (Next 16 "proxy" sözleşmesi — eski adıyla middleware)
```

## Otomatik veri kaynakları (API anahtarı gerekmez)

| Veri | Kaynak | Yenileme | Not |
|---|---|---|---|
| Dolar / Euro / Sterlin | TCMB günlük kur bülteni (`today.xml`) | 15 dk | Resmî kaynak; TCMB gün içi değişim oranı yayımlamaz |
| Ons altın, gram altın, çeyrek altın | Binance `PAXGUSDT` + TCMB dolar kuru | 15 dk | Gram = ons × USD/TRY ÷ 31,1035 · çeyrek = gram × 1,6 |
| Gram gümüş | CoinGecko (`kinesis-silver`) | 15 dk | Ons gümüş üzerinden hesaplanır |
| Bitcoin / Ethereum | Binance `BTCTRY`, `ETHTRY` (yedek: CoinGecko) | 15 dk | 24 saatlik değişim oranıyla |
| Hava durumu (81 il) | Open-Meteo | 30 dk | Anlık sıcaklık, hissedilen, nem, rüzgâr + 5 günlük tahmin |

Dayanıklılık: sağlayıcılar birbirinden bağımsız çağrılır ve her kalem için **son başarılı
değer** bellekte tutulur. Bir kaynak geçici olarak yanıt vermezse (ör. CoinGecko 429) o
kalem kaybolmaz; "son bilinen değer" etiketiyle gösterilir. Hiçbir kaynak yanıt vermezse
ilgili şerit/bölüm hiç render edilmez — sayfada asla uydurma veya boş değer görünmez.

İlgili sayfalar: `/piyasalar` (tüm kurlar), `/hava-durumu` (81 il), `/hava-durumu/[il]`
(şehir detayı + 5 günlük tahmin). Şerit üzerindeki hava durumu rozetinden şehir seçilebilir;
tercih tarayıcıda saklanır. Varsayılan şehir ve modüllerin açık/kapalı durumu yönetim
panelindeki **Ayarlar** ekranından yönetilir.

## Yönetim paneli ekranları

Gösterge paneli · Haberler (+ önizleme) · Kategoriler · Etiketler · Yazarlar ·
Medya · Galeriler · Sayfalar · Menüler · Reklamlar · Yönlendirmeler ·
Kullanıcılar · Denetim kayıtları · Ayarlar · **Profilim**

- **Profilim:** her kullanıcı kendi adını, şifresini ve yazar profilini (ünvan,
  biyografi, profil fotoğrafı, sosyal hesaplar) düzenler. Şifre değişimi mevcut
  şifreyi ister ve diğer cihazlardaki oturumları kapatır.
- **Yazarlar:** yazar profili bir panel hesabına bağlanabilir (`Panel hesabı`
  alanı); bağlandığında o kullanıcı kendi profilini Profilim'den yönetir.
- **Denetim kayıtları:** panelde yapılan her yazma işlemi (kim, ne zaman, hangi
  kayıt, hangi IP) 90 gün boyunca tutulur ve buradan okunur.

### Önemli kararlar

- **URL yapısı:** kanonik adres `/{kategori}/{haber-slug}`. `/haber/{slug}` kalıcı olarak
  kanonik adrese yönlenir. Slug veya kategori değişince eski adres `redirects` tablosuna
  yazılır ve proxy 301 verir — paylaşılan bağlantılar kırılmaz.
- **404 doğruluğu:** Next 16'da `(site)` düzeni altındaki `notFound()` gövdeyi doğru basıyor
  ancak HTTP 200 dönüyor (soft 404). Proxy (middleware), var olmayan içerik adreslerini kök
  seviyedeki `/icerik-bulunamadi` sayfasına rewrite eder; orada gerçek **404** üretilir.
- **Zamanlanmış yayın:** public sorgular `status='PUBLISHED' AND published_at <= now`
  filtresini kullanır. Cron kurulmasa bile saati gelen haber görünür; cron yalnızca
  kaydın durumunu günceller ve önbelleği tazeler.
- **Tailwind kaynak listesi:** bu ortamda Tailwind'in özyinelemeli dosya taraması
  çalışmadığı için `scripts/gen-tw-sources.mjs` her `dev`/`build` öncesi
  `src/styles/_sources.css` dosyasını üretir. Yeni klasör eklendiğinde otomatik yakalanır.
- **Reklamlar:** `AdSlot` alanı rezerve yükseklikle render eder → CLS 0. Reklam yoksa alan
  hiç basılmaz (yarım boşluk oluşmaz).

## Güvenlik

- Admin rotaları middleware + sunucu tarafı oturum kontrolü ile korunur; her yazma
  isteğinde ayrıca rol (RBAC) doğrulanır.
- CSRF: double-submit token (çerez + `x-csrf-token` başlığı), `SameSite=Lax`.
- Brute force: IP bazlı rate limit + hesap kilidi (5 hata → 15 dk).
- Upload: magic-byte doğrulaması (uzantıya güvenilmez), MIME beyaz listesi, 10MB sınırı,
  sharp ile yeniden kodlama (EXIF ve gömülü içerik temizlenir), rastgele dosya adı.
- Editör HTML'i her kayıtta ve her render'da `sanitize-html` ile temizlenir; iframe yalnızca
  YouTube/Vimeo/Dailymotion host'larından kabul edilir.
- Güvenlik başlıkları (CSP, HSTS, X-Content-Type-Options, Referrer-Policy) `next.config.ts` içinde.
- Şifreler bcrypt (cost 12); şifre/rol değişiminde kullanıcının tüm oturumları kapatılır.

## SEO

- Her sayfada `generateMetadata`: title, description, canonical, OpenGraph, Twitter Card.
- JSON-LD: `NewsArticle`, `BreadcrumbList`, `ImageGallery`, `VideoObject`,
  `NewsMediaOrganization`, `WebSite` + SearchAction, `CollectionPage`, `Person`.
- `sitemap.xml` (index) → `sitemap-genel.xml`, `sitemap-haberler/N.xml` (2.000'lik parçalar),
  **`sitemap-news.xml`** (son 48 saat, Google News).
- `rss.xml` ve kategori bazlı `/{kategori}/rss.xml`.
- `robots.txt`: `/admin`, `/api`, `/arama` kapalı; sitemap referansları var.

## cPanel'e dağıtım

```bash
bash scripts/deploy-cpanel.sh      # deploy/ klasörünü üretir
```

Sonra `deploy/KURULUM.txt` adımlarını izleyin. Özet:

1. `deploy/` içeriğini uygulama dizinine yükleyin (örn. `~/ramazandan`).
2. cPanel → **Setup Node.js App**: Node 20+, startup file `app.js`.
3. `.env` dosyasını oluşturun (`SESSION_SECRET`, `CRON_TOKEN` mutlaka değiştirilmeli).
4. `npm install --omit=dev` → `npx tsx --env-file=.env scripts/migrate.ts`
5. Yönetici hesabı: `npx tsx --env-file=.env scripts/create-admin.ts "eposta" "sifre" "Ad Soyad"`
6. Cron: yayın görevi (dakikada bir) ve bakım görevi (haftalık) — `KURULUM.txt` içinde hazır satırlar var.

**Kalıcı veriler:** `data/` (SQLite) ve `storage/uploads/` sunucuda kalır; deploy paketi
bunların üzerine yazmaz. Yedekleme `npm run cleanup` ile `data/backups/` altına alınır.

### Medya neden `public/` altında değil?

Next.js üretim modunda `public/` içeriğini **derleme anında** indeksler; sunucu çalışırken
eklenen dosyalar statik olarak sunulmaz (404). Bu yüzden yüklenen görseller
`storage/uploads/` altında tutulur ve `/uploads/[...path]` route handler'ı tarafından
1 yıllık `immutable` önbellek + ETag ile servis edilir.

**İsteğe bağlı hızlandırma (Apache/LiteSpeed önde ise):** `/uploads` isteklerini Node'a hiç
uğratmadan doğrudan diskten sunmak için uygulama kökündeki `.htaccess` dosyasına ekleyin:

```apache
RewriteEngine On
RewriteCond %{REQUEST_URI} ^/uploads/
RewriteRule ^uploads/(.*)$ storage/uploads/$1 [L]

# ZORUNLU: veritabani, ortam dosyasi ve kaynak klasorleri web'den erisilemez olmali
RedirectMatch 404 ^/(data|drizzle|scripts|src)(/|$)
<FilesMatch "^\.env">
  Require all denied
</FilesMatch>
```

> Uygulama dizini web kökünden erişilebiliyorsa bu kurallar **şart**: aksi halde
> `data/ramazandan.db` (şifre hash'leri, oturum kayıtları) ve `.env` (SESSION_SECRET,
> CRON_TOKEN) doğrudan indirilebilir. Daha güvenlisi: `DATABASE_PATH` değerini web
> kökü dışına alın (ör. `/home/kullanici/private/ramazandan.db`).
