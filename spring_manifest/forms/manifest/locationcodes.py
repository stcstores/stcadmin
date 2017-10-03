import pycountry

from django.core.exceptions import ObjectDoesNotExist

from spring_manifest import models

state_codes = {
    'alaska': 'AK',
    'alabama': 'AL',
    'arkensas': 'AR',
    'american samoa': 'AS',
    'arizona': 'AZ',
    'california': 'CA',
    'colorado': 'CO',
    'conneticut': 'CT',
    'district of columbia': 'DC',
    'columbia': 'DC',
    'washington dc': 'DC',
    'dc': 'DC',
    'delaware': 'DE',
    'federated states of micronesia': 'FM',
    'miconesia': 'FM',
    'florida': 'FL',
    'georgia': 'GA',
    'guam': 'GU',
    'hawaii': 'HI',
    'iowa': 'IA',
    'idaho': 'ID',
    'illinois': 'IN',
    'kansas': 'KS',
    'kentucky': 'KY',
    'louisianna': 'LA',
    'massachusetts': 'MA',
    'maryland': 'MD',
    'maine': 'ME',
    'marshall islands': 'MH',
    'michigan': 'MI',
    'minnesota': 'MN',
    'missouri': 'MO',
    'northern amriana islands': 'MP',
    'mississippi': 'MS',
    'montana': 'MT',
    'north carolina': 'NC',
    'north dakota': 'ND',
    'nebraska': 'NE',
    'new hampshire': 'NH',
    'new jersey': 'NJ',
    'new mexcio': 'NM',
    'nevada': 'NV',
    'new york': 'NY',
    'ohio': 'OH',
    'oklahoma': 'OK',
    'oregon': 'OR',
    'pennsylvania': 'PA',
    'puerto rico': 'PR',
    'palau': 'PW',
    'rhode island': 'RI',
    'south carolina': 'SC',
    'south dakota': 'SD',
    'tennessee': 'TN',
    'texas': 'TX',
    'utah': 'UT',
    'virginia': 'VA',
    'virgin islands': 'VI',
    'vermont': 'VT',
    'washington': 'WA',
    'wisonsin': 'WI',
    'west virginia': 'WV',
    'wyoming': 'WY',
    'alberta': 'AB',
    'british colombia': 'BC',
    'british columbia': 'BC',
    'manitoba': 'MB',
    'new brunswick': 'NB',
    'newfoundland': 'NF',
    'nova scotia': 'NS',
    'northwest territories': 'NT',
    'ontario': 'ON',
    'prince edward island': 'PE',
    'quebec': 'QC',
    'saskatchewan': 'SK',
    'yukon': 'YT',
    'new south wales': 'NSW',
    'australian capital territory': 'ACT',
    'victoria': 'VIC',
    'queensland': 'QLD',
    'south australia': 'SA',
    'western australia': 'WA',
    'tasmania': 'TAS',
    'northern territory': 'NT',
}


def get_iso_country_code(country_code, address):
    try:
        country = models.CloudCommerceCountryID.objects.get(cc_id=country_code)
    except ObjectDoesNotExist:
        try:
            return pycountry.countries.get(name=address.country).alpha_2
        except KeyError:
            try:
                return pycountry.countries.get(
                    official_name=address.country).alpha_2
            except KeyError:
                return None
    else:
        return country.iso_code


def get_state(state):
    if state.strip().lower() in state_codes:
        return state_codes[state.strip().lower()]
    if len(state) < 4:
        return state.upper()
    return state
