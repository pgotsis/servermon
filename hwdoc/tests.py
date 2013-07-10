# -*- coding: utf-8 -*- vim:fileencoding=utf-8:
# vim: tabstop=4:shiftwidth=4:softtabstop=4:expandtab

# Copyright © 2010-2012 Greek Research and Technology Network (GRNET S.A.)
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND ISC DISCLAIMS ALL WARRANTIES WITH REGARD
# TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS. IN NO EVENT SHALL ISC BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT,
# OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF
# USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
# TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE
# OF THIS SOFTWARE.
'''
Unit tests for hwdoc package
'''

from django import VERSION as DJANGO_VERSION

if DJANGO_VERSION[:2] >= (1, 3):
    from django.utils import unittest
else:
    import unittest
from hwdoc.models import Vendor, EquipmentModel, Equipment, \
    ServerManagement, Project, Rack, RackPosition, RackModel, RackRow, \
    Datacenter
from hwdoc.functions import search, populate_tickets
from projectwide.functions import get_search_terms
from django.test.client import Client

class EquipmentTestCase(unittest.TestCase):
    '''
    A test case for equipment
    '''

    def setUp(self):
        '''
        Commands run before every test
        '''

        self.vendor = Vendor.objects.create(name='HP')
        self.model1 = EquipmentModel.objects.create(vendor=self.vendor, name='DL 385 G7', u=2)
        self.model2 = EquipmentModel.objects.create(vendor=self.vendor, name='DL 380 G7', u=2)
        self.model2 = EquipmentModel.objects.create(vendor=self.vendor, name='Fujisu PRIMERGY 200 S', u=1)
        self.rackmodel = RackModel.objects.create(
                                vendor=self.vendor,
                                max_mounting_depth = 99,
                                min_mounting_depth = 19,
                                height = 42,
                                width = 19)
        self.dc = Datacenter.objects.create(name='Test DC')
        self.rackrow = RackRow.objects.create(name='testing', dc=self.dc)
        self.rack = Rack.objects.create(model=self.rackmodel, name='testrack')
        RackPosition.objects.create(rack=self.rack, rr=self.rackrow, position=10)

        self.server1 = Equipment.objects.create(
                                model = self.model1,
                                serial = 'G123456',
                                rack = self.rack,
                                unit = '20',
                                purpose = 'Nothing',
                            )

        self.server2 = Equipment.objects.create(
                                model = self.model2,
                                serial = 'R123457',
                                rack = self.rack,
                                unit = '22',
                                purpose = 'Nothing',
                                comments = 'Nothing',
                            )

        self.management = ServerManagement.objects.create (
                            equipment = self.server2,
                            method = 'dummy',
                            hostname = 'example.com',
                            )

    def tearDown(self):
        '''
        Command run after every test
        '''

        ServerManagement.objects.all().delete()
        Equipment.objects.all().delete()
        EquipmentModel.objects.all().delete()
        Vendor.objects.all().delete()

    # Tests start here
    def test_if_servers_in_same_rack(self):
        self.assertEqual(self.server1.rack, self.server2.rack)

    def test_dummy_management_fuctions(self):
        self.assertTrue(self.management.power_on())
        self.assertTrue(self.management.power_off())
        self.assertTrue(self.management.power_cycle())
        self.assertTrue(self.management.power_reset())
        self.assertTrue(self.management.power_off_acpi())
        self.assertTrue(self.management.pass_change(**{'change_username': 'me', 'newpass': 'us'}))
        self.assertTrue(self.management.set_settings())
        self.assertTrue(self.management.set_ldap_settings())
        self.assertTrue(self.management.boot_order())
        self.assertTrue(self.management.license_set())
        self.assertTrue(self.management.bmc_reset())
        self.assertTrue(self.management.bmc_factory_defaults())
        self.assertTrue(self.management.add_user())
        self.assertTrue(self.management.remove_user())
        self.assertTrue(self.management.get_all_users())
        self.assertTrue(self.management.firmware_update())

    def test_equipment_number(self):
        self.assertEqual(Equipment.objects.all().count(), 2)

    def test_search_empty(self):
        self.assertFalse(search(''))

    def test_search_rack(self):
        self.assertEqual(search(str(self.server1.rack.name)).count(), 2)

    def test_search_serial(self):
        self.assertEqual(search(self.server1.serial)[0].serial, self.server1.serial)
        self.assertEqual(search(self.server2.serial)[0].serial, self.server2.serial)

    def test_free_text_search(self):
        text=u'''
        This is a text that is not going to make any sense apart from containing
        a hostname for a server (aka example.com) and a rackunit aka R10U22
        '''

        tokens = get_search_terms(text)
        self.assertNotEqual(len(tokens), 0)

    def test_populate_tickets(self):
        self.assertEqual(populate_tickets(search(str(self.server2.rack.name))).count(), 2)


