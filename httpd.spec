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
