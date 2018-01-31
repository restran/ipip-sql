# -*- coding: utf-8 -*-
# created by restran on 2018/01/26
import os
import struct
from socket import inet_ntoa, inet_aton

import records

_unpack_V = lambda b: struct.unpack("<L", b)
_unpack_N = lambda b: struct.unpack(">L", b)
_unpack_C = lambda b: struct.unpack("B", b)

db = records.Database('mysql://user:password@localhost/ip_databse')


"""
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
"""


class IP(object):
    offset = 0
    index = 0
    binary = ""

    @staticmethod
    def load(file):
        try:
            path = os.path.abspath(file)
            with open(path, "rb") as f:
                IP.binary = f.read()
                IP.offset, = _unpack_N(IP.binary[:4])
                IP.index = IP.binary[4:IP.offset]
        except Exception as ex:
            print("cannot open file %s" % file)
            print(ex)

    @staticmethod
    def save_to_database(dat_file='17monipdb.dat'):
        IP.load(dat_file)

        ip = '"0.0.0.0"'
        index = IP.index
        offset = IP.offset
        binary = IP.binary
        ipdot = ip.split('.')
        if int(ipdot[0]) < 0 or int(ipdot[0]) > 255 or len(ipdot) != 4:
            return "N/A"

        tmp_offset = int(ipdot[0]) * 4
        start, = _unpack_V(index[tmp_offset:tmp_offset + 4])

        max_comp_len = offset - 1028
        start = start * 8 + 1024

        print(max_comp_len)
        count = 0
        total_count = 0
        data = []
        sql = 'insert into app_ip (ip_gateway, ip_gateway_int, country, province, city, operator) ' \
              'values (:ip_gateway, :ip_gateway_int, :country, :province, :city, :operator)'
        while start < max_comp_len:
            try:
                count += 1
                bytes_ip = index[start:start + 4]
                raw_ip = inet_ntoa(bytes_ip)
                int_ip = int.from_bytes(bytes_ip, byteorder='big')
                index_offset, = _unpack_V(index[start + 4:start + 7] + chr(0).encode('utf-8'))
                t = index[start + 7:start + 8]
                index_length, = _unpack_C(t)
                if index_offset == 0:
                    print("N/A")
                    print(raw_ip)
                else:
                    res_offset = offset + index_offset - 1024
                    address = binary[res_offset:res_offset + index_length].decode('utf-8')
                    country, province, city, operator = address.split('\t')
                    item = {
                        'ip_gateway': raw_ip,
                        'ip_gateway_int': int_ip,
                        'country': country,
                        'province': province,
                        'city': city,
                        'operator': operator
                    }

                    data.append(item)

                if count > 2000:
                    db.bulk_query(sql, data)
                    total_count += count
                    print('%.5f' % (total_count * 8 / max_comp_len))
                    data = []
                    count = 0

            except Exception as e:
                print(e)
                print(start)

            start += 8

        db.bulk_query(sql, data)
        print('done')

    @staticmethod
    def int_ip(ip):
        int_ip = int.from_bytes(inet_aton(ip), byteorder='big')
        print(int_ip)
        return int_ip

    @staticmethod
    def query(ip_list):
        params = {}
        sql_tpl = '(select t.country, t.province, t.city from app_ip t where ip_gateway_int >= :int_ip_%s limit 1)'
        sql = []
        for i, ip in enumerate(ip_list):
            int_ip = int.from_bytes(inet_aton(ip), byteorder='big')
            sql.append(sql_tpl % i)
            params['int_ip_%s' % i] = int_ip

        sql = ' union '.join(sql)
        rows = db.query(sql, **params)
        rows = rows.as_dict()
        print(rows)
        return rows


if __name__ == '__main__':
    # convert dat file data to mysql database
    # IP.save_to_database()

    # select ip
    IP.query(['114.114.114.114', '8.8.8.8'])
