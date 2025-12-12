# Formatos de Archivos - Fase de Reconocimiento

**Fecha:** 10 de Diciembre 2025  
**Entorno:** DEV4-IMPROVEMENTS  

---

## 1. SUBDOMAIN ENUMERATION

### Subfinder (`.txt`)
```txt
www.fravega.kopernicus.tech
assurant.kopernicus.tech
www.kopernicus.tech
kopernicus.tech
```
**Formato:** Lista simple, un subdominio por línea, sin metadata

### Amass (`.txt`)
```txt
kopernicus.tech
uy.kopernicus.tech
cl.kopernicus.tech
```
**Formato:** Idéntico a Subfinder

### Assetfinder, Sublist3r, Findomain, crt.sh (`.txt`)
**Formato:** Todos generan listas planas similares a Subfinder

---

## 2. DNS ENUMERATION

### DNSRecon (`.json`)
```json
[
    {
        "arguments": "/usr/bin/dnsrecon -d kopernicus.tech",
        "date": "2025-12-09 15:01:48",
        "type": "ScanInfo"
    },
    {
        "address": "200.58.97.2",
        "domain": "kopernicus.tech",
        "mname": "ns9.hostmar.com",
        "type": "SOA"
    },
    {
        "address": "200.58.97.2",
        "domain": "kopernicus.tech",
        "target": "ns9.hostmar.com",
        "type": "NS"
    },
    {
        "address": "192.178.223.27",
        "domain": "kopernicus.tech",
        "exchange": "aspmx2.googlemail.com",
        "type": "MX"
    },
    {
        "address": "66.97.42.227",
        "domain": "kopernicus.tech",
        "name": "kopernicus.tech",
        "type": "A"
    },
    {
        "domain": "kopernicus.tech",
        "name": "kopernicus.tech",
        "strings": "v=spf1 include:_spf.mailersend.net",
        "type": "TXT"
    }
]
```
**Tipos de registro:** ScanInfo, SOA, NS, MX, A/AAAA, TXT, CNAME

### Fierce (`.txt`)
```txt
NS: ns4711.banahosting.com. ns4710.banahosting.com.
SOA: ns4710.banahosting.com. (216.246.112.35)
Zone: failure
Wildcard: failure
Found: ftp.alquilersura.com.uy. (216.246.112.39)
Nearby:
{'216.246.112.34': 'single-4710.banahosting.com.',
 '216.246.112.35': 'ns4710.banahosting.com.'}
Found: mail.alquilersura.com.uy. (216.246.112.39)
```
**Formato:** Texto estructurado con NS, SOA, subdominios encontrados, diccionario de IPs cercanas

### DNSEnum (`.txt`)
```txt
dnsenum.pl VERSION:1.2.6
-----   example.com   -----
Host's addresses:
example.com.    5    IN    A    192.0.2.1
Name Servers:
ns1.example.com.    5    IN    A    192.0.2.10
```
**Formato:** Texto con secciones (addresses, name servers, MX)

### Traceroute (`.txt`)
```txt
traceroute to kopernicus.tech (66.97.42.227), 30 hops max
 1  192.168.0.1 (192.168.0.1)  5.203 ms
 2  10.42.64.1 (10.42.64.1)  9.512 ms
 5  * * *
16  vps-1889901-x.dattaweb.com (66.97.42.227)  151.231 ms
```
**Formato:** Línea por salto, `* * *` indica timeout

---

## 3. OSINT TOOLS

### Shodan (`.json`)
```json
{
  "query": "hostname:example.com",
  "total": 12,
  "matches": [
    {
      "ip_str": "192.0.2.1",
      "port": 443,
      "product": "nginx",
      "version": "1.18.0",
      "os": "Linux",
      "hostnames": ["example.com"],
      "location": {
        "country_code": "US",
        "city": "San Francisco"
      },
      "ssl": {
        "cert": {
          "issued": "2023-01-15",
          "expires": "2024-01-15"
        }
      },
      "vulns": ["CVE-2021-44228"]
    }
  ]
}
```
**Campos clave:** ip_str, port, product, version, location, ssl, vulns

### Censys (`.json`)
```json
{
  "status": "ok",
  "results": [
    {
      "ip": "192.0.2.1",
      "protocols": ["443/https", "80/http"],
      "services": [
        {
          "port": 443,
          "certificate": {
            "parsed": {
              "subject_dn": "CN=example.com"
            }
          }
        }
      ]
    }
  ]
}
```
**Enfoque:** Certificados SSL/TLS, servicios por puerto

### TheHarvester (`.json`)
```json
{
  "hosts": ["www.example.com", "api.example.com"],
  "emails": ["admin@example.com"],
  "ips": ["192.0.2.1"],
  "urls": ["https://www.example.com"],
  "interesting_urls": ["https://example.com/admin"]
}
```
**Campos:** hosts, emails, ips, urls, interesting_urls

### Hunter.io (`.json`)
```json
{
  "data": {
    "domain": "example.com",
    "pattern": "{first}.{last}",
    "emails": [
      {
        "value": "john.doe@example.com",
        "confidence": 95,
        "position": "Software Engineer"
      }
    ]
  }
}
```
**Campos:** pattern, confidence, position, sources

### Wayback Machine (`.txt`)
```txt
https://web.archive.org/web/20200101/http://example.com/
https://web.archive.org/web/20200615/http://example.com/admin
```
**Formato:** URLs con timestamp

---

## 4. WEB RECONNAISSANCE

### WhatWeb (`.json`)
```json
[
  {
    "target": "https://example.com",
    "http_status": 200,
    "plugins": {
      "HTTPServer": {"string": ["nginx/1.18.0"]},
      "X-Powered-By": {"string": ["PHP/7.4.3"]},
      "JQuery": {"version": ["3.5.1"]},
      "Bootstrap": {"version": ["4.5.0"]},
      "Google-Analytics": {"account": ["UA-12345678-1"]}
    }
  }
]
```
**Detecta:** Servidor web, lenguaje backend, frameworks JS, CMS, analytics

### Web Crawling - Gospider/Hakrawler (`.txt`)
```txt
https://example.com/
https://example.com/api/v1/users
https://example.com/admin/login
https://example.com/static/js/app.js
```
**Formato:** Lista de URLs

---

## 5. OTROS

### WHOIS (`.txt`)
```txt
Domain Name: KOPERNICUS.TECH
Creation Date: 2020-06-24T10:15:05.0Z
Registry Expiry Date: 2026-06-24T23:59:59.0Z
Registrar: Dattatec.com SRL
Name Server: NS9.HOSTMAR.COM
Name Server: NS10.HOSTMAR.COM
Registrar Abuse Contact Email: abuse@donweb.com
```
**Campos:** Creation Date, Expiry Date, Registrar, Name Servers

