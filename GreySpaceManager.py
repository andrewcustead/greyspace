import subprocess
import os
import tempfile
import dns.resolver


class GreySpaceManager:
    def __init__(self, root_dir, vhost_dir, cert_dir, etc_dir, info_dir, nginx_conf, vhosts_file):
        self.root_dir = root_dir
        self.vhost_dir = vhost_dir
        self.cert_dir = cert_dir
        self.etc_dir = etc_dir
        self.info_dir = info_dir
        self.nginx_conf = nginx_conf
        self.vhosts_file = vhosts_file

    def make_structure(self):
        make_root = f'mkdir {self.root_dir}'
        make_vhost_dir = f'mkdir {self.vhost_dir}'
        make_cert_dir = f'mkdir {self.cert_dir}'
        make_etc_dir = f'mkdir {self.etc_dir}'
        make_info_dir = f'mkdir {self.info_dir}'
        os.system(make_root)
        os.system(make_vhost_dir)
        os.system(make_cert_dir)
        os.system(make_etc_dir)
        os.system(make_info_dir)

    def create_ca_certificate(self):
        openssl_command = f'openssl req -newkey rsa:2048 -nodes -keyout "{self.info_dir}/greyspace_ca.key" ' \
                          f'-days 7300 -x509 -out "{self.info_dir}/greyspace_ca.cer" ' \
                          '-subj \'/C=US/ST=MD/L=BAL/O=MDANG/OU=CERT/CN=greyspace_ca\' 2>/dev/null'
        mv_ca_cert = f'cp {self.info_dir}/greyspace_ca.cer {self.etc_dir}'
        mv_ca_key = f'cp {self.info_dir}/greyspace_ca.key {self.etc_dir}'
        os.system(openssl_command)
        os.system(mv_ca_cert)
        os.system(mv_ca_key)

    def wget_domains(self):
        if not os.path.isfile(self.vhosts_file):
            print("sites.txt file not found!")
            return

        with open(self.vhosts_file, 'r') as file:
            domains = file.read().splitlines()

        for domain in domains:
            wget_command = f'wget -prEHN --convert-file-only --no-check-certificate -e robots=off ' \
                           f'--random-wait -t 2 "Mozilla/5.0 (X11)" -P {self.vhost_dir} -l 1 {domain}'
            os.system(wget_command)

    def generate_greyspace_site(self):
        pass  # Add code for generating greyspace.info landing page

    def generate_greyspace_vhost_key(self):
        create_vh_key = f'openssl genrsa -out "{self.etc_dir}/greyspace_vh.key" 2048 2>/dev/null'
        os.system(create_vh_key)

    def create_ca_configuration(self):
        TMP_CA_DIR = tempfile.mkdtemp(prefix='/tmp/GreySpaceCA.')

        with open(os.path.join(TMP_CA_DIR, 'serial'), 'w') as serial_file:
            serial_file.write('000a\n')

        open(os.path.join(TMP_CA_DIR, 'index'), 'a').close()

        TMP_CA_CONF = f'''[ ca ]
        default_ca = greyspace_ca

        [ crl_ext ]
        authorityKeyIdentifier=keyid:always

        [ greyspace_ca ]
        private_key = {os.path.join(self.etc_dir, 'greyspace_ca.key')}
        certificate = {os.path.join(self.etc_dir, 'greyspace_ca.cer')}
        new_certs_dir = {TMP_CA_DIR}
        database = {os.path.join(TMP_CA_DIR, 'index')}
        serial = {os.path.join(TMP_CA_DIR, 'serial')}
        default_days = 3650
        default_md = sha512
        copy_extensions = copy
        unique_subject = no
        policy = greyspace_ca_policy
        x509_extensions = greyspace_ca_ext

        [ greyspace_ca_policy ]
        countryName = supplied
        stateOrProvinceName = supplied
        localityName = supplied
        organizationName = supplied
        organizationalUnitName = supplied
        commonName = supplied
        emailAddress = optional

        [ greyspace_ca_ext ]
        basicConstraints = CA:false
        nsCertType = server
        nsComment = "GreySpace CA Generated Certificate"
        subjectKeyIdentifier = hash
        authorityKeyIdentifier = keyid,issuer:always
        '''

        TMP_VH_CONF = '''\
        [ v3_req ]
        subjectAltName = @alt_names
        '''

        return TMP_CA_DIR, TMP_CA_CONF, TMP_VH_CONF

    def start_nginx(self):
        with open(self.nginx_conf, 'w') as f:
            f.write('''# use a common key for all certificates:
            ssl_certificate_key /var/lib/greyspace/etc/topgen_vh.key
            # ensure enumerated https server blocks fit into nginx hash table:
            server_names_hash_bucket_size 256;
            server_names_hash_max_size 131070;''')

    def process_each_vhost(self, TMP_CA_CONF, TMP_VH_CONF):
        for vh_file in os.listdir(self.vhost_dir):
            if not os.path.isdir(os.path.join(self.vhost_dir, vh_file)):
                continue

            VB = vh_file  # basename
            # Remaining code for issuing certificate, appending nginx conf block, etc.

    def resolve_DNS(self):
        with open(self.vhosts_file, 'r') as domains:
            with open(os.path.join(self.etc_dir, 'hosts.nginx'), 'w') as hosts_file:
                resolver = dns.resolver.Resolver()
                for line in domains:
                    domain = line.strip()
                    try:
                        answers = resolver.resolve(domain, 'A')
                        VHIP = answers[0].address if answers else '1.1.1.1'
                    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
                        VHIP = '1.1.1.1'

                    hosts_file.write(f"{VHIP} {domain}\n")

    def main(self):
        self.make_structure()
        self.create_ca_certificate()
        self.wget_domains()
        TMP_CA_DIR, TMP_CA_CONF, TMP_VH_CONF = self.create_ca_configuration()
        self.generate_greyspace_vhost_key()
        self.create_ca_configuration()
        self.start_nginx()
        self.process_each_vhost(TMP_CA_CONF, TMP_VH_CONF)
        self.resolve_DNS()
        pass


if __name__ == "__main__":
    # Set paths and directories here
    root_dir = '/var/lib/greyspace'
    vhost_dir = '/var/lib/greyspace/vhosts'
    cert_dir = '/var/lib/greyspace/certs'
    etc_dir = '/var/lib/greyspace/etc'
    info_dir = '/var/lib/greyspace/vhosts/greyspace.info'
    nginx_conf = '/var/lib/greyspace/etc/nginx.conf'
    vhosts_file = 'sites.txt'

    manager = GreySpaceManager(root_dir, vhost_dir, cert_dir, etc_dir, info_dir, nginx_conf, vhosts_file)
    manager.main()
