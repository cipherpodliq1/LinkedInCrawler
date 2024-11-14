from json.decoder import JSONDecodeError
from util.session import Response
from typing import Optional, Union
from settings import settings
from items import Profile


class Scraper:
    @staticmethod
    def __extract_about(text_component: Optional[dict]) -> Optional[dict]:
        if text_component:
            return text_component["text"]["text"]

    @staticmethod
    def __extract_experience(fixed_list_component: Optional[dict]) -> Union[list[dict], dict]:
        if not fixed_list_component: return {}
        if not fixed_list_component["components"]: return {}
        return [
            {
                "title": comp["components"]['entityComponent']['titleV2']['text']["text"],
                "description": comp["components"]['entityComponent']['subtitle']['text'],
                "location": (comp["components"]['entityComponent']['metadata'] or {"text": None})['text'],
                "date": (comp["components"]['entityComponent']['caption'] or {"text": None})['text'],
            }
            for comp in fixed_list_component["components"]
            if comp["components"]
        ]

    @staticmethod
    def __extract_education(fixed_list_component: Optional[dict]) -> Union[list[dict], dict]:
        if not fixed_list_component: return {}
        if not fixed_list_component["components"]: return {}
        return [
            {
                "title": comp["components"]['entityComponent']['titleV2']['text']["text"],
                "description": (comp["components"]['entityComponent']['subtitle'] or {"text": None})['text'],
                "date": (comp["components"]['entityComponent']['caption'] or {"text": None})['text'],
            }
            for comp in fixed_list_component["components"]
            if comp["components"]
        ]

    @staticmethod
    def __extract_licenses_and_certifications(fixed_list_component: Optional[dict]) -> Union[list[dict], dict]:
        if not fixed_list_component: return {}
        if not fixed_list_component["components"]: return {}
        return [
            {
                "title": comp["components"]['entityComponent']['titleV2']['text']["text"],
                "description": (comp["components"]['entityComponent'].get('subtitle') or {"text": None})['text'],
                "date": (comp["components"]['entityComponent']['caption'] or {"text": None})['text'],
            }
            for comp in fixed_list_component["components"]
            if comp["components"]
        ]

    @staticmethod
    def __extract_volunteering_experience(fixed_list_component: Optional[dict]) -> Union[list[dict], dict]:
        if not fixed_list_component: return {}
        if not fixed_list_component["components"]: return {}

        volunteering_experiences_list: list = []
        for comp in fixed_list_component["components"]:
            if not comp["components"]: continue
            description: Union[list[dict], None] = (comp["components"]['entityComponent']['subComponents'] or {"components": None}).get('components')
            if description: description: str = description[0]['components']['textComponent']['text']['text']
            volunteering_experiences_list.append({
                "title": comp["components"]['entityComponent']['titleV2']['text']["text"],
                "description": description,
                "date": (comp["components"]['entityComponent']['caption'] or {"text": None})['text'],
            })

        return volunteering_experiences_list

    @staticmethod
    def __extract_languages(fixed_list_component: Optional[dict]) -> Union[list[str], list]:
        if not fixed_list_component: return []
        if not fixed_list_component["components"]: return []
        return [
            comp["components"]['entityComponent']['titleV2']['text']["text"]
            for comp in fixed_list_component["components"]
            if comp["components"]
        ]

    @staticmethod
    def __extract_volunteer_causes(text_component: dict) -> Optional[dict]:
        if text_component: return text_component["text"]["text"]

    def scrape_profile(self, crawler, profile_id: str) -> Union[Profile, bool]:
        """
        this function scrapes the main profile page and returns the extracted information in a dictionary

        :param crawler:
        :type crawler: an object of LinkedInCrawler

        :param profile_id: LinkedIn profileUrn to scrape from
        :type profile_id: str

        :rtype: Profile
        :return: a Profile object with all the extracted information from the profile
        """
        profile: Profile = Profile()

        req_response: Response = crawler.get(
            settings['endpoint'] + f'/voyager/api/graphql?variables=(profileUrn:urn%3Ali%3Afsd_profile%3A{profile_id})&queryId=voyagerIdentityDashProfileCards.abf1d77cbd7b2aa4fe448cec18b44f2b'
        )
        try: response: list[dict] = req_response.json()["data"]["identityDashProfileCardsByInitialCards"]["elements"]
        except (KeyError, IndexError, TypeError, JSONDecodeError):
            if settings["VERBOSE"]: crawler.logger.error(f"couldn't scrape main profile page for profile_id: {profile_id} response: {req_response.text}")
            return False

        for component in response:
            if not component["topComponents"]: continue
            key = component["entityUrn"].split(',')[-2].lower()
            match key:
                case 'about':
                    profile["about"] = [
                        self.__extract_about(component_info)
                        for component_data in component["topComponents"]
                        if (component_info := component_data['components']["textComponent"])
                    ]

                case 'experience':
                    profile["experience"] = [
                        self.__extract_experience(component_info)
                        for component_data in component["topComponents"]
                        if (component_info := component_data['components']["fixedListComponent"])
                    ]

                case 'education':
                    profile["education"] = [
                        self.__extract_education(component_info)
                        for component_data in component["topComponents"]
                        if (component_info := component_data['components']["fixedListComponent"])
                    ]

                case 'licenses_and_certifications':
                    profile["licenses_and_certifications"] = [
                        self.__extract_licenses_and_certifications(component_info)
                        for component_data in component["topComponents"]
                        if (component_info := component_data['components']["fixedListComponent"])
                    ]

                case 'volunteering_experience':
                    profile["volunteering_experience"] = [
                        self.__extract_volunteering_experience(component_info)
                        for component_data in component["topComponents"]
                        if (component_info := component_data['components']["fixedListComponent"])
                    ]

                case 'languages':
                    profile["languages"] = [
                        self.__extract_languages(component_info)
                        for component_data in component["topComponents"]
                        if (component_info := component_data["components"]["fixedListComponent"])
                    ]

                case 'interests':
                    profile["languages"] = [
                        print(component_info)  # self.__extract_interests(component_info)
                        for component_data in component["topComponents"]
                        if (component_info := component_data["components"]["fixedListComponent"])
                    ]

                case 'volunteer_causes':
                    profile["volunteer_causes"] = [
                        self.__extract_volunteer_causes(component_info)
                        for component_data in component["topComponents"]
                        if (component_info := component_data["components"]["textComponent"])
                    ]

        return profile
