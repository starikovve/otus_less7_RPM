# otus_less7_RPM
Administrator Linux. Professional

1) Создать свой RPM пакет (можно взять свое приложение, либо собрать, например,
Apache с определенными опциями).
2) Создать свой репозиторий и разместить там ранее собранный RPM.

3) Реализовать это все либо в Vagrant, либо развернуть у себя через Nginx и дать ссылку на репозиторий.

 1. Создать свой RPM пакет. Будем собирать apache из исходников с измененной начальной страницей. Дистрибутив CentOS-Stream-10-latest и httpd-2.4.66
   
1.1 Подготовка среды сборки.
Для начала необходимо установить инструменты разработки и зависимости, необходимые для компиляции Apache (httpd).

```
sudo dnf install -y rpm-build rpmdevtools gcc make apr-devel apr-util-devel pcre2-devel openssl-devel systemd-devel
```
rpm-build — основной инструмент для сборки RPM

rpmdevtools — вспомогательные утилиты (rpmdev-setuptree и др.)

gcc, make — компилятор и система сборки

apr-devel, apr-util-devel — библиотеки Apache Portable Runtime

pcre2-devel — библиотека регулярных выражений (новая версия для CentOS 10)

openssl-devel — для SSL/TLS поддержки

systemd-devel — интеграция с systemd



rpmdev-setuptree
Эта команда создает в домашней директории пользователя структуру каталогов ~/rpmbuild. Внутри появятся папки: BUILD (для временных файлов сборки), RPMS (для готовых пакетов), SOURCES (для исходников), SPECS (для файлов конфигурации сборки) и SRPMS (для исходных rpm-пакетов).

<img width="340" height="104" alt="image" src="https://github.com/user-attachments/assets/43fdc3fe-4c75-4901-8d5b-951666fcb44c" />


1.2 Загрузка исходных кодов.

Переходим в директорию для исходников и скачайте архив с официального сайта Apache.

cd ~/rpmbuild/SOURCES

Переходим в папку, где rpmbuild ожидает увидеть исходные файлы.

Скачиваем стабильную версию Apache

wget https://downloads.apache.org/httpd/httpd-2.4.66.tar.gz

<img width="583" height="58" alt="image" src="https://github.com/user-attachments/assets/9ab811af-f71f-40d7-8948-9247c6cdb4f1" />


1.3 Создание кастомной страницы.

Подготовим файл index.html, который будет вшит в пакет.

nano index.html
```
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Apache Custom Build</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            background: white;
            padding: 50px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            text-align: center;
        }
        h1 {
            color: #333;
            margin-bottom: 20px;
        }
        .subtitle {
            color: #666;
            font-size: 18px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Administrator Linux. Professional - lesson 7 RPM</h1>
        <p class="subtitle">Custom Apache httpd 2.4.66 Build</p>
    </div>
</body>
</html>
```

1.4 Создание SPEC-файла.
```
cd ~/rpmbuild/SPECS
nano httpd.spec
```
c содержимым:
```
Name:           httpd-custom
Version:        2.4.66
Release:        1%{?dist}
Summary:        Apache HTTP Server with custom index page

License:        ASL 2.0
URL:            https://httpd.apache.org/
Source0:        httpd-%{version}.tar.gz
Source1:        index.html

BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  apr-devel
BuildRequires:  apr-util-devel
BuildRequires:  pcre2-devel
BuildRequires:  openssl-devel
BuildRequires:  systemd-devel

Requires:       apr
Requires:       apr-util
Requires:       pcre2

%description
Apache HTTP Server 2.4.66 compiled from sources with custom index page
for Administrator Linux Professional course - Lesson 7 RPM

%prep
%setup -q -n httpd-%{version}

%build
./configure \
    --prefix=/usr/local/apache2 \
    --enable-so \
    --enable-ssl \
    --with-mpm=event \
    --with-apr=/usr/bin/apr-1-config \
    --with-apr-util=/usr/bin/apu-1-config \
    --with-pcre=/usr/bin/pcre2-config

make %{?_smp_mflags}

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}

# Установка кастомной начальной страницы
install -m 644 %{SOURCE1} %{buildroot}/usr/local/apache2/htdocs/index.html

# Создание systemd unit файла
mkdir -p %{buildroot}%{_unitdir}
cat > %{buildroot}%{_unitdir}/httpd-custom.service << 'UNIT'
[Unit]
Description=Apache HTTP Server Custom Build
After=network.target

[Service]
Type=forking
ExecStart=/usr/local/apache2/bin/apachectl start
ExecStop=/usr/local/apache2/bin/apachectl stop
ExecReload=/usr/local/apache2/bin/apachectl graceful
PrivateTmp=true

[Install]
WantedBy=multi-user.target
UNIT

%files
/usr/local/apache2/*
%{_unitdir}/httpd-custom.service

%changelog
* $(date "+%a %b %d %Y") Builder <builder@localhost> - 2.4.66-1
- Custom build of Apache httpd 2.4.66 for lesson 7
- Added custom index page with course information
- Built with PCRE2 support for CentOS 10

```

