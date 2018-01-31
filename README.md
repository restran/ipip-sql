# ipip-sql

SQL version for IPIP.net free global ipv4 address database

## Motivation

[IPIP.net](https://www.ipip.net) provides a free global ipv4 address database, specially better for China. The [oficial recommended sdk](https://github.com/lxyu/17monip) queries ip address based on file seeking. In some case, i would like to use sql query. This project transfers ip address data from file to mysql databse. 

## Usage 

Step 1, download latest dat file

- https://www.ipip.net/download.html

Step 2, create ip databse

```sql
CREATE TABLE `app_ip` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ip_gateway` varchar(20) NOT NULL,
  `ip_gateway_int` bigint(20) NOT NULL,
  `city` varchar(50) NOT NULL,
  `country` varchar(50) NOT NULL,
  `operator` varchar(30) NOT NULL,
  `province` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `app_ip_f199e5d0` (`ip_gateway_int`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
```

Step 3, save to databse

```
# modify your databse account
db = records.Database('mysql://user:password@localhost/qr_track'
# save to databse
IP.save_to_database()
```

Step 4, query ip

```
IP.query(['114.114.114.114', '8.8.8.8'])
```

Output

```
[{'country': '114DNS.COM', 'province': '114DNS.COM', 'city': ''}, {'country': 'GOOGLE.COM', 'province': 'GOOGLE.COM', 'city': ''}]
```