from settings import settings
from items import Profile
from typing import Union


class Scraper:
    def __init__(self):
        self.profile = Profile()

    def __extract_extra_info(self, extra_info: dict) -> None:
        self.profile["public_identifier"] = extra_info.get("publicIdentifier")
        if (prime_local := extra_info.get("primaryLocale")) and isinstance(prime_local, dict):
            self.profile["variant"] = prime_local.get("variant")
            self.profile["based_location"] = prime_local.get("country")
            self.profile["profile_language"] = prime_local.get("language")

        if first_name := extra_info.get("firstName"): self.profile["first_name"] = first_name
        if maiden_name := extra_info.get("maidenName"): self.profile["maiden_name"] = maiden_name
        if last_name := extra_info.get("lastName"): self.profile["last_name"] = last_name
        if full_name := f"{first_name} {maiden_name} {last_name}".replace('None', '').replace('  ', ' ').strip(): self.profile["fullname"] = full_name

    def __extract_elements(self, elements: list[dict]) -> None:
        items: list = []
        profile_updates: dict = {}

        for element in elements:
            if not element.get("verifiedProfileInfoSection"): continue
            for item in map(lambda x: x["veracityInfo"], element["verifiedProfileInfoSection"]): items.extend(item)
            for info in items:
                case: str = info["text"]["text"].lower()
                if case == "joined":
                    self.profile["joined_date"] = info["supplementaryText"]["text"]
                elif case == "workplace":
                    profile_updates.update({info["subtext"]["text"]: info["supplementaryText"]["text"]})
                else:
                    profile_updates.update({info["text"]["text"]: info["supplementaryText"]["text"]})
                self.profile["last_profile_updates"] = profile_updates

    def __extract_about_page_1(self, response: dict, crawler, profile_id: str) -> Profile:
        """
        Extracts profile information from "about this profile" page.

        :param crawler: a LinkedInCrawler object
        :type crawler: LinkedInCrawler

        :param profile_id: profile id to scrape
        :type profile_id: str

        :rtype: Profile
        :return: the extracted profile info in a Profile object
        """
        try: extra_info: dict = response['included'][0]
        except (KeyError, IndexError): crawler.logger.warning(f"couldn't scrape full about page info some profile info will be lost - invalid response from request with profile_id: '{profile_id}' check your profile_id input before contacting developer")
        else: self.__extract_extra_info(extra_info)
        try:
            if response.get('data', {"data": None}).get("data"):
                elements: list[dict] = response['data']['data']['identityDashProfileVerifiedInfoByVerifiedInfoUseCase']['elements']
            else: elements: list[dict] = response['data']['identityDashProfileVerifiedInfoByVerifiedInfoUseCase']['elements']
        except (TypeError, KeyError):
            crawler.logger.error(f"couldn't scrape about page - invalid response from request from page with profile_id: '{profile_id}' check your profile_id input before contacting developer")
            return self.profile
        else: self.__extract_elements(elements)

        return self.profile

    def __extract_about_page_2(self, response: dict, crawler, profile_id: str) -> Union[Profile, bool]:
        """
        Extracts profile information from "about this profile" page.

        :rtype: Profile
        :return: the extracted profile info in a Profile object
        """
        try: response: list[dict] = response["data"]["identityDashProfileVerifiedInfoByVerifiedInfoUseCase"]["elements"]
        except (KeyError, TypeError):
            crawler.logger.error(f"couldn't scrape about page - invalid response from request with profile_id: '{profile_id}' check your profile_id input before contacting developer response: {response}")
            return False

        self.__extract_extra_info(response[0]["viewee"])
        self.__extract_elements(response)
        return self.profile

    def scrape_about_profile(self, crawler, profile_id: str) -> Union[Profile, bool]:
        response: dict = crawler.get(
            url=settings["endpoint"] + f'/voyager/api/graphql?variables=(profileUrn:urn%3Ali%3Afsd_profile%3A{profile_id},useCase:PROFILE)&queryId=voyagerIdentityDashProfileVerifiedInfo.f436a65c265ef6d32cea7d10b5280833'
        ).json()

        self.profile["profile_id"] = profile_id
        if response.get('included'): return self.__extract_about_page_1(response, crawler, profile_id)
        elif response.get('data'): return self.__extract_about_page_2(response, crawler, profile_id)

        crawler.logger.error(f"couldn't scrape about page - invalid response from request with profile_id: '{profile_id}' contacting developer page response {response}")
        return self.profile
