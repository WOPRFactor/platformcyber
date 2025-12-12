# 🔍 HERRAMIENTAS DE SCANNING - FORMATOS DE ARCHIVOS

**Fecha:** 2025-12-10  
**Ambiente:** DEV4-Improvements

---

## 📊 RESUMEN EJECUTIVO

Este documento lista todas las herramientas de **SCANNING** y **ENUMERATION** implementadas, el tipo de archivo que generan y ejemplos detallados de formato basados en el código fuente y documentación del proyecto.

**Total herramientas:** 27 (4 Scanning + 23 Enumeration)  
**Parsers existentes:** 1 (Nmap - usado por 9 herramientas de enumeration)  
**Parsers faltantes:** 18 herramientas únicas que necesitan parser nuevo

---

## 🔴 PORT SCANNING (`/scans/`)

### 1. **Nmap**
- **Archivo generado:** `nmap_{scan_id}.xml` + `nmap_{scan_id}.txt` + `nmap_{scan_id}.gnmap`
- **Formato principal:** XML (`.xml`)
- **Formato secundario:** TXT (`.txt`), GNMAP (`.gnmap`)
- **Parser existente:** ✅ `scanning/nmap_parser.py`
- **Ejemplo XML:**
```xml
<?xml version="1.0"?>
<nmaprun>
  <host>
    <address addr="192.168.1.1" addrtype="ipv4"/>
    <ports>
      <port protocol="tcp" portid="22">
        <state state="open"/>
        <service name="ssh" product="OpenSSH" version="8.2"/>
      </port>
    </ports>
  </host>
</nmaprun>
```

### 2. **RustScan**
- **Archivo generado:** `rustscan_{scan_id}.txt`
- **Formato:** TXT (`.txt`) - Formato grepeable similar a Nmap
- **Parser existente:** ❌ NO (pero hay `RustScanParser` en utils)
- **Ubicación código:** `services/scanning/tools/rustscan_scanner.py`
- **Ejemplo formato completo:**
```
# Nmap 7.80 scan initiated Tue Dec 10 12:00:00 2024 as: nmap -sV -oN rustscan_123.txt
Nmap scan report for 192.168.1.1
Host is up (0.05s latency).

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.5
80/tcp open  http    Apache httpd 2.4.41
443/tcp open  ssl/http Apache httpd 2.4.41

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
# Nmap done at Tue Dec 10 12:00:05 2024 -- 1 IP address (1 host up) scanned in 5.23 seconds
```
- **Formato alternativo (grepeable):**
```
Host: 192.168.1.1 (up) Ports: 22/open/tcp//ssh///, 80/open/tcp//http///, 443/open/tcp//ssl|http///
```

### 3. **Masscan**
- **Archivo generado:** `masscan_{scan_id}.json`
- **Formato:** JSON (`.json`) - Formato JSON de Masscan
- **Parser existente:** ❌ NO (pero hay `MasscanParser` en utils)
- **Ubicación código:** `services/scanning/tools/masscan_scanner.py` (línea 68: genera `.json`)
- **Ejemplo formato completo:**
```json
[
  {
    "ip": "192.168.1.1",
    "timestamp": 1702214400,
    "ports": [
      {"port": 22, "proto": "tcp"},
      {"port": 80, "proto": "tcp"},
      {"port": 443, "proto": "tcp"}
    ]
  },
  {
    "ip": "192.168.1.2",
    "timestamp": 1702214401,
    "ports": [
      {"port": 22, "proto": "tcp"},
      {"port": 3306, "proto": "tcp"}
    ]
  }
]
```
- **Nota:** Masscan también puede generar formato XML compatible con Nmap, pero el código actual genera JSON.

### 4. **Naabu**
- **Archivo generado:** `naabu_{scan_id}.txt`
- **Formato:** TXT (`.txt`) - Formato simple IP:PUERTO por línea
- **Parser existente:** ❌ NO
- **Ubicación código:** `services/scanning/tools/naabu_scanner.py` (línea 68)
- **Ejemplo formato completo:**
```
192.168.1.1:22
192.168.1.1:80
192.168.1.1:443
192.168.1.1:8080
192.168.1.2:22
192.168.1.2:3306
```
- **Nota:** Naabu también puede generar JSON con flag `-json`, pero el código actual genera TXT simple.

---

## 🟡 ENUMERATION (`/enumeration/`)

