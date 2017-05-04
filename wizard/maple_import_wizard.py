# -*- coding:utf-8 -*-
import base64
from tempfile import TemporaryFile
from openerp import models, fields, api, _
import csv
from datetime import datetime
from openerp.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class ImportAcerReport(models.TransientModel):
    _name = 'import.acer'

    import_file = fields.Binary(string="Import CSV File", redonly=True)
    datas_fname = fields.Char('Import File Name')
    acer_location_id = fields.Many2one(
        'stock.location', 'Destination Location',
#        index=True,
        required=True,
        domain="[('name','ilike','class'),('maxItem','>',0)]", #Classement 1, Classement 2, Classement NB
        help="Select the classification location involved."
        )
    
    @api.multi
    def action_acer_import_file(self):
#        active_id = self._context.get('active_id')
#        active_model = self._context.get('active_model')
#        stock_id = self.env[active_model].browse(active_id)
#        product_obj = self.env['product.product']
#        product_uom_obj = self.env['product.uom']
        partner_obj = self.env['res.partner']
        product_obj = self.env['product.product']
        acer_obj = self.env['maple.import_acer']
        site_obj = self.env['maple.weighing_classif_site']
        weighing_obj = self.env['maple.weighing_picking']
        employee_obj = self.env['hr.employee']
        quant_obj = self.env['stock.quant']
        flavor_obj = self.env['maple.flavors']
        flaw_obj = self.env['maple.flaws']
#        stock_inv_line_obj = self.env['stock.inventory.line']
#       ctx = self.env.context
#         if self.location_id:
#             location_id = self.location_id.id
#        elif 'active_id' in ctx:
#            inventory_obj = self.env['stock.inventory']
#            inventory = inventory_obj.browse(ctx['active_id'])
#            location_id = inventory.location_id and inventory.location_id.id or False

        if self.datas_fname[-4:] == '.txt':
            fileobj = TemporaryFile('w+')
            fileobj.write(base64.decodestring(self.import_file))
            fileobj.seek(0)
            reader = csv.reader(fileobj, quotechar='"', delimiter=';')
            count = 1
            lines = []
            missing_partner = []
            for row in reader:
                
                
                row_prod_id = row[41]+row[21] #barrel type
                row_serial = row[19]
                row_dom = [('container_serial','=ilike',row_serial)]
                row_quant = quant_obj.search(row_dom)
                row_flavor = flavor_obj.search([('name','=',str(row[29]))])
                row_flaw = flaw_obj.search([('name','=',row[30])])
                
# DOIT MODIFIER LA RECHERCHE EN CAS DE NUMÉRO DE SÉRIE EN DOUBLE
#                if row_quant and len(row_quant) == 1:
                    
                                
#                _logger.info(u"line %s - Scellé = %s"% (count,row[18]))
#                if count == 1:
#                    count += 1
#                    continue
                _logger.info(u"line %s - Scellé = %s"% (count,row[18]))
                count += 1
                classif_date = datetime.strptime(row[3], '%Y-%m-%d')
#                product = product_obj.search([('default_code','=',row[0])])
#                if product:
                partner = partner_obj.search([('fpaqCode','=',row[1])])
                if len(partner) == 1:
                    while partner.parent_id:
                        partner = partner.parent_id
                else:
                    parent = []
                    for p in partner:
                        while p.parent_id:
                            p = p.parent_id
                        if p not in parent:
                            parent.append(p)
                    if len(parent) == 1:
                        partner = parent[0]
