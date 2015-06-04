# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    
############################################################################
#    Coded by: 
#
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

{
    "name" : "Creacion de Factura Electronica para Mexico (CFDI-2015) - PAC Finkok",
    "version" : "1.0",
    "author" : "Martha Alcalá & Finkok S.A de C.V",
    "category" : "Localization/Mexico",
    "description" : """This module creates interface for e-invoice files from invoices with Finkok.
Ubuntu Package Depends:
    sudo apt-get install python-soappy
""",
    "website" : "http://www.finkok.com/",
    "license" : "AGPL-3",
    "depends" : ["l10n_mx_facturae_groups", "l10n_mx_params_pac", 
        "l10n_mx_account_tax_category",
        "l10n_mx_facturae_report",
        "l10n_mx_facturae_seq", 
        "l10n_mx_ir_attachment_facturae_finkok",
        "l10n_mx_facturae_pac",
        "l10n_mx_facturae_group_show_wizards",
        "l10n_mx_settings_facturae",
        ],
    "demo" : [
        "demo/l10n_mx_facturae_pac_finkok_demo.xml",
        "demo/l10n_mx_facturae_seq_demo.xml",
        "demo/account_invoice_cfdi_pac_finkok_demo.xml",
    ],
    "data" : [
        #"security/l10n_mx_facturae_pac_finkok_security.xml",
        "wizard/wizard_cancel_invoice_pac_finkok_view.xml",
        "wizard/wizard_export_invoice_pac_finkok_view_v6.xml",
    ],
    "test" : [
        "test/account_invoice_cfdi_pac_finkok.yml",
    ],
    "installable" : True,
    "active" : False,
}