### Google Dorks (`.txt`)
```txt
https://example.com/admin/config.php
https://example.com/backup/db_backup.sql
https://example.com/.env
```
**Formato:** URLs sensibles

### Secrets Detection - Gitleaks/Trufflehog (`.json`)
```json
[
  {
    "Description": "AWS Access Key",
    "Match": "AKIAIOSFODNN7EXAMPLE",
    "File": "config/aws.js",
    "StartLine": 15,
    "RuleID": "aws-access-token",
    "Entropy": 4.5
  }
]
```
**Campos:** Description, Match, File, StartLine, RuleID

---

## RESUMEN POR FORMATO

### TXT (12 herramientas):
- **Subdominios:** Subfinder, Amass, Assetfinder, Sublist3r, Findomain, crt.sh
- **DNS:** DNSEnum, Fierce, Host/NSLookup, Traceroute
- **OSINT:** Wayback Machine, LinkedIn Enum
- **Web:** Web Crawling
- **Otros:** WHOIS, Google Dorks

### JSON (7 herramientas):
- **DNS:** DNSRecon
- **OSINT:** Shodan, Censys, TheHarvester, Hunter.io
- **Web:** WhatWeb
- **Otros:** Secrets Detection

---

## CONSIDERACIONES PARA PARSERS

### Archivos TXT:
- Filtrar banners y líneas vacías
- Split por `\n` para listas simples
- Regex para formatos estructurados (Fierce, DNSEnum)

### Archivos JSON:
- Validar JSON antes de parsear
- Manejar campos opcionales
- Verificar arrays vacíos

---

**Fin del documento**


**Fecha:** 10 de Diciembre 2025  
**Entorno:** DEV4-IMPROVEMENTS  
**Propósito:** Documentar los formatos de salida de todas las herramientas de reconocimiento

---

## 📋 Tabla de Contenidos

