# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields
from wand.image import Image
from odoo import tools
import base64
import os
import tempfile


class ir_attachment(models.Model):
    _inherit = 'ir.attachment'

    @api.depends('datas')
    def _get_display_image(self):
        for attachment in self:
            try:
                if attachment.mimetype != 'application/pdf' or not attachment.datas:
                    attachment.display_image_kanban = False
                    continue
                original_image = attachment.datas
                temp_file = tempfile.NamedTemporaryFile(delete=False)
                temp_file.write(base64.decodestring(original_image))
                temp_file.close()

                temp_image_file = tempfile.NamedTemporaryFile(delete=False)
                with Image(filename=temp_file.name) as img:
                    images = img.sequence
                    pages = len(images)
                    for page in range(pages):
                        Image(images[page]).save(filename=temp_image_file.name)
                        break
                    os.unlink(temp_file.name)
                file_base64 = tools.image_resize_image_big(open(temp_image_file.name, 'rb').read().encode('base64'))
                os.unlink(temp_image_file.name)
                attachment.display_image_kanban = file_base64
            except:
                continue

    display_image_kanban = fields.Binary(
        string='Medium image',
        compute='_get_display_image',
        store=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
