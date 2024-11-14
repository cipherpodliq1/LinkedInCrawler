from typing import Union
from json.decoder import JSONDecodeError

from util.session import Response
from items import Profile
from settings import settings


def __extract_4_cards(crawler, profile_id: str) -> Union[Profile, bool]:
    """
    Extracts "5 cards" information from profile page.
    this function extracts from LinkedIn account profile the following info from their cards:
    1. interests
    2. skills
    3. recommendations
    4. services

    :param crawler: a LinkedInCrawler object
    :type crawler: LinkedInCrawler

    :rtype: Profile
    :return: the extracted information in a Profile object
    """
    def __extract_recommendations(entity_component: dict) -> dict:
        return {
            "name": entity_component["titleV2"]["text"]["text"],
            "url": entity_component["image"]["actionTarget"],
            "description": entity_component["caption"]["text"],
            "headline": entity_component["subtitle"]['text'] if entity_component["subtitle"] else None,
            "review": entity_component["subComponents"]["components"][0]["components"]["fixedListComponent"]["components"][0]["components"]["textComponent"]["text"]["text"],
        }

    profile: Profile = Profile()
    req_response: Response = crawler.get(
        settings["endpoint"] + f"/voyager/api/graphql?includeWebMetadata=false&variables=(profileUrn:urn%3Ali%3Afsd_profile%3A{profile_id})&queryId=voyagerIdentityDashProfileCards.42c58dd11dfbd49a67c5b79d1e45062d"
    )

    try: response: list[dict] = req_response.json()["data"]["identityDashProfileCardsByDeferredCards"]["elements"]
    except (KeyError, TypeError, JSONDecodeError):
        crawler.logger.error(f"couldn't scrape 4 cards - invalid response from request with profile_id: '{profile_id}' check your profile_id input before contacting developer response: {req_response.text}")
        return False

    for component in response:
        if not isinstance(component, dict):
            crawler.logger.warning(f"couldn't extract one of the 4 cards for profile_id: {profile_id} invalid request (contact developer) or invalid profile_id check before retrying. request response: {req_response.text[:400]}...{req_response.text[-400:]}")
            continue
        if not component.get("topComponents"): continue
        key = component["entityUrn"].split(',')[-2].lower()
        match key:
            case 'interests':
                for interest in component["topComponents"]:
                    if not interest.get("components", {"tabComponent": None}).get("tabComponent"): continue
                    for item in interest["components"]["tabComponent"]["sections"]:
                        profile["interests"][item["label"]["text"].lower()] = [
                            {
                                "name": component_info["titleV2"]["text"]["text"],
                                "headline": component_info["subtitle"]['text'] if component_info["subtitle"] else None,
                                "followers": component_info["caption"]["text"],
                                "url": component_info["textActionTarget"]
                            }
                            for component in item['subComponent']["components"]["fixedListComponent"]["components"]
                            if (component_info := component["components"]["entityComponent"])
                        ]

            case 'skills':
                for skill in component["topComponents"]:
                    if not skill.get("components", {"fixedListComponent": None}).get("fixedListComponent"): continue
                    for item in skill["components"]["fixedListComponent"]["components"]:
                        component_info: dict = item["components"]["entityComponent"]
                        profile["skills"].append({
                                "title": component_info["titleV2"]["text"]["text"],
                                "headline": component_info["subComponents"]["components"][0]["components"]["insightComponent"]["text"]['text']['text'] if component_info["subComponents"]["components"] else None,
                                "url": component_info["textActionTarget"]
                            })

            case 'recommendations':
                for recommendation in component["topComponents"]:
                    if not recommendation["components"]["tabComponent"]: continue
                    for item in recommendation["components"]["tabComponent"]["sections"]:
                        if sub_component := (item.get("subComponent", {"subComponent": None}).get("subComponent") or item.get("subComponent", {"components": None}).get("components")):
                            profile["recommendations"]["received"] = [
                                __extract_recommendations(component)
                                for component_info in sub_component["fixedListComponent"]["components"]
                                if (component := component_info["components"]["entityComponent"])
                            ]

                        elif components := item.get("subComponent", {"components": None}).get("components"):
                            if not components["fixedListComponent"]: continue
                            profile["recommendations"]["given"] = [
                                __extract_recommendations(component)
                                for component_info in components["fixedListComponent"]["components"]
                                if (component := component_info["components"]["entityComponent"])
                            ]

            case 'services':
                for services in component["topComponents"]:
                    service = str(services)
                    title_headline: list[str] = service.split("'accessibilityText': '")
                    profile["services"].update({
                        "title": title if (title := title_headline[1].split("'", 1)[0].strip()) and len(title.split()) > 1 else None,
                        "headline": headline if (headline := title_headline[-1].split("'", 1)[0].strip().replace('Show all services link', '')) and len(headline.split()) > 1 else None,
                        "service_link": url if 'http' in (url := service.split("'deeplink': '", 1)[-1].split("'", 1)[0]) else None,
                        "more_url": url if 'http' in (url := service.split("'actionTarget': '", 5)[-1].split("'", 1)[-2]) else None,
                    })

    return profile
