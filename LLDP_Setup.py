from jnpr.junos.utils.config import Config

#=====================================================================================

def LLDP_Setup(dlist, if_s):
    for d in dlist:
        d.open()
        d.bind(conf=Config)
        print("Connected")
        d.conf.load(template_path = 'Config Files/LLDP_Setup.conf', template_vars = {'if_s': if_s},  merge = True)
        d.conf.commit()
        d.close()

#=====================================================================================

if __name__ == "__main__":
    LLDP_Setup()
