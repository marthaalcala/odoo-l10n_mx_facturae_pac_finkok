# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
############################################################################
#    Coded by: 

############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import pooler, tools
from openerp import netsvc
from openerp.tools.misc import ustr

import time
import base64
import StringIO
import csv
import tempfile
import os
import sys
import codecs
try:
    from SOAPpy import WSDL
except:
    print "Package SOAPpy missed"
    pass
import time


class wizard_cancel_invoice_pac_finkok(osv.TransientModel):
    _name = 'wizard.cancel.invoice.pac.finkok'

    def _get_cancel_invoice_id(self, cr, uid, data, context=None):
        """
        @params data : Dictionary with information of the user, and active ids
        """
        if context is None:
            context = {}
        res = {}
        invoice_obj = self.pool.get('account.invoice')
        res = invoice_obj._get_file_cancel(cr, uid, data['active_ids'])
        return res['file']

    def upload_cancel_to_pac(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = {}
        invoice_obj = self.pool.get('account.invoice')
        res = invoice_obj.finkok_cancel(cr, uid, context[
                                    'active_ids'], context=None)
        self.write(cr, uid, ids, {'message': res['message']}, context=None)
        return True

    _columns = {
        'file': fields.binary('File', readonly=True,
                              help='Shows the file returned'),
        'message': fields.text('text', readonly=True, help='Shows the message \
            that returned after of cancel the Electronic Invoice'),
    }

    _defaults = {
        'message': 'Choose the button Cancel Invoice for send the cancellation to PAC',
        'file': _get_cancel_invoice_id,
    }
