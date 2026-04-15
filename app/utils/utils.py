from fastapi import Response
import dicttoxml # type: ignore


# Helper function for format handling
def format_response(data: dict, accept_header: str):
    """Converts data to XML if user wants this, else JSON"""
    if "application/xml" in accept_header:
        xml_data = dicttoxml.dicttoxml(data, custom_root="response", attr_type=False)
        return Response(content=xml_data, media_type="application/xml")

    # FastAPI will return JSON automatically if we send a dict
    return data
