import time

from Crawlers.ProfileScraper import LinkedInCrawler
from util.database import Database
from logger.logger import Logger
from settings import settings
from items import Profile
from typing import Union

logger: Logger = Logger("Control")
crawler: LinkedInCrawler = LinkedInCrawler(settings['LI_AT'])
insert_db_conn: Database = Database(settings['DATABASE'])


def main() -> None:
    while True:
        time.sleep(1)
        profiles_counter: int = 0
        total_counter: int = 0
        db: Database = Database(settings['DATABASE'])
        logger.debug(f"looping through database for scraping the new recommended profiles_ids.")
        for db_id, profile_id in db.fetch_all("profiles_ids"):
            total_counter += 1
            if total_counter > 0 and total_counter % 100 == 0:
                logger.info(f"Finished checking '{total_counter}' profiles_ids from the database.")

            profile: Union[Profile, bool] = crawler.run_scraper(profile_id)

            db.delete_record("profiles_ids", db_id)
            if not (profile and isinstance(profile, Profile)) or not profile.public_identifier:
                insert_db_conn.insert_profile_id((profile_id,), "failed_ids")
                continue

            if profile.insert_to_db(insert_db_conn):
                logger.info(f"scraped and inserted a new profile: '{profile_id}' to database")
            else:
                insert_db_conn.insert_profile_id((profile_id, ), "failed_ids")
                logger.warning(f"couldn't scrape from profile_id: '{profile_id}' will be flagged as a failure")

            for _id in profile.recommended_profiles_ids:
                insert_db_conn.insert_profile_id((_id, ))
                profiles_counter += 1

        if profiles_counter > 0:
            logger.info(f"Found & inserted '{profiles_counter}' new profiles_ids ready for scraping")


if __name__ == '__main__':
    main()
