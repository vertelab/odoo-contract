from odoo import http, fields
from odoo.http import request
from odoo.exceptions import AccessError, MissingError, UserError
from odoo.addons.project.controllers.portal import ProjectCustomerPortal
import logging

_logger = logging.getLogger(__name__)


class ProjectCustomerPortalExtended(ProjectCustomerPortal):


    @http.route('/my/tasks/sign/<int:task_id>', type='http', auth='public', methods=['POST'], csrf=True)
    def sign_task(self, task_id, access_token=None, **kw):
        try:
            task_sudo = self._document_check_access('project.task', task_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        try:
            if task_sudo.is_aaw and request.httprequest.method == 'POST':
                task_sudo.is_signed = True
                task_sudo.message_post(
                    body=f"You have agreed to this AAW Task.",
                    message_type='comment',
                    subtype_xmlid='mail.mt_comment',
                    author_id=request.env.user.partner_id.id
                )
                # Redirect back to task with success message
                return request.redirect(f'/my/tasks/{task_id}?message=signed_success')
        except Exception as e:
            _logger.error(f"Error signing task: {str(e)}")
            return request.redirect(f'/my/task/{task_id}?message=error')

