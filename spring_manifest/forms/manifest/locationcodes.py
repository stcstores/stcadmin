import pycountry

from django.core.exceptions import ObjectDoesNotExist

from spring_manifest import models




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


def get_state(state_name):
    if state_name.strip().lower() in state_codes:
        return state_codes[state_name.strip().lower()]
    if len(state_name) < 4:
        return state_name.upper()
    return state_name
