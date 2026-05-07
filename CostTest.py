from jnpr.junos import Device
d0=Device(host='192.168.1.30',user='labuser',password='Labuser')


#========================================================================

def Extract_Speed(speed):
    s = ''

    i = 1    
    while i < len(speed) and speed[i].isdigit():
        s +=  speed[i]
        i += 1

    s_ = int(s)

    if i < len(speed) and speed[i] == 'g':
        s_ *= 1000
    return s_

def Cost(d):
    c = 1
    d.open()
    int_info = d.rpc.get_interface_information(interface_name='ge-0/0/0', brief=True)
    speed_str = int_info.xpath('.//speed/text()')[0]
    speed = Extract_Speed(speed_str)
    c = 100000 / speed
    d.close()
    return c

#========================================================================

if __name__ == '__main__':
    print(Cost(d0))
