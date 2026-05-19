def telebe_hesabatı(telebeler):
    # XƏTA 1: Boş lüğət (dictionary) yaradılıb, amma aşağıda siyahı (list) kimi istifadə olunur
    neticeler = {} 
    
    for ad, qiymetler in telebeler.items():
        # XƏTA 2: Qiymətlərin cəmini tapmaq üçün 'sum' funksiyası əvəzinə səhv dəyişən yazılıb
        # Və sətir (string) tipli məlumat toplamağa çalışır
        cem = sum(qiymetler)
        
        # XƏTA 3: Sıfıra bölünmə (ZeroDivisionError) təhlükəsi var, əgər tələbənin qiyməti yoxdursa
        ortalama = cem / len(qiymetler)
        
        if ortalama >= 51:
            durum = "Keçdi"
        else:
            durum = "Kəsildi"
            
        # XƏTA 1-in davamı: .append() metodu lüğətlərdə (dict) yox, siyahılarda (list) olur
        neticeler.append({"ad": ad, "ortalama": ortalama, "neticem": durum})
        
    return neticeler

# Test məlumatları
sinif_melumati = {
    "Əli": [85, 90, 78],
    "Aytən": [40, 50, 45],
    "Vaqif": [] # Bu boş siyahı XƏTA 3-ü tetikləyəcək
}

# XƏTA 4: Funksiyanın adı yuxarıda 'telebe_hesabatı'dır, amma burada səhv çağırılıb
hesabat = telebe_hesabati(sinif_melumati)

# XƏTA 5: Dövrün daxilində 'print' edərkən indeksləmə səhvi var
for telebe in hesabat:
    print(f"{telebe['ad']} - Ortalama: {telebe['ortlama']} - Status: {telebe['neticem']}")
