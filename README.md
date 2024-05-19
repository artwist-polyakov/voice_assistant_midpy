# Проектная работа: голосовой ассистент

## Порядок развёртования проекта

1. Разместите пустой файл `logs.log` в директории 'logs'.
2. Скопируйте содержимое файла `.env.example` в файл `.env`.
3. Заполните сертификаты в папке `.certs` ( https://disk.yandex.ru/d/xy-vpk18OrDatw )
4. Сгенерируйте dpem ключи в папке `.certs` командой:
```bash
openssl dhparam -out ssl-dhparams.pem 2048
```

## Проект в интернете

https://practix-cinema.ru/api/openapi