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

from openerp.tools.translate import _
from openerp.osv import fields, osv, orm
from openerp import tools
from openerp import netsvc
from openerp.tools.misc import ustr
import wizard
import base64
import xml.dom.minidom
import time
import StringIO
import csv
import tempfile
import os
import sys
import codecs
from xml.dom import minidom
import urllib
import pooler
from openerp.tools.translate import _
from datetime import datetime, timedelta
from pytz import timezone
import pytz
import time
from openerp import tools
from suds.client import Client
import logging
import base64
from string import maketrans
from lxml import etree
from qrtools import QR

##etree
from xml.etree.ElementTree import ElementTree
from xml.etree.ElementTree import fromstring

import UserString


logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


class ir_attachment_facturae_mx(osv.Model):
    _inherit = 'ir.attachment.facturae.mx'

    def _get_type(self, cr, uid, ids=None, context=None):
        if context is None:
            context = {}
        types = super(ir_attachment_facturae_mx, self)._get_type(
            cr, uid, ids, context=context)
        types.extend([
            ('cfdi32_pac_finkok', 'CFDI 3.2 Finkok'),
        ])
        return types
    

    def get_driver_fc_cancel(self):
        
        factura_mx_type__fc = super(ir_attachment_facturae_mx, self).get_driver_fc_cancel()
        if factura_mx_type__fc == None:
            factura_mx_type__fc = {}
        factura_mx_type__fc.update({'cfdi32_pac_finkok': self.sf_cancel})
        return factura_mx_type__fc


    def get_driver_fc_sign(self):
        factura_mx_type__fc = super(ir_attachment_facturae_mx, self).get_driver_fc_sign()
        if factura_mx_type__fc == None:
            factura_mx_type__fc = {}
        factura_mx_type__fc.update({'cfdi32_pac_finkok': self._upload_ws_file})
        return factura_mx_type__fc
    

    _columns = {
        'type': fields.selection(_get_type, 'Type', type='char', size=64,
                                 required=True, readonly=True, help="Type of Electronic Invoice"),
    }
    
    
    
    def sf_cancel(self, cr, uid, ids, context=None):
        
            ## Si todo es correcto debe realizar la cancelación
            if context is None:
                context = {}
            msg = ''
            certificate_obj = self.pool.get('res.company.facturae.certificate')
            pac_params_obj = self.pool.get('params.pac')
            invoice_obj = self.pool.get('account.invoice')
            

            
            for ir_attachment_facturae_mx_id in self.browse(cr, uid, ids, context=context):
                status = False
                invoice = ir_attachment_facturae_mx_id.invoice_id
                pac_params_ids = pac_params_obj.search(cr, uid, [
                    ('method_type', '=', 'cancel'),
                    ('company_id', '=', invoice.company_emitter_id.id),
                    ('active', '=', True),
                ], limit=1, context=context)
                pac_params_id = pac_params_ids and pac_params_ids[0] or False

                try:
                    ## Verifica si los parametros del PAC son correctos
                    if pac_params_id:
                        file_globals = invoice_obj._get_file_globals(
                            cr, uid, [invoice.id], context=context)
                        pac_params_brw = pac_params_obj.browse(
                            cr, uid, [pac_params_id], context=context)[0]


                        user = pac_params_brw.user
                        password = pac_params_brw.password
                        wsdl_url = pac_params_brw.url_webservice
                        namespace = pac_params_brw.namespace

                        
                        client = Client(wsdl_url, cache=None)
                            

                        fname_cer_no_pem = file_globals['fname_cer']
                        cerCSD = fname_cer_no_pem and base64.encodestring(
                            open(fname_cer_no_pem, "r").read()) or ''
                        fname_key_no_pem = file_globals['fname_key']
                        keyCSD = fname_key_no_pem and base64.encodestring(
                            open(fname_key_no_pem, "r").read()) or ''

                        contrasenaCSD = file_globals.get('password', '')
                        uuids = invoice.cfdi_folio_fiscal # cfdi_folio_fiscal
                        invoices_list = client.factory.create('UUIDS')
                        invoices_list.uuids.string = uuids
                           
                           
                        ## Sacar el RFC para la solicitud de cancelación
                          

                        ## Sacar el RFC emisor del invoice 
                        rfc_emisor = invoice.company_emitter_id.vat
                            
                        #Borrando el prefijo MX
                        rfc_emisor = UserString.MutableString(rfc_emisor)
                        del rfc_emisor[0:2]
                        rfc_emisor = str(rfc_emisor)
                                   
                        ## Respuesta del webservice
                        result_cancel = client.service.cancel(invoices_list, user, password, rfc_emisor, cerCSD, keyCSD)
                            
                        ## Si ya esta timbrado y fue cancelado (si tiene acuse de cancelación) 
                        try:
                            if result_cancel['Acuse']:
                                folio_cancel = result_cancel['Folios'] and result_cancel['Folios']['Folio'] and result_cancel['Folios']['Folio'][0]['UUID'] or ''
                                codigo_cancel = result_cancel['Folios'] and result_cancel['Folios']['Folio'] and result_cancel['Folios']['Folio'][0]['EstatusUUID'] or ''
                                status_uuid = result_cancel['Folios'] and result_cancel['Folios']['Folio'] and result_cancel['Folios']['Folio'][0]['EstatusUUID'] or ''

                                    
                                mensaje_cancel = 'UUID Cancelado exitosamente' ## Para mandarlo cuando se cancele
                                   
                                ## Si fue correctamente cancelado
                                if int(codigo_cancel) in (201, 202):
                                    # EXITO            
                                    msg =  mensaje_cancel + _('<br>El proceso de cancelacion se ha completado correctamente. El UUID cancelado es: ') + folio_cancel + '.'
                                    invoice_obj.write(cr, uid, [invoice.id], {
                                        'cfdi_fecha_cancelacion': time.strftime(
                                        '%Y-%m-%d %H:%M:%S')
                                    })
                                    status = True

                                    return {'message': msg, 'status_uuid': status_uuid, 'status': status}
                                    

                                else:
                                    # ERROR
                                    
                                    return {'status':False, 'codigo_cancel':codigo_cancel, 'folio_cancel':folio_cancel}
                                    ##Lo manda a ir_attach/ir_attach signal_cancel()
                            else:
                                raise Exception('No se puede Cancelar')            
                        ## Si no tiene acuse (no ha sido timbrado)
                        except Exception as e:
                            return {'status':False, 'message': 'El comprobante aun no puede ser cancelado. Intente más tarde por favor.'} 
                 
                ## Error Params
                except Exception as e:
                    msg = 'No se encontro informacion del webservice o PAC, verifique que la configuracion sea correcta'
                    return {'status':False, 'message': msg}      

          
    
    def _upload_ws_file(self, cr, uid, ids, fdata=None, context=None):
        
            """
            @params fdata : File.xml codification in base64
            """
           
            if context is None:
                context = {}
            invoice_obj = self.pool.get('account.invoice')

            pac_params_obj = invoice_obj.pool.get('params.pac')

            for ir_attachment_facturae_mx_id in self.browse(cr, uid, ids, context=context):
                invoice = ir_attachment_facturae_mx_id.invoice_id
                comprobante = invoice_obj._get_type_sequence(
                    cr, uid, [invoice.id], context=context)
                cfd_data = base64.decodestring(fdata or invoice_obj.fdata)
                xml_res_str = xml.dom.minidom.parseString(cfd_data)
                xml_res_addenda = invoice_obj.add_addenta_xml(
                    cr, uid, xml_res_str, comprobante, context=context)
                xml_res_str_addenda = xml_res_addenda.toxml('UTF-8')
                xml_res_str_addenda = xml_res_str_addenda.replace(codecs.BOM_UTF8, '')
                
                if tools.config['test_report_directory']:#TODO: Add if test-enabled:
                    ir_attach_facturae_mx_file_input = ir_attachment_facturae_mx_id.file_input and ir_attachment_facturae_mx_id.file_input or False
                    fname_suffix = ir_attach_facturae_mx_file_input and ir_attach_facturae_mx_file_input.datas_fname or ''
                    open( os.path.join(tools.config['test_report_directory'], 'l10n_mx_facturae_pac_finkok' + '_' + \
                      'before_upload' + '-' + fname_suffix), 'wb+').write( xml_res_str_addenda )

                compr = xml_res_addenda.getElementsByTagName(comprobante)[0]
                date = compr.attributes['fecha'].value
                date_format = datetime.strptime(
                    date, '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d')
                context['date'] = date_format
                invoice_ids = [invoice.id]
                file = False
                msg = ''
                cfdi_xml = False

                pac_params_ids = pac_params_obj.search(cr, uid, [
                    ('method_type', '=', 'stamp'), (
                        'company_id', '=', invoice.company_emitter_id.id), (
                            'active', '=', True)], limit=1, context=context)
                
                if pac_params_ids:
                    pac_params = pac_params_obj.browse(
                        cr, uid, pac_params_ids, context)[0]
                    user = pac_params.user
                    password = pac_params.password
                    wsdl_url = pac_params.url_webservice
                    namespace = pac_params.namespace

                    ## Establece el url del PAC Puede ser demo o producción
                    url = 'https://facturacion.finkok.com/servicios/soap/stamp.wsdl'
                    testing_url = 'http://demo-facturacion.finkok.com/servicios/soap/stamp.wsdl'

                    ## Compara si el url establecido es el mismo que el de la configuración del módulo.
                    if (wsdl_url == url):
                        url = url
                    elif (wsdl_url == testing_url):
                        url = testing_url
                        
                    else:
                        raise osv.except_osv(_('Aviso'), _('URL  o PAC incorrecto'))
                        
                    ## Verifica si se esta timbrando en webservice Demo    
                    if 'demo' in wsdl_url:
                        msg += _('¡AVISO, FIRMADO EN MODO PRUEBA!<br/>')
                   
                    
                    ## Conexión
                    client = Client(url,cache=None)
                    
                    if True:  # if wsdl_client:
                        file_globals = invoice_obj._get_file_globals(
                            cr, uid, invoice_ids, context=context)
                        fname_cer_no_pem = file_globals['fname_cer']
                        cerCSD = fname_cer_no_pem and base64.encodestring(
                            open(fname_cer_no_pem, "r").read()) or ''
                        fname_key_no_pem = file_globals['fname_key']
                        keyCSD = fname_key_no_pem and base64.encodestring(
                            open(fname_key_no_pem, "r").read()) or ''
                        cfdi = base64.encodestring(xml_res_str_addenda)
                        cfdi = cfdi.replace('\n', '')
                                                
                        ## Respuesta del webservice
                        resultado = client.service.stamp(cfdi,user,password)

                        htz = int(invoice_obj._get_time_zone(
                            cr, uid, [ir_attachment_facturae_mx_id.invoice_id.id], context=context))
            

                        if resultado['Incidencias']:
                            # ERROR
                            codigo_incidencia = resultado['Incidencias'] and \
                                resultado['Incidencias']['Incidencia'] and \
                                resultado['Incidencias']['Incidencia'][0]['CodigoError'] or ''

                            mensaje_incidencia = resultado['Incidencias'] and \
                                resultado['Incidencias']['Incidencia'] and \
                                resultado['Incidencias']['Incidencia'][0]['MensajeIncidencia'] or ''

                       
                            
                            msg_error = 'Error al intentar timbrar. ' + 'Codigo error: ' + codigo_incidencia + "." + ' Descripcion: ' + mensaje_incidencia + '.' 
                            raise orm.except_orm('Aviso', msg_error)


                            ## Tiene q retornar esto para que pase a firmado              
                            #return {'file': ' ', 'msg': msg_error, 'cfdi_xml': ' '}
                            

                        else:
                            # EXITO
                            mensaje = _(tools.ustr(resultado['CodEstatus']))  ## Comprobante timbrado satisfactoriamente                 
                            folio_fiscal= resultado['UUID'] or ''
                            fecha_timbrado_cfdi = resultado['Fecha'] or False
                            fecha_timbrado = resultado[
                                'Fecha'] or False
                            fecha_timbrado = fecha_timbrado and time.strftime(
                                '%Y-%m-%d %H:%M:%S', time.strptime(
                                    fecha_timbrado[:19], '%Y-%m-%dT%H:%M:%S')) or False
                            fecha_timbrado = fecha_timbrado and datetime.strptime(
                                fecha_timbrado, '%Y-%m-%d %H:%M:%S') + timedelta(
                                    hours=htz) or False


                            ## Generar Cadena Original
                            version='1.0'
                            ## folio_fiscal lo saca arriba de la respuesta del webservice
                            ## fecha_timbrado_cfdi la saca de arriba de la respuesta del webservice

                            ## Extraer datos del xml
                            xml_string = resultado['xml']
                            xml_string = xml_string.encode('UTF-8')


                            ## Extraer los rfc's de los nodos hijos
                            xml_etree = etree.fromstring(xml_string)
                            xml_etree.getchildren()
                            xml_childrens = xml_etree.getchildren()
                            ## Obtener rfc emisor
                            re=xml_childrens[0].get('rfc')
                            ## Obtener rfc receptor
                            rr=xml_childrens[1].get('rfc')
                           

                            ##Extraer selloCSD
                            selloCFD = xml_etree.get('sello')

                            ## Extraer total
                            total_factura= xml_etree.get('total') 

                            ## Pasar el total a 17 caracteres como lo especifica el anexo 20

                            ## Convertir el total a float para sacarle los decimales
                            total_factura=float(total_factura)
                           
                            ## Sacarle 6 decimales
                            total_factura = format(total_factura, '.6f')

                            ## Convertir a string
                            total_factura=str(total_factura)
                            
                            ## Sacar la logitud de la cadena
                            total=len(total_factura)

                            ## Agregar los ceros a la izquiera hasta completar 17 caracteres
                            while total < 17:
                                i=''
                                i+='0'
                                total += 1
                                total_factura=i+total_factura
                                
                            NoCertificadoSAT='20001000000100005761'
                            cadena_original='||' + version + '|' + folio_fiscal + '|' + fecha_timbrado_cfdi + '|' + selloCFD + '|' + NoCertificadoSAT + '||'

                            ## Generar CBB                                                               
                            qr_string = "?re="+re+"&rr="+rr+"&tt="+total_factura+"&id="+folio_fiscal ## Cadena de Texto
                            qr_code = QR(data=qr_string) 
                            qr_code.encode() ##Encodeamos la Cadena
                            qr_file = open(qr_code.filename, "rb") ## Escribimos la Imagen
                            temp_bytes = qr_file.read() ## Leemos la Imagen
                            qr_bytes = base64.encodestring(temp_bytes) ## Convertimos la Imagen para Escribirla en Base64
                            qr_file.close() ## Cerramos la lectura del archivo con la imagen QR
                           

                            cfdi_data = {     
                                'cfdi_cbb': qr_bytes, 
                                'cfdi_sello': resultado['SatSeal'] or False,
                                'cfdi_no_certificado': resultado['NoCertificadoSAT'] or False,
                                'cfdi_cadena_original': cadena_original,                            
                                'cfdi_fecha_timbrado': fecha_timbrado,
                                'cfdi_xml': resultado['xml'] or '',  # este se necesita en uno que no es base64
                                'cfdi_folio_fiscal': resultado['UUID'] or '',
                                'pac_id': pac_params.id,
                            }

                            ## Comprobante timbrado satisfactoriamente. Folio Fiscal: Folio
                            msg += mensaje + "." + \
                                " Folio Fiscal: " + folio_fiscal
                            msg += (". Asegurese que el archivo fue generado correctamente en el SAT https://www.consulta.sat.gob.mx/sicofi_web/moduloECFD_plus/ValidadorCFDI/Validador%20cfdi.html")
                            
                            if cfdi_data.get('cfdi_xml', False):
                                url_pac = '</"%s"><!--Para validar el XML CFDI puede descargar el certificado del PAC desde la siguiente liga: la liga de los certificados del PAC-->' % (
                                    comprobante)
                                cfdi_data['cfdi_xml'] = cfdi_data[
                                    'cfdi_xml'].replace('</"%s">' % (comprobante), url_pac)
                                file = base64.encodestring(
                                    cfdi_data['cfdi_xml'] or '')
                                cfdi_xml = cfdi_data.pop('cfdi_xml')

                            if cfdi_xml:
                                invoice_obj.write(cr, uid, [invoice.id], cfdi_data)
                                cfdi_data['cfdi_xml'] = cfdi_xml

                            else:
                                msg = 'No se pudo extraer el XML del PAC'

                            

                else:
                    msg = 'No se encontro informacion del web services del PAC, verifique que la configuracion sea correcta'
                    raise osv.except_osv('Aviso', msg)
                
                
            return {'file': file, 'msg': msg, 'cfdi_xml': cfdi_xml}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
{}


