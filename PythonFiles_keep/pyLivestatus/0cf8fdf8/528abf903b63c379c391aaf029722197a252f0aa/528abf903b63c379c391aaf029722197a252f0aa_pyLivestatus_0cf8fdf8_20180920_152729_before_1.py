import telnetlib
import time

from .columns import *
from .exceptions import HostNotFoundException, NotFoundException


class Livestatus:
    ip = None
    port = None

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def _send_raw_command(self, cmd, want_response=True):
        self.livestatus = telnetlib.Telnet(self.ip, self.port)

        self.livestatus.write(cmd.encode('utf-8'))
        if want_response:
            response = self.livestatus.read_all().decode('utf-8').rstrip(u'\n')
        else:
            response = u''
        self.livestatus.close()
        return response

    def _send_command(self, cmd):
        cmd = u"COMMAND [{}] {}\n\n".format(int(time.time()), cmd)
        return self._send_raw_command(cmd, want_response=False)

    @staticmethod
    def _get_custom_data(custom_data_list):
        custom_data = str(custom_data_list).split(',')
        custom_data_list = {}
        for d in custom_data:
            nagios_macro_data = str(d).split('|')
            try:
                custom_data_list[nagios_macro_data[0]] = nagios_macro_data[1]
            except IndexError:
                custom_data_list[nagios_macro_data[0]] = u''
        return custom_data_list

    def _parse_item_data(self, data, attribute_list):
        this_result = {}
        data = data.split(';')
        for attribute_index in range(len(attribute_list)):
            if attribute_list[attribute_index] == u'custom_variables':
                this_data = self._get_custom_data(data[attribute_index].encode('utf-8', 'replace'))
            elif attribute_list[attribute_index] == u'members':
                this_data = data[attribute_index].encode('utf-8', 'replace').split(',')[:-1]
            else:
                this_data = data[attribute_index].encode('utf-8', 'replace')
            this_result[attribute_list[attribute_index]] = this_data
        return this_result

    def _get_by_query_multi(self, query, attribute_list):
        response = self._send_raw_command(query)
        if response == u'':
            raise HostNotFoundException
        all_results = []
        for result in response.split('\n'):
            all_results.append(self._parse_item_data(result, attribute_list))
        return all_results

    def _get_by_query_single(self, query, attribute_list):
        response = self._send_raw_command(query)
        if response == u'':
            raise NotFoundException
        return self._parse_item_data(response, attribute_list)

    def get_hosts(self):
        try:
            query = u"GET hosts\nColumns: " + u' '.join(host) + u'\n\n'
            return self._get_by_query_multi(query, host)
        except NotFoundException:
            return []

    def get_host(self, search_host):
        query = u"GET hosts\nColumns: {}\nFilter: host_name = {}\n\n".format(u' '.join(host), search_host)
        return self._get_by_query_single(query, host)

    def get_services(self, search_host):
        try:
            self.get_host(search_host)
        except NotFoundException:
            raise HostNotFoundException
        query = u"GET services\nColumns: {}\nFilter: host_name = {}\n\n".format(u' '.join(service), search_host)
        return self._get_by_query_multi(query, service)

    def get_all_services(self):
        try:
            query = u"GET services\nColumns: {}\n\n".format(u' '.join(service))
            return self._get_by_query_multi(query, service)
        except NotFoundException:
            return []

    def get_hostgroups(self):
        try:
            query = u"GET hostgroups\nColumns: {}\n\n".format(u' '.join(hostgroup))
            return self._get_by_query_multi(query, hostgroup)
        except NotFoundException:
            return []

    def get_servicegroups(self):
        try:
            query = u"GET servicegroups\nColumns: {}\n\n".format(u' '.join(servicegroup))
            return self._get_by_query_multi(query, servicegroup)
        except NotFoundException:
            return []

    def get_comments(self):
        try:
            query = u"GET comments\nColumns: {}\n\n".format(u' '.join(comment))
            return self._get_by_query_multi(query, comment)
        except NotFoundException:
            return []

    def set_host_disable_notification(self, host):
        cmd = u"DISABLE_HOST_NOTIFICATIONS;{}".format(host)
        return self._send_command(cmd)

    def set_host_disable_service_notification(self, host):
        cmd = u"DISABLE_HOST_SVC_NOTIFICATIONS;{}".format(host)
        return self._send_command(cmd)

    def set_service_disable_notification(self, host, svc):
        cmd = u"DISABLE_SVC_NOTIFICATIONS;{};{}".format(host, svc)
        return self._send_command(cmd)

    def set_service_comment(self, host, svc, user, comment):
        cmd = u"ADD_SVC_COMMENT;{};{};1;{};{}".format(host, svc, user, comment)
        return self._send_command(cmd)

    def set_service_disable_notifications_and_comment(self, host, svc, user, comment):
        self.set_service_disable_notification(host, svc)
        self.set_service_comment(host, svc, user, comment)
        return

    def set_host_comment(self, host, user, comment):
        cmd = u"ADD_HOST_COMMENT;{};1;{};{}".format(host, user, comment)
        return self._send_command(cmd)

    def set_host_disable_all_notification_comment(self, host, user, comment):
        self.set_host_disable_notification(host)
        self.set_host_disable_service_notification(host)
        self.set_host_comment(host, user, comment)
        return

    def set_host_downtime(self, host, user, comment, start, end):
        cmd = u"SCHEDULE_HOST_DOWNTIME;{host};{start};{end};{fixed};{trigger};{duration};{author};{comment}". \
            format(host=host, start=start, end=end, fixed=1, trigger=0, duration=0, author=user, comment=comment)
        return self._send_command(cmd)
