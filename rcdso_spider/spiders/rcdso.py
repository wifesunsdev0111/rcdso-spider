import scrapy

class RcdsoSpider(scrapy.Spider):
    name = 'rcdso'
    main_keys = ["AN", "EN", "ME", "OP", "OR", "OS", "OX", "PD", "PE", "PH", "PR"]
    # main_keys = ["AN"]
    main_urls = []
    
    for key in main_keys:
        url = f'https://www.rcdso.org/find-a-dentist/search-results?Alpha=&City=&MbrSpecialty={key}&ConstitID=&District=&AlphaParent=&Address1=&PhoneNum=&SedationType=&SedationProviderType=&GroupCode=&DetailsCode='
        main_urls.append(url)

    def start_requests(self):
        for url in self.main_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    result_urls = []
    def parse(self, response):
        search_sections = response.xpath("//div[@id='dentistSearchResults']//section")
        # yield response.follow("https://www.rcdso.org/find-a-dentist/search-results/dentist?id=117690", self.detail_pase)
        for section in search_sections:
            result_url = section.xpath(".//a/@href").get()  # Extract the href attribute
            
            self.result_urls.append(result_url)
            if result_url:  # Only yield if result_url is not None
                # yield {
                #     "result_url": response.urljoin(result_url)  # Make the URL absolute
                # }
                yield response.follow(result_url, self.detail_pase)

        # Follow pagination or other URLs
        print(f'result url is ', len(self.result_urls))
        yield response.follow_all(self.main_urls, self.parse)
    
    def detail_pase(self, response):
        
        #Extract all main information
        full_name = ""
        registration_number = ""
        current_status = ""
        designated_electoral_district =""
        specialty = ""
        try:
            main_info_names = response.xpath("//div[@id='dentistDetails']//header//dl//dt")
            main_info_values = response.xpath("//div[@id='dentistDetails']//header//dl//dd")
            for index, main_info_name in enumerate(main_info_names):
                name = main_info_name.xpath("text()").get()
                print(name)
                if name in "Full Name:":
                    full_name = main_info_values[index].xpath("text()").get()
                if name in "Registration Number:":
                    registration_number = main_info_values[index].xpath("text()").get()
                if name in "Current Status:":
                    current_status = main_info_values[index].xpath("text()").get().strip()
                if name in "Designated Electoral District:":
                    designated_electoral_district = main_info_values[index].xpath("text()").get()
                if name in "Specialty:":
                    specialty = main_info_values[index].xpath(".//ul//li/text()").get()
        except:
            pass
            
        #Extract NoConcerns data
        no_concerns = ""
        try:
            no_concerns = response.xpath("//div[@id='NoConcerns']//p//strong/text()").get()
        except:
            pass
        
        #Extract all Practice Information
        try:
            practice_section = response.xpath("//section[@id='Practices']//div")
        except:
            pass
        
        address = ""
        try:
            primary_practice_name = practice_section.xpath(".//div[2]//h4/text()").get()
        except:
            pass
        try:
            address = practice_section.xpath(".//div[2]//div[1]//address//span[1]/text()").get().strip() + ", " + practice_section.xpath(".//div[2]//div[1]//address//span[2]/text()").get().strip() + ", " + practice_section.xpath(".//div[2]//div[1]//address//span[3]/text()").get().strip()
        except:
            pass
        phone = ""
        try:
            phone = practice_section.xpath(".//div[2]//div[1]//dl[1]//dd[1]//a[1]/text()").get().strip()
        except:
            pass
        permit_info = []
        try:
            view_facility_permit_link = practice_section.xpath(".//div[2]//div[2]//a[1]/@href").get()
        except:
            pass
        try:
            permit_dts = practice_section.xpath(".//div[2]//div[2]//dl/dt")
            permit_dds = practice_section.xpath(".//div[2]//div[2]//dl/dd")
            for index, permit_dt in enumerate(permit_dts):
                name = permit_dt.xpath("text()").get()
                value = permit_dds[index].xpath("text()").get().strip()
                permit_info.append({name: value})
        except:
            pass  
        
        primary_practice = {
            "practice_name": primary_practice_name,
            "address": address,
            "phone": phone,
            "permit_info": permit_info,
            "view_facility_permit_link": view_facility_permit_link
            
        }
        
        #Extract all other practices
        all_practices = []
        try:
            all_practice_lis = response.xpath("//section[@id='OtherPractices']//div[1]//div[1]//ul[1]/li")
        except:
            pass
        for practice_li in all_practice_lis:
            try:
                a_name = practice_li.xpath(".//h6/text()").get()
            except:
                pass
            try:
                a_address = practice_li.xpath(".//div[1]//address[1]//span[1]/text()").get().strip() + ", " + practice_li.xpath(".//div[1]//address[1]//span[2]/text()").get().strip() + ", " + practice_li.xpath(".//div[1]//address[1]//span[3]/text()").get().strip()
            except:
                pass
            try:
                a_phone = practice_li.xpath(".//div[1]//dl[1]//dd[1]//a[1]/text()").get().strip()
            except:
                a_phone = ""
                pass
            try:
                a_view_facility_permit_link = practice_li.xpath(".//div[2]//a/@href").get()
            except:
                pass
            
            a_permit_info = []
            try:
                a_permit_dts = practice_li.xpath(".//div[2]//dl/dt")
                a_permit_dds = practice_li.xpath(".//div[2]//dl/dd")
            except:
                pass
            
            for index, a_permit_dt in enumerate(a_permit_dts):
                try:
                    permit_name = a_permit_dt.xpath("text()").get()
                except:
                    pass
                try:
                    permit_value = a_permit_dds[index].xpath("text()").get().strip()
                except:
                    pass
                a_permit_info.append({permit_name: permit_value})
            all_practices.append({"practice_name": a_name, "address": a_address, "phone": a_phone, "permit_info": a_permit_info, "view_facility_permit_link": a_view_facility_permit_link})
        
       
        #Extract all Professional Corporation Information
        professional_corporation_information = []
        try:
            corporation_lis = response.xpath("//section[@id='OtherPractices']//div[2]//div[1]//ul[1]/li[not(parent::ul/parent::li)]")
        except:
            pass
        for corporation_li in corporation_lis:
            c_address = {}
            try:
                c_address_name = corporation_li.xpath(".//address[1]//strong/text()").get().strip()
            except:
                c_address_name = ""
                pass
            try:
                c_address_value = corporation_li.xpath(".//address[1]//span[1]/text()").get().strip() + ", " + corporation_li.xpath(".//address[1]//span[2]/text()").get().strip() + ", " + corporation_li.xpath(".//address[1]//span[3]/text()").get().strip()
            except:
                c_address_value = ""
                pass
            try:
                c_address_phone = corporation_li.xpath(".//address[1]//span[4]//a/text()").get().strip()
            except:
                c_address_phone = ""
                pass
            c_address = {
                "name": c_address_name,
                "address": c_address_value,
                "phone": c_address_phone
            }
            try:
                c_permit_dts = corporation_li.xpath(".//dl/dt")
                c_permit_dds = corporation_li.xpath(".//dl/dd")
            except:
                pass
            certificate_of_authorization = []
            for index, c_permit_dt in enumerate(c_permit_dts):
                try:
                    c_permit_name = c_permit_dt.xpath("text()").get()
                except:
                    pass
                try:
                    c_permit_value = c_permit_dds[index].xpath("text()").get().strip()
                except:
                    pass
                certificate_of_authorization.append({c_permit_name: c_permit_value})
            shareholders = []
            try:
                shareholder_lis = corporation_li.xpath(".//ul//li")
            except:
                pass
            for shareholder in shareholder_lis:
                try:
                    shareholder_name = shareholder.xpath(".//a/text()").get().strip()
                except:
                    pass
                try:
                    shareholder_link = shareholder.xpath(".//a/@href").get()
                except:
                    pass
                shareholders.append({"name": shareholder_name, "link": shareholder_link})
            professional_corporation_information.append({"address": c_address, "certification_of_authorization": certificate_of_authorization, "shareholders": shareholders})
            
        #Extract academic information
        academic_information = []
        try:
            academic_names = response.xpath("//section[@id='Academic']//div[1]//h3")
            academic_values = response.xpath("//section[@id='Academic']//div[1]//dl")
        except:
            pass
        for index, academic_name in enumerate(academic_names):
            try:
                ac_name = academic_name.xpath("text()").get()
            except:
                pass
            try:
                ac_year = academic_values[index].xpath(".//dt/text()").get()
            except:
                pass
            try:
                ac_degree = academic_values[index].xpath(".//dd/text()").get()
            except:
                pass
            academic_information.append({"name": ac_name, "year": ac_year, "description": ac_degree})
            
        #Extract certificate of registration
        certificate_of_registration = []
        try:
            c_r_names = response.xpath("//section[@id='Membership']//div[1]//h3")
            c_r_values = response.xpath("//section[@id='Membership']//div[1]//dl")
        except:
            pass
        for index, c_r_name in enumerate(c_r_names):
            try:
                cr_name = c_r_name.xpath("text()").get()
            except:
                pass
            try:
                try:
                    cr_year = c_r_values[index].xpath(".//dd//time/text()").get().strip()
                except:
                    cr_year =  response.xpath("//section[@id='Membership']//div[1]//time/text").get().strip()
                    pass
            except:
                pass
            try:
                cr_description = c_r_values[index].xpath(".//dt/text()").get()
            except:
                pass
            certificate_of_registration.append({"name": cr_name, "year": cr_year, "description": cr_description})
        
        #Extract other licenses
        other_licenses = []
        try:
            o_l_divs = response.xpath("//section[@id='OtherLicenses']//div[2]//div")
        except:
            pass
        for index, o_l_div in enumerate(o_l_divs):
            try:
                ol_name = o_l_div.xpath(".//h4/text()").get()
            except:
                pass
            try:
                ol_value = o_l_div.xpath(".//div/text()").get()
            except:
                pass
            other_licenses.append({"name": ol_name, "value": ol_value})
        
        #Extract sedation & anesthesia details
        sedation_anesthesia_details = []
        try:
            s_a_d_divs = response.xpath("//section[@id='SedationAuth']//div[2]//div")
        except:
            pass
        for index, s_a_d_div in enumerate(s_a_d_divs):
            try:
                sad_name = s_a_d_div.xpath(".//h4/text()").get()
            except:
                pass
            try:
                sad_value = s_a_d_div.xpath(".//div/text()").get()
            except:
                pass
            sedation_anesthesia_details.append({"name": sad_name, "value": sad_value})
        
        #Extract dental CT scanner authorizations
        dental_ct_scanner_authorizations = ""
        try:
            dental_ct_scanner_authorizations = response.xpath("//section[@id='CTScanAuth']//div[2]/text()").get().strip()
        except:
            pass
        yield {
            "main_info" : {
                "full_name": full_name,
                "registration_number": registration_number,
                "current_status": current_status,
                "designated_electoral_district": designated_electoral_district,
                "specialty": specialty
            },
            "no_concerns": no_concerns,
            "practice_information": {
                "primary_practice": primary_practice,
                "all_practice_location": all_practices,
                "professional_corporation_information": professional_corporation_information
            },
            "academic_information": academic_information,
            "certification_of_registration": certificate_of_registration,
            "other_licenses": other_licenses,
            "dental_ct_scanner_authorizations": dental_ct_scanner_authorizations
            
        }