### 5. **Enum4linux**
- **Archivo generado:** `enum4linux_{scan_id}.txt`
- **Formato:** TXT (`.txt`) - Output estructurado con secciones claramente delimitadas
- **Parser existente:** ❌ NO
- **Ubicación código:** `services/enumeration/smb_enum.py`
- **Ejemplo formato completo:**
```
Starting enum4linux v0.9.1 on Sun Dec  7 05:20:19 2025

=========================================( Target Information )=========================================
Target ........... 192.168.1.100
Workgroup/Domain .. WORKGROUP
OS ................ Windows 10 Enterprise 19042
Computer .......... TARGET-PC

=========================================( Share Enumeration )=========================================
Share name       Type      Comment
---------       ----      -------
ADMIN$          Disk      Remote Admin
C$              Disk      Default share
IPC$            IPC       Remote IPC
Shared          Disk      Public Share

=========================================( Password Policy Information )=========================================
[+] Attaching to 192.168.1.100...
[+] Trying protocol 139/SMB...
[+] Found domain(s):
   [+] WORKGROUP
   [+] Domain: WORKGROUP

=========================================( Groups on 192.168.1.100 )=========================================
[+] Getting builtin groups:
group:[Administrators] rid:[0x220]
group:[Users] rid:[0x221]
group:[Guests] rid:[0x222]

=========================================( Users on 192.168.1.100 )=========================================
index: 0x1 RID: 0x3f2 acb: 0x00000010 Account: Administrator	Name: (null)
index: 0x2 RID: 0x3f3 acb: 0x00000010 Account: Guest	Name: (null)
index: 0x3 RID: 0x3f4 acb: 0x00000010 Account: user1	Name: User One
```
- **Estructura:** Secciones separadas por líneas de `===`, cada sección tiene información específica (shares, usuarios, grupos, políticas).

### 6. **SMBMap**
- **Archivo generado:** `smbmap_{scan_id}.txt`
- **Formato:** TXT (`.txt`) - Tabla de shares con permisos
- **Parser existente:** ❌ NO
- **Ubicación código:** `services/enumeration/smb_enum.py`
- **Ejemplo formato completo:**
```
[+] IP: 192.168.1.100:445	Name: TARGET-PC                                      
	Disk					Permissions	Comment
	----					-----------	-------
	ADMIN$					READ, WRITE	Remote Admin
	C$						READ, WRITE	Default share
	IPC$					READ ONLY	Remote IPC
	Shared					READ, WRITE	Public Share
	Documents				READ ONLY	User Documents
```
- **Estructura:** Línea de header con IP y nombre, luego tabla con columnas: Disk, Permissions, Comment.

### 7. **SMBClient**
- **Archivo generado:** `smbclient_{scan_id}.txt`
- **Formato:** TXT (`.txt`) - Output interactivo de smbclient
- **Parser existente:** ❌ NO
- **Ubicación código:** `services/enumeration/smb_enum.py`
- **Ejemplo formato completo:**
```
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Mon Jan  1 00:00:00 2024
  ..                                  D        0  Mon Jan  1 00:00:00 2024
  file.txt                           A     1024  Mon Jan  1 00:00:00 2024
  document.pdf                       A    51200  Mon Jan  1 00:00:00 2024
  folder                             D        0  Mon Jan  1 00:00:00 2024

		524288 blocks of size 1024. 400000 blocks available
smb: \> get file.txt
getting file \file.txt of size 1024 as file.txt (1024.0 KiloBytes/sec) (average 1024.0 KiloBytes/sec)
```
- **Estructura:** Comandos interactivos con prompt `smb: \>`, output tipo `ls` con columnas: nombre, tipo (D/A), tamaño, fecha.

