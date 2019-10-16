{
    #Product Info
    'name': 'Export Sale Order in Excel',
    'version': '12.0',
    'category': 'Sales',
    'license': 'OPL-1',    
    'summary':"Export Single or Multiple Sale Order by Single Click",
    
    #Writer
    'author': 'YoungWings Technologies',
    'maintainer': 'YoungWings Technologies',
    'description': """ You can export Single or Multiple SaleOrder to by single click""",
    
    #Dependencies
    'depends': ['sale_management'],
    
    #View
    'data': [ 'wizard/ywt_export_sale_order_views.xml' ],
     
    #Banner     
    "images": ["static/description/banner.png"],
    
    
    'installable': True,
    'auto_install': False,
    'application' : True,
    'price':5,
    'currency': 'EUR'
    
}
