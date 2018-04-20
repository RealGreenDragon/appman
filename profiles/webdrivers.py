from ._base import Meta_Profile

class Webdrivers_Meta_Profile(Meta_Profile):

    meta_name = 'Webdrivers'

    programs = set(['webdriver-chrome', 'webdriver-edge', 'webdriver-firefox', 'webdriver-ie'])