### 8. **SSLScan**
- **Archivo generado:** `sslscan_{scan_id}.txt`
- **Formato:** TXT (`.txt`) - Output estructurado de análisis SSL/TLS
- **Parser existente:** ❌ NO
- **Ubicación código:** `services/enumeration/ssl_enum.py` (línea 54)
- **Ejemplo formato completo:**
```
Testing SSL server 192.168.1.1 on port 443

  Supported Server Cipher(s):
    Accepted  TLSv1.2  256 bits  ECDHE-RSA-AES256-GCM-SHA384
    Accepted  TLSv1.2  128 bits  ECDHE-RSA-AES128-GCM-SHA256
    Accepted  TLSv1.1  256 bits  ECDHE-RSA-AES256-SHA
    Accepted  TLSv1.0  256 bits  ECDHE-RSA-AES256-SHA
    Accepted  SSLv3   256 bits  ECDHE-RSA-AES256-SHA
    Accepted  SSLv2   256 bits  ECDHE-RSA-AES256-SHA

  Prefered Server Cipher(s):
    TLSv1.2  256 bits  ECDHE-RSA-AES256-GCM-SHA384

  SSL Certificate:
    Signature Algorithm: sha256WithRSAEncryption
    RSA Key Size: 2048
    Issuer: /C=US/O=Let's Encrypt/CN=R3
    Not valid before: Jan  1 00:00:00 2024 GMT
    Not valid after:  Apr  1 00:00:00 2024 GMT
    Subject: /CN=example.com
    Serial Number: 12345678901234567890
```
- **Estructura:** Secciones claras: Supported Ciphers, Preferred Ciphers, Certificate Info. Cada cipher tiene formato: `Accepted  PROTOCOL  BITS  CIPHER_NAME`.

### 9. **SSLyze**
- **Archivo generado:** `sslyze_{scan_id}.txt`
- **Formato:** TXT (`.txt`) - Output estructurado de análisis SSL/TLS avanzado
- **Parser existente:** ❌ NO
- **Ubicación código:** `services/enumeration/ssl_enum.py` (línea 113)
- **Ejemplo formato completo:**
```
SCAN RESULTS FOR 192.168.1.1:443

  * TLS 1.3 Cipher Suites:
      Preferred:
        TLS_AES_256_GCM_SHA384
      Accepted:
        TLS_AES_256_GCM_SHA384
        TLS_AES_128_GCM_SHA256

  * TLS 1.2 Cipher Suites:
      Preferred:
        TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
      Accepted:
        TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
        TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
        TLS_RSA_WITH_AES_256_GCM_SHA384

  * Certificate Information:
      Hostname(s) validated: example.com
      Common Name: example.com
      Issuer: Let's Encrypt R3
      Serial Number: 12345678901234567890
      Not Before: 2024-01-01 00:00:00
      Not After: 2024-04-01 00:00:00
      Public Key Algorithm: RSA
      Key Size: 2048
      Signature Algorithm: SHA256withRSA

  * Session Renegotiation:
      Secure Renegotiation: Supported
      Insecure Renegotiation: Not supported
```
- **Estructura:** Secciones por protocolo TLS (1.3, 1.2, etc.), cada una con Preferred y Accepted ciphers. Información detallada del certificado.

### 10. **SSH-Audit**
- **Archivo generado:** `ssh-audit_{scan_id}.txt`
- **Formato:** TXT (`.txt`) - Output estructurado con categorías y niveles de severidad
- **Parser existente:** ❌ NO
- **Ubicación código:** `services/enumeration/network_services/ssh_enum.py` (línea 44)
- **Ejemplo formato completo:**
```
# general
(gen) banner: SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5
(gen) software: OpenSSH 8.2p1
(gen) compatibility: OpenSSH 7.4+, Dropbear SSH 2018.76+
(gen) compression: disabled
(gen) server_host_key_algorithms: ssh-rsa, rsa-sha2-256, rsa-sha2-512

# key exchange algorithms
(kex) diffie-hellman-group14-sha256   -- [info] available
(kex) diffie-hellman-group16-sha512   -- [warn] using weak hashing algorithm
(kex) diffie-hellman-group1-sha1      -- [fail] removed (in server)
(kex) diffie-hellman-group-exchange-sha256 -- [info] available

# server host key algorithms
(key) ssh-rsa                          -- [warn] using weak hashing algorithm
(key) rsa-sha2-256                    -- [info] available
(key) rsa-sha2-512                    -- [info] available

# encryption algorithms (ciphers)
(enc) chacha20-poly1305@openssh.com   -- [info] available
(enc) aes256-gcm@openssh.com          -- [info] available
(enc) aes128-gcm@openssh.com          -- [info] available
(enc) aes256-ctr                       -- [info] available
(enc) aes192-ctr                       -- [info] available
(enc) aes128-ctr                       -- [info] available
(enc) 3des-cbc                         -- [fail] removed (in server)

# message authentication code algorithms
(mac) umac-128-etm@openssh.com        -- [info] available
(mac) hmac-sha2-256-etm@openssh.com   -- [info] available
(mac) hmac-sha2-512-etm@openssh.com   -- [info] available
(mac) hmac-sha1                       -- [warn] using weak hashing algorithm
```
- **Estructura:** Categorías con prefijos `(gen)`, `(kex)`, `(key)`, `(enc)`, `(mac)`. Cada línea tiene formato: `(category) algorithm_name -- [level] message`. Niveles: `[info]`, `[warn]`, `[fail]`.

