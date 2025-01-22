## Panduan Instalasi

1. Install library yang dipakai dengan

```bash
pip install pandas Rpython pyqt6
```

2. Untuk menjalankan program menggunakan perintah

```bash
python3 __main__.py
```

## Penulisan Commit 💬

Penulisan pesan commit menggunakan standar dari [European Commission](https://ec.europa.eu/component-library/v1.15.0/eu/docs/conventions/git/) dengan beberapa penyesuaian dengan format:

```
<type>(<scope>): <subject> <meta>
<BLANK LINE>
<body>
```

### Type

Type yang diizinkan untuk digunakan dalam pesan commit antara lain:

- **feat**: Menambahkan fitur baru
- **fix**: Memperbaiki bug
- **docs**: Memperbaiki dokumentasi
- **style**: Merapikan gaya penulisan kode
- **refactor**: Mengefisienkan penulisan kode yang tidak menambah fitur
- **perf**: Mengefisienkan performa
- **test**: Menambahkan kode testing
- **chore**: Mengubah konfigurasi tools dan dependency

### Scope

Bersifat opsional dengan batasan yang jelas.

### Subject

Deskripsi singkat mengenai perubahan yang dibuat.

### Body

Bersifat opsional. Berisi alasan perubahan dan perbedaan dari sebelumnya

### Revert

Log revert harus menggunakan kata _revert:_ dan dilanjutkan dengan header commitnya

Contoh Commit:

```
//Commit benar
style(location): menambahkan titik koma
```

```
//Commit benar
feat: menambahkan onURLChange event

New $browser event:
- forward popstate event if available
- forward hashchange event if popstate not available
- do polling when neither popstate nor hashchange available
```

```
//Commit salah
style: membuat fitur auth dan memperbaiki bug 1
//Penggunaan style tidak sesuai dengan subject. Subject juga harus memisahkan 2 hal yang berbeda
```

## Struktur File Resource 📒

```
├── controller
├── model
├── view
│ __main.js
```

| No  | Nama Folder | Keterangan                                                                                                                                                                                          |
| --- | ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1.  | assets      | Menyimpan asset berupa gambar yang akan digunakan                                                                                                                                                   |
| 2.  | components  | Menyimpan reuseable componen AppButton, AppNavBar, dll, yang dapat digunakan oleh seluruh page/komponen lain                                                                                        |
| 3.  | constants   | Menyimpan konstanta yang digunakan berulang kali                                                                                                                                                    |
| 4.  | helpers     | Menyimpan kumpulan method umum yang digunakan berulang kali                                                                                                                                         |
| 5.  | layout      | Layout utama dari web. Setiap layout dipisahkan dengan masing-masing folder. Dalam folder tersebut, terdapat juga komponen/section yang hanya digunakan oleh layout tersebut.                       |
| 6.  | pages       | Halaman web yang terdiri dari beberapa komponen. Setiap page dipisahkan dengan masing-masing folder. Dalam folder tersebut, terdapat juga komponen/section yang hanya digunakan oleh page tersebut. |

Dalam file vue, susunan kode yang ditulis adalah berupa

```js
<script setup></script>

<template></template>
```

## Penulisan Kode 🖋️

Penulisan kode menggunakan standar yang digunakan pada bahasa pemrograman JavaScript dari [Airbnb](https://github.com/airbnb/javascript?tab=readme-ov-file#naming-conventions). Dalam penamaan _identifier_, menggunakan format penamaan yang informatif dan mudah untuk dipahami menggunakan bahasa Inggris. Contoh yang benar:

```
errorCount          // Tidak ada singkatan.
DNSConnectionIndex  // Orang-orang sudah tahu tentang DNS.
referrerURL         // Ditto for "URL".
customerID          // Id tidak akan salah diinterpretasikan
```

Singkatan menggunakan huruf besar dan hanya boleh untuk kata-kata yang lazim disingkat.
Contoh Salah:

```
n                   // Tidak bermakna.
pcReader            // Singkatan Ambigu.
wgcConnections      // Tidak semua orang tau WGC
cstmrID             // Deletes internal letters.
```

Tipe penulisan nama berdasarkan jenis identifier:

| No  | Kategori            | Penulisan                                                                                              | Contoh                   |
| --- | ------------------- | ------------------------------------------------------------------------------------------------------ | ------------------------ |
| 1.  | Package             | **camelCase**                                                                                          | my.exampleCode.deepSpace |
| 2.  | Kelas               | **PascalCase**                                                                                         | Request, ImmutableList   |
| 3.  | Method              | **camelCase**                                                                                          | sendMessage              |
| 4.  | Enumerated          | **PascalCase**, setiap item didalamnya berupa **CONSTANT_CASE**                                        | UserRoles                |
| 5.  | Konstanta           | **CONSTANT_CASE**                                                                                      | ENUM_CONSTANT            |
| 6.  | Variabel nonkonstan | Untuk vue, **camelCase**. Sementara pada laravel mengikuti best practice pada laravel dengan diawali $ | customerID               |
| 7.  | Parameter           | Untuk vue, **camelCase**. Sementara pada laravel mengikuti best practice pada laravel dengan diawali $ | customerID               |
| 8.  | Variabel lokal      | Untuk vue, **camelCase** Sementara pada laravel mengikuti best practice pada laravel dengan diawali $  | customerID               |

Dalam hal standardisasi kerapian dalam hal penulisan, diharapkan untuk menginstall extension [Prettier](https://github.com/prettier/prettier) pada Visual Studio Code masing-masing.

Selengkapnya mengenai format penulisan dapat dilihat [disini](https://github.com/airbnb/javascript?tab=readme-ov-file#naming-conventions)

## Panduan membuat executable (.exe)

1. install pyinstaller

```
pip install pyinstaller
```

2. jalankan perintah

```
pyinstaller main.spec
```