1. [Subdomain Enumeration](#1-subdomain-enumeration)
2. [DNS Enumeration](#2-dns-enumeration)
3. [OSINT Tools](#3-osint-tools)
4. [Web Reconnaissance](#4-web-reconnaissance)
5. [Otros](#5-otros)

---

## 1. SUBDOMAIN ENUMERATION

### 1.1 Subfinder (`.txt`)

**Formato:** Lista simple de subdominios, un subdominio por línea

**Ejemplo:**
```txt
www.fravega.kopernicus.tech
assurant.kopernicus.tech
www.assurant.kopernicus.tech
www.kopernicus.tech
macro.kopernicus.tech
www.macro.kopernicus.tech
kopernicus.tech
fravega.kopernicus.tech
```

**Características:**
- Sin encabezados ni metadata
- Sin ordenamiento específico
- Puede contener duplicados
- Puede incluir subdominios con y sin "www"

---

### 1.2 Amass (`.txt`)

**Formato:** Similar a Subfinder, lista simple de subdominios

**Ejemplo:**
```txt
kopernicus.tech
uy.kopernicus.tech
cl.kopernicus.tech
```

**Características:**
- Lista plana sin metadata
- Ordenamiento aleatorio
- Usualmente menos resultados pero más precisos

---

### 1.3 Assetfinder (`.txt`)

**Formato:** Lista simple de dominios/subdominios

**Ejemplo:**
```txt
kopernicus.tech
uy.kopernicus.tech
cl.kopernicus.tech
```

**Características:**
- Formato idéntico a Amass
- Sin metadata adicional
- Puede incluir dominios relacionados

---

### 1.4 Sublist3r (`.txt`)

**Formato:** Lista de subdominios con posibles banners

**Ejemplo:**
```txt
www.alquilersura.com.uy
cpanel.alquilersura.com.uy
cpcalendars.alquilersura.com.uy
cpcontacts.alquilersura.com.uy
mail.alquilersura.com.uy
webdisk.alquilersura.com.uy
webmail.alquilersura.com.uy
```

**Características:**
- Lista simple sin banners (cuando se procesa correctamente)
- Puede incluir servicios comunes (mail, cpanel, webdisk, etc.)
- Un subdominio por línea

---

### 1.5 Findomain (`.txt`)

**Formato:** Lista simple de subdominios

**Ejemplo:**
```txt
api.example.com
mail.example.com
www.example.com
staging.example.com
```

**Características:**
- Formato plano
- Sin metadata
- Usualmente incluye subdominios de APIs y staging

---

### 1.6 crt.sh (`.txt`)

**Formato:** Lista de subdominios obtenidos desde Certificate Transparency logs

**Ejemplo:**
```txt
*.example.com
example.com
www.example.com
mail.example.com
api.example.com
```

**Características:**
- Puede incluir wildcards (`*.example.com`)
- Basado en certificados SSL/TLS emitidos
- Generalmente muy completo para dominios con HTTPS

---

## 2. DNS ENUMERATION

### 2.1 DNSRecon (`.json`)

**Formato:** JSON array con objetos estructurados por tipo de registro DNS

**Ejemplo:**
```json
[
    {
        "arguments": "/usr/bin/dnsrecon -d kopernicus.tech -t std -j output.json",
        "date": "2025-12-09 15:01:48.826325",
        "type": "ScanInfo"
    },
    {
        "address": "200.58.97.2",
        "domain": "kopernicus.tech",
        "mname": "ns9.hostmar.com",
        "type": "SOA"
    },
    {
        "Version": "root@dnsded01.dattaweb.com)\"",
        "address": "200.58.97.2",
        "domain": "kopernicus.tech",
        "recursive": "True",
        "target": "ns9.hostmar.com",
        "type": "NS"
    },
    {
        "address": "192.178.223.27",
        "domain": "kopernicus.tech",
        "exchange": "aspmx2.googlemail.com",
        "type": "MX"
    },
    {
        "address": "66.97.42.227",
        "domain": "kopernicus.tech",
        "name": "kopernicus.tech",
        "type": "A"
    },
    {
        "domain": "kopernicus.tech",
        "name": "kopernicus.tech",
        "strings": "v=spf1 include:_spf.mailersend.net include:_spf.google.com ~all",
        "type": "TXT"
    },
    {
        "domain": "kopernicus.tech",
        "name": "_dmarc.kopernicus.tech",
        "strings": "v=DMARC1; p=quarantine; rua=mailto:abuso@kopernicus.tech",
        "type": "TXT"
    }
]
```

**Características:**
- **ScanInfo:** Metadata de la ejecución (comando, fecha)
- **SOA:** Start of Authority (servidor DNS autorizado, mname)
- **NS:** Name Servers (servidores DNS)
- **MX:** Mail Exchange servers (servidores de correo)
- **A/AAAA:** Registros de dirección IP (IPv4/IPv6)
- **TXT:** Registros de texto (SPF, DMARC, verificación de dominio)
- **CNAME:** Canonical names (alias)

**Campos comunes:**
- `type`: Tipo de registro DNS
- `domain`: Dominio consultado
- `address`: Dirección IP asociada
- `name`: Nombre del registro
- `strings`: Contenido de registros TXT

---

### 2.2 DNSEnum (`.txt`)

**Formato:** Texto plano con resultados estructurados por secciones

**Ejemplo:**
```txt
dnsenum.pl VERSION:1.2.6

-----   example.com   -----

Host's addresses:
__________________

example.com.                             5       IN      A        192.0.2.1

Name Servers:
______________

ns1.example.com.                         5       IN      A        192.0.2.10
ns2.example.com.                         5       IN      A        192.0.2.11

Mail (MX) Servers:
___________________

mail.example.com.                        10      IN      A        192.0.2.20

Trying Zone Transfers and getting Bind Versions:
_________________________________________________

Trying Zone Transfer for example.com on ns1.example.com ...
AXFR record query failed: NOTAUTH
```

**Características:**
- Formato de texto con secciones claramente delimitadas
- Incluye registros A, NS, MX
- Intenta transferencias de zona (AXFR)
- Puede incluir errores y warnings

---

### 2.3 Fierce (`.txt`)

**Formato:** Texto con análisis estructurado y diccionario de IP cercanas

**Ejemplo:**
```txt
NS: ns4711.banahosting.com. ns4710.banahosting.com.
SOA: ns4710.banahosting.com. (216.246.112.35)
Zone: failure
Wildcard: failure
Found: ftp.alquilersura.com.uy. (216.246.112.39)
Nearby:
{'216.246.112.34': 'single-4710.banahosting.com.',
 '216.246.112.35': 'ns4710.banahosting.com.',
 '216.246.112.36': 'ns4711.banahosting.com.',
 '216.246.112.37': 'single-4710.banahosting.com.',
 '216.246.112.38': 'single-4710.banahosting.com.',
 '216.246.112.39': 'single-4710.banahosting.com.',
 '216.246.112.40': 'single-4710.banahosting.com.',
 '216.246.112.41': 'single-4710.banahosting.com.',
 '216.246.112.42': 'single-4710.banahosting.com.',
 '216.246.112.43': 'single-4710.banahosting.com.',
 '216.246.112.44': 'single-4710.banahosting.com.'}
Found: mail.alquilersura.com.uy. (216.246.112.39)
```

**Características:**
- **NS:** Name servers del dominio
- **SOA:** Start of Authority con IP
- **Zone:** Resultado de intento de transferencia de zona
- **Wildcard:** Detección de wildcard DNS
- **Found:** Subdominios descubiertos con IPs
- **Nearby:** Diccionario Python de IPs adyacentes y sus hostnames

---

### 2.4 Host/NSLookup (`.txt`)

**Formato:** Texto plano con resultados de consulta DNS

**Ejemplo:**
```txt
kopernicus.tech has address 66.97.42.227
kopernicus.tech mail is handled by 10 aspmx.l.google.com.
kopernicus.tech mail is handled by 20 alt1.aspmx.l.google.com.
kopernicus.tech mail is handled by 20 alt2.aspmx.l.google.com.
```

**Características:**
- Formato legible para humanos
- Muestra registros A, MX, NS, etc.
- Sin estructura JSON

---

### 2.5 Traceroute (`.txt`)

**Formato:** Texto plano con saltos de red

**Ejemplo:**
```txt
traceroute to kopernicus.tech (66.97.42.227), 30 hops max, 60 byte packets
 1  192.168.0.1 (192.168.0.1)  5.203 ms  4.207 ms  4.129 ms
 2  10.42.64.1 (10.42.64.1)  9.512 ms  16.778 ms  18.606 ms
 3  100.72.8.130 (100.72.8.130)  9.929 ms  9.239 ms  9.174 ms
 4  192.168.65.239 (192.168.65.239)  10.582 ms  10.527 ms  9.909 ms
 5  * * *
 6  * * *
 7  * * *
 8  100.72.9.57 (100.72.9.57)  10.278 ms  14.381 ms  14.237 ms
 9  * * *
10  * * *
11  200.0.17.131 (200.0.17.131)  10.557 ms  14.589 ms  14.176 ms
12  * * *
13  host61.181-96-114.telecom.net.ar (181.96.114.61)  20.426 ms  17.994 ms host75.181-96-114.telecom.net.ar (181.96.114.75)  17.932 ms
14  host65.181-96-71.telecom.net.ar (181.96.71.65)  18.323 ms host67.181-96-71.telecom.net.ar (181.96.71.67)  21.722 ms host65.181-96-71.telecom.net.ar (181.96.71.65)  19.265 ms
15  host206.181-15-45.telecom.net.ar (181.15.45.206)  143.714 ms  146.288 ms  150.803 ms
16  vps-1889901-x.dattaweb.com (66.97.42.227)  151.231 ms  146.278 ms  155.246 ms
```

**Características:**
- Línea de encabezado con destino, max hops, tamaño de paquete
- Cada línea = 1 salto (hop)
- Formato: `hop_number  hostname (IP)  tiempo1 ms  tiempo2 ms  tiempo3 ms`
- `* * *` indica timeout (router no responde ICMP)
- Útil para mapeo de red y detección de firewall

---

## 3. OSINT TOOLS

### 3.1 Shodan (`.json`)

**Formato:** JSON con información de servicios expuestos en Internet

**Ejemplo (simplificado):**
```json
{
  "query": "hostname:example.com",
  "total": 12,
  "matches": [
    {
      "ip_str": "192.0.2.1",
      "port": 443,
      "transport": "tcp",
      "product": "nginx",
      "version": "1.18.0",
      "os": "Linux",
      "hostnames": ["example.com", "www.example.com"],
      "location": {
        "country_code": "US",
        "country_name": "United States",
        "city": "San Francisco"
      },
      "org": "Example Hosting LLC",
      "isp": "Example ISP",
      "asn": "AS12345",
      "ssl": {
        "cert": {
          "issued": "2023-01-15T00:00:00",
          "expires": "2024-01-15T23:59:59",
          "subject": {
            "CN": "example.com"
          },
          "issuer": {
            "CN": "Let's Encrypt Authority X3"
          }
        }
      },
      "vulns": ["CVE-2021-44228"],
      "tags": ["cloud"]
    }
  ]
}
```

**Características:**
- **query:** Query utilizado
- **total:** Total de resultados
- **matches:** Array de servicios encontrados
  - **ip_str:** IP del host
  - **port:** Puerto
  - **product/version:** Software y versión
  - **hostnames:** Dominios asociados
  - **location:** Geolocalización
  - **ssl:** Información de certificados
  - **vulns:** CVEs detectados
  - **org/isp/asn:** Información de proveedor

---

### 3.2 Censys (`.json`)

**Formato:** JSON similar a Shodan, con información de hosts y certificados

**Ejemplo (simplificado):**
```json
{
  "status": "ok",
  "results": [
    {
      "ip": "192.0.2.1",
      "protocols": ["443/https", "80/http"],
      "location": {
        "country": "United States",
        "city": "San Francisco"
      },
      "autonomous_system": {
        "asn": 12345,
        "name": "EXAMPLE-AS"
      },
      "services": [
        {
          "port": 443,
          "service_name": "HTTPS",
          "certificate": {
            "parsed": {
              "subject_dn": "CN=example.com",
              "issuer_dn": "C=US, O=Let's Encrypt",
              "validity": {
                "start": "2023-01-15T00:00:00Z",
                "end": "2024-01-15T23:59:59Z"
              }
            }
          }
        }
      ]
    }
  ]
}
```

**Características:**
- Enfoque en certificados SSL/TLS
- Información detallada de servicios por puerto
- Metadata de ASN y geolocalización

---

### 3.3 TheHarvester (`.json`)

**Formato:** JSON con emails, hosts, IPs, URLs

**Ejemplo:**
```json
{
  "hosts": [
    "www.example.com",
    "mail.example.com",
    "api.example.com"
  ],
  "emails": [
    "admin@example.com",
    "contact@example.com",
    "support@example.com"
  ],
  "ips": [
    "192.0.2.1",
    "192.0.2.2"
  ],
  "urls": [
    "https://www.example.com",
    "https://api.example.com/v1"
  ],
  "asns": [
    "AS12345"
  ],
  "shodan_urls": [],
  "interesting_urls": [
    "https://example.com/admin",
    "https://example.com/login"
  ]
}
```

**Características:**
- **hosts:** Subdominios encontrados
- **emails:** Direcciones de correo
- **ips:** IPs asociadas
- **urls:** URLs descubiertas
- **interesting_urls:** URLs potencialmente sensibles (admin, login, etc.)

---

### 3.4 Hunter.io (`.json`)

**Formato:** JSON con emails y su metadata

**Ejemplo:**
```json
{
  "data": {
    "domain": "example.com",
    "disposable": false,
    "webmail": false,
    "accept_all": false,
    "pattern": "{first}.{last}",
    "organization": "Example Inc",
    "emails": [
      {
        "value": "john.doe@example.com",
        "type": "personal",
        "confidence": 95,
        "sources": [
          {
            "domain": "linkedin.com",
            "uri": "https://linkedin.com/in/johndoe",
            "extracted_on": "2023-05-20"
          }
        ],
        "first_name": "John",
        "last_name": "Doe",
        "position": "Software Engineer",
        "seniority": "senior",
        "department": "engineering"
      }
    ]
  }
}
```

**Características:**
- **pattern:** Patrón de emails de la organización
- **confidence:** Nivel de confianza (0-100)
- **sources:** Fuentes donde se encontró el email
- **position/department:** Información laboral

---

### 3.5 Wayback Machine (`.txt`)

**Formato:** Lista de URLs históricas

**Ejemplo:**
```txt
https://web.archive.org/web/20200101000000/http://example.com/
https://web.archive.org/web/20200615120000/http://example.com/admin
https://web.archive.org/web/20210301000000/http://example.com/api/v1
https://web.archive.org/web/20220801000000/http://example.com/backup.sql
```

**Características:**
- URLs con timestamp de captura
- Útil para encontrar rutas antiguas, backups, endpoints deprecados

---

### 3.6 LinkedIn Enum (`.txt`)

**Formato:** Lista de perfiles/empleados

**Ejemplo:**
```txt
John Doe - Software Engineer - john.doe@example.com
Jane Smith - Security Analyst - jane.smith@example.com
Bob Johnson - DevOps Lead - bob.johnson@example.com
```

**Características:**
- Información de empleados
- Nombres, posiciones, posibles emails

---

## 4. WEB RECONNAISSANCE

### 4.1 WhatWeb (`.json`)

**Formato:** JSON con tecnologías detectadas

**Ejemplo:**
```json
[
  {
    "target": "https://example.com",
    "http_status": 200,
    "request_config": {
      "headers": {},
      "max_redirects": 10
    },
    "plugins": {
      "HTTPServer": {
        "string": ["nginx/1.18.0"]
      },
      "UncommonHeaders": {
        "x-powered-by": ["PHP/7.4.3"],
        "x-frame-options": ["SAMEORIGIN"]
      },
      "Country": {
        "string": ["UNITED STATES"]
      },
      "IP": {
        "string": ["192.0.2.1"]
      },
      "HTML5": {},
      "Script": {
        "string": ["text/javascript"]
      },
      "JQuery": {
        "version": ["3.5.1"]
      },
      "Bootstrap": {
        "version": ["4.5.0"]
      },
      "Google-Analytics": {
        "account": ["UA-12345678-1"]
      },
      "Cookies": {
        "session": ["PHPSESSID"]
      },
      "Title": {
        "string": ["Example Website"]
      },
      "X-Powered-By": {
        "string": ["PHP/7.4.3"]
      }
    }
  }
]
```

**Características:**
- **plugins:** Tecnologías detectadas (CMS, frameworks, librerías)
- **HTTPServer:** Servidor web y versión
- **X-Powered-By:** Lenguaje/framework backend
- **Country/IP:** Información de hosting
- Útil para fingerprinting de stack tecnológico

---

### 4.2 Web Crawling - Gospider/Hakrawler (`.txt`)

**Formato:** Lista de URLs encontradas

**Ejemplo:**
```txt
https://example.com/
https://example.com/about
https://example.com/contact
https://example.com/api/v1/users
https://example.com/api/v1/products
https://example.com/admin/login
https://example.com/static/js/app.js
https://example.com/static/css/style.css
https://example.com/uploads/document.pdf
```

**Características:**
- Lista plana de URLs descubiertas
- Incluye paths, archivos estáticos, endpoints API
- Puede contener duplicados

---

## 5. OTROS

### 5.1 WHOIS (`.txt`)

**Formato:** Texto plano con información de registro de dominio

**Ejemplo:**
```txt
Domain Name: KOPERNICUS.TECH
Registry Domain ID: D191163699-CNIC
Registrar WHOIS Server: whois.donweb.com
Registrar URL: https://www.donweb.com
Updated Date: 2025-06-22T03:21:34.0Z
Creation Date: 2020-06-24T10:15:05.0Z
Registry Expiry Date: 2026-06-24T23:59:59.0Z
Registrar: Dattatec.com SRL
Registrar IANA ID: 1388
Domain Status: ok https://icann.org/epp#ok
Name Server: NS9.HOSTMAR.COM
Name Server: NS10.HOSTMAR.COM
DNSSEC: unsigned
Registrar Abuse Contact Email: abuse@donweb.com
Registrar Abuse Contact Phone: +54.1152388127
URL of the ICANN Whois Inaccuracy Complaint Form: https://www.icann.org/wicf/
>>> Last update of WHOIS database: 2025-12-09T20:06:09.0Z <<<

For more information on Whois status codes, please visit https://icann.org/epp

The Whois and RDAP services are provided by CentralNic, and contain
information pertaining to Internet domain names registered by our
customers. By using this service you are agreeing (1) not to use any
information presented here for any purpose other than determining
ownership of domain names...
```

**Características:**
- **Creation Date:** Fecha de registro del dominio
- **Registry Expiry Date:** Fecha de expiración
- **Registrar:** Registrador del dominio
- **Name Server:** Servidores DNS autoritativos
- **Domain Status:** Estado del dominio (ok, clientTransferProhibited, etc.)
- **Registrar Abuse Contact:** Contacto para reportar abuso
- Incluye disclaimers legales al final

---

### 5.2 Google Dorks (`.txt`)

**Formato:** Lista de URLs encontradas mediante Google Dorks

**Ejemplo:**
```txt
https://example.com/admin/config.php
https://example.com/backup/db_backup_2023.sql
https://example.com/.env
https://example.com/phpinfo.php
https://files.example.com/confidential/report.pdf
```

**Características:**
- URLs potencialmente sensibles
- Archivos de configuración, backups, información confidencial
- Obtenido mediante búsquedas avanzadas en Google

---

### 5.3 Secrets Detection - Gitleaks/Trufflehog (`.json`)

**Formato:** JSON con secretos detectados (API keys, passwords, tokens)

**Ejemplo:**
```json
[
  {
    "Description": "AWS Access Key",
    "StartLine": 15,
    "EndLine": 15,
    "StartColumn": 20,
    "EndColumn": 40,
    "Match": "AKIAIOSFODNN7EXAMPLE",
    "Secret": "AKIAIOSFODNN7EXAMPLE",
    "File": "config/aws.js",
    "Commit": "a1b2c3d4e5f6",
    "Entropy": 4.5,
    "Author": "john.doe@example.com",
    "Date": "2023-05-20T10:30:00Z",
    "Message": "Add AWS configuration",
    "Tags": ["key", "AWS"],
    "RuleID": "aws-access-token"
  },
  {
    "Description": "Generic API Key",
    "Match": "api_key=sk_live_1234567890abcdef",
    "Secret": "sk_live_1234567890abcdef",
    "File": ".env",
    "Tags": ["key", "API"],
    "RuleID": "generic-api-key"
  }
]
```

**Características:**
- **Description:** Tipo de secreto detectado
- **Match/Secret:** Valor del secreto encontrado
- **File:** Archivo donde se encontró
- **StartLine/EndLine:** Ubicación en el archivo
- **Entropy:** Nivel de entropía (aleatoriedad)
- **RuleID:** Regla que detectó el secreto
- **Tags:** Categorías

---

## 📊 Resumen por Formato

### Archivos TXT (12 herramientas):
- Subfinder, Amass, Assetfinder, Sublist3r, Findomain, crt.sh
- DNSEnum, Fierce, Host/NSLookup, Traceroute
- Wayback Machine, LinkedIn Enum
- Web Crawling (Gospider/Hakrawler)
- WHOIS, Google Dorks

**Características comunes:**
- Formato legible para humanos
- Sin estructura JSON
- Generalmente listas simples o texto con secciones
- Fácil de parsear con regex o split de líneas

### Archivos JSON (7 herramientas):
- DNSRecon
- Shodan, Censys, TheHarvester, Hunter.io
- WhatWeb
- Secrets Detection (Gitleaks/Trufflehog)

**Características comunes:**
- Estructura de datos bien definida
- Fácil de parsear programáticamente
- Incluyen metadata adicional
- Mejor para procesamiento automatizado

---

## 🛠️ Consideraciones para Parsers

### Para archivos TXT:
1. **Filtrado de banners:** Algunas herramientas incluyen banners ASCII o mensajes de versión
2. **Líneas vacías:** Pueden existir líneas en blanco que deben ignorarse
3. **Comentarios:** Algunas herramientas incluyen comentarios con `#` o `//`
4. **Encoding:** Verificar UTF-8, algunos archivos pueden usar ASCII

### Para archivos JSON:
1. **Validación:** Verificar que el JSON sea válido antes de parsear
2. **Campos opcionales:** No todos los campos están siempre presentes
3. **Arrays vacíos:** Manejar casos donde no hay resultados
4. **Tipos de datos:** Validar tipos (strings, números, booleanos)
5. **JSON Lines (.jsonl):** Algunas herramientas (Nuclei) usan JSONL (un JSON por línea)

---

## 📌 Notas Adicionales

1. **Duplicados:** Es común que diferentes herramientas encuentren los mismos subdominios/IPs
2. **False Positives:** Especialmente en web crawling y subdomain enum
3. **Rate Limiting:** APIs como Shodan, Censys, Hunter.io tienen límites
4. **Permisos:** WHOIS y algunas APIs pueden requerir autenticación
5. **Timeouts:** DNS queries y traceroute pueden tener timeouts (líneas con `* * *`)

---

**Fin del documento**


**Fecha:** 10 de Diciembre 2025  
**Entorno:** DEV4-IMPROVEMENTS  
**Propósito:** Documentar los formatos de salida de todas las herramientas de reconocimiento

---

## 📋 Tabla de Contenidos

1. [Subdomain Enumeration](#1-subdomain-enumeration)
2. [DNS Enumeration](#2-dns-enumeration)
3. [OSINT Tools](#3-osint-tools)
4. [Web Reconnaissance](#4-web-reconnaissance)
5. [Otros](#5-otros)

---

## 1. SUBDOMAIN ENUMERATION

### 1.1 Subfinder (`.txt`)

**Formato:** Lista simple de subdominios, un subdominio por línea

**Ejemplo:**
```txt
www.fravega.kopernicus.tech
assurant.kopernicus.tech
www.assurant.kopernicus.tech
www.kopernicus.tech
macro.kopernicus.tech
www.macro.kopernicus.tech
kopernicus.tech
fravega.kopernicus.tech
```

**Características:**
- Sin encabezados ni metadata
- Sin ordenamiento específico
- Puede contener duplicados
- Puede incluir subdominios con y sin "www"

---

### 1.2 Amass (`.txt`)

**Formato:** Similar a Subfinder, lista simple de subdominios

**Ejemplo:**
```txt
kopernicus.tech
uy.kopernicus.tech
cl.kopernicus.tech
```

**Características:**
- Lista plana sin metadata
- Ordenamiento aleatorio
- Usualmente menos resultados pero más precisos

---

### 1.3 Assetfinder (`.txt`)

**Formato:** Lista simple de dominios/subdominios

**Ejemplo:**
```txt
kopernicus.tech
uy.kopernicus.tech
cl.kopernicus.tech
```

**Características:**
- Formato idéntico a Amass
- Sin metadata adicional
- Puede incluir dominios relacionados

---

### 1.4 Sublist3r (`.txt`)

**Formato:** Lista de subdominios con posibles banners

**Ejemplo:**
```txt
www.alquilersura.com.uy
cpanel.alquilersura.com.uy
cpcalendars.alquilersura.com.uy
cpcontacts.alquilersura.com.uy
mail.alquilersura.com.uy
webdisk.alquilersura.com.uy
webmail.alquilersura.com.uy
```

**Características:**
- Lista simple sin banners (cuando se procesa correctamente)
- Puede incluir servicios comunes (mail, cpanel, webdisk, etc.)
- Un subdominio por línea

---

### 1.5 Findomain (`.txt`)

**Formato:** Lista simple de subdominios

**Ejemplo:**
```txt
api.example.com
mail.example.com
www.example.com
staging.example.com
```

**Características:**
- Formato plano
- Sin metadata
- Usualmente incluye subdominios de APIs y staging

---

### 1.6 crt.sh (`.txt`)

**Formato:** Lista de subdominios obtenidos desde Certificate Transparency logs

**Ejemplo:**
```txt
*.example.com
example.com
www.example.com
mail.example.com
api.example.com
```

**Características:**
- Puede incluir wildcards (`*.example.com`)
- Basado en certificados SSL/TLS emitidos
- Generalmente muy completo para dominios con HTTPS

---

## 2. DNS ENUMERATION

### 2.1 DNSRecon (`.json`)

**Formato:** JSON array con objetos estructurados por tipo de registro DNS

**Ejemplo:**
```json
[
    {
        "arguments": "/usr/bin/dnsrecon -d kopernicus.tech -t std -j output.json",
        "date": "2025-12-09 15:01:48.826325",
        "type": "ScanInfo"
    },
    {
        "address": "200.58.97.2",
        "domain": "kopernicus.tech",
        "mname": "ns9.hostmar.com",
        "type": "SOA"
    },
    {
        "Version": "root@dnsded01.dattaweb.com)\"",
        "address": "200.58.97.2",
        "domain": "kopernicus.tech",
        "recursive": "True",
        "target": "ns9.hostmar.com",
        "type": "NS"
    },
    {
        "address": "192.178.223.27",
        "domain": "kopernicus.tech",
        "exchange": "aspmx2.googlemail.com",
        "type": "MX"
    },
    {
        "address": "66.97.42.227",
        "domain": "kopernicus.tech",
        "name": "kopernicus.tech",
        "type": "A"
    },
    {
        "domain": "kopernicus.tech",
        "name": "kopernicus.tech",
        "strings": "v=spf1 include:_spf.mailersend.net include:_spf.google.com ~all",
        "type": "TXT"
    },
    {
        "domain": "kopernicus.tech",
        "name": "_dmarc.kopernicus.tech",
        "strings": "v=DMARC1; p=quarantine; rua=mailto:abuso@kopernicus.tech",
        "type": "TXT"
    }
]
```

**Características:**
- **ScanInfo:** Metadata de la ejecución (comando, fecha)
- **SOA:** Start of Authority (servidor DNS autorizado, mname)
- **NS:** Name Servers (servidores DNS)
- **MX:** Mail Exchange servers (servidores de correo)
- **A/AAAA:** Registros de dirección IP (IPv4/IPv6)
- **TXT:** Registros de texto (SPF, DMARC, verificación de dominio)
- **CNAME:** Canonical names (alias)

**Campos comunes:**
- `type`: Tipo de registro DNS
- `domain`: Dominio consultado
- `address`: Dirección IP asociada
- `name`: Nombre del registro
- `strings`: Contenido de registros TXT

---

### 2.2 DNSEnum (`.txt`)

**Formato:** Texto plano con resultados estructurados por secciones

**Ejemplo:**
```txt
dnsenum.pl VERSION:1.2.6

-----   example.com   -----

Host's addresses:
__________________

example.com.                             5       IN      A        192.0.2.1

Name Servers:
______________

ns1.example.com.                         5       IN      A        192.0.2.10
ns2.example.com.                         5       IN      A        192.0.2.11

Mail (MX) Servers:
___________________

mail.example.com.                        10      IN      A        192.0.2.20

Trying Zone Transfers and getting Bind Versions:
_________________________________________________

Trying Zone Transfer for example.com on ns1.example.com ...
AXFR record query failed: NOTAUTH
```

**Características:**
- Formato de texto con secciones claramente delimitadas
- Incluye registros A, NS, MX
- Intenta transferencias de zona (AXFR)
- Puede incluir errores y warnings

---

### 2.3 Fierce (`.txt`)

**Formato:** Texto con análisis estructurado y diccionario de IP cercanas

**Ejemplo:**
```txt
NS: ns4711.banahosting.com. ns4710.banahosting.com.
SOA: ns4710.banahosting.com. (216.246.112.35)
Zone: failure
Wildcard: failure
Found: ftp.alquilersura.com.uy. (216.246.112.39)
Nearby:
{'216.246.112.34': 'single-4710.banahosting.com.',
 '216.246.112.35': 'ns4710.banahosting.com.',
 '216.246.112.36': 'ns4711.banahosting.com.',
 '216.246.112.37': 'single-4710.banahosting.com.',
 '216.246.112.38': 'single-4710.banahosting.com.',
 '216.246.112.39': 'single-4710.banahosting.com.',
 '216.246.112.40': 'single-4710.banahosting.com.',
 '216.246.112.41': 'single-4710.banahosting.com.',
 '216.246.112.42': 'single-4710.banahosting.com.',
 '216.246.112.43': 'single-4710.banahosting.com.',
 '216.246.112.44': 'single-4710.banahosting.com.'}
Found: mail.alquilersura.com.uy. (216.246.112.39)
```

**Características:**
- **NS:** Name servers del dominio
- **SOA:** Start of Authority con IP
- **Zone:** Resultado de intento de transferencia de zona
- **Wildcard:** Detección de wildcard DNS
- **Found:** Subdominios descubiertos con IPs
- **Nearby:** Diccionario Python de IPs adyacentes y sus hostnames

---

### 2.4 Host/NSLookup (`.txt`)

**Formato:** Texto plano con resultados de consulta DNS

**Ejemplo:**
```txt
kopernicus.tech has address 66.97.42.227
kopernicus.tech mail is handled by 10 aspmx.l.google.com.
kopernicus.tech mail is handled by 20 alt1.aspmx.l.google.com.
kopernicus.tech mail is handled by 20 alt2.aspmx.l.google.com.
```

**Características:**
- Formato legible para humanos
- Muestra registros A, MX, NS, etc.
- Sin estructura JSON

---

### 2.5 Traceroute (`.txt`)

**Formato:** Texto plano con saltos de red

**Ejemplo:**
```txt
traceroute to kopernicus.tech (66.97.42.227), 30 hops max, 60 byte packets
 1  192.168.0.1 (192.168.0.1)  5.203 ms  4.207 ms  4.129 ms
 2  10.42.64.1 (10.42.64.1)  9.512 ms  16.778 ms  18.606 ms
 3  100.72.8.130 (100.72.8.130)  9.929 ms  9.239 ms  9.174 ms
 4  192.168.65.239 (192.168.65.239)  10.582 ms  10.527 ms  9.909 ms
 5  * * *
 6  * * *
 7  * * *
 8  100.72.9.57 (100.72.9.57)  10.278 ms  14.381 ms  14.237 ms
 9  * * *
10  * * *
11  200.0.17.131 (200.0.17.131)  10.557 ms  14.589 ms  14.176 ms
12  * * *
13  host61.181-96-114.telecom.net.ar (181.96.114.61)  20.426 ms
14  host65.181-96-71.telecom.net.ar (181.96.71.65)  18.323 ms
15  host206.181-15-45.telecom.net.ar (181.15.45.206)  143.714 ms
16  vps-1889901-x.dattaweb.com (66.97.42.227)  151.231 ms
```

**Características:**
- Línea de encabezado con destino, max hops, tamaño de paquete
- Cada línea = 1 salto (hop)
- Formato: `hop_number  hostname (IP)  tiempo1 ms  tiempo2 ms  tiempo3 ms`
- `* * *` indica timeout (router no responde ICMP)
- Útil para mapeo de red y detección de firewall

---

## 3. OSINT TOOLS

### 3.1 Shodan (`.json`)

**Formato:** JSON con información de servicios expuestos en Internet

**Ejemplo:**
```json
{
  "query": "hostname:example.com",
  "total": 12,
  "matches": [
    {
      "ip_str": "192.0.2.1",
      "port": 443,
      "transport": "tcp",
      "product": "nginx",
      "version": "1.18.0",
      "os": "Linux",
      "hostnames": ["example.com", "www.example.com"],
      "location": {
        "country_code": "US",
        "country_name": "United States",
        "city": "San Francisco"
      },
      "org": "Example Hosting LLC",
      "isp": "Example ISP",
      "asn": "AS12345",
      "ssl": {
        "cert": {
          "issued": "2023-01-15T00:00:00",
          "expires": "2024-01-15T23:59:59",
          "subject": {
            "CN": "example.com"
          },
          "issuer": {
            "CN": "Let's Encrypt Authority X3"
          }
        }
      },
      "vulns": ["CVE-2021-44228"],
      "tags": ["cloud"]
    }
  ]
}
```

**Características:**
- **query:** Query utilizado
- **total:** Total de resultados
- **matches:** Array de servicios encontrados
  - **ip_str:** IP del host
  - **port:** Puerto
  - **product/version:** Software y versión
  - **hostnames:** Dominios asociados
  - **location:** Geolocalización
  - **ssl:** Información de certificados
  - **vulns:** CVEs detectados
  - **org/isp/asn:** Información de proveedor

---

### 3.2 Censys (`.json`)

**Formato:** JSON similar a Shodan, con información de hosts y certificados

**Ejemplo:**
```json
{
  "status": "ok",
  "results": [
    {
      "ip": "192.0.2.1",
      "protocols": ["443/https", "80/http"],
      "location": {
        "country": "United States",
        "city": "San Francisco"
      },
      "autonomous_system": {
        "asn": 12345,
        "name": "EXAMPLE-AS"
      },
      "services": [
        {
          "port": 443,
          "service_name": "HTTPS",
          "certificate": {
            "parsed": {
              "subject_dn": "CN=example.com",
              "issuer_dn": "C=US, O=Let's Encrypt",
              "validity": {
                "start": "2023-01-15T00:00:00Z",
                "end": "2024-01-15T23:59:59Z"
              }
            }
          }
        }
      ]
    }
  ]
}
```

**Características:**
- Enfoque en certificados SSL/TLS
- Información detallada de servicios por puerto
- Metadata de ASN y geolocalización

---

### 3.3 TheHarvester (`.json`)

**Formato:** JSON con emails, hosts, IPs, URLs

**Ejemplo:**
```json
{
  "hosts": [
    "www.example.com",
    "mail.example.com",
    "api.example.com"
  ],
  "emails": [
    "admin@example.com",
    "contact@example.com",
    "support@example.com"
  ],
  "ips": [
    "192.0.2.1",
    "192.0.2.2"
  ],
  "urls": [
    "https://www.example.com",
    "https://api.example.com/v1"
  ],
  "asns": [
    "AS12345"
  ],
  "shodan_urls": [],
  "interesting_urls": [
    "https://example.com/admin",
    "https://example.com/login"
  ]
}
```

**Características:**
- **hosts:** Subdominios encontrados
- **emails:** Direcciones de correo
- **ips:** IPs asociadas
- **urls:** URLs descubiertas
- **interesting_urls:** URLs potencialmente sensibles

---

### 3.4 Hunter.io (`.json`)

**Formato:** JSON con emails y su metadata

**Ejemplo:**
```json
{
  "data": {
    "domain": "example.com",
    "disposable": false,
    "webmail": false,
    "accept_all": false,
    "pattern": "{first}.{last}",
    "organization": "Example Inc",
    "emails": [
      {
        "value": "john.doe@example.com",
        "type": "personal",
        "confidence": 95,
        "sources": [
          {
            "domain": "linkedin.com",
            "uri": "https://linkedin.com/in/johndoe",
            "extracted_on": "2023-05-20"
          }
        ],
        "first_name": "John",
        "last_name": "Doe",
        "position": "Software Engineer",
        "seniority": "senior",
        "department": "engineering"
      }
    ]
  }
}
```

**Características:**
- **pattern:** Patrón de emails de la organización
- **confidence:** Nivel de confianza (0-100)
- **sources:** Fuentes donde se encontró el email
- **position/department:** Información laboral

---

### 3.5 Wayback Machine (`.txt`)

**Formato:** Lista de URLs históricas

**Ejemplo:**
```txt
https://web.archive.org/web/20200101000000/http://example.com/
https://web.archive.org/web/20200615120000/http://example.com/admin
https://web.archive.org/web/20210301000000/http://example.com/api/v1
https://web.archive.org/web/20220801000000/http://example.com/backup.sql
```

**Características:**
- URLs con timestamp de captura
- Útil para encontrar rutas antiguas, backups, endpoints deprecados

---

### 3.6 LinkedIn Enum (`.txt`)

**Formato:** Lista de perfiles/empleados

**Ejemplo:**
```txt
John Doe - Software Engineer - john.doe@example.com
Jane Smith - Security Analyst - jane.smith@example.com
Bob Johnson - DevOps Lead - bob.johnson@example.com
```

**Características:**
- Información de empleados
- Nombres, posiciones, posibles emails

---

## 4. WEB RECONNAISSANCE

### 4.1 WhatWeb (`.json`)

**Formato:** JSON con tecnologías detectadas

**Ejemplo:**
```json
[
  {
    "target": "https://example.com",
    "http_status": 200,
    "request_config": {
      "headers": {},
      "max_redirects": 10
    },
    "plugins": {
      "HTTPServer": {
        "string": ["nginx/1.18.0"]
      },
      "UncommonHeaders": {
        "x-powered-by": ["PHP/7.4.3"],
        "x-frame-options": ["SAMEORIGIN"]
      },
      "Country": {
        "string": ["UNITED STATES"]
      },
      "IP": {
        "string": ["192.0.2.1"]
      },
      "HTML5": {},
      "Script": {
        "string": ["text/javascript"]
      },
      "JQuery": {
        "version": ["3.5.1"]
      },
      "Bootstrap": {
        "version": ["4.5.0"]
      },
      "Google-Analytics": {
        "account": ["UA-12345678-1"]
      },
      "Cookies": {
        "session": ["PHPSESSID"]
      },
      "Title": {
        "string": ["Example Website"]
      },
      "X-Powered-By": {
        "string": ["PHP/7.4.3"]
      }
    }
  }
]
```

**Características:**
- **plugins:** Tecnologías detectadas (CMS, frameworks, librerías)
- **HTTPServer:** Servidor web y versión
- **X-Powered-By:** Lenguaje/framework backend
- **Country/IP:** Información de hosting
- Útil para fingerprinting de stack tecnológico

---

### 4.2 Web Crawling - Gospider/Hakrawler (`.txt`)

**Formato:** Lista de URLs encontradas

**Ejemplo:**
```txt
https://example.com/
https://example.com/about
https://example.com/contact
https://example.com/api/v1/users
https://example.com/api/v1/products
https://example.com/admin/login
https://example.com/static/js/app.js
https://example.com/static/css/style.css
https://example.com/uploads/document.pdf
```

**Características:**
- Lista plana de URLs descubiertas
- Incluye paths, archivos estáticos, endpoints API
- Puede contener duplicados

---

## 5. OTROS

### 5.1 WHOIS (`.txt`)

**Formato:** Texto plano con información de registro de dominio

**Ejemplo:**
```txt
Domain Name: KOPERNICUS.TECH
Registry Domain ID: D191163699-CNIC
Registrar WHOIS Server: whois.donweb.com
Registrar URL: https://www.donweb.com
Updated Date: 2025-06-22T03:21:34.0Z
Creation Date: 2020-06-24T10:15:05.0Z
Registry Expiry Date: 2026-06-24T23:59:59.0Z
Registrar: Dattatec.com SRL
Registrar IANA ID: 1388
Domain Status: ok https://icann.org/epp#ok
Name Server: NS9.HOSTMAR.COM
Name Server: NS10.HOSTMAR.COM
DNSSEC: unsigned
Registrar Abuse Contact Email: abuse@donweb.com
Registrar Abuse Contact Phone: +54.1152388127
```

**Características:**
- **Creation Date:** Fecha de registro del dominio
- **Registry Expiry Date:** Fecha de expiración
- **Registrar:** Registrador del dominio
- **Name Server:** Servidores DNS autoritativos
- **Domain Status:** Estado del dominio

---

### 5.2 Google Dorks (`.txt`)

**Formato:** Lista de URLs encontradas mediante Google Dorks

**Ejemplo:**
```txt
https://example.com/admin/config.php
https://example.com/backup/db_backup_2023.sql
https://example.com/.env
https://example.com/phpinfo.php
https://files.example.com/confidential/report.pdf
```

**Características:**
- URLs potencialmente sensibles
- Archivos de configuración, backups, información confidencial

---

### 5.3 Secrets Detection - Gitleaks/Trufflehog (`.json`)

**Formato:** JSON con secretos detectados

**Ejemplo:**
```json
[
  {
    "Description": "AWS Access Key",
    "StartLine": 15,
    "EndLine": 15,
    "StartColumn": 20,
    "EndColumn": 40,
    "Match": "AKIAIOSFODNN7EXAMPLE",
    "Secret": "AKIAIOSFODNN7EXAMPLE",
    "File": "config/aws.js",
    "Commit": "a1b2c3d4e5f6",
    "Entropy": 4.5,
    "Author": "john.doe@example.com",
    "Date": "2023-05-20T10:30:00Z",
    "Message": "Add AWS configuration",
    "Tags": ["key", "AWS"],
    "RuleID": "aws-access-token"
  }
]
```

**Características:**
- **Description:** Tipo de secreto detectado
- **Match/Secret:** Valor del secreto encontrado
- **File:** Archivo donde se encontró
- **Entropy:** Nivel de entropía
- **RuleID:** Regla que detectó el secreto

---

## 📊 Resumen por Formato

### Archivos TXT (12 herramientas):
- Subfinder, Amass, Assetfinder, Sublist3r, Findomain, crt.sh
- DNSEnum, Fierce, Host/NSLookup, Traceroute
- Wayback Machine, LinkedIn Enum, Web Crawling
- WHOIS, Google Dorks

**Características comunes:**
- Formato legible para humanos
- Sin estructura JSON
- Generalmente listas simples o texto con secciones
- Fácil de parsear con regex o split de líneas

### Archivos JSON (7 herramientas):
- DNSRecon
- Shodan, Censys, TheHarvester, Hunter.io
- WhatWeb
- Secrets Detection (Gitleaks/Trufflehog)

**Características comunes:**
- Estructura de datos bien definida
- Fácil de parsear programáticamente
- Incluyen metadata adicional
- Mejor para procesamiento automatizado

---

## 🛠️ Consideraciones para Parsers

### Para archivos TXT:
1. **Filtrado de banners:** Algunas herramientas incluyen banners ASCII
2. **Líneas vacías:** Pueden existir líneas en blanco que deben ignorarse
3. **Comentarios:** Algunas herramientas incluyen comentarios
4. **Encoding:** Verificar UTF-8

### Para archivos JSON:
1. **Validación:** Verificar que el JSON sea válido antes de parsear
2. **Campos opcionales:** No todos los campos están siempre presentes
3. **Arrays vacíos:** Manejar casos donde no hay resultados
4. **Tipos de datos:** Validar tipos (strings, números, booleanos)

---

## 📌 Notas Adicionales

1. **Duplicados:** Es común que diferentes herramientas encuentren los mismos subdominios
2. **False Positives:** Especialmente en web crawling y subdomain enum
3. **Rate Limiting:** APIs como Shodan, Censys, Hunter.io tienen límites
4. **Permisos:** WHOIS y algunas APIs pueden requerir autenticación
5. **Timeouts:** DNS queries pueden tener timeouts

---

**Fin del documento**


