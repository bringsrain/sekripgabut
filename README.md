# sekripgabut


> Pengen gitu bikin README pake bahasa yang proper biar kek orang-orang, tapi bikinnya pas lagi gabut juga sih. Beginilah jadinya. 

`sekripgabut` adalah koleksi skrip yang dibuat untuk mengisi waktu gabut. Momen gabut bisa disebabkan oleh beberapa hal:

1. Mentok saat melakukan task.
2. Kesel karena repetitive action kecil setiap hari.
3. Mendadak butuh tool untuk eksekusi task tertentu.
4. Lagi libur dan ga ada oprekan lain.
5. Gabut aja!

Yaah, seenggaknya skrip ini bisa mengubah *"gabut"* jadi **ga** *"gabut-gabut"* banget.

## Visi

Sapa tau kedepannya bisa jadi **swiss army knife** buat daily operations. At least for myself. Nyiahiahiahiahiahia...

## Udah Bisa Apa?

* **Integrasi Splunk**: Belum semua endpoint yak, di-*update* seperlunya aja.
* **Configurable**: Skripnya bisa dikonfigurasi dengan *options* untuk macem-macem use case, misal; ngobrol sama Splunk API; atur-atur parameter query; *handling time ranges*.
* **Logging**: Udah ada fitur *logging built-in*. Weiit, ini belom rapi semua juga yak, kalo lagi rajin ya didetilin, kalo lagi males pake *output default* ae.
* **Modular**: Fungsinya udah dipecah-pecah. Maksudnya biar gampang *manage*-nya, tadinya malah mo bikin dukungan buat *plugins*, apa daya *skill* masih kureng. Sementara fungsional aja dulu.

## Instalasi

### Prerequisites

* Python >= 3.9.
* `pip` buat instalasi dependensi.

### Install Dependensi

```
# Clone repo
# github
git clone https://github.com/bringsrain/sekripgabut.git

# gitlab
git clone https://gitlab.com/bringsrain/sekripgabut.git

# nganu -- yang tau-tau aja
git clone http://nganu:3000/usernamegw/sekripgabut.git

cd sekripgabut
pip install .
```
### Upgrade Versi
```
# Masuk ke existing directory
cd sekripgabut

# git clone or git pull for existing directory
# github
git pull https://github.com/bringsrain/sekripgabut.git

# gitlab
git pull https://gitlab.com/bringsrain/sekripgabut.git

# nganu -- yang tau-tau aja
git pull http://nganu:3000/usernamegw/sekripgabut.git

# Upgrade menggunakan pip
pip install --upgrade .
```

### Setup Virtual Environment (Optional)

#### Anaconda/Miniconda

```
# Bikin virtual environment
conda create -n sekripgabut python=3.9

# Aktifin virtual environment
conda activate sekripgabut

# Install dependensi
pip install .
```

#### Python Venv

```
# Bikin virtual environment
python -m venv .venv

# Aktifin virtual environment
# Windows
.venv\Scripts\activate

# MacOS/Linux
source .venv/bin/activate
python 
### Setup Virtual Environment

# Install dependensi
pip install .
```
## Related Files

### Splunk Configuration File (`config.ini` or `[any].ini`)

Contoh file config.ini

Saat ini baru untuk Splunk
```
[Auth]
token = place_your_token_here

[Splunk]
base_url = https://example.com:8089

```

### Log File

`sekrigabut.log` akan tersimpan di-*path* yang sama saat eksekusi `sekripgabut`
## Cara Pake

### Command-Line Interace(CLI)

`sekripgabut` itu jalan di-*command-line* atau di terminal (bukan pulogadung atau rambutan yak) *emulator*.

### Available Commands

#### `sekripgabut es`

##### Notable Events Operations

