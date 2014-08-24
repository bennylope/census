__title__ = "census"
__version__ = "0.6"

import json
import requests

from functools import wraps
from xml.etree.ElementTree import XML
from .exceptions import APIKeyError, CensusException, UnsupportedYearException


ALL = '*'  # Used to query all states
ENDPOINT_URL = 'http://api.census.gov/data/%s/%s'
DEFINITIONS = {
    'acs5': {
        # '2012': 'http://api.census.gov/data/2012/acs5/variables.xml',
        '2011': 'http://api.census.gov/data/2011/acs5/variables.xml',
        '2010': 'http://api.census.gov/data/2010/acs5/variables.xml',
    },
    'acs1/profile': {
        '2012': 'http://api.census.gov/data/2012/acs1/profile/variables.xml',
    },
    'sf1': {
        '2010': 'http://api.census.gov/data/2010/sf1/variables.xml',
        '2000': 'http://api.census.gov/data/2000/sf1/variables.xml',
        '1990': 'http://api.census.gov/data/1990/sf1/variables.xml',
    },
    'sf3': {
        '2000': 'http://api.census.gov/data/2000/sf3/variables.xml',
        '1990': 'http://api.census.gov/data/1990/sf3/variables.xml',
    },
}


def supported_years(*years):
    """
    Decorator verifies requested year is available from the specified years
    argument.
    """
    def inner(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            year = kwargs.get('year', self.default_year)
            if int(year) not in years:
                raise UnsupportedYearException('geography is not available in %s' % year)
            return func(self, *args, **kwargs)
        return wrapper
    return inner


class Client(object):
    """
    Base client class for interacting with the Census API.
    """

    def __init__(self, key, year=None, session=None):
        self._key = key
        self.session = session or requests.session()
        if year:
            self.default_year = year

    @property
    def years(self):
        return [int(y) for y in DEFINITIONS[self.dataset].keys()]

    def fields(self, year, flat=False):

        data = {}

        fields_url = DEFINITIONS[self.dataset].get(str(year))

        if not fields_url:
            raise CensusException('%s is not available for %s' % (self.dataset, year))

        resp = requests.get(fields_url)
        doc = XML(resp.text)

        if flat:

            for elem in doc.iter('variable'):
                data[elem.attrib['name']] = "%s: %s" % (elem.attrib['concept'], elem.text)

        else:

            for concept_elem in doc.iter('concept'):

                concept = concept_elem.attrib['name']
                variables = {}

                for variable_elem in concept_elem.iter('variable'):
                    variables[variable_elem.attrib['name']] = variable_elem.text

                data[concept] = variables

        return data

    def get(self, fields, geo, year=None):

        if len(fields) > 50:
            raise CensusException("only 50 columns per call are allowed")

        if year is None:
            year = self.default_year

        fields = fields if isinstance(fields, (list, tuple)) else [fields]

        url = ENDPOINT_URL % (year, self.dataset)

        params = {
            'get': ",".join(fields),
            'for': geo['for'],
            'key': self._key,
        }

        if 'in' in geo:
            params['in'] = geo['in']

        headers = {
            'User-Agent': 'python-census/%s github.com/sunlightlabs/census' % __version__
        }
        resp = self.session.get(url, params=params, headers=headers)

        if resp.status_code == 200:
            try:
                data = json.loads(resp.text)
            except ValueError as ex:
                if '<title>Invalid Key</title>' in resp.text:
                    raise APIKeyError(' '.join(resp.text.splitlines()))
                else:
                    raise ex

            headers = data[0]
            return [dict(zip(headers, d)) for d in data[1:]]

        elif resp.status_code == 204:
            return []

        else:
            raise CensusException(resp.text)


class ACS5Client(Client):
    """
    Client class for querying the American Community Survey 5 Year data set.

    http://www.census.gov/data/developers/data-sets/acs-survey-5-year-data.html
    """

    default_year = 2011
    dataset = 'acs5'

    @supported_years(2011, 2010)
    def us(self, fields, **kwargs):
        return self.get(fields, geo={'for': 'us:1'}, **kwargs)

    @supported_years(2011, 2010)
    def state(self, fields, state_fips, **kwargs):
        return self.get(fields, geo={
            'for': 'state:%s' % state_fips,
        }, **kwargs)

    @supported_years(2011, 2010)
    def state_county(self, fields, state_fips, county_fips, **kwargs):
        return self.get(fields, geo={
            'for': 'county:%s' % county_fips,
            'in': 'state:%s' % state_fips,
        }, **kwargs)

    @supported_years(2011, 2010)
    def state_county_subdivision(self, fields, state_fips, county_fips, subdiv_fips, **kwargs):
        return self.get(fields, geo={
            'for': 'county subdivision:%s' % subdiv_fips,
            'in': 'state:%s county:%s' % (state_fips, county_fips),
        }, **kwargs)

    @supported_years(2011, 2010)
    def state_county_tract(self, fields, state_fips, county_fips, tract, **kwargs):
        return self.get(fields, geo={
            'for': 'tract:%s' % tract,
            'in': 'state:%s county:%s' % (state_fips, county_fips),
        }, **kwargs)

    @supported_years(2011, 2010)
    def state_place(self, fields, state_fips, place, **kwargs):
        return self.get(fields, geo={
            'for': 'place:%s' % place,
            'in': 'state:%s' % state_fips,
        }, **kwargs)

    @supported_years(2011, 2010)
    def state_district(self, fields, state_fips, district, **kwargs):
        return self.get(fields, geo={
            'for': 'congressional district:%s' % district,
            'in': 'state:%s' % state_fips,
        }, **kwargs)

    @supported_years(2011)
    def zipcode(self, fields, zcta, **kwargs):
        return self.get(fields, geo={
            'for': 'zip code tabulation area:%s' % zcta,
        }, **kwargs)


class ACS1DpClient(Client):
    """
    Client class for querying the American Community Survey 1 Year data set.

    http://www.census.gov/data/developers/data-sets/acs-survey-1-year-data.html
    """

    default_year = 2012
    dataset = 'acs1/profile'

    @supported_years(2012)
    def us(self, fields, **kwargs):
        return self.get(fields, geo={'for': 'us:1'}, **kwargs)

    @supported_years(2012)
    def state(self, fields, state_fips, **kwargs):
        return self.get(fields, geo={
            'for': 'state:%s' % state_fips,
        }, **kwargs)

    @supported_years(2012)
    def state_district(self, fields, state_fips, district, **kwargs):
        return self.get(fields, geo={
            'for': 'congressional district:%s' % district,
            'in': 'state:%s' % state_fips,
        }, **kwargs)


class SF1Client(Client):
    """
    Client class for querying Summary File 1 data from the Decennial Census
    data sets.

    As described by the Census Bureau:

        Summary File 1 (SF 1) contains the data compiled from the questions
        asked of all people and about every housing unit. Population items
        include sex, age, race, Hispanic or Latino origin, household
        relationship, household type, household size, family type, family size,
        and group quarters. Housing items include occupancy status, vacancy
        status, and tenure (whether a housing unit is owner-occupied or
        renter-occupied).

        SF 1 includes population and housing characteristics for the total
        population, population totals for an extensive list of race (American
        Indian and Alaska Native tribes, Asian, and Native Hawaiian and Other
        Pacific Islander) and Hispanic or Latino groups, and population and
        housing characteristics for a limited list of race and Hispanic or
        Latino groups. Population and housing items may be cross-tabulated.
        Selected aggregates and medians also are provided.

    http://www.census.gov/data/developers/data-sets/decennial-census-data.html
    """

    default_year = 2010
    dataset = 'sf1'

    @supported_years(2010, 2000, 1990)
    def state(self, fields, state_fips, **kwargs):
        return self.get(fields, geo={
            'for': 'state:%s' % state_fips,
        }, **kwargs)

    @supported_years(2010, 2000, 1990)
    def state_county(self, fields, state_fips, county_fips, **kwargs):
        return self.get(fields, geo={
            'for': 'county:%s' % county_fips,
            'in': 'state:%s' % state_fips,
        }, **kwargs)

    @supported_years(2010)
    def state_county_subdivision(self, fields, state_fips, county_fips, subdiv_fips, **kwargs):
        return self.get(fields, geo={
            'for': 'county subdivision:%s' % subdiv_fips,
            'in': 'state:%s county:%s' % (state_fips, county_fips),
        }, **kwargs)

    @supported_years(2010, 2000, 1990)
    def state_county_tract(self, fields, state_fips, county_fips, tract, **kwargs):
        return self.get(fields, geo={
            'for': 'tract:%s' % tract,
            'in': 'state:%s county:%s' % (state_fips, county_fips),
        }, **kwargs)

    @supported_years(2010, 2000, 1990)
    def state_place(self, fields, state_fips, place, **kwargs):
        return self.get(fields, geo={
            'for': 'place:%s' % place,
            'in': 'state:%s' % state_fips,
        }, **kwargs)

    @supported_years(2010)
    def state_district(self, fields, state_fips, district, **kwargs):
        return self.get(fields, geo={
            'for': 'congressional district:%s' % district,
            'in': 'state:%s' % state_fips,
        }, **kwargs)

    @supported_years(2010)
    def state_msa(self, fields, state_fips, msa, **kwargs):
        return self.get(fields, geo={
            'for': 'metropolitan statistical area/micropolitan statistical area:%s' % msa,
            'in': 'state:%s' % state_fips,
        }, **kwargs)

    @supported_years(2010)
    def state_csa(self, fields, state_fips, csa, **kwargs):
        return self.get(fields, geo={
            'for': 'combined statistical area:%s' % csa,
            'in': 'state:%s' % state_fips,
        }, **kwargs)

    @supported_years(2010)
    def state_district_place(self, fields, state_fips, district, place, **kwargs):
        return self.get(fields, geo={
            'for': 'place:' % place,
            'in': 'state:%s congressional district:%s' % (state_fips, district),
        }, **kwargs)

    @supported_years(2010)
    def state_zipcode(self, fields, state_fips, zcta, **kwargs):
        return self.get(fields, geo={
            'for': 'zip code tabulation area:%s' % zcta,
            'in': 'state:%s' % state_fips,
        }, **kwargs)


class SF3Client(Client):
    """
    Client class for querying Summary File 3 data from the Decennial Census
    data sets.

    As described by the Census Bureau:

        Summary File 3 consists of 813 detailed tables of Census [2000] social,
        economic and housing characteristics compiled from a sample of
        approximately 19 million housing units (about 1 in 6 households) that
        received the Census [2000] long-form questionnaire.

    http://www.census.gov/data/developers/data-sets/decennial-census-data.html
    """

    default_year = 2000
    dataset = 'sf3'

    @supported_years(2000, 1990)
    def state(self, fields, state_fips, **kwargs):
        return self.get(fields, geo={
            'for': 'state:%s' % state_fips,
        }, **kwargs)

    @supported_years(2000, 1990)
    def state_county(self, fields, state_fips, county_fips, **kwargs):
        return self.get(fields, geo={
            'for': 'county:%s' % county_fips,
            'in': 'state:%s' % state_fips,
        }, **kwargs)

    @supported_years(2000, 1990)
    def state_county_tract(self, fields, state_fips, county_fips, tract, **kwargs):
        return self.get(fields, geo={
            'for': 'tract:%s' % tract,
            'in': 'state:%s county:%s' % (state_fips, county_fips),
        }, **kwargs)

    @supported_years(2000, 1990)
    def state_place(self, fields, state_fips, place, **kwargs):
        return self.get(fields, geo={
            'for': 'place:%s' % place,
            'in': 'state:%s' % state_fips,
        }, **kwargs)


class Census(object):
    """
    Master client class which provides the primary interface for querying all
    Census data.
    """

    ALL = ALL  # Convenience attribute for querying all states

    def __init__(self, key, year=None, session=None):

        if not session:
            session = requests.session()

        self.acs = ACS5Client(key, year, session)
        self.acs5 = ACS5Client(key, year, session)
        self.acs1dp = ACS1DpClient(key, year, session)
        self.sf1 = SF1Client(key, year, session)
        self.sf3 = SF3Client(key, year, session)
