from app.main.tools.utils import api_call
import app.main.config as config


def get_companyInfo(req_context):
    """Get CompanyInfo of connected QBO company"""
    uri = "/companyinfo/" + req_context.realm_id + "?minorversion=" + config.API_MINORVERSION
    response = api_call.get_request(req_context, uri, params={})
    return response