from sodapy import Socrata


class ApiService:
    def __init__(self, socrata_domain, app_token=None):
        """
        Wrapper class that interacts with the SODA API sodapy client. This class allows user to chain query methods
        like 'select' and 'where' used by the SODA API client.
        Sample usage:
        from api_service import ApiService
        api_service = ApiService(socrata_domain, app_token)
        result = api_service.select('field1','field2').where(field1='a',field2__lt=10).query(socrata_dataset)

        :param socrata_domain: Socrata Domain URL for querying data
        :param app_token: your Socrata application token for authorization. Default is 'None'
        """
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
        """
        method to provide field names to be selected in the result
        :param fields: Field names for SoQL select clause. Takes comma separated field names or a list of field names
        :return: instance of the object 'self'
        """
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
        """
        method takes where conditions for SoQL.
        Sample usage:
        api_service.where(field1__gt=1) -> where field1 > 1
        api_service.where(field1__lte=1) -> where field1 <= 1
        api_service.where(field1__lte=1, field2__gt='hello',field3=10) -> where field1 <= 1 and field2 > 'hello' and field3 = 10

        :param kwargs: It takes multiple fields as arguments
        :return: instance of the object 'self'
        """
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
        """
        This method takes the predicate by which you want your result to be ordered by.
        By default the order is Ascending and the result can be ordered in Descending order by setting desc=True
        :param predicate: field by which you want your result to be ordered
        :param desc: Descending or Ascending order
        :return: instance of the object 'self'
        """
        self.order_predicate = str(predicate)
        self.order_descending = desc
        return self

    def limit(self, limit):
        """
        This method takes the number by which you would like to limit your result
        :param limit: Max number of rows in the result
        :return: instance of the object 'self'
        """
        self.query_limit = int(limit)
        return self

    def offset(self, offset):
        """
        This method takes the number by which you would like to offset your result
        :param offset: Start index of the offset
        :return: instance of the object 'self'
        """
        self.query_offset = int(offset)
        return self

    def query(self, dataset_id, **kwargs):
        """
        This method creates the final query and calls the SODA API client.
        You can also pass all the other arguments support by SODA API client in kwargs that are not supported by
        this wrapper class
        :param dataset_id: Socrata dataset identifier
        :param kwargs: Extra arguments that you want to pass to the API client
        :return: Returns result set of the query
        """
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
        """
        This method is use to close the SODA API session in a clean way
        :return: None
        """
        self.client.close()
