catalogo_veiculos/
│
├── manage.py
│
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── veiculos/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   │
│   ├── migrations/
│   │   └── __init__.py
│   │
│   └── templates/
│       └── veiculos/
│           ├── home.html
│           ├── catalogo.html
│           ├── detalhe.html
│           └── partials/
│               ├── card_veiculo.html
│               ├── filtros.html
│               └── header.html
│
├── templates/
│   └── base.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── img/
│
├── media/
│   └── veiculos/
│
├── requirements.txt
└── .env