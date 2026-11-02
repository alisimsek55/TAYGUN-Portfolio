# TAYGUN | Proje portföyü

Üniversitede ekip olarak yürüttüğümüz TAYGUN projesinde İHA uçuş simülasyonu ve yazılım entegrasyonu tarafında çalışıyorum. Bu depo, projedeki sorumluluğumu ve telemetri inceleme yaklaşımını paylaşmak için hazırlandı.

## Projedeki görevim

- PX4, Gazebo ve QGroundControl ile simülasyon ve telemetri entegrasyonu.
- Sanal kamera görüntülerinden hedef takibi yapan algoritmanın geliştirilmesi ve simülasyonda çalışmasının doğrulanması.
- Kalkış, eve dönüş ve belirlenen noktaya iniş senaryolarının simülasyon ortamında test edilmesi.

TAYGUN bir ekip projesi. Uçak tasarımı ve özel algılama modeli ekipte ayrı çalışmalar olarak ilerliyor. Burada anlatılan sonuçlar simülasyon kapsamındadır.

## Bu depodaki örnek

`telemetry_summary.py`, JSON Lines biçimindeki bir kayıttan süre, irtifa, yer hızı ve mod sürelerini çıkarır. TAYGUN'daki günlük inceleme ihtiyacını göstermek için portföye özel, bağımsız bir örnek olarak hazırlandı; ana projenin kaynak kodu buraya kopyalanmadı.

Örnek veri tamamen **sentetiktir**. Gerçek uçuş kaydı, gerçek konum veya TAYGUN performans ölçümü değildir. Araç dosya okur; donanım bağlantısı ve uçuş komutu içermez.

## Çalıştırma

Python 3.10 veya üzeri yeterlidir. Ek paket gerekmez.

```bash
python telemetry_summary.py examples/synthetic_telemetry.jsonl
python telemetry_summary.py examples/synthetic_telemetry.jsonl --out summary.json
python -m unittest discover -s tests -v
```

İlk komut ekrana JSON yazar. İkinci komut aynı sonucu dosyaya kaydeder.

Örnek kayıtta beklenen temel sonuçlar: **6 örnek**, **10 saniye kayıt süresi**, **25 metre en yüksek bağıl irtifa**. Tam çıktı [examples/expected_summary.json](examples/expected_summary.json) içindedir. Bu değerler yalnızca örnek veriye aittir.

## Veri ve hesaplama

Her satır bir JSON nesnesidir:

```json
{"t_s": 0, "altitude_m": 0, "groundspeed_m_s": 0, "mode": "GROUND"}
```

- `t_s`: saniye cinsinden kayıt zamanı; artan sırada olmalıdır.
- `altitude_m`: metre cinsinden bağıl irtifa.
- `groundspeed_m_s`: metre/saniye cinsinden, negatif olmayan yer hızı.
- `mode`: kayıtta kullanılan mod etiketi.

Süre, son zaman ile ilk zamanın farkıdır. Bir örneğin modu bir sonraki örneğe kadar geçerli kabul edilir; son örneğin ek süresi yoktur. Ortalama hız, örneklerin aritmetik ortalamasıdır. Uzun kayıt aralıkları için en büyük zaman aralığı da raporlanır. Araç eksik alanları, bozuk JSON'u, sonlu olmayan sayıları ve sırasız zamanları açıklayıcı hatalarla reddeder.

## Dosyalar

| Dosya | İçerik |
| --- | --- |
| `telemetry_summary.py` | Dosya okuma, doğrulama ve özetleme |
| `tests/test_telemetry_summary.py` | Hesaplama, hatalı girdi ve komut satırı testleri |
| `examples/` | Sentetik kayıt ve beklenen çıktı |
| `.github/workflows/tests.yml` | Otomatik Python testleri |

Ana TAYGUN deposu özel tutuluyor. Bu portföyde ekip içi belgeler, erişim bilgileri, model ağırlıkları ve gerçek uçuş günlükleri bulunmuyor. Örnek aracın testleri, ana projenin veya gerçek uçağın doğrulanması anlamına gelmez.

[Ali Şimşek - GitHub](https://github.com/alisimsek55) · [LinkedIn](https://www.linkedin.com/in/ali-%C5%9Fim%C5%9Fek-701a88294/)