### 11. **Nmap SSH Enumeration**
- **Archivo generado:** `nmap_ssh_{scan_id}.xml`
- **Formato:** XML (`.xml`)
- **Parser existente:** ✅ (usa `NmapParser`)
- **Ejemplo:** Similar a Nmap general

### 12. **Nmap FTP Enumeration**
- **Archivo generado:** `nmap_ftp_{scan_id}.xml`
- **Formato:** XML (`.xml`)
- **Parser existente:** ✅ (usa `NmapParser`)
- **Ejemplo:** Similar a Nmap general

### 13. **SMTP User Enumeration**
- **Archivo generado:** `smtp-user-enum_{scan_id}.txt`
- **Formato:** TXT (`.txt`) - Lista de usuarios encontrados/no encontrados
- **Parser existente:** ❌ NO
- **Ubicación código:** `services/enumeration/network_services/smtp_enum.py` (línea 47)
- **Ejemplo formato completo:**
```
192.168.1.1:25     admin exists
192.168.1.1:25     user exists
192.168.1.1:25     administrator exists
192.168.1.1:25     guest doesn't exist
192.168.1.1:25     test doesn't exist
192.168.1.1:25     root doesn't exist
```
- **Estructura:** Formato simple: `IP:PUERTO    USERNAME STATUS`. Status puede ser `exists` o `doesn't exist`.

### 14. **Nmap SMTP Enumeration**
- **Archivo generado:** `nmap_smtp_{scan_id}.xml`
- **Formato:** XML (`.xml`)
- **Parser existente:** ✅ (usa `NmapParser`)
- **Ejemplo:** Similar a Nmap general

### 15. **DNS Zone Transfer (dig)**
- **Archivo generado:** `dig_zone_{scan_id}.txt`
- **Formato:** TXT (`.txt`) - Output estándar de dig con registros DNS
- **Parser existente:** ❌ NO
- **Ubicación código:** `services/enumeration/network_services/dns_enum.py` (línea 54)
- **Ejemplo formato completo:**
```
; <<>> DiG 9.16.1-Ubuntu <<>> example.com AXFR @ns1.example.com
; (1 server found)
; global options: +cmd
example.com.		3600	IN	SOA	ns1.example.com. admin.example.com. (
				2024010101 ; serial
				3600       ; refresh (1 hour)
				1800       ; retry (30 minutes)
				604800     ; expire (1 week)
				3600       ; minimum (1 hour)
				)
example.com.		3600	IN	NS	ns1.example.com.
example.com.		3600	IN	NS	ns2.example.com.
example.com.		3600	IN	A	192.168.1.1
example.com.		3600	IN	MX	10 mail.example.com.
www.example.com.	3600	IN	A	192.168.1.2
api.example.com.	3600	IN	A	192.168.1.3
subdomain.example.com.	3600	IN	CNAME	www.example.com.
```
- **Estructura:** Header con versión de dig, luego registros DNS en formato estándar: `DOMAIN  TTL  CLASS  TYPE  VALUE`.

### 16. **Nmap DNS Enumeration**
- **Archivo generado:** `nmap_dns_{scan_id}.xml`
- **Formato:** XML (`.xml`)
- **Parser existente:** ✅ (usa `NmapParser`)
- **Ejemplo:** Similar a Nmap general

### 17. **SNMPWalk**
- **Archivo generado:** `snmpwalk_{scan_id}.txt`
- **Formato:** TXT (`.txt`) - Output de OIDs SNMP con valores
- **Parser existente:** ❌ NO
- **Ubicación código:** `services/enumeration/network_services/snmp_enum.py` (línea 46)
- **Ejemplo formato completo:**
```
SNMPv2-MIB::sysDescr.0 = STRING: Linux server 5.4.0-74-generic #83-Ubuntu SMP
SNMPv2-MIB::sysObjectID.0 = OID: NET-SNMP-MIB::netSnmpAgentOIDs.10
SNMPv2-MIB::sysUpTime.0 = Timeticks: (123456789) 14 days, 6:56:07.89
SNMPv2-MIB::sysContact.0 = STRING: admin@example.com
SNMPv2-MIB::sysName.0 = STRING: server.example.com
SNMPv2-MIB::sysLocation.0 = STRING: Data Center
IF-MIB::ifNumber.0 = INTEGER: 2
IF-MIB::ifDescr.1 = STRING: eth0
IF-MIB::ifDescr.2 = STRING: lo
IF-MIB::ifType.1 = INTEGER: ethernetCsmacd(6)
IF-MIB::ifMtu.1 = INTEGER: 1500
```
- **Estructura:** Formato `OID = TYPE: VALUE`. Tipos comunes: STRING, INTEGER, Timeticks, OID.