#                site_no = site_obj.search([('site_no','=',row[9])])
                acer = acer_obj.search([('seal_no','=',row[18])])
                inspectNb = row[18][2:3]
                employee = employee_obj.search([('inspectNb','=',inspectNb)])
                if not employee:
                    employee_vals = {
                            'name':row[17],
                            'inspectNb':inspectNb,
                            'barrelCnt':str(int(row[18][5:9]) - 1)
                            }
                    employee = employee_obj.create(employee_vals)
                weighing = weighing_obj.search([('name','=',row[0])])
                if not weighing:
                    weighing_vals = {
                            'name':row[0],
                            'maple_producer':partner.id, #link to maple_weighing
                            'employee_id':employee.id,
                            }
                    weighing = weighing_obj.create(weighing_vals)
                if not partner :
                    missing_partner.append(row[1])
                else:
                                        
                    line_vals = {
                            'maple_producer':partner.id, #link to res.partner
                            'weighing_no':row[0], #link to maple_weighing
                            'weighing_picking_id':weighing.id,
                            'producer_fpaq':row[1], #used to link to res.partner
                            'report_no':row[2],
                            'classif_date':classif_date, #from import - but fixed - row 3
                            'producer_name':row[4], #from import
                            'producer_city':row[5], #from import
                            'producer_zip': row[6], #from import
                            'producer_phone':row[7], #from import
                            'container_owner':row[8],
#                            'site_no':site_no.id, #link to maple.classif_site - from row 9
                            'site_no':row[9], #from import
                            'fpaqContact_name': row[10], #from import
                            'fpaqContact_address':row[11], #from import
                            'fpaqContact_city':row[12], #from import
                            'fpaqContact_state':row[13], #from import
                            'fpaqContact_zip': row[14], #from import
                            'fpaqContact_phone':row[15], #from import
                            'supervised':row[16], #from import
                            'inspector':row[17], #from import
                            'seal_no': row[18], #OUR MAIN KEY
                            'container_no':row[19], #from import
                            'gross_weight':row[20], #from import
                            'tare':row[21], #from import
                            'net_weight': row[22], #from import
                            'container_state':row[23], #TO LINK
                            'weight_adjust':row[24], #from import
                            'maple_grade': row[25], #from import
                            'maple_type':row[26], #from import
                            'maple_brix':row[27], #from import
                            'maple_light':row[28], #from import
                            'maple_flaw': row_flaw.id, #from import
                            'maple_flavor': row_flavor.id, #from import
                            'maple_clarity':row[31], #from import
                            'maple_si':row[32], #from import
                            'maple_ph': row[33], #from import
                            'maple_iodine':row[34], #from import
                            'maple_na': row[35], #from import
                            'maple_pb':row[36], #from import
                            'maple_retained':row[37], #from import
                            'maple_special_test':row[38], #from import
                            'classif_revision': row[39], #from import
                            'weighing_order':row[40], #from import
                            'container_type': row[41] #from import
                            }

                # row 3 = serial
#                     if row[3]:
#                         lot = product_lot_obj.search([('name','=',row[3])])
#                         if not lot:
#                             serial_vals = {
#                             'product_id':product.id,
#                             'product_qty':row[1],
#                             'name':row[3]
#                                 }
#                             serial_line = product_lot_obj.create(serial_vals)
#                             lot = product_lot_obj.search([('name','=',row[3])])
#                         if lot:
#                             line_vals.update({'prod_lot_id':lot.id})
                # check si le baril existe ailleur
                    if acer: #connées déjà importées
                        _logger.info(u"line %s - Scellé = %s - write"% (count,row[18]))
                        acer.write(line_vals)
                    else:
                        _logger.info(u"line %s - Scellé = %s - append"% (count,row[18]))
                        acer = acer_obj.create(line_vals)

#                    
                    quant_vals = {
                            'acer_report_no': row[2],
                            'class_date': classif_date,
#                            'site_no':site_no.id, #link to maple.classif_site - from row 9
                            'supervised':row[16], #from import
                            'controler':employee.id,
                            'maple_seal_no': row[18], #OUR MAIN KEY
#                            'net_weight': row[22], #from import
#                            'weight_adjust':row[24], #from import INDIQUER SI DIFFÉRENT DE LA VALEUR CALCULÉE
                            'maple_grade': row[25], #from import > CHAR
                            'maple_brix':row[27], #from import > FLOAT
                            'maple_light':row[28], #from import > INTEGER
                            'maple_flaw': row_flaw.id, #from import - ajouter à stock quant
                            'maple_flavor': row_flavor.id, #from import
                            'maple_clarity':row[31], #from import
                            'maple_si':row[32], #from import
                            'maple_ph': row[33], #from import
                            'maple_iodine':row[34], #from import
                            'maple_na': row[35], #from import
                            'maple_pb':row[36], #from import
                            'maple_retained':row[37], #from import
                            'maple_special_test':row[38], #from import
                            'classif_revision': row[39], #from import
                            }
                    row_quant.write(quant_vals)

#            else:
#                missing_product.append(row[0])
#        if not missing_product and lines:
#            for line_vals in lines:
#                acer = acer_obj.create(line_vals)
#        else:
#            missing_product_name = ',\n'.join(missing_product)
#                raise ValidationError(_('Below products are missing in system \n %s.'%missing_product_name))
        else:
            raise ValidationError(_('Wrong file format. Please enter .csv file.'))
