# sekripgabut


> Pengen gitu bikin README pake bahasa yang proper biar kek orang-orang, tapi bikinnya pas lagi gabut juga sih. Beginilah jadinya. 

`sekripgabut` adalah koleksi skrip yang dibuat untuk mengisi waktu gabut. Momen gabut bisa disebabkan oleh beberapa hal:

1. Mentok saat melakukan task.
2. Kesel karena repetitive action kecil setiap hari.
3. Mendadak butuh tool untuk eksekusi task tertentu.
4. Lagi libur dan ga ada oprekan lain.
5. Gabut aja!

Yaah, seenggaknya skrip ini bisa mengubah *"gabut"* menjadi **ga** *"gabut-gabut"* banget.

## Visi

Sapa tau kedepannya bisa menjadi **swiss army knife** buat daily operations. At least for myself. Nyiahiahiahiahiahia...

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

### Setup Virtual Environment (Optional)

### Anaconda/Miniconda

```
# Bikin virtual environment
conda create -n sekripgabut python=3.9

# Aktifin virtual environment
conda activate sekripgabut

# Install dependensi
pip install .
```

### Python Venv

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
    - `--earliest`: Tentuin waktu awal *search*. (Optional. Default: `""`)
    - `--latest`: Tentuin batas waktu akhir *search*. (Optional. Default: `now`)

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