* Cek waktu **Notable Event** pertama kali diindeks dalam suatu *time-range*.

    ```
    sekripgabut es --config config.ini --first-notable-index --earliest="2024-12-21T00:00:00" --latest="2024-12-21T24:00:00"
    ```
    - `--config`: *Path* ke file konfigurasi (optional. Default: `config.ini`)
    - `--first-notable-index`: Flag buat dapetin waktu pertama kali notable event diindeks dalam rentang waktu tertentu (Default: **All-time**).
    - `--earliest`: Batas waktu awal pencarian. (Optional. Default: `""`). Format bisa menggunakan *time modifier* Splunk, baik *fixed* atau *relative time*.
    - `--latest`: Batas waktu akhir pencarian. (Optional. Default: `""`). Format bisa menggunakan *time modifier* Splunk, baik *fixed* atau *relative time*.

* *Fetch `event_id` notable event* yang belum di-*close* yang di-*split* per tujuh hari, kemudian disimpan ke dalam file JSON pada *output file* yang ditentukan.
    ```
    sekripgabut es --config config.ini --weekly-unclosed-notable --path .\output-dir --earliest="-15m" --latest="now"
    ```
    - `--config`: *Path* ke file konfigurasi (optional. Default: `config.ini`)
    - `--weekly-unclosed-notable`: Flag buat *fetch `event_id` notable event* yang belum di-*close* dalam rentang waktu tertentu (Default: **All-time**).
    - `--earliest`: Batas waktu awal pencarian. (Optional. Default: `""`). Format bisa menggunakan *time modifier* Splunk, baik *fixed* atau *relative time*. Jika opsi tidak digunakan maka waktu index pertama akan ditentukan dari output opsi `--first-notable-index`.
    - `--latest`: Batas waktu akhir pencarian. (Optional. Default: `""`). Format bisa menggunakan *time modifier* Splunk, baik *fixed* atau *relative time*. Jika opsi tidak digunakan maka batas waktu akhir adalah `"now"`

#### `sekripgabut pemutihan`

* Tutup semua notable event dalam *range* waktu yang ditentukan.
    > "Command ini dibuat dalam rangka menyambut tahun baru 2025"
    ```
    sekripgabut pemutihan --config config.ini --path fs-okt-2024 --earliest="2024-10-01T00:00:00" --latest="2024-11-01T00:00:00"
    ```
    **Seluruh opsi REQUIRED yak!**
    - `pemutihan`: *Command* yang dipake khusus untuk menyambut tahun baru 2025.
    - `--config`: *Path* ke file konfigurasi (optional. Default: `config.ini`)
    - `--path`: *Path* output direktori (folder) tempat JSON file berisi `event_id` akan disimpan. `event_id` merujuk pada notable event yang akan diputihkan.
    - `--earlest`: Batas waktu awal pencarian. Format bisa menggunakan *time modifier* Splunk, baik *fixed* atau *relative time*.
    - `--latest`: Batas waktu akhir pencarian. Format bisa menggunakan *time modifier* Splunk, baik *fixed* atau *relative time*.

#### `sekripgabut pemutihan v2`

* Tutup semua notable event dalam *range* waktu yang ditentukan versi **Lebih Ngacir** atau mungkin **Lebih Ganteng**.
    > "Command ini dibuat dalam rangka menyambut tahun baru 2025"
    ```
    sekripgabut pemutihan v2 --config config.ini --earliest="2021-01-01T00:00:00" --latest="2024-11-01T00:00:00"
    ```
    - `pemutihan`: *Command* yang dipake khusus untuk menyambut tahun baru 2025.
    - `v2`: *Positional argument* `ver`. Untuk menjalankan sekrip `pemutihan_v2`.
    - `--config`: *Path* ke file konfigurasi (optional. Default: `config.ini`)
    - `--earlest`: Batas waktu awal pencarian. Format bisa menggunakan *time modifier* Splunk, baik *fixed* atau *relative time*.
    - `--latest`: Batas waktu akhir pencarian. Format bisa menggunakan *time modifier* Splunk, baik *fixed* atau *relative time*.

#### `sekripgabut --help`

* Buat buka help liat semua opsi dan arguments.
    ```
    # Global help
    sekripgabut --help

    # Options help
    sekripgabut es --help
    sekripgabut splunk --help
    ...
    ```
