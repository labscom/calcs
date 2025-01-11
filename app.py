from flask import Flask, render_template
import json

app = Flask(__name__)

@app.route('/')
def index():
    # Чтение первого JSON файла
    with open('data/limit_re102g_figure_re102-4_army.json', 'r') as file1:
        limit_data = json.load(file1)
    
    # Чтение второго JSON файла
    with open('data/antenna_factor.json', 'r') as file2:
        antenna_data = json.load(file2)
    
    # Частоты для калибровочной таблицы
    calibration_frequencies = [2.1, 12, 29.5, 197, 990, 17500]
    
    # Создание таблицы Calibration Signal Generator Output
    calibration_table = []
    for freq in calibration_frequencies:
        # Найти соответствующее значение Calibration field strength из limit_data
        cal_field_strength = None
        for row in limit_data[1:]:
            row_freq = float(row["Fig. RE102-4"])
            if row_freq >= freq:
                cal_field_strength = float(row[""]) - 6  # Взять Limit и вычесть 6
                break
        
        # Найти соответствующее значение Antenna factor из antenna_data
        antenna_factor = None
        for row in antenna_data[1:]:
            row_freq_range = row["Frequency, MHz"].split("-")
            if float(row_freq_range[0]) <= freq <= float(row_freq_range[1]):
                antenna_factor = float(row["Antenna factor"])
                break
        
        # Если данные найдены, вычисляем остальные значения
        if cal_field_strength is not None and antenna_factor is not None:
            sig_gen_output_dbmv = cal_field_strength - antenna_factor
            sig_gen_output_dbm = -107 + sig_gen_output_dbmv
            calibration_table.append({
                "Frequency, MHz": freq,
                "Calibration field strength, dB(mV/m)": round(cal_field_strength, 2),
                "Antenna factor, dB(1/m)": round(antenna_factor, 2),
                "Signal generator output, dB(mV)": round(sig_gen_output_dbmv, 2),
                "Signal generator output, dBm": round(sig_gen_output_dbm, 2)
            })
    
    # Передача всех данных в шаблон
    return render_template(
        'table.html',
        table1_data=limit_data,
        table2_data=antenna_data,
        calibration_table=calibration_table
    )

if __name__ == '__main__':
    app.run(debug=True)
