import csv


class DomainExtractor:
    def __init__(self):
        self.domains_count = {}

    def get_domains(self):
        tlds = input("Which top level domains would you like to emulate? (Separate with commas): \n").split(',')

        for tld in tlds:
            count = int(input(f"How many domains for {tld.strip()} top level domain? "))
            self.domains_count[tld.strip()] = count

    def extract_domains(self):
        domains_to_write = []

        with open('topdomains.csv', 'r') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                if row['TLD'] in self.domains_count and self.domains_count[row['TLD']] > 0:
                    domains_to_write.append(row['Domain'])
                    self.domains_count[row['TLD']] -= 1

        return domains_to_write

    def write_to_file(self, domains_to_write):
        with open('sites.txt', 'w') as file:
            for domain in domains_to_write:
                file.write(domain + '\n')

    def run_extraction(self):
        self.get_domains()
        selected_domains = self.extract_domains()
        self.write_to_file(selected_domains)
        print("Domains written to sites.txt")


if __name__ == "__main__":
    domain_extractor = DomainExtractor()
    domain_extractor.run_extraction()
