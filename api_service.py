from sodapy import Socrata


class ApiService:
    def __init__(self, socrata_domain, app_token=None):
        self.domain = socrata_domain
        self.app_token = app_token
        self.client = Socrata(self.domain, app_token=self.app_token)
        self.fields = ""
        self.where_clause = None
        self.order_descending = False
        self.order_predicate = None
        self.select_all_fields = True
        self.query_limit = None
        self.query_offset = None
        self.conditions = []

    def select(self, fields):
        if isinstance(fields, list) and len(fields) > 0:
            self.select_all_fields = False
            self.fields = ",".join(fields)
        elif isinstance(fields, str):
            if fields != '*':
                self.select_all_fields = False
                self.fields = fields.split(",")
            else:
                self.fields = fields
                self.select_all_fields = True
        return self

    def where(self, **kwargs):
        for key in kwargs:
            if "__" in key:
                field, operator = key.split("__")
                if operator == 'gt':
                    self.conditions.append(field + ">" + str(kwargs[key]))
                elif operator == 'gte':
                    self.conditions.append(field + ">=" + str(kwargs[key]))
                elif operator == 'lt':
                    self.conditions.append(field + "<" + str(kwargs[key]))
                elif operator == 'lte':
                    self.conditions.append(field + "<=" + str(kwargs[key]))
                elif operator == 'ne':
                    self.conditions.append(field + "!=" + str(kwargs[key]))
            else:
                self.conditions.append(key + "=" + str(kwargs[key]))
        self.where_clause = " and ".join(self.conditions)
        return self

    def order_by(self, predicate=None, desc=False):
        self.order_predicate = str(predicate)
        self.order_descending = desc
        return self

    def limit(self, limit):
        self.query_limit = int(limit)
        return self

    def offset(self, offset):
        self.query_offset = int(offset)
        return self

    def query(self, dataset_id, **kwargs):
        if not dataset_id:
            raise Exception("dataset_id required to query data")
        params = {'dataset_identifier': dataset_id}
        if not self.select_all_fields:
            params['select'] = self.fields
        if self.where_clause is not None:
            params['where'] = self.where_clause
        if self.query_limit is not None:
            params['limit'] = self.query_limit
        if self.query_offset is not None:
            params['offset'] = self.query_offset
        if self.order_predicate is not None:
            params['order'] = self.order_predicate
            if self.order_descending:
                params['order'] += " DESC"
        params.update(kwargs)
        return self.client.get(**params)

    def close(self):
        self.client.close()
