from items import Profile
from settings import settings


def __extract_contacts_page(crawler, public_identifier: str, profile_id: str) -> Profile:
    """
    Extracts profile information from "contacts info" page.

    :param crawler: a LinkedInCrawler object
    :type crawler: LinkedInCrawler

    :param public_identifier: public identifier
    :type public_identifier: str

    :rtype: Profile
    :return: the extracted profile info in a Profile object
    """
    profile = Profile()

    response: dict = crawler.get(
        url=settings["endpoint"] + f'/voyager/api/graphql?includeWebMetadata=false&variables=(memberIdentity:{public_identifier})&queryId=voyagerIdentityDashProfiles.c7452e58fa37646d09dae4920fc5b4b9'
    ).json()

    try: response: list[dict] = response['data']['identityDashProfilesByMemberIdentity']['elements']
    except (KeyError, IndexError): response: list[dict] = response['included']
    except TypeError:
        crawler.logger.error(f"couldn't scrape contacts page - invalid response from request with public_identifier: '{public_identifier}' check your public_identifier input before contacting developer")
        return profile

    for info in response:
        if info.get('entityUrn', '').split(':')[-1] == profile_id:
            profile["public_identifier"] = public_identifier

            if first_name := info.get("firstName"): profile["first_name"] = first_name
            if last_name := info.get('lastName'): profile["last_name"] = last_name
            if birthdate := info.get('birthDateOn'): profile["birthdate"] = birthdate
            if address := info.get('address'): profile["address"] = address
            if email_address := info.get('emailAddress'): profile["email_address"] = email_address["emailAddress"]
            if phone_numbers := info.get('phoneNumbers'): profile["phone_numbers"] = phone_numbers
            if wechat_contact_info := info.get('weChatContactInfo'): profile["wechat_contact_info"] = wechat_contact_info
            if twitter := info.get('twitterHandles'): profile["twitter"] = twitter
            if headline := info.get('headline'): profile["headline"] = headline
            if websites := [website_url for website in info.get('websites', []) if (website_url := website.get('url', '').split('?')[0])]: profile["websites"] = websites

    return profile
