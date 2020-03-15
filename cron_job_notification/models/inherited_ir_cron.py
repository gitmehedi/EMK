import logging
import time

import odoo
from odoo import api, fields, models, _
from odoo import SUPERUSER_ID
from odoo.tools.safe_eval import safe_eval


_logger = logging.getLogger(__name__)

def str2tuple(s):
    return safe_eval('tuple(%s)' % (s or ''))


class IrCron(models.Model):
    _name = 'ir.cron'
    _inherit = ['ir.cron', 'mail.thread']

    is_success_notification = fields.Boolean('Notification On Success', default=False)
    is_failure_notification = fields.Boolean('Notification On Failure', default=False)

    @api.multi
    def success_mail_reminder(self, cron_obj):
        if cron_obj.is_success_notification:
            users = cron_obj.message_follower_ids
            if users:
                for i in users:
                    self.send_success_notification(i)
        return

    @api.multi
    def send_success_notification(self, user):
        su_id = self.env['res.partner'].browse(SUPERUSER_ID)
        template_id = self.env['ir.model.data'].get_object_reference('cron_job_notification',
                                                                     'cron_job_success_notification')[1]
        template_browse = self.env['mail.template'].browse(template_id)
        email_to = self.env['res.partner'].browse(user.partner_id.id).email
        if template_browse:
            values = template_browse.generate_email(user.res_id)
            values['email_to'] = email_to
            values['email_from'] = su_id.email
            values['res_id'] = False
            if not values['email_to'] and not values['email_from']:
                pass
            mail_mail_obj = self.env['mail.mail']
            msg_id = mail_mail_obj.create(values)
            if msg_id:
                mail_mail_obj.send(msg_id)
            return True

    @api.multi
    def failure_mail_reminder(self, cron_obj):
        if cron_obj.is_failure_notification:
            users = cron_obj.message_follower_ids
            if users:
                for i in users:
                    self.send_failure_notification(i)
        return

    @api.multi
    def send_failure_notification(self, user):
        su_id = self.env['res.partner'].browse(SUPERUSER_ID)
        template_id = self.env['ir.model.data'].get_object_reference('cron_job_notification',
                                                                     'cron_job_failure_notification')[1]
        template_browse = self.env['mail.template'].browse(template_id)
        email_to = self.env['res.partner'].browse(user.partner_id.id).email
        if template_browse:
            values = template_browse.generate_email(user.res_id)
            values['email_to'] = email_to
            values['email_from'] = su_id.email
            values['res_id'] = False
            if not values['email_to'] and not values['email_from']:
                pass
            mail_mail_obj = self.env['mail.mail']
            msg_id = mail_mail_obj.create(values)
            if msg_id:
                mail_mail_obj.send(msg_id)
            return True

    @api.model
    def _callback(self, model_name, method_name, args, job_id):
        #overwriting the base module function of ir.cron model
        """ Run the method associated to a given job

                It takes care of logging and exception handling.

                :param model_name: model name on which the job method is located.
                :param method_name: name of the method to call when this job is processed.
                :param args: arguments of the method (without the usual self, cr, uid).
                :param job_id: job id.
                """
        try:
            cron_obj = self.browse(job_id)
            args = str2tuple(args)
            if self.pool != self.pool.check_signaling():
                # the registry has changed, reload self in the new registry
                self.env.reset()
                self = self.env()[self._name]
            if model_name in self.env:
                model = self.env[model_name]
                if hasattr(model, method_name):
                    log_depth = (None if _logger.isEnabledFor(logging.DEBUG) else 1)
                    odoo.netsvc.log(_logger, logging.DEBUG, 'cron.object.execute',
                                    (self._cr.dbname, self._uid, '*', model_name, method_name) + tuple(args),
                                    depth=log_depth)
                    start_time = False
                    if _logger.isEnabledFor(logging.DEBUG):
                        start_time = time.time()
                    getattr(model, method_name)(*args)
                    if start_time and _logger.isEnabledFor(logging.DEBUG):
                        end_time = time.time()
                        _logger.debug('%.3fs (%s, %s)', end_time - start_time, model_name, method_name)
                    self.pool.signal_caches_change()
                    #sending success notification
                    self.success_mail_reminder(cron_obj)
                else:
                    _logger.warning("Method '%s.%s' does not exist.", model_name, method_name)
            else:
                _logger.warning("Model %r does not exist.", model_name)
        except Exception, e:
            _logger.exception("Call of self.env[%r].%s(*%r) failed in Job #%s",
                              model_name, method_name, args, job_id)
            self._handle_callback_exception(model_name, method_name, args, job_id, e)
            #sending failure notification
            self.failure_mail_reminder(cron_obj)



