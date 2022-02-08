# -*- coding: utf-8 -*-
#############################################################################
#
#
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

{
    'name': 'Create Purchase Order From Sales',
    'category': 'Sales, Purchase',
    'summary': "Create Purchase Order From Sales and Vice versa",
    'author': 'APPSGATE FZC LLC',
    'depends': ['sale', 'purchase', 'account'],

    'description': """ 
            Sales 
            Purchase

		Create Sales Order, 
		Create Purchase Order,
	 	Purchase Order From Sales,
		Sales Order From Purchase,


     """,

    'data': [
        'views/sale_view.xml',
        'views/purchase_view.xml'


    ],

    'images': [
        'static/src/img/main-screenshot.png'
    ],

    'demo': [
    ],
    'license': 'AGPL-3',
    'price':'5',
    'currency':'USD',
    'application': True,
    'installable': True,
    'auto_install': False,
}