### 18. **OneSixtyOne (SNMP Brute Force)**
- **Archivo generado:** `onesixtyone_{scan_id}.txt`
- **Formato:** TXT (`.txt`) - Lista de hosts con community strings válidos
- **Parser existente:** ❌ NO
- **Ubicación código:** `services/enumeration/network_services/snmp_enum.py` (línea 51)
- **Ejemplo formato completo:**
```
192.168.1.1 [public] Linux server 5.4.0-74-generic
192.168.1.2 [public] Cisco IOS Software
192.168.1.3 [private] Windows Server 2019
192.168.1.4 [public] HP ProCurve Switch
```
- **Estructura:** Formato simple: `IP [COMMUNITY] SYSTEM_INFO`. Muestra IP, community string válido y descripción del sistema.

### 19. **Nmap SNMP Enumeration**
- **Archivo generado:** `nmap_snmp_{scan_id}.xml`
- **Formato:** XML (`.xml`)
- **Parser existente:** ✅ (usa `NmapParser`)
- **Ejemplo:** Similar a Nmap general

### 20. **LDAPSearch**
- **Archivo generado:** `ldapsearch_{scan_id}.txt`
- **Formato:** TXT (`.txt`) - Formato LDIF (LDAP Data Interchange Format)
- **Parser existente:** ❌ NO
- **Ubicación código:** `services/enumeration/network_services/ldap_enum.py` (línea 45)
- **Ejemplo formato completo:**
```
# extended LDIF
#
# LDAPv3
# base <dc=example,dc=com> with scope subtree
# filter: (objectClass=*)
# requesting: ALL
#

# example.com
dn: dc=example,dc=com
objectClass: top
objectClass: domain
dc: example

# admin, example.com
dn: cn=admin,dc=example,dc=com
objectClass: person
objectClass: organizationalPerson
cn: admin
sn: Administrator
mail: admin@example.com

# users, example.com
dn: ou=users,dc=example,dc=com
objectClass: organizationalUnit
ou: users

# john.doe, users, example.com
dn: cn=john.doe,ou=users,dc=example,dc=com
objectClass: person
objectClass: inetOrgPerson
cn: john.doe
sn: Doe
mail: john.doe@example.com
```
- **Estructura:** Formato LDIF estándar. Cada entrada comienza con `dn:` (Distinguished Name), seguido de atributos `atributo: valor`. Entradas separadas por línea en blanco.

### 21. **Nmap LDAP Enumeration**
- **Archivo generado:** `nmap_ldap_{scan_id}.xml`
- **Formato:** XML (`.xml`)
- **Parser existente:** ✅ (usa `NmapParser`)
- **Ejemplo:** Similar a Nmap general

### 22. **Nmap RDP Enumeration**
- **Archivo generado:** `nmap_rdp_{scan_id}.xml`
- **Formato:** XML (`.xml`)
- **Parser existente:** ✅ (usa `NmapParser`)
- **Ejemplo:** Similar a Nmap general

### 23. **MySQL Enumeration**
- **Archivo generado:** `mysql_{scan_id}.txt`
- **Formato:** TXT (`.txt`) - Output de comandos MySQL
- **Parser existente:** ❌ NO
- **Ubicación código:** `services/enumeration/database_enum.py` (línea 61)
- **Ejemplo formato completo:**
```
MySQL version: 8.0.23
Server version: 8.0.23-0ubuntu0.20.04.1

Databases:
  information_schema
  mysql
  performance_schema
  sys
  app_database
  test_db

Users:
  root@localhost
  admin@%
  user@192.168.1.%
  readonly@%

Tables in app_database:
  users
  products
  orders
```
- **Estructura:** Secciones claras: versión, databases (lista), users (lista con formato `user@host`), tables por database.

