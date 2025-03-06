from app.main.tools.utils import APICallService
import app.main.config as config


def get_companyInfo(req_context):
    """Get CompanyInfo of connected QBO company"""
    uri = "/companyinfo/" + req_context.realm_id + "?minorversion=" + config.API_MINORVERSION
    response = APICallService.get_request(req_context, uri, params={})
    return response