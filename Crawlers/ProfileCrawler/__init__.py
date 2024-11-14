from typing import Union
from items import Profile

from Crawlers.ProfileCrawler.scrape_main_profile_cards import Scraper as CardScraper
from Crawlers.ProfileCrawler.scrape_about_and_contacts import __extract_contacts_page
from Crawlers.ProfileCrawler.scrape_profile_4_cards import __extract_4_cards
from Crawlers.ProfileCrawler.scrape_about_profile_page import Scraper as AboutScraper
from Crawlers.ProfileCrawler.scrape_profiles_recommendations import Scraper as RecommendationScraper


def extract_contacts_page(crawler, public_identifier: str, profile_id: str) -> Profile:
    profile: Union[Profile, bool] = __extract_contacts_page(crawler, public_identifier, profile_id)
    if not profile:
        crawler.logger.error(f"couldn't extract contacts page for profile_id: '{profile_id}' with public_identifier: '{public_identifier}'")
        return Profile()
    return profile


def extract_4_cards(crawler, profile_id: str) -> Profile:
    profile: Union[Profile, bool] = __extract_4_cards(crawler, profile_id)
    if not profile:
        crawler.logger.error(f"couldn't extract 4 cards layout for profile_id: '{profile_id}'")
        return Profile()
    return profile


def scrape_profile(crawler, profile_id: str) -> Profile:
    profile: Union[Profile, bool] = CardScraper().scrape_profile(crawler, profile_id)
    if not profile:
        crawler.logger.error(f"couldn't scrape profile for profile_id: '{profile_id}'")
        return Profile()
    return profile


def extract_about_page(crawler, profile_id: str) -> Profile:
    profile: Union[Profile, bool] = AboutScraper().scrape_about_profile(crawler, profile_id)
    if not profile:
        crawler.logger.error(f"couldn't extract about page for profile_id: '{profile_id}' - failed")
        return Profile()
    return profile


def extract_page_recommendations(crawler, profile_id: str) -> Profile:
    profile: Union[Profile, bool] = RecommendationScraper().scrape_profile_recommendations(crawler, profile_id)
    if not profile:
        crawler.logger.warning(f"couldn't extract side-page 'recommendations' for profile_id: '{profile_id}' - failed (contact developer) or no recommendations found")
        return Profile()
    return profile


__all__ = [
    'scrape_profile',
    'extract_contacts_page',
    'extract_4_cards',
    'extract_about_page',
    'extract_page_recommendations'
]