### 24. **Nmap MySQL Enumeration**
- **Archivo generado:** `nmap_mysql_{scan_id}.xml`
- **Formato:** XML (`.xml`)
- **Parser existente:** ✅ (usa `NmapParser`)
- **Ejemplo:** Similar a Nmap general

### 25. **PostgreSQL Enumeration**
- **Archivo generado:** `psql_{scan_id}.txt`
- **Formato:** TXT (`.txt`) - Output de comandos psql
- **Parser existente:** ❌ NO
- **Ubicación código:** `services/enumeration/database_enum.py` (línea 128)
- **Ejemplo formato completo:**
```
PostgreSQL version: 13.2
Server version: PostgreSQL 13.2 (Ubuntu 13.2-1.pgdg20.04+1)

Databases:
  postgres
  template0
  template1
  app_db
  test_db

Users/Roles:
  postgres (Superuser)
  admin (Superuser)
  readonly (Login)
  app_user (Login)

Schemas in app_db:
  public
  app_schema
```
- **Estructura:** Similar a MySQL: versión, databases, users/roles con permisos entre paréntesis, schemas.

### 26. **Nmap PostgreSQL Enumeration**
- **Archivo generado:** `nmap_postgresql_{scan_id}.xml`
- **Formato:** XML (`.xml`)
- **Parser existente:** ✅ (usa `NmapParser`)
- **Ejemplo:** Similar a Nmap general

### 27. **Redis Enumeration**
- **Archivo generado:** `redis-cli_{scan_id}.txt`
- **Formato:** TXT (`.txt`)
- **Parser existente:** ❌ NO
- **Ejemplo formato:**
```
Redis version: 6.2.6
Keys: 100
Memory: 1048576 bytes
```

### 28. **Nmap Redis Enumeration**
- **Archivo generado:** `nmap_redis_{scan_id}.xml`
- **Formato:** XML (`.xml`)
- **Parser existente:** ✅ (usa `NmapParser`)
- **Ejemplo:** Similar a Nmap general

### 29. **Nmap MongoDB Enumeration**
- **Archivo generado:** `nmap_mongodb_{scan_id}.xml`
- **Formato:** XML (`.xml`)
- **Parser existente:** ✅ (usa `NmapParser`)
- **Ejemplo:** Similar a Nmap general

---

## 🟢 VULNERABILITY ASSESSMENT (`/vuln_scans/`)

### 30. **Nuclei**
- **Archivo generado:** `nuclei_{scan_id}.jsonl`
- **Formato:** JSONL (`.jsonl`) - Una línea JSON por finding
- **Parser existente:** ✅ `vulnerability/nuclei_parser.py`
- **Ejemplo formato:**
```json
{"template-id":"cve-2024-1234","info":{"name":"Apache Log4j RCE","severity":"critical"},"matched-at":"http://example.com/api","extracted-results":[],"request":"GET /api HTTP/1.1","response":"HTTP/1.1 200 OK"}
{"template-id":"exposed-panel","info":{"name":"Exposed Admin Panel","severity":"high"},"matched-at":"http://example.com/admin"}
```

### 31. **Nikto**
- **Archivo generado:** `nikto_{scan_id}.json`
- **Formato:** JSON (`.json`)
- **Parser existente:** ✅ `vulnerability/nikto_parser.py`
- **Ejemplo formato:**
```json
{
  "hostname": "example.com",
  "port": 80,
  "vulnerabilities": [
    {
      "id": "12345",
      "osvdb_id": "67890",
      "method": "GET",
      "url": "/",
      "msg": "Server leaks inodes via ETags"
    }
  ]
}
```

### 32. **SQLMap**
- **Archivo generado:** `sqlmap_{scan_id}/` (directorio) + `results-*.csv`
- **Formato:** CSV (`.csv`) dentro del directorio
- **Parser existente:** ❌ NO
- **Ejemplo formato CSV:**
```csv
id,title,payload,where,vector,parameter
1,"SQL injection","1' OR '1'='1","GET","boolean-based blind","id"
2,"SQL injection","1' UNION SELECT NULL--","GET","union query-based","id"
```

