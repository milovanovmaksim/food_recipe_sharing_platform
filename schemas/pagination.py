from urllib.parse import urlencode
from flask import request
from marshmallow import Schema, fields


class PaginationSchema(Schema):
    class Meta:
        ordered = True

    links = fields.Method(serialize="get_pagination_links")
    page = fields.Integer(dump_only=True)
    pages = fields.Integer(dump_only=True)
    per_page = fields.Integer(dump_only=True)
    total = fields.Integer(dump_only=True)

    @staticmethod
    def get_url(page):
        query_args = request.args.to_dict()
        query_args['page'] = page
        return f"{request.base_url}?{urlencode(query_args)}"

    def get_pagination_links(self, paginated_object):
        pagination_links = {}
        if paginated_object.has_prev:
            pagination_links['prev'] = self.get_url(page=paginated_object.prev_num)
        if paginated_object.has_next:
            pagination_links['next'] = self.get_url(page=paginated_object.next_num)
        pages = paginated_object.pages
        if pages >= 1:
            pagination_links['first'] = self.get_url(page=1)
            pagination_links['last'] = self.get_url(page=paginated_object.pages)
        return pagination_links
