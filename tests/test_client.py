import unittest

from census import Client
from mock import patch, MagicMock


class TestClient(unittest.TestCase):

    def setUp(self):
        self.sample_response = """
<census-api xmlns="http://thedataweb.rm.census.gov/api/discovery/" xmlns:dcat="http://www.w3.org/ns/dcat#" xmlns:dct="http://purl.org/dc/terms/" xmlns:pod="http://project-open-data.github.io/schema/">
    <vars>
        <var xml:id="SDSEC" label="GEO PLACE HOLDER" concept="Geographic Summary Level"/>
        <var xml:id="DIVISION" label="GEO PLACE HOLDER" concept="Geographic Summary Level"/>
        <var xml:id="REGION" label="GEO PLACE HOLDER" concept="Geographic Summary Level"/>
        <var xml:id="BLKGRP" label="GEO PLACE HOLDER" concept="Geographic Summary Level"/>
        <var xml:id="SLDU" label="GEO PLACE HOLDER" concept="Geographic Summary Level"/>
        <var xml:id="TRACT" label="Tract (FIPS))" concept="Geographic Summary Level"/>
        <var xml:id="SUBMCD" label="GEO PLACE HOLDER" concept="Geographic Summary Level"/>
        <var xml:id="COUNTY" label="County (FIPS))" concept="Geographic Summary Level"/>
        <var xml:id="NECTA" label="GEO PLACE HOLDER" concept="Geographic Summary Level"/>
        <var xml:id="STATE" label="State (FIPS)" concept="Geographic Summary Level"/>
        <var xml:id="CSA" label="GEO PLACE HOLDER" concept="Geographic Summary Level"/>
        <var xml:id="CD" label="GEO PLACE HOLDER" concept="Geographic Summary Level"/>
        <var xml:id="SDUNI" label="GEO PLACE HOLDER" concept="Geographic Summary Level"/>
        <var xml:id="COUSUB" label="GEO PLACE HOLDER" concept="Geographic Summary Level"/>
        <var xml:id="CONCIT" label="GEO PLACE HOLDER" concept="Geographic Summary Level"/>
        <var xml:id="BLOCK" label="GEO PLACE HOLDER"/>
        <var xml:id="AIANHH" label="GEO PLACE HOLDER" concept="Geographic Summary Level"/>
        <var xml:id="SDELEM" label="GEO PLACE HOLDER" concept="Geographic Summary Level"/>
        <var xml:id="CBSA" label="GEO PLACE HOLDER" concept="Geographic Summary Level"/>
        <var xml:id="PLACE" label="Place (FIPS))" concept="Geographic Summary Level"/>
        <var xml:id="SLDL" label="GEO PLACE HOLDER" concept="Geographic Summary Level"/>
        <var xml:id="PCT013B007" label="Male: !! 18 and 19 years" concept="PCT13B. SEX BY AGE FOR THE POPULATION IN HOUSEHOLDS (BLACK OR AFRICAN AMERICAN ALONE) [49]"/>
        <var xml:id="PCT013B026" label="Female: !! 85 years and over" concept="PCT13B. SEX BY AGE FOR THE POPULATION IN HOUSEHOLDS (BLACK OR AFRICAN AMERICAN ALONE) [49]"/>
        <var xml:id="PCT013H030" label="Female: !! 15 to 17 years" concept="PCT13H. SEX BY AGE FOR THE POPULATION IN HOUSEHOLDS (HISPANIC OR LATINO) [49]"/>
        <var xml:id="H0190001" label="Occupied housing units" concept="H19. TENURE BY PRESENCE OF PEOPLE UNDER 18 YEARS (EXCLUDING HOUSEHOLDERS, SPOUSES, AND UNMARRIED PARTNERS) [7]"/>
        <var xml:id="P031B006" label="In households: !! Related child: !! Own child: !! In husband-wife family" concept="P31B. HOUSEHOLD TYPE BY RELATIONSHIP FOR THE POPULATION UNDER 18 YEARS (BLACK OR AFRICAN AMERICAN ALONE) [16]"/>
        <var xml:id="H0040002" label="Owned with a mortgage or a loan" concept="H4. TENURE [4]"/>
    </vars>
</census-api>"""
        self.client = Client("WHATEVERKEYIWANT", year=2010)

    @patch('census.requests')
    def test_fields(self, mocked_requests):
        """"""
        mocked_result = MagicMock()
        mocked_result.text = self.sample_response
        mocked_requests.get.return_value = mocked_result

        # print self.client.fields("sf1", "2010")

        self.assertTrue(isinstance(self.client.fields("sf1", "2010"), dict))
        self.assertTrue('H0040002' in self.client.fields("sf1", "2010"))


if __name__ == '__main__':
    unittest.main()