### 33. **OWASP ZAP**
- **Archivo generado:** `zap_{scan_id}.json`
- **Formato:** JSON (`.json`)
- **Parser existente:** ❌ NO
- **Ejemplo formato:**
```json
{
  "site": [
    {
      "@name": "http://example.com",
      "alerts": [
        {
          "pluginid": "10021",
          "alert": "X-Frame-Options Header Missing",
          "name": "X-Frame-Options Header Missing",
          "riskcode": "1",
          "confidence": "2",
          "riskdesc": "Low (Medium)",
          "desc": "X-Frame-Options header is not included in the HTTP response"
        }
      ]
    }
  ]
}
```

### 34. **WPScan**
- **Archivo generado:** `wpscan_{scan_id}.json`
- **Formato:** JSON (`.json`)
- **Parser existente:** ❌ NO
- **Ejemplo formato:**
```json
{
  "url": "http://example.com",
  "version": {
    "number": "5.8",
    "release_date": "2021-07-20"
  },
  "vulnerabilities": [
    {
      "id": 12345,
      "title": "WordPress Core XSS",
      "fixed_in": "5.9"
    }
  ],
  "plugins": [
    {
      "slug": "akismet",
      "version": "4.1.10"
    }
  ]
}
```

### 35. **testssl.sh**
- **Archivo generado:** `testssl_{scan_id}.json` + `testssl_{scan_id}.html`
- **Formato:** JSON (`.json`) + HTML (`.html`)
- **Parser existente:** ❌ NO
- **Ejemplo formato JSON:**
```json
{
  "scanTime": "2024-01-01 12:00:00",
  "target": "example.com:443",
  "protocols": {
    "TLSv1.2": "offered",
    "TLSv1.3": "offered"
  },
  "ciphers": [
    {
      "cipher": "ECDHE-RSA-AES256-GCM-SHA384",
      "protocol": "TLSv1.2"
    }
  ]
}
```

---

## 📊 RESUMEN POR FORMATO

### XML (`.xml`)
- Nmap (todos los tipos)
- Masscan (según código, pero en realidad genera JSON)

### JSON (`.json`)
- Masscan
- OWASP ZAP
- WPScan
- testssl.sh

### JSONL (`.jsonl`)
- Nuclei

### TXT (`.txt`)
- RustScan
- Naabu
- Enum4linux
- SMBMap
- SMBClient
- SSLScan
- SSLyze
- SSH-Audit
- SMTP User Enumeration
- DNS Zone Transfer (dig)
- SNMPWalk
- OneSixtyOne
- LDAPSearch
- MySQL Enumeration
- PostgreSQL Enumeration
- Redis Enumeration

### CSV (`.csv`)
- SQLMap (dentro de directorio)

### HTML (`.html`)
- testssl.sh

---

## ✅ PARSERS EXISTENTES

1. ✅ **NmapParser** - `scanning/nmap_parser.py` (XML)
2. ✅ **NucleiParser** - `vulnerability/nuclei_parser.py` (JSONL)
3. ✅ **NiktoParser** - `vulnerability/nikto_parser.py` (JSON)

---

## ❌ PARSERS FALTANTES (32 herramientas)

### Port Scanning (3)
- RustScan (TXT)
- Masscan (JSON)
- Naabu (TXT)

### Enumeration (23)
- Enum4linux (TXT)
- SMBMap (TXT)
- SMBClient (TXT)
- SSLScan (TXT)
- SSLyze (TXT)
- SSH-Audit (TXT)
- SMTP User Enumeration (TXT)
- DNS Zone Transfer/dig (TXT)
- SNMPWalk (TXT)
- OneSixtyOne (TXT)
- LDAPSearch (TXT)
- MySQL Enumeration (TXT)
- PostgreSQL Enumeration (TXT)
- Redis Enumeration (TXT)
- (Los Nmap específicos usan NmapParser existente)

### Vulnerability Assessment (6)
- SQLMap (CSV)
- OWASP ZAP (JSON)
- WPScan (JSON)
- testssl.sh (JSON + HTML)

---

## 📝 NOTAS

1. **Masscan**: Según código genera `.json`, pero la documentación menciona `.xml`. Verificar formato real.
2. **Nmap específicos**: Todos usan el mismo `NmapParser` existente, solo cambia el nombre del archivo.
3. **SQLMap**: Genera un directorio con múltiples archivos CSV. El parser deberá leer el directorio.
4. **testssl.sh**: Genera JSON y HTML. Priorizar JSON para parsing.

---

**Total herramientas de scanning:** 35  
**Parsers existentes:** 3  
**Parsers faltantes:** 32

