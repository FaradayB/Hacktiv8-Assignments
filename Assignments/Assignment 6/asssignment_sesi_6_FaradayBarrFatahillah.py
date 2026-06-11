import math
from datetime import datetime

def format_angka(amount):
    return 'Rp {:,}'.format(amount)


def hitung_subtotal(unit, harga_satuan):
    return unit*harga_satuan


def hitung_diskon(subtotal, persen_diskon=0):
    return int(subtotal * persen_diskon/100)

def hitung_total(subtotal, persen_diskon=0):
    return subtotal - hitung_diskon(subtotal,persen_diskon)

def buat_laporan_data(data_penjualan, persentase_diskon=0):
    harga_total = 0
    grand_total = 0
    total_stok = 0
    list_detail = []
    detail_laporan = {}
    diskon = persentase_diskon
    for produk in data_penjualan:
        subtotal = hitung_subtotal(produk["unit"], produk["harga_satuan"])
        diskon = hitung_diskon(subtotal,persentase_diskon)
        harga_total = hitung_total(subtotal,persentase_diskon)

        total_stok += produk["unit"]
        grand_total += harga_total

        list_detail.append({**produk, "persentase_diskon":persentase_diskon, "subtotal":subtotal, "diskon":diskon, "total":harga_total})

    rata2_unit = round(total_stok/len(list_detail), 2)

    detail_laporan.update({
        "detail": list_detail,
        "grand_total": grand_total,
        "rata_unit" : rata2_unit
    })
    
    return detail_laporan

def tambahkan_timestamp(laporan):
    bulan_indo = {"January": "Januari", 
                  "February": "Februari", 
                  "March": "Maret", 
                  "April": "April", 
                  "May": "Mei", 
                  "June": "Juni", 
                  "July": "Juli", 
                  "August": "Agustus", 
                  "September": "September", 
                  "October": "Oktober", 
                  "November": "November", 
                  "December": "Desember"}
   
    now = datetime.now()
    laporan["dibuat_pada"] = (f'{now.day} {bulan_indo[now.strftime('%B')]} {now.year}, {now.strftime('%H:%M:%S')}')

    return laporan

def statistik_penjualan(data_penjualan):
    subtotals = []
    i = 0

    for data in data_penjualan:
        subtotal = hitung_subtotal(data["unit"], data["harga_satuan"])
        subtotals.append(subtotal)
        i+=1
    
    mean = sum(subtotals)/len(subtotals)
    variance = sum((x-mean) ** 2 for x in subtotals)/len(subtotals)
    std_subtotal = math.sqrt(variance)

    return {
        "max_subtotal": max(subtotals),
        "min_subtotal": min(subtotals),
        "std_subtotal": std_subtotal
    }