class ViewsTestCase(unittest.TestCase):
    '''
    Testing views class
    '''

    def setUp(self):
        '''
        Command run before every test
        '''

        self.vendor = Vendor.objects.create(name='HP')
        self.model = EquipmentModel.objects.create(vendor=self.vendor, name='DL 385 G7', u=2)
        self.rackmodel = RackModel.objects.create(
                                vendor=self.vendor,
                                max_mounting_depth = 99,
                                min_mounting_depth = 19,
                                height = 42,
                                width = 19)
        self.rack = Rack.objects.create(model=self.rackmodel, name='testrack')

        self.server = Equipment.objects.create(
                                model = self.model,
                                serial = 'dontcare',
                                rack = self.rack,
                                unit = '2',
                                purpose = 'Nothing',
                            )

        self.project = Project.objects.create(name='project')
        self.dc = Datacenter.objects.create(name='Test DC')
        self.rackrow = RackRow.objects.create(name='1st rackrow', dc=self.dc)
        RackPosition.objects.create(rack=self.rack, rr=self.rackrow, position=10)
        self.racknotinrow = Rack.objects.create(model=self.rackmodel, name='racknotinrow')
    def tearDown(self):
        '''
        Command run after every test
        '''

        ServerManagement.objects.all().delete()
        Equipment.objects.all().delete()
        EquipmentModel.objects.all().delete()
        Vendor.objects.all().delete()

    def test_search_get(self):
        c = Client()
        data = ['', 'dummy', '562346', 'R5U21', 'UI2354']
        for d in data:
            response = c.get('/search/', {'q': d})
            self.assertEqual(response.status_code, 200)

    def test_search_get_txt(self):
        c = Client()
        data = ['', 'dummy', '562346', 'R5U21', 'UI2354']
        for d in data:
            response = c.get('/search/', {'q': d, 'txt': 'yes'})
            self.assertEqual(response.status_code, 200)

    def test_free_text_search_post(self):
        c = Client()
        strings = [ 'this is a dummy string', '0.0', '.example.tld' ]
        for s in strings:
            response = c.post('/search/', {'qarea': s})
            self.assertEqual(response.status_code, 200)

    def test_index(self):
        c = Client()
        response = c.get('/hwdoc/')
        self.assertEqual(response.status_code, 200)

    def test_equipment(self):
        c = Client()
        response = c.get('/hwdoc/equipment/%s/' % self.server.pk)
        self.assertEqual(response.status_code, 200)

    def test_project(self):
        c = Client()
        response = c.get('/hwdoc/project/%s/' % self.project.pk)
        self.assertEqual(response.status_code, 200)

    def test_datacenter(self):
        c = Client()
        response = c.get('/hwdoc/datacenter/%s/' % self.dc.pk)
        self.assertEqual(response.status_code, 200)

    def test_rackrow(self):
        c = Client()
        response = c.get('/hwdoc/rackrow/%s/' % self.rackrow.pk)
        self.assertEqual(response.status_code, 200)

    def test_rack_in_row(self):
        c = Client()
        response = c.get('/hwdoc/rack/%s/' % self.rack.pk)
        self.assertEqual(response.status_code, 200)

    def test_rack_not_in_row(self):
        c = Client()
        response = c.get('/hwdoc/rack/%s/' % self.racknotinrow.pk)
        self.assertEqual(response.status_code, 200)

    def test_subnav(self):
        c = Client()
        response = c.get('/hwdoc/subnav/%s/' % 'datacenters',
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)

