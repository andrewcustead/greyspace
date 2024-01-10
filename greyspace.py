from DomainExtractor import DomainExtractor
from greyspace_scraper import GreySpaceManager

def main():
    # Set paths and directories here
    root_dir = '/var/lib/greyspace'
    vhost_dir = '/var/lib/greyspace/vhosts'
    cert_dir = '/var/lib/greyspace/certs'
    etc_dir = '/var/lib/greyspace/etc'
    info_dir = '/var/lib/greyspace/vhosts/greyspace.info'
    nginx_conf = '/var/lib/greyspace/etc/nginx.conf'
    vhosts_file = '/Users/drew/PycharmProjects/greyspace/sites.txt'
    domainExtractor = DomainExtractor()
    domainExtractor.run_extraction()
    # Create an instance of GreySpaceManager
    manager = GreySpaceManager(root_dir, vhost_dir, cert_dir, etc_dir, info_dir, nginx_conf, vhosts_file)

    # Execute the main method of GreySpaceManager
    manager.main()

if __name__ == "__main__":
    main()
