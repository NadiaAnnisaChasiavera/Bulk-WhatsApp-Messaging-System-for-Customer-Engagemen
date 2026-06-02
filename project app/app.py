from flask import Flask, render_template, request, redirect
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os

app = Flask(__name__)

# Fungsi untuk memulai Selenium (hanya sekali)
def start_browser():
    options = webdriver.ChromeOptions()
    options.add_argument("--user-data-dir=")  # Sesuaikan path profil Chrome
    driver = webdriver.Chrome(options=options)
    return driver

# Fungsi untuk mengirim pesan ke satu nomor
def kirim_pesan_satu(driver, nama, no_hp, pesan):
    try:
        # Format pesan
        formatted_message = pesan.replace("[Nama]", nama).replace("\n", "%0A").replace(" ", "%20")
        url = f"https://web.whatsapp.com/send?phone={no_hp}&text={formatted_message}"
        driver.get(url)

        time.sleep(10)  # Tunggu hingga halaman WhatsApp Web selesai dimuat
        send_button = driver.find_element(By.XPATH, '//span[@data-icon="send"]')
        send_button.click()
        print(f"Pesan berhasil dikirim ke {nama}")
        time.sleep(5)  # Tunggu pengiriman
    except Exception as e:
        print(f"Error mengirim pesan ke {nama}: {e}")

# Halaman utama untuk form upload dan input pesan
@app.route('/')
def index():
    return render_template('index.html')

# Endpoint untuk upload file CSV
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file and file.filename.endswith('.csv'):
        file.save('customers.csv')  # Simpan file dengan nama 'customers.csv'
        return redirect('/')
    return "File harus berupa CSV", 400

# Endpoint untuk mengirim pesan
@app.route('/send', methods=['POST'])
def send():
    message = request.form['message']  # Pesan yang diinput pengguna
    if not os.path.exists('customers.csv'):
        return "File CSV belum diupload", 400

    # Baca data dari file CSV
    with open('customers.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Lewati header

        # Mulai satu sesi browser Selenium
        driver = start_browser()
        try:
            for row in reader:
                nama, no_hp = row
                kirim_pesan_satu(driver, nama, no_hp, message)
        finally:
            driver.quit()  # Tutup browser setelah semua pesan terkirim

    return render_template('send.html', message=message)

if __name__ == '__main__':
    app.run(debug=True)
