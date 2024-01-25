from bs4 import BeautifulSoup
import pytz
import hashlib
import unicodedata
from pyquery import PyQuery as pq
import re
import json

from requests.sessions import Session
from urllib.parse import quote, unquote, urlencode
from faker import Faker
from datetime import datetime
# from helper.utility import Utility
# from helper.exception import *
from typing import Optional, Any


from requests import RequestException


class MySQLProjectException(Exception):
    """Base exception for this script.

    :note: Pengecualian ini tidak boleh diajukan secara langsung.
    """
    pass


class HTTPErrorException(Exception):
    pass


class RequestProcessingError(RequestException):
    pass


class CSRFTokenMissingError(Exception):
    pass


class URLValidationError(Exception):
    pass


class FunctionNotFoundError(Exception):
    pass


class CookieFileNotFoundError(Exception):
    pass


class CookieCreationError(Exception):
    pass


class HtmlParser:
    """
    Provides a framework for parsing HTML content using different parsing libraries. 
    Offers flexibility in choosing parsing methods based on preferences or specific needs.
    """

    def __init__(self):
        pass

    def bs4_parser(self, html, selector):
        """
        Employs the BeautifulSoup library for parsing.
        Parses the provided HTML string using the "lxml" parser.
        Applies the specified selector to extract relevant elements.
        Handles potential exceptions and returns the parsed results.
        """
        result = None
        try:
            html = BeautifulSoup(html, "lxml")
            result = html.select(selector)
        except Exception as e:
            print(e)
        finally:
            return result

    def pyq_parser(self, html, selector):
        """
        Utilizes the PyQuery library for parsing.
        Processes the HTML string using PyQuery's syntax.
        Applies the selector to select desired elements.
        Manages exceptions and returns the extracted data.
        """
        result = None
        try:
            html = pq(html)
            result = html(selector)
        except Exception as e:
            print(e)
        finally:
            return result


class Utility:
    """
    Encapsulates a collection of utility functions for various tasks.
    """
    @staticmethod
    def hashmd5(url: str):
        """Calculates the MD5 hash of the given URL.
        Returns the hashed value as a hexadecimal string.
        """
        md5hash = hashlib.md5()
        md5hash.update(url.encode('utf-8'))
        hashed = md5hash.hexdigest()
        return hashed

    @staticmethod
    def timezone(date_time, format):
        """Converts a datetime string to the corresponding time zone offset for Asia/Jakarta.
        Takes the datetime string, a format string specifying its format, and returns the offset as a string like "+0700".
        """
        tz = pytz.timezone("Asia/Jakarta")
        date = datetime.strptime(date_time, format)
        timezone = tz.localize(date).strftime("%z")
        return timezone

    @staticmethod
    def UniqClear(text):
        """Normalizes and removes non-ASCII characters from the given text.
        Returns the ASCII-only version of the text.
        """
        normalized = unicodedata.normalize('NFKD', text)
        ascii_text = normalized.encode('ascii', 'ignore').decode('ascii')
        return ascii_text

    @staticmethod
    def makeunique(datas: list):
        """
        Removes duplicate elements from a list while preserving order.
        Returns a new list containing only unique elements.
        """
        unique_list = []
        [unique_list.append(x) for x in datas if x not in unique_list]
        return unique_list

    @staticmethod
    def convertws(data: dict):
        """
        Converts dict data to string and removes spaces at the end of the text.
        """
        dumps = json.dumps(data)
        without_whitespace = re.sub(r'\s+', '', dumps)
        return without_whitespace

    @staticmethod
    def current_funcname():
        """
        Calls the name of the function used.
        """
        import inspect
        current_frame = inspect.currentframe()
        caller_frame = inspect.getouterframes(current_frame)[1]
        function_name = caller_frame[3]
        return function_name


