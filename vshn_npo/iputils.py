# This file provides a stripped down version of
# https://github.com/pydron/ifaddr

import collections
import ctypes.util
import ipaddress
import os
import socket

class sockaddr(ctypes.Structure):
    _fields_= [('sa_familiy', ctypes.c_uint16),
               ('sa_data', ctypes.c_uint8 * 14)]


class sockaddr_in(ctypes.Structure):
    _fields_= [('sin_familiy', ctypes.c_uint16),
               ('sin_port', ctypes.c_uint16),
               ('sin_addr', ctypes.c_uint8 * 4),
               ('sin_zero', ctypes.c_uint8 * 8)]


class sockaddr_in6(ctypes.Structure):
    _fields_= [('sin6_familiy', ctypes.c_uint16),
               ('sin6_port', ctypes.c_uint16),
               ('sin6_flowinfo', ctypes.c_uint32),
               ('sin6_addr', ctypes.c_uint8 * 16),
               ('sin6_scope_id', ctypes.c_uint32)]


class ifaddrs(ctypes.Structure):
    _fields_ = [('ifa_next', ctypes.POINTER(ifaddrs)),
                ('ifa_name', ctypes.c_char_p),
                ('ifa_flags', ctypes.c_uint),
                ('ifa_addr', ctypes.POINTER(sockaddr)),
                ('ifa_netmask', ctypes.POINTER(sockaddr))]


libc = ctypes.CDLL(ctypes.util.find_library("socket" if os.uname()[0] == "SunOS" else "c"), use_errno=True)


Adapter=collections.namedtuple('Adapter', ['name', 'ips'])


def _sockaddr_to_ip(sockaddr_ptr):
    if sockaddr_ptr:
        if sockaddr_ptr[0].sa_familiy == socket.AF_INET:
            ipv4 = ctypes.cast(sockaddr_ptr, ctypes.POINTER(sockaddr_in))
            ippacked = bytes(bytearray(ipv4[0].sin_addr))
            ip = str(ipaddress.ip_address(ippacked))
            return ip
        elif sockaddr_ptr[0].sa_familiy == socket.AF_INET6:
            ipv6 = ctypes.cast(sockaddr_ptr, ctypes.POINTER(sockaddr_in6))
            flowinfo = ipv6[0].sin6_flowinfo
            ippacked = bytes(bytearray(ipv6[0].sin6_addr))
            ip = str(ipaddress.ip_address(ippacked))
            scope_id = ipv6[0].sin6_scope_id
            return(ip, flowinfo, scope_id)
    return None


def get_adapters(include_unconfigured=False):

    addr0 = addr = ctypes.POINTER(ifaddrs)()
    retval = libc.getifaddrs(ctypes.byref(addr))
    if retval != 0:
        eno = ctypes.get_errno()
        raise OSError(eno, os.strerror(eno))

    ips = collections.OrderedDict()

    def add_ip(adapter_name, ip):
        if not adapter_name in ips:
            ips[adapter_name] = Adapter(adapter_name, [])
        if ip is not None:
            ips[adapter_name].ips.append(ip)

    while addr:
        name = addr[0].ifa_name
        ip = _sockaddr_to_ip(addr[0].ifa_addr)
        if ip:
            if addr[0].ifa_netmask and not addr[0].ifa_netmask[0].sa_familiy:
                addr[0].ifa_netmask[0].sa_familiy = addr[0].ifa_addr[0].sa_familiy
            if isinstance(ip, tuple):
                ip = ip[0]
            add_ip(name, ipaddress.ip_address(ip))
        else:
            if include_unconfigured:
                add_ip(name, None)
        addr = addr[0].ifa_next

    libc.freeifaddrs(addr0)

    return ips.values()


def host_has_global_ip6():
    has_ipv6 = False
    ips = get_adapters()
    for ip in ips:
        for i in ip.ips:
            if isinstance(i, ipaddress.IPv6Address):
                has_ipv6 = has_ipv6 or i.is_global

    return has_ipv6
