#!/usr/bin/python

import requests
import json


def _join(*args):
    return '/'.join(map(str, filter(bool, args)))


class VScale:
    def __init__(self, token, api_url='https://api.vscale.io/v1'):
        self.token = token
        self.url = api_url
        self.headers = {'Content-Type': 'application/json',
                        'X-Token': self.token}

    def token_manager(self):
        return TokenManager(self)

    def account_manager(self):
        return AccountManager(self)

    def misc_manager(self):
        return MiscManager(self)

    def server_manager(self):
        return ServerManager(self)

    def ticket_manager(self):
        return TicketManager(self)

    def billing_manager(self):
        return BillingManager(self)

    def key_manager(self):
        return KeyManager(self)

    def _request(self, path, method, params=None, data=None):
        response = requests.request(method=method,
                                    url=_join(self.url, path),
                                    headers=self.headers,
                                    params=params,
                                    data=data)
        response.raise_for_status()
        return response.json()


class Manager(object):
    delete = 'DELETE'
    get = 'GET'
    patch = 'PATCH'
    post = 'POST'
    put = 'PUT'

    def __init__(self, vscale, name):
        self.vscale = vscale
        self.name = name

    def _delete(self, path):
        return self._request(path, self.delete)

    def _get(self, path='', **kwargs):
        return self._request(path, self.get, params=kwargs)

    def _patch(self, path, **kwargs):
        return self._request(path, self.patch, data=kwargs)

    def _post(self, path, **kwargs):
        return self._request(path, self.post, data=kwargs)

    def _put(self, path, **kwargs):
        return self._request(path, self.put, data=kwargs)

    def _request(self, path, method, data=None, params=None):
        return self.vscale._request(_join(self.name, path), method=method,
                                    params=params, data=data)


class TokenManager(Manager):
    def __init__(self, vscale):
        super(TokenManager, self).__init__(vscale, 'tokens')

    def generate_token(self, description, enabled, read_only):
        return self._post('', description=description, enabled=enabled,
                          read_only=read_only)

    def get_tokens(self):
        return self._get()

    def get_token_info(self, token_id):
        return self._get(token_id)

    def change_token(self, token_id, description=None, enabled=None,
                     read_only=None):
        return self._post(token_id, description=description,
                          enabled=enabled, read_only=read_only)

    def delete_token(self, token_id):
        return self._delete(token_id)


class AccountManager(Manager):
    def __init__(self, vscale):
        super(AccountManager, self).__init__(vscale, 'account')

    def get_account_info(self):
        return self._get()


class MiscManager(Manager):
    def __init__(self, vscale):
        super(MiscManager, self).__init__(vscale, None)

    def get_operations(self):
        return self._get('tasks')

    def get_locations(self):
        return self._get('locations')

    def get_images(self):
        return self._get('images')

    def get_configurations(self):
        return self._get('rplans')


class ServerManager(Manager):
    def __init__(self, vscale):
        super(ServerManager, self).__init__(vscale, 'scalets')
        self.misc_manager = MiscManager(vscale)

    def get_servers(self):
        return self._get()

    def create_server(self, make_from, rplan, name, keys, do_start=True,
                      password=None, location='spb'):
        return self._post('', make_from=make_from, rplan=rplan,
                          do_start=do_start, name=name, keys=keys,
                          password=password, location=location)

    def get_server_info(self, server_id):
        return self._get(server_id)

    def restart_server(self, server_id):
        return self._patch(_join(server_id, 'restart'))

    def rebuild_server(self, server_id, password=None):
        return self._patch(_join(server_id, 'rebuild'), password=password)

    def stop_server(self, server_id):
        return self._patch(_join(server_id, 'stop'))

    def start_server(self, server_id):
        return self._patch(_join(server_id, 'start'))

    def upgrade_server(self, server_id, rplan):
        return self._post(_join(server_id, 'upgrade'), rplan=rplan)

    def delete_server(self, server_id):
        return self._delete(server_id)

    def add_ssh_keys(self, server_id, keys):
        return self._patch(server_id, keys=keys)

    def get_operations(self):
        return self.misc_manager.get_operations()


class TicketManager(Manager):
    def __init__(self, vscale):
        super(TicketManager, self).__init__(vscale, 'tickets')

    def get_tickets(self):
        return self._get()

    def create_ticket(self, header, text, notify=False):
        return self._post('', header=header, text=text, notify=notify)

    def get_ticket_comments(self, ticket_id):
        return self._get(_join(ticket_id, 'comments'))

    def add_comment(self, ticket_id, text):
        return self._post(_join(ticket_id, 'comments'), text=text)

    def close_ticket(self, ticket_id):
        return self._post(_join(ticket_id, 'close'))


class BillingManager(Manager):
    def __init__(self, vscale):
        super(BillingManager, self).__init__(vscale, 'billing')

    def get_prices(self):
        return self._get('prices')

    def get_consumption(self, start, end):
        return self._get('consumption', start=start, end=end)

    def get_payments(self):
        return self._get('payments')

    def get_balance(self):
        return self._get('balance')

    def get_notify_balance(self):
        return self._get('notify')

    def set_notify_balance(self, notify_balance):
        return self._put('notify', notify_balance=notify_balance)


class KeyManager(Manager):
    def __init__(self, vscale):
        super(KeyManager, self).__init__(vscale, 'sshkeys')

    def get_keys(self):
        return self._get()

    def add_key(self, name, key):
        return self._post('', name=name, key=key)

    def delete_key(self, key_id):
        return self._delete(key_id)


def log(value):
    print json.dumps(value, indent=4)


def main():
    vscale = VScale('598225dffa0b1a9a61f82a30ca7bb31acb835c4ee74ac4969dd5f9b7acd1d99a')
    # token_manager = vscale.token_manager()
    # log(token_manager.get_tokens())
    # log(token_manager.get_token_info(274))
    server_manager = vscale.server_manager()
    log(server_manager.get_servers())
    log(server_manager.get_server_info(1))


if __name__ == '__main__':
    main()