class XCrawl:
    def __init__(self, cookie: str = None) -> Any:
        if not isinstance(cookie, str):
            raise TypeError("Invalid parameter for 'XCrawl'. Expected str, got {}".format(
                type(cookie).__name__)
            )

        self.__cookie = cookie
        self.__session = Session()
        self.__fake = Faker()

        self.__headers = dict()
        self.__headers["Accept"] = "application/json, text/plain, */*"
        self.__headers["Accept-Language"] = "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7"
        self.__headers["Sec-Fetch-Dest"] = "empty"
        self.__headers["Sec-Fetch-Mode"] = "cors"
        self.__headers["Sec-Fetch-Site"] = "same-site"
        self.__headers["Authorization"] = "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
        if cookie is not None:
            self.__headers["Cookie"] = cookie

        self.__generatekey = lambda datas, keys:  [
            key for key in datas if key in keys
        ]

    def __guest_token(self) -> str:
        user_agent = self.__fake.user_agent()
        url = "https://api.twitter.com/1.1/guest/activate.json"
        self.__headers["User-Agent"] = user_agent
        resp = self.__session.post(
            url=url,
            headers=self.__headers,
            timeout=60
        )
        status_code = resp.status_code
        content = resp.json().get("guest_token")
        if status_code == 200:
            self.__headers.update({
                "X-Guest-Token": content
            })
            return self.__headers.get("X-Guest-Token")
        else:
            raise HTTPErrorException(
                f"Error! status code {resp.status_code} : {resp.reason}"
            )

    def __Csrftoken(self) -> str:
        pattern = re.compile(r'ct0=([a-zA-Z0-9_-]+)')
        matches = pattern.search(self.__cookie)
        if matches:
            csrftoken = matches.group(1)
            return csrftoken
        else:
            raise CSRFTokenMissingError(
                "Error! CSRF token is missing. Please ensure that a valid CSRF token is included in the cookie."
            )

    def __buildparams(self, **kwargs):
        rawquery = kwargs["rawquery"]
        count = kwargs["count"]
        cursor = kwargs["cursor"]
        product = kwargs["product"]

        variables = {
            "rawQuery": f"{rawquery}",
            "count": count,
            "cursor": f"{cursor}",
            "querySource": "typed_query",
            "product": f"{product}"
        } if cursor else {
            "rawQuery": f"{rawquery}",
            "count": count,
            "querySource": "typed_query",
            "product": f"{product}"
        }

        params = {
            "variables": variables,
            "features": {
                "responsive_web_graphql_exclude_directive_enabled": True,
                "verified_phone_label_enabled": False,
                "creator_subscriptions_tweet_preview_api_enabled": True,
                "responsive_web_graphql_timeline_navigation_enabled": True,
                "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
                "c9s_tweet_anatomy_moderator_badge_enabled": True,
                "tweetypie_unmention_optimization_enabled": True,
                "responsive_web_edit_tweet_api_enabled": True,
                "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
                "view_counts_everywhere_api_enabled": True,
                "longform_notetweets_consumption_enabled": True,
                "responsive_web_twitter_article_tweet_consumption_enabled": False,
                "tweet_awards_web_tipping_enabled": False,
                "freedom_of_speech_not_reach_fetch_enabled": True,
                "standardized_nudges_misinfo": True,
                "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
                "rweb_video_timestamps_enabled": True,
                "longform_notetweets_rich_text_read_enabled": True,
                "longform_notetweets_inline_media_enabled": True,
                "responsive_web_media_download_video_enabled": False,
                "responsive_web_enhance_cards_enabled": False
            }
        }

        return params

    def __removeallentites(self, keyword: str, datas: dict) -> dict:
        if not isinstance(datas, dict):
            raise TypeError("Invalid parameter for '__removeallentites'. Expected dict, got {}".format(
                type(datas).__name__)
            )
        if not isinstance(keyword, str):
            raise TypeError("Invalid parameter for '__removeallentites'. Expected str, got {}".format(
                type(keyword).__name__)
            )

        KEYS_REMOVE = [
            "id_str",
            "indices",
            "media_key",
            "ext_media_availability",
            "features",
            "sizes",
            "original_info",
            "additional_media_info"
        ]
        if keyword in datas["legacy"]:
            KEY_CHECK = ["hashtags", "media", "symbols",
                         "timestamps", "urls", "user_mentions"]
            for kc in KEY_CHECK:
                if kc in datas["legacy"][keyword]:
                    if "hashtags" in datas["legacy"][keyword] and datas["legacy"][keyword]["hashtags"]:
                        hashtags = []
                        try:
                            for e_hashtag in datas["legacy"][keyword]["hashtags"]:
                                hashtags.append(e_hashtag["text"])
                            datas["legacy"][keyword].update(
                                {"hashtags": hashtags})
                        except TypeError:
                            pass

                    if "media" in datas["legacy"][keyword] and datas["legacy"][keyword]["media"]:
                        for e_media in datas["legacy"][keyword]["media"]:
                            for key in self.__generatekey(
                                datas=e_media,
                                keys=KEYS_REMOVE
                            ):
                                del e_media[key]
                                if "video_info" in e_media:
                                    if "aspect_ratio" in e_media["video_info"]:
                                        del e_media["video_info"]["aspect_ratio"]
                                url = e_media["url"]

                            for key, value in datas["legacy"].items():
                                if key == "full_text":
                                    datas["legacy"].update(
                                        {
                                            key: value.replace(
                                                url, "").rstrip()
                                        }
                                    )

                    if "symbols" in datas["legacy"][keyword] and datas["legacy"][keyword]["symbols"]:
                        for e_symbol in datas["legacy"][keyword]["symbols"]:
                            for key in self.__generatekey(
                                datas=e_symbol,
                                keys=KEYS_REMOVE
                            ):
                                del e_symbol[key]

                    if "timestamps" in datas["legacy"][keyword] and datas["legacy"][keyword]["timestamps"]:
                        for e_tt in datas["legacy"][keyword]["timestamps"]:
                            for key in self.__generatekey(
                                datas=e_tt,
                                keys=KEYS_REMOVE
                            ):
                                del e_tt[key]

                    if "urls" in datas["legacy"][keyword] and datas["legacy"][keyword]["urls"]:
                        for e_url in datas["legacy"][keyword]["urls"]:
                            for key in self.__generatekey(
                                datas=e_url,
                                keys=KEYS_REMOVE
                            ):
                                del e_url[key]

                    if "user_mentions" in datas["legacy"][keyword] and datas["legacy"][keyword]["user_mentions"]:
                        for e_um in datas["legacy"][keyword]["user_mentions"]:
                            for key in self.__generatekey(
                                datas=e_um,
                                keys=[kr for kr in KEYS_REMOVE if kr != "id_str"]
                            ):
                                del e_um[key]

    def __replacechar(self, text: str, replacement: str) -> str:
        if not isinstance(text, str):
            raise TypeError("Invalid parameter for '__replacechar'. Expected str, got {}".format(
                type(text).__name__)
            )
        if not isinstance(replacement, str):
            raise TypeError("Invalid parameter for '__replacechar'. Expected str, got {}".format(
                type(replacement).__name__)
            )

        pattern = re.compile(r'_(.*?)\.jpg')
        matches = pattern.search(
            string=text.split("/")[-1]
        )
        if matches:
            replace = matches.group(1)
            result = text.replace(replace, replacement)
            return result
        return text

    def __processuserresults(self, data: dict) -> dict:
        """
        Process user results data and return a cleaned dictionary.
        """
        if not isinstance(data, dict):
            raise TypeError("Invalid parameter for '__processuserresults'. Expected dict, got {}".format(
                type(data).__name__)
            )
        datas = data["user_results"]["result"]
        KEYS_RESULT_REMOVE = [
            "affiliates_highlighted_label",
            "has_graduated_access",
            "profile_image_shape",
            "smart_blocked_by",
            "smart_blocking",
            "legacy_extended_profile",
            "is_profile_translatable",
            "has_hidden_likes_on_profile",
            "has_hidden_subscriptions_on_profile",
            "verification_info",
            "highlights_info",
            "creator_subscriptions_count"
        ]
        for key in self.__generatekey(
            datas=datas,
            keys=KEYS_RESULT_REMOVE
        ):
            del datas[key]

        KEYS_LEGACY_REMOVE = [
            "can_dm",
            "can_media_tag",
            "created_at",
            "default_profile",
            "default_profile_image",
            "fast_followers_count",
            "favourites_count",
            "followers_count",
            "friends_count",
            "has_custom_timelines",
            "is_translator",
            "listed_count",
            "media_count",
            "normal_followers_count",
            "pinned_tweet_ids_str",
            "possibly_sensitive",
            "statuses_count",
            "translator_type",
            "want_retweets",
            "withheld_in_countries"
        ]
        for key in self.__generatekey(
            datas=datas["legacy"],
            keys=KEYS_LEGACY_REMOVE
        ):
            del datas["legacy"][key]

        for key, value in datas["legacy"].items():
            if key == "entities":
                for entities_key in datas["legacy"][key]:
                    if "urls" in datas["legacy"][key][entities_key]:
                        if datas["legacy"][key][entities_key]["urls"]:
                            for item in datas["legacy"][key][entities_key]["urls"]:
                                del item["indices"]
            if key == "profile_image_url_https":
                datas["legacy"].update(
                    {
                        key: self.__replacechar(
                            value,
                            "400x400"
                        )
                    }
                )
            if key == "created_at":
                initially = datetime.strptime(
                    datas["legacy"][key], "%a %b %d %H:%M:%S +0000 %Y"
                )
                new = initially.strftime("%Y-%m-%dT%H:%M:%S")
                datas["legacy"].update({key: new})
        datas.update(
            {
                "legacy": {
                    "name": datas["legacy"].get(
                        "name", ""
                    ),
                    "screen_name": datas["legacy"].get(
                        "screen_name", ""
                    ),
                    "verified": datas["legacy"].get(
                        "verified", ""
                    ),
                    "description": datas["legacy"].get(
                        "description", ""
                    ),
                    "entities": datas["legacy"].get(
                        "entities", ""
                    ),
                    "location": datas["legacy"].get(
                        "location", ""
                    ),
                    "profile_banner_url": datas["legacy"].get(
                        "profile_banner_url", ""
                    ),
                    "profile_image_url_https": datas["legacy"].get(
                        "profile_image_url_https", ""
                    ),
                    "profile_interstitial_type": datas["legacy"].get(
                        "profile_interstitial_type", ""
                    ),
                    "url": datas["legacy"].get(
                        "url", ""
                    )
                }
            }
        )
        if "professional" not in datas:
            datas.update({"professional": {}})
        return datas

    def __processretweeted(self, data: dict) -> dict:
        """
        Process retweeted tweet data and return a cleaned dictionary.
        """
        if not isinstance(data, dict):
            raise TypeError("Invalid parameter for '__processretweeted'. Expected dict, got {}".format(
                type(data).__name__)
            )

        id = data["rest_id"] if "rest_id" in data else ""

        views = {
            key: value for key, value in data["views"].items()
            if key != "state"
        } if "views" in data else dict()

        core = {}
        if "core" in data:
            core = self.__processuserresults(data=data["core"])

        self.__removeallentites(
            keyword="entities",
            datas=data
        )
        self.__removeallentites(
            keyword="extended_entities",
            datas=data
        )

        KEYS_REMOVE = [
            "conversation_id_str",
            "display_text_range",
            "is_quote_status",
            "possibly_sensitive",
            "possibly_sensitive_editable",
            "quoted_status_id_str",
            "quoted_status_permalink",
            "favorited",
            "retweeted",
            "user_id_str",
            "id_str",
            "place"
        ]

        for key in self.__generatekey(
            datas=data["legacy"],
            keys=KEYS_REMOVE
        ):
            del data["legacy"][key]

        for key, value in data["legacy"].items():
            if key == "created_at":
                initially = datetime.strptime(
                    value, "%a %b %d %H:%M:%S +0000 %Y"
                )
                new = initially.strftime("%Y-%m-%dT%H:%M:%S")
                data["legacy"].update({key: new})

        legacy = data["legacy"]

        result = {
            "id": id,
            "views": views,
            "core": core,
            "legacy": legacy
        }
        return result

    def __processmedia(self, entry: Optional[dict] = None) -> dict:
        """
        Process media entry data and return a cleaned dictionary.
        """
        if not isinstance(entry, dict):
            raise TypeError("Invalid parameter for '__processmedia'. Expected dict, got {}".format(
                type(entry).__name__)
            )

        if "content" in entry:
            deeper = entry["content"]["itemContent"]["tweet_results"]["result"]
        else:
            if "rest_id" in entry:
                deeper = entry
            else:
                deeper = entry["tweet"]

        id = deeper["rest_id"] if "rest_id" in deeper else ""
        views = {
            key: value for key, value in deeper["views"].items()
            if key != "state"
        } if "views" in deeper else dict()

        core = {}
        if "core" in deeper:
            core = self.__processuserresults(data=deeper["core"])

        legacy = {}
        if "legacy" in deeper:
            self.__removeallentites(
                keyword="entities",
                datas=deeper
            )
            self.__removeallentites(
                keyword="extended_entities",
                datas=deeper
            )

            KEYS_REMOVE = [
                "conversation_id_str",
                "display_text_range",
                "is_quote_status",
                "possibly_sensitive",
                "possibly_sensitive_editable",
                "quoted_status_id_str",
                "quoted_status_permalink",
                "favorited",
                "retweeted",
                "user_id_str",
                "id_str",
                "place"
            ]

            for key in self.__generatekey(
                datas=deeper["legacy"],
                keys=KEYS_REMOVE
            ):
                del deeper["legacy"][key]

            legacy = deeper["legacy"]

            for key, value in legacy.items():
                if key == "created_at":
                    initially = datetime.strptime(
                        value, "%a %b %d %H:%M:%S +0000 %Y"
                    )
                    new = initially.strftime(
                        "%Y-%m-%dT%H:%M:%S")
                    legacy.update(
                        {key: new})

            if "retweeted_status_result" in legacy:
                retweeted_result: dict = legacy["retweeted_status_result"]["result"]
                rw = self.__processretweeted(data=retweeted_result)
                retweeted_result.clear()
                legacy["retweeted_status_result"]["result"].update(rw)
            elif "retweeted_status_result" not in legacy:
                legacy.update(
                    {
                        "retweeted_status_result": {}
                    }
                )

        data = {
            "id": id,
            "views": views,
            "core": core,
            "legacy": legacy
        }
        return data

    def trends(
            self,
            proxy: str = None,
            **kwargs
    ) -> dict:

        user_agent = self.__fake.user_agent()
        url_api = "https://twitter.com/i/api/2/guide.json"
        payload = {
            'include_profile_interstitial_type': 1,
            'include_blocking': 1,
            'include_blocked_by': 1,
            'include_followed_by': 1,
            'include_want_retweets': 1,
            'include_mute_edge': 1,
            'include_can_dm': 1,
            'include_can_media_tag': 1,
            'include_ext_has_nft_avatar': 1,
            'include_ext_is_blue_verified': 1,
            'include_ext_verified_type': 1,
            'include_ext_profile_image_shape': 1,
            'skip_status': 1,
            'cards_platform': 'Web-12',
            'include_cards': 1,
            'include_ext_alt_text': True,
            'include_ext_limited_action_results': True,
            'include_quote_count': True,
            'include_reply_count': 1,
            'tweet_mode': 'extended',
            'include_ext_views': True,
            'include_entities': True,
            'include_user_entities': True,
            'include_ext_media_color': True,
            'include_ext_media_availability': True,
            'include_ext_sensitive_media_warning': True,
            'include_ext_trusted_friends_metadata': True,
            'send_error_codes': True,
            'simple_quoted_tweet': True,
            'count': 20,
            'requestContext': 'launch',
            'candidate_source': 'trends',
            'include_page_configuration': False,
            'entity_tokens': False,
            'ext': 'mediaStats,highlightedLabel,hasNftAvatar,voiceInfo,birdwatchPivot,superFollowMetadata,unmentionInfo,editControl'
        }

        url = f"{url_api}?{urlencode(payload)}"

        self.__headers["User-Agent"] = user_agent
        if self.__cookie is None:
            self.__headers["X-Guest-Token"] = self.__guest_token()
        else:
            self.__headers["X-Csrf-Token"] = self.__Csrftoken()

        resp = self.__session.request(
            method="GET",
            url=url,
            timeout=60,
            proxies=proxy,
            headers=self.__headers,
            **kwargs
        )
        status_code = resp.status_code
        content = resp.content
        if status_code == 200:
            response = content.decode('utf-8')
            data = json.loads(response)
            instructions = data.get("timeline", {}).get("instructions", [])

            datas = []

            for intruction in instructions:

                if isinstance(intruction, dict) and intruction.get("addEntries", {}):

                    for entry in intruction.get("addEntries", {}).get("entries", []):
                        if entry.get("entryId") == "trends":
                            for item in entry.get("content", {}).get("timelineModule", {}).get("items", []):
                                trend_name = item.get("item", {}).get(
                                    "content", {}
                                ).get("trend", {}).get("name", "")
                                metaDescription = item.get("item", {}).get("content", {}).get(
                                    "trend", {}
                                ).get("trendMetadata", {}).get("metaDescription", "")
                                domainContext = item.get("item", {}).get("content", {}).get(
                                    "trend", {}
                                ).get("trendMetadata", {}).get("domainContext", "")

                                trend = {
                                    "name": trend_name,
                                    "metaDescription": metaDescription,
                                    "domainContext": domainContext
                                }
                                datas.append(trend)

            result = {
                "result": datas
            }
            return result
            # dumps = json.dumps(result, indent=4)
            # with open("controller/x/trends.json", "w") as file:
            #     file.write(dumps)
        else:
            HTTPErrorException(
                f"Error! status code {resp.status_code} : {resp.reason}"
            )

    def search(
            self,
            rawquery: str,
            product: str,
            count: Optional[int] = 20,
            cursor: Optional[str] = None,
            proxy: Optional[str] = None,
            **kwargs
    ) -> dict:
        """Function to search for the intended user from the given rawquery parameter value using the obtained Twitter API.

        Arguments :
          - rawquery (Required) The raw query to search for.
          - product (Required) Choose between Top, Latest, People, and Media.
          - count (Optional) Amount of data.
          - cursor (Optional) The key used to load the next page.
          - proxy (Optional) Used as an intermediary between the client and the server you access. These parameters are an important part of the request configuration and can help you direct traffic through proxy servers that may be needed for various purposes, such as security, anonymity, or access control.

        Keyword Arguments :
          - **kwargs
        """

        if isinstance(rawquery, str):
            rawquery = quote(rawquery)
        elif not isinstance(rawquery, str):
            raise TypeError("Invalid parameter for 'search'. Expected str, got {}".format(
                type(rawquery).__name__)
            )
        if not isinstance(product, str):
            raise TypeError("Invalid parameter for 'search'. Expected str, got {}".format(
                type(product).__name__)
            )
        if isinstance(count, str):
            count = int(count)
        elif not isinstance(count, int):
            raise TypeError("Invalid parameter for 'search'. Expected int, got {}".format(
                type(count).__name__)
            )
        if cursor is not None:
            if not isinstance(cursor, str):
                raise TypeError("Invalid parameter for 'search'. Expected str, got {}".format(
                    type(cursor).__name__)
                )

        user_agent = self.__fake.user_agent()
        function_name = Utility.current_funcname()

        params = self.__buildparams(
            func_name=function_name,
            rawquery=rawquery,
            product=product,
            count=count,
            cursor=cursor,
            **kwargs
        )

        for key in params:

            params.update({key: Utility.convertws(params[key])})

            if key == "variables":

                pattern = re.compile(r'"rawQuery":"([^"]+)"')
                matches = pattern.search(params["variables"])

                if matches:
                    rq_value = matches.group(1)
                    params.update(
                        {
                            "variables": params["variables"].replace(
                                rq_value, unquote(rq_value)
                            )
                        }
                    )

        variables = quote(params["variables"])
        features = quote(params["features"])
        url = "https://twitter.com/i/api/graphql/Aj1nGkALq99Xg3XI0OZBtw/SearchTimeline?variables={variables}&features={features}".format(
            variables=variables,
            features=features
        )

        self.__headers["User-Agent"] = user_agent

        if self.__cookie is None:
            self.__headers["X-Guest-Token"] = self.__guest_token()
        else:
            self.__headers["X-Csrf-Token"] = self.__Csrftoken()

        resp = self.__session.request(
            method="GET",
            url=url,
            params=params,
            timeout=60,
            proxies=proxy,
            headers=self.__headers
        )

        status_code = resp.status_code
        content = resp.content

        if status_code == 200:
            response = content.decode('utf-8')
            data = json.loads(response)

            intructions = data["data"]["search_by_raw_query"]["search_timeline"]["timeline"]["instructions"]

            datas = []

            for intruction in intructions:

                if isinstance(intruction, dict) and intruction["type"] == "TimelineAddEntries":

                    cursor_value = ""
                    for entry in intruction["entries"]:
                        match product:
                            case "People":
                                if "itemContent" in entry["content"]:
                                    user_results = entry["content"]["itemContent"]["user_results"]["result"]

                                    KEYS_RESULT_REMOVE = [
                                        "affiliates_highlighted_label",
                                        "has_graduated_access",
                                        "profile_image_shape"
                                    ]
                                    for key in self.__generatekey(
                                        datas=user_results,
                                        keys=KEYS_RESULT_REMOVE
                                    ):
                                        del user_results[key]

                                    KEYS_LEGACY_REMOVE = [
                                        "can_dm",
                                        "can_media_tag",
                                        "fast_followers_count",
                                        "has_custom_timelines",
                                        "is_translator",
                                        "possibly_sensitive",
                                        "translator_type",
                                        "want_retweets",
                                        "withheld_in_countries"
                                    ]
                                    for key in self.__generatekey(
                                        datas=user_results["legacy"],
                                        keys=KEYS_LEGACY_REMOVE
                                    ):
                                        del user_results["legacy"][key]

                                    for key, value in user_results["legacy"].items():
                                        if key == "profile_image_url_https":
                                            user_results["legacy"].update(
                                                {
                                                    key: self.__replacechar(
                                                        value,
                                                        "400x400"
                                                    )
                                                }
                                            )
                                        if key == "created_at":
                                            initially = datetime.strptime(
                                                user_results["legacy"][key], "%a %b %d %H:%M:%S +0000 %Y"
                                            )
                                            new = initially.strftime(
                                                "%Y-%m-%dT%H:%M:%S")
                                            user_results["legacy"].update(
                                                {key: new})

                                if entry["content"].get("cursorType", "") == "Bottom":
                                    cursor_value += entry["content"].get(
                                        "value", ""
                                    )
                                datas.append(user_results)

                            case "Media":
                                for key_content in entry["content"]:
                                    if "items" in key_content:
                                        for item in entry["content"]["items"]:
                                            if "item" in item:
                                                if "itemContent" in item["item"]:
                                                    deeper = item["item"]["itemContent"]["tweet_results"]["result"]
                                                    tweet_results = self.__processmedia(
                                                        entry=deeper
                                                    )
                                                    datas.append(
                                                        tweet_results
                                                    )

                                if entry["content"].get("cursorType", "") == "Bottom":
                                    cursor_value += entry["content"].get(
                                        "value", ""
                                    )

                            case "Top" | "Latest":
                                if "itemContent" in entry["content"]:

                                    deeper = entry.get("content", {}).get("itemContent", {}).get(
                                        "tweet_results", {}).get("result", {})

                                    if deeper:
                                        tweet_results = self.__processmedia(
                                            entry=deeper)
                                        datas.append(tweet_results)

                                if entry["content"].get("cursorType", "") == "Bottom":
                                    cursor_value += entry["content"].get(
                                        "value", ""
                                    )

                if isinstance(intruction, dict) and intruction["type"] == "TimelineAddToModule":

                    for entry in intruction["moduleItems"]:
                        if "item" in entry:
                            deeper = entry["item"]["itemContent"]["tweet_results"]["result"]
                            tweet_results = self.__processmedia(
                                entry=deeper
                            )
                            datas.append(tweet_results)

                if isinstance(intruction, dict) and intruction["type"] == "TimelineReplaceEntry":

                    if not cursor_value:
                        if intruction["entry"]["content"].get("cursorType", "") == "Bottom":
                            cursor_value += intruction["entry"]["content"].get(
                                "value", ""
                            )

            if not datas:
                raise HTTPErrorException(
                    "Error! status code 404 : Not Found"
                )

            result = {
                "result": datas,
                "cursor_value": cursor_value
            }

            return result
            # dumps = json.dumps(result, indent=4)
            # with open("controller/x/xcrawl.json", "w") as file:
            #     file.write(dumps)
        else:
            raise HTTPErrorException(
                f"Error! status code {resp.status_code} : {resp.reason}"
            )


if __name__ == "__main__":
    cookie = ''
    sb = XCrawl(cookie=cookie)