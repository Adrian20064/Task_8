
from django.shortcuts import render
from .forms import NetworkForm
from pymongo import MongoClient
from datetime import datetime
import ipaddress

leases = {}  

def is_valid_mac(mac):
    parts = mac.split(":")
    if len(parts) != 6:
        return False
    try:
        return all(len(part) == 2 and int(part, 16) >= 0 for part in parts)
    except:
        return False

def generate_ipv4():
    base = ipaddress.IPv4Address('192.168.1.10')
    for i in range(1, 245):
        ip = str(base + i)
        if ip not in leases.values():
            return ip

def generate_ipv6(mac):
    parts = mac.split(":")
    binary_mac = [int(part, 16) for part in parts]
    binary_mac[0] ^= 0b00000010  # Toggle U/L bit
    ipv6 = '2001:db8::{:02x}{:02x}:{:02x}ff:fe{:02x}:{:02x}{:02x}'.format(*binary_mac)
    return ipv6

def network_view(request):
    result = None
    if request.method == 'POST':
        form = NetworkForm(request.POST)
        if form.is_valid():
            mac = form.cleaned_data['mac_address']
            version = form.cleaned_data['dhcp_version']

            if not is_valid_mac(mac):
                result = "Invalid MAC address format."
            else:
                if mac in leases:
                    ip = leases[mac]
                else:
                    ip = generate_ipv4() if version == 'DHCPv4' else generate_ipv6(mac)
                    leases[mac] = ip

                # Guardar en MongoDB
                client = MongoClient('mongodb://<IP-MONGODB>:27017/')
                db = client.network
                db.leases.insert_one({
                    'mac_address': mac,
                    'dhcp_version': version,
                    'assigned_ip': ip,
                    'lease_time': '3600 seconds',
                    'timestamp': datetime.utcnow().isoformat()
                })

                result = {
                    'mac': mac,
                    'ip': ip,
                    'version': version,
                    'lease_time': '3600 seconds'
                }
    else:
        form = NetworkForm()

    return render(request, 'form.html', {'form': form, 'result': result})

def lease_list_view(request):
    client = MongoClient('mongodb://44.223.7.134:27017/') #ip de la base de datos
    db = client.network
    leases = list(db.leases.find())
    return render(request, 'leases.html', {'leases': leases})