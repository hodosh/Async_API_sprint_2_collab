from api.v1.pagination_shema import PaginationSchema


class QueryBuilder:
    def __init__(self):
        self.query = {}

    def set_pagination(self, pagination: PaginationSchema):
        self.query['from'] = (pagination.page_number - 1) * pagination.page_size
        self.query['size'] = pagination.page_size

    def set_order(self, field, direction):
        sort_item = {field: {'order': direction}}

        self.query['sort'] = []
        self.query['sort'].append(sort_item)

    def set_query_match_all(self):
        self.query['query'] = {'match_all': {}}

    def set_simple_match(self, field, value):
        pass

    def set_nested_match(self, parent_field, full_path, value):
        self.query['query'] = {
            'nested': {
                'path': parent_field,
                'query': {
                    'bool': {
                        'must': [
                            {'match': {full_path: value}}
                        ]
                    }
                }
            }
        }

    def set_fuzzy_query(self, search_string: str, fields: list[str]):
        self.query['query'] = {
            "multi_match": {
                "query": search_string,
                "fields": fields,
                "fuzziness": "AUTO"
            }
        }

    def get_query(self):
        return self.query
