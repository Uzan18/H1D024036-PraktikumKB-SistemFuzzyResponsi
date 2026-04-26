import os
import sys
import importlib.util

# Patch untuk modul 'imp' yang dihapus di Python 3.12+ agar scikit-fuzzy (skfuzzy) bisa berjalan
if 'imp' not in sys.modules:
    import types
    imp = types.ModuleType('imp')
    def find_module(name, path=None):
        spec = importlib.util.find_spec(name)
        if spec is None:
            raise ImportError(f"No module named {name}")
        return None, spec.origin, None
    imp.find_module = find_module
    sys.modules['imp'] = imp

from flask import Flask, render_template, request, jsonify
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# Inisialisasi Flask app. Vercel membutuhkan ini di dalam api/index.py
# Atur template_folder ke path relatif '../templates' karena index.py ada di dalam folder 'api'
app = Flask(__name__, template_folder='../templates', static_folder='../static')

# ==========================================
# 1. DEFINISI VARIABEL INPUT DAN OUTPUT
# ==========================================
# Menggunakan numpy arange untuk membuat rentang semesta pembicaraan (universe of discourse)
tekanan_darah = ctrl.Antecedent(np.arange(0, 201, 1), 'tekanan_darah') # 0 - 200 mmHg
kolesterol = ctrl.Antecedent(np.arange(0, 301, 1), 'kolesterol')       # 0 - 300 mg/dL
usia = ctrl.Antecedent(np.arange(0, 101, 1), 'usia')                   # 0 - 100 Tahun
risiko = ctrl.Consequent(np.arange(0, 101, 1), 'risiko')               # 0 - 100 Persen

# ==========================================
# 2. MEMBERSHIP FUNCTIONS (FUNGSI KEANGGOTAAN)
# ==========================================
# Menggunakan fungsi trapesium (trapmf) untuk mendapatkan presisi yang lebih baik pada himpunan batas

# Variabel Tekanan Darah (mmHg)
# Rendah (0-100), Normal (90-130), Tinggi (120-160), Sangat Tinggi (>150)
tekanan_darah['rendah'] = fuzz.trapmf(tekanan_darah.universe, [0, 0, 90, 100])
tekanan_darah['normal'] = fuzz.trapmf(tekanan_darah.universe, [90, 100, 120, 130])
tekanan_darah['tinggi'] = fuzz.trapmf(tekanan_darah.universe, [120, 130, 150, 160])
tekanan_darah['sangat_tinggi'] = fuzz.trapmf(tekanan_darah.universe, [150, 160, 200, 200])

# Variabel Kadar Kolesterol (mg/dL)
# Normal (0-200), Cukup Tinggi (190-240), Tinggi (>230)
kolesterol['normal'] = fuzz.trapmf(kolesterol.universe, [0, 0, 190, 200])
kolesterol['cukup_tinggi'] = fuzz.trapmf(kolesterol.universe, [190, 200, 230, 240])
kolesterol['tinggi'] = fuzz.trapmf(kolesterol.universe, [230, 240, 300, 300])

# Variabel Usia (Tahun)
# Muda (0-35), Paruh Baya (30-55), Tua (>50)
usia['muda'] = fuzz.trapmf(usia.universe, [0, 0, 30, 35])
usia['paruh_baya'] = fuzz.trapmf(usia.universe, [30, 35, 50, 55])
usia['tua'] = fuzz.trapmf(usia.universe, [50, 55, 100, 100])

# Variabel Output: Tingkat Risiko Penyakit Jantung
# Rendah (0-40), Sedang (30-70), Tinggi (60-100)
risiko['rendah'] = fuzz.trapmf(risiko.universe, [0, 0, 30, 40])
risiko['sedang'] = fuzz.trapmf(risiko.universe, [30, 40, 60, 70])
risiko['tinggi'] = fuzz.trapmf(risiko.universe, [60, 70, 100, 100])

# Set metode defuzzifikasi ke Centroid (metode default Mamdani yang paling umum dan akurat)
risiko.defuzzify_method = 'centroid'

# ==========================================
# 3. BASIS ATURAN (RULE BASE) INFERENSI
# ==========================================
# Minimum 15 aturan sesuai spesifikasi yang menghubungkan variabel input dengan tingkat risiko
rule1 = ctrl.Rule(tekanan_darah['rendah'] & kolesterol['normal'] & usia['muda'], risiko['rendah'])
rule2 = ctrl.Rule(tekanan_darah['normal'] & kolesterol['normal'] & usia['muda'], risiko['rendah'])
rule3 = ctrl.Rule(tekanan_darah['normal'] & kolesterol['normal'] & usia['paruh_baya'], risiko['rendah'])
rule4 = ctrl.Rule(tekanan_darah['normal'] & kolesterol['cukup_tinggi'] & usia['muda'], risiko['sedang'])
rule5 = ctrl.Rule(tekanan_darah['tinggi'] & kolesterol['normal'] & usia['muda'], risiko['sedang'])

