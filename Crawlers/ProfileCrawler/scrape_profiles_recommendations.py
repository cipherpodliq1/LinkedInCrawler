from util.session import Response
import json.decoder
from typing import Union
from settings import settings
from items import Profile


class Scraper:
    @staticmethod
    def __extract_profile_recommendations_1(response: str, crawler, profile_id: str) -> Union[Profile, bool]:
        profiles = set()
        for item in response.split(','):
            if "urn:li:fsd_profile" not in item: continue
            profile_id: str = item.replace(" ", "").split(":")[-1].split('"')[0]
            if len(profile_id) != 39: continue
            profiles.add(profile_id)

        profile = Profile()
        profile.recommended_profiles_ids = list(profiles)
        if not profile.recommended_profiles_ids:
            if len(str(response)) > 750: crawler.logger.error(f"couldn't extract profile recommendations for profile_id {profile_id} response: {response} - func 1")
            return False
        return profile

    @staticmethod
    def __extract_profile_recommendations_2(response: list[dict], crawler, profile_id: str) -> Union[Profile, bool]:
        """
        Extracts the profile recommendations at the page side from the profile page.

        :param crawler: a LinkedInCrawler object
        :type crawler: LinkedInCrawler

        :param profile_id: profile id to scrape
        :type profile_id: str

        :param verbose: whether to print error messages or not
        :type verbose: bool

        :rtype: bool | None | str
        :return: an object of Profile with all attributes
        """
        profile = Profile()
        for profile_id in response:
            if not profile_id.get("entityUrn"): continue
            profile.recommended_profiles_ids.append(
                profile_id["entityUrn"].split(":")[-1]
            )

        if not profile.recommended_profiles_ids:
            if len(str(response)) > 750: crawler.logger.error(f"couldn't extract profile recommendations for profile_id {profile_id} response: {response} - func 2")
            return False

        return profile

    def scrape_profile_recommendations(self, crawler, profile_id: str) -> Union[Profile, bool]:
        """
        Extracts the profile recommendations at the page side from the profile page.

        :param crawler: a LinkedInCrawler object
        :type crawler: LinkedInCrawler

        :param profile_id: profile id to scrape
        :type profile_id: str

        :param verbose: whether to print error messages or not
        :type verbose: bool

        :rtype: bool | None | str
        :return: an object of Profile with all attributes
        """
        response: Response = crawler.get(
            url=settings["endpoint"] + f'/voyager/api/graphql?includeWebMetadata=false&variables=(profileUrn:urn%3Ali%3Afsd_profile%3A{profile_id})&queryId=voyagerIdentityDashProfileCards.3d73369275fe09171bcb7731cc8f71fe'
        )

        try:
            response: list[dict] = response.json()["included"]; response[0]["entityUrn"]
            return self.__extract_profile_recommendations_2(response, crawler, profile_id)
        except (json.decoder.JSONDecodeError, IndexError, KeyError):
            return self.__extract_profile_recommendations_1(response.text, crawler, profile_id)
