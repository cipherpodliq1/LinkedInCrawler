import json
from typing import Optional
from util.decorators import catch_exceptions
from settings import settings


@catch_exceptions
def search_people(
        crawler: 'LinkedInCrawler',
        keyword: str,
        geo_filter_id: Optional[str] = None,
        starting_page: int = 0,
        max_pages: int = 100,
) -> dict:
    """
    return found search results for a keyword with specific filters.

    :param crawler: a LinkedInCrawler object
    :type crawler: LinkedInCrawler

    :param starting_page: starting page
    :type starting_page: int

    :param max_pages: max pages to scrape from (each page returns 10 results)
    :type max_pages: int

    :param keyword: search keyword
    :type keyword: str

    :param geo_filter_id: search filters
    :type geo_filter_id: Optional[str]

    :param verbose_logger: if the logger should show warnings or not
    :type verbose_logger: bool

    :rtype: Profile
    :yield: found search result
    """
    if max_pages > 100:
        crawler.logger.warning(f"max_pages can't be set to {max_pages} now it's set to the default and max value which is '100' with a max results of '1000' LinkedIn profiles_ids.")
        max_pages: int = 100

    if starting_page > max_pages or starting_page < 0:
        crawler.logger.warning(f"starting_page can't be set to '{starting_page}' now it's set to the default value which is '0'.")
        starting_page: int = 0

    for next_page in range(starting_page, max_pages * 10, 10):
        if geo_filter_id: query_parameters: str = f"List((key:geoUrn,value:List({geo_filter_id})),(key:resultType,value:List(PEOPLE))),includeFiltersInResponse:false))"
        else: query_parameters: str = "List((key:resultType,value:List(PEOPLE))),includeFiltersInResponse:false))"

        try:
            response: Optional[dict] = crawler.get(
                url=settings['endpoint'] + f'/voyager/api/graphql?includeWebMetadata=false&variables=(start:{next_page},origin:GLOBAL_SEARCH_HEADER,query:(keywords:{keyword},flagshipSearchIntent:SEARCH_SRP,queryParameters:{query_parameters}&queryId=voyagerSearchDashClusters.dec2e0cf0d4c89523266f6e3b44cc87c'
            ).json().get("data")
        except (AttributeError, json.decoder.JSONDecodeError):
            crawler.logger.warning(f'No more results found for keyword: {keyword}')
            return {}

        try:
            response: list[dict] = (                         # response["data"]["data"]["searchDashClustersByAll"]
                    response.get("searchDashClustersByAll") or response.get('data').get("searchDashClustersByAll")
            )["elements"]
        except (TypeError, KeyError, AttributeError):
            crawler.logger.warning(f'No results found for keyword: {keyword}')
            return {}

        for item in map(lambda items: items["items"], response):
            for urn_link in item:
                if urn := (urn_link["item"].get("*entityResult") or urn_link["item"].get("entityResult")):
                    yield str(urn).split("fsd_profile:", 1)[-1].split(',', 1)[0]


if __name__ == '__main__':
    from Crawlers.ProfileScraper import LinkedInCrawler

    scraper = LinkedInCrawler(settings['li_at'])
    for i in search_people(scraper, 'muhammad'): print(i)