Разбор SPEC-файла по секциям:

Секция метаданных:

Name — имя пакета (httpd-custom, чтобы не конфликтовать с системным)

Version — версия Apache

Release — номер релиза пакета

Summary — краткое описание

Source0 — основной исходный архив

Source1 — дополнительный файл (наша index.html)

BuildRequires:

Зависимости для сборки пакета (нужны только при компиляции)

Requires:
Зависимости для работы установленного пакета

%prep (подготовка):

%setup -q -n httpd-%{version} — распаковка архива

%build (сборка):

./configure — настройка параметров компиляции--prefix=/usr/local/apache2 — куда устанавливать

--enable-ssl — поддержка HTTPS

--enable-rewrite — mod_rewrite для URL

--with-pcre2 — использовать PCRE2 (для CentOS 10)


make — компиляция

%install (установка в buildroot):

make install DESTDIR=%{buildroot} — установка в временный каталог

install -m 644 %{SOURCE1} — копирование нашей index.html

Создание systemd unit файла для автозапуска

%files:
Список файлов, которые войдут в пакет

1.5 Сборка пакета.

Чтобы не устанавливать каждую зависимость вручную, в CentOS/RHEL есть удобный инструмент, который считывает ваш SPEC-файл и устанавливает всё необходимое одной командой:
```
sudo dnf builddep ~/rpmbuild/SPECS/httpd.spec
```
Запустим сам процесс создания RPM
```
cd ~/rpmbuild/SPECS
rpmbuild -ba httpd.spec
```
Что означает -ba:

b — build (собрать)
a — all (и бинарный RPM, и исходный SRPM)

Что происходит:
Распаковка httpd-2.4.66.tar.gz в ~/rpmbuild/BUILD/
Выполнение ./configure с указанными параметрами
Компиляция (make)
Установка в ~/rpmbuild/BUILDROOT/
Создание RPM пакета

<img width="1111" height="110" alt="image" src="https://github.com/user-attachments/assets/de11ba39-bb09-4822-ae09-0511d3ed15ac" />

1.6 Проверка результата
```
ls -lh ~/rpmbuild/RPMS/x86_64/
```
<img width="995" height="113" alt="image" src="https://github.com/user-attachments/assets/7c7ba05a-3349-4d3a-9db4-496ac624657b" />

Проверка содержимого пакета:

```
rpm -qpl ~/rpmbuild/RPMS/x86_64/httpd-custom-2.4.66-1.el10.x86_64.rpm | head -20
```

<img width="1004" height="398" alt="image" src="https://github.com/user-attachments/assets/c8c8bf5e-f429-4123-b81d-b200ffdba178" />

Проверка метаданных:

```
rpm -qpi ~/rpmbuild/RPMS/x86_64/httpd-custom-2.4.66-1.el10.x86_64.rpm
```

<img width="974" height="345" alt="image" src="https://github.com/user-attachments/assets/d8a11128-8313-43df-9ae1-64a0f7f63362" />


1.7 Установка пакета.

```
sudo dnf install -y ~/rpmbuild/RPMS/x86_64/httpd-custom-2.4.66-1.el10.x86_64.rpm
```
Проверка установки:

```
rpm -qa | grep httpd-custom
ls -la /usr/local/apache2/
```

<img width="563" height="411" alt="image" src="https://github.com/user-attachments/assets/ee5d366c-9262-4b90-8bfb-345eb0e0b0ad" />

Запуск через systemd:

```
sudo systemctl daemon-reload
sudo systemctl start httpd-custom.service
sudo systemctl enable httpd-custom.service
```

Проверка статуса:
```
sudo systemctl status httpd-custom.service
```

<img width="1107" height="385" alt="image" src="https://github.com/user-attachments/assets/4529541c-5e8a-45fb-a319-cb30a7ac8cdc" />

Настройка firewall:
```
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --reload
```

1.8 Заходим на сервер  и видим нашу кастомную страницу:

<img width="737" height="653" alt="image" src="https://github.com/user-attachments/assets/c40aa4d8-051a-481d-8baf-c44e5f3d9f37" />



