from util.session import Session
from util.decorators import catch_exceptions
from settings import settings
from logger.logger import Logger
from items import Profile
from Crawlers.ProfileCrawler import (extract_contacts_page,
                                     extract_4_cards,
                                     scrape_profile,
                                     extract_about_page,
                                     extract_page_recommendations)


class LinkedInCrawler(Session):
    def __init__(self, li_at: str):
        self.logger = Logger('LinkedInCrawler')
        super(LinkedInCrawler, self).__init__()

        jsessionid: str = self.get(settings["endpoint"]).cookies.get_dict().get('JSESSIONID')
        self.headers.update(
            {
                "csrf-token": jsessionid,
                "cookie": f'li_at="{li_at}"; JSESSIONID="{jsessionid}"',
            }
        )

        self.logger.info('LinkedInCrawler initialized successfully')

    @catch_exceptions
    def run_scraper(self, profile_id: str) -> Profile:
        """
        this is the manager to run the crawler and all its functionalities for scraping a specific profile.

        :param profile_id: id of the LinkedIn profile
        :type profile_id: str

        :return: an object of Profile with all attributes
        :rtype: Profile
        """
        profile_items: dict = {}
        func_exec = lambda func, args=None: [profile_items.update({k: v}) for k, v in func(*args).items() if v and v not in profile_items.values()]

        if profile_id:
            func_exec(extract_about_page, (self, profile_id))
            func_exec(extract_4_cards, (self, profile_id))
            func_exec(scrape_profile, (self, profile_id))
            func_exec(extract_page_recommendations, (self, profile_id))
            if public_identifier := profile_items.get("public_identifier"):
                func_exec(extract_contacts_page, (self, public_identifier, profile_id))

        return Profile(**profile_items)


if __name__ == '__main__':
    crawler = LinkedInCrawler(settings['LI_AT'])
    test_profile = crawler.run_scraper('ACoAAAc-_yEBDbEZ0yk-N5U15AyZ8dwveDX9VKo')  # olawale-kolawole-751a3514
    for i in test_profile.items(): print(i)