rule6 = ctrl.Rule(tekanan_darah['tinggi'] & kolesterol['cukup_tinggi'] & usia['paruh_baya'], risiko['tinggi'])
rule7 = ctrl.Rule(tekanan_darah['sangat_tinggi'] & kolesterol['tinggi'] & usia['tua'], risiko['tinggi'])
rule8 = ctrl.Rule(tekanan_darah['rendah'] & kolesterol['tinggi'] & usia['tua'], risiko['sedang'])
rule9 = ctrl.Rule(tekanan_darah['normal'] & kolesterol['tinggi'] & usia['paruh_baya'], risiko['sedang'])
rule10 = ctrl.Rule(tekanan_darah['tinggi'] & kolesterol['tinggi'] & usia['muda'], risiko['tinggi'])

rule11 = ctrl.Rule(tekanan_darah['sangat_tinggi'] & kolesterol['normal'] & usia['paruh_baya'], risiko['tinggi'])
rule12 = ctrl.Rule(tekanan_darah['sangat_tinggi'] & kolesterol['cukup_tinggi'] & usia['tua'], risiko['tinggi'])
rule13 = ctrl.Rule(tekanan_darah['rendah'] & kolesterol['cukup_tinggi'] & usia['paruh_baya'], risiko['rendah'])
rule14 = ctrl.Rule(tekanan_darah['tinggi'] & kolesterol['normal'] & usia['tua'], risiko['sedang'])
rule15 = ctrl.Rule(tekanan_darah['normal'] & kolesterol['tinggi'] & usia['tua'], risiko['tinggi'])

rule16 = ctrl.Rule(tekanan_darah['tinggi'] & kolesterol['tinggi'] & usia['tua'], risiko['tinggi'])
rule17 = ctrl.Rule(tekanan_darah['sangat_tinggi'] & kolesterol['tinggi'] & usia['muda'], risiko['tinggi'])
# Tambahan rule untuk menutupi default value di UI (normal, cukup_tinggi, paruh_baya)
rule18 = ctrl.Rule(tekanan_darah['normal'] & kolesterol['cukup_tinggi'] & usia['paruh_baya'], risiko['sedang'])

# ==========================================
# 4. CONTROL SYSTEM & SIMULATION
# ==========================================
# Inisialisasi control system dengan semua aturan yang ada
risiko_ctrl = ctrl.ControlSystem([
    rule1, rule2, rule3, rule4, rule5, 
    rule6, rule7, rule8, rule9, rule10, 
    rule11, rule12, rule13, rule14, rule15,
    rule16, rule17, rule18
])

# ==========================================
# 5. FLASK ROUTES
# ==========================================
@app.route('/')
def index():
    # Menampilkan UI frontend
    return render_template('index.html')

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        # Ambil data dari JSON request frontend
        data = request.get_json()
        
        try:
            td_val = float(data.get('tekanan_darah', 0))
            kol_val = float(data.get('kolesterol', 0))
            usia_val = float(data.get('usia', 0))
        except (ValueError, TypeError):
            return jsonify({'error': 'Data input tidak valid. Pastikan semua field berupa angka.'}), 400

        # Error Handling: Pastikan input tidak diluar range ekstrim semesta pembicaraan
        if not (0 <= td_val <= 200):
            return jsonify({'error': 'Tekanan darah harus antara 0 - 200 mmHg'}), 400
        if not (0 <= kol_val <= 300):
            return jsonify({'error': 'Kadar kolesterol harus antara 0 - 300 mg/dL'}), 400
        if not (0 <= usia_val <= 120):
            return jsonify({'error': 'Usia harus antara 0 - 120 tahun'}), 400

        # Inisialisasi ulang simulasi untuk state isolasi per request
        risiko_sim = ctrl.ControlSystemSimulation(risiko_ctrl)

        # Memasukkan nilai input dari pengguna
        risiko_sim.input['tekanan_darah'] = td_val
        risiko_sim.input['kolesterol'] = kol_val
        risiko_sim.input['usia'] = usia_val

        try:
            # Menjalankan proses perhitungan fuzzy mamdani
            risiko_sim.compute()
            score = float(risiko_sim.output['risiko'])
        except ValueError as e:
            # Jika skfuzzy melempar ValueError (biasanya karena tidak ada rule yang terpicu)
            if "crisp value cannot be calculated" in str(e).lower():
                return jsonify({'error': 'Kombinasi parameter ini tidak memiliki kecocokan pada basis aturan (Rule Base). Sistem tidak dapat menyimpulkan risiko.'}), 400
            else:
                raise e
        
        # Interpretasi Skor berdasarkan range himpunan (Rendah: 0-40, Sedang: 30-70, Tinggi: 60-100)
        # Menentukan kategori dominan
        if score < 40:
            kategori = "Rendah"
            color_class = "text-green-600"
            bg_class = "bg-green-100"
        elif score < 65: # Threshold overlap penengah
            kategori = "Sedang"
            color_class = "text-yellow-600"
            bg_class = "bg-yellow-100"
        else:
            kategori = "Tinggi"
            color_class = "text-red-600"
            bg_class = "bg-red-100"

        return jsonify({
            'score': round(score, 2),
            'kategori': kategori,
            'color': color_class,
            'bg': bg_class
        })

    except Exception as e:
        return jsonify({'error': f'Terjadi kesalahan internal: {str(e)}'}), 500

if __name__ == '__main__':
    # Mode debug saat pengembangan lokal, diubah ke port 5005 agar tidak bentrok
    app.run(debug=True, port=5005)
