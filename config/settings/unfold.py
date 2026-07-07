UNFOLD = {
    "SITE_TITLE": "MedCore CRM Admin",
    "SITE_HEADER": "MedCore",
    "SITE_SUBHEADER": "Klinika boshqaruv tizimi",
    "SITE_URL": "/",
    "SITE_SYMBOL": "medical_services",
    "BORDER_RADIUS": "16px",
    "THEME": "dark",
    "SITE_LOGO": {
        "light": "/static/images/logo.png",
        "dark": "/static/images/logo.png",
    },
    "STYLES": {
        "css": [
            lambda request: """
                html body div.flex.items-center.gap-4 img.unfold-logo,
                html body .unfold-sidebar header img,
                html body a[href="/admin/"] img {
                    width: 70px !important;
                    height: 70px !important;
                    object-fit: cover !important;
                    border-radius: 50% !important;
                    border: 3px solid #10b981 !important;
                    box-shadow: 0 0 15px rgba(16, 185, 129, 0.4) !important;
                    margin: 15px auto !important;
                    display: block !important;
                }
                html body div.flex.items-center.gap-4 .material-symbols-outlined {
                    display: none !important;
                }
                html body main .grid > div,
                html body main div[class*="shadow"] {
                    background-color: #1a2333 !important;
                    border: 2px solid #2e3b52 !important;
                    border-radius: 20px !important;
                    padding: 24px !important;
                    margin-bottom: 30px !important;
                    box-shadow: 0 10px 25px -5px rgba(0,0,0,0.3) !important;
                }
                html body main .grid > div table,
                html body main .grid > div div[class*="border-b"] {
                    background: #151c2c !important;
                    border-radius: 12px !important;
                    border: 1px solid #243146 !important;
                }
                html body div[class*="login"] img,
                html body .unfold-login-box img {
                    width: 130px !important;
                    height: 130px !important;
                    border-radius: 50% !important;
                    border: 4px solid #10b981 !important;
                    box-shadow: 0 0 25px rgba(16, 185, 129, 0.5) !important;
                    margin: 0 auto 30px auto !important;
                }
                html body .unfold-sidebar {
                    background-color: #0f141c !important;
                    border-right: 1px solid #1e293b !important;
                }
                html .unfold-sidebar-section-title {
                    color: #10b981 !important;
                    font-weight: 700 !important;
                    text-transform: uppercase !important;
                    letter-spacing: 0.05em !important;
                    border-left: 3px solid #10b981 !important;
                    padding-left: 10px !important;
                }
            """
        ],
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "Asosiy Dashboard",
                "separator": True,
                "items": [
                    {"title": "Bosh sahifa", "icon": "space_dashboard", "link": "/admin/"},
                ],
            },
            {
                "title": "Foydalanuvchilar (Accounts)",
                "separator": True,
                "collapsible": False,
                "items": [
                    {"title": "Xodimlar (Users)", "icon": "group", "link": "/admin/accounts/user/"},
                    {"title": "Profillar (Profiles)", "icon": "contact_page", "link": "/admin/accounts/profile/"},
                ],
            },
            {
                "title": "Tashkilot (Organizations)",
                "separator": True,
                "collapsible": False,
                "items": [
                    {"title": "Klinikalar", "icon": "local_hospital", "link": "/admin/organizations/clinic/"},
                    {"title": "Filiallar", "icon": "account_balance", "link": "/admin/organizations/branch/"},
                    {"title": "Bo'limlar", "icon": "meeting_room", "link": "/admin/organizations/department/"},
                    {"title": "Xonalar", "icon": "door_front", "link": "/admin/organizations/room/"},
                ],
            },
            {
                "title": "Xavfsizlik Tizimi",
                "separator": True,
                "collapsible": True,
                "items": [
                    {"title": "Guruhlar", "icon": "shield_person", "link": "/admin/auth/group/"},
                    {"title": "API Tokenlar", "icon": "key", "link": "/admin/authtoken/tokenproxy/"},
                ],
            },
            {
                "title": "Bemorlar (Patients)",
                "separator": True,
                "collapsible": False,
                "items": [
                    {"title": "Bemorlar", "icon": "personal_injury", "link": "/admin/patients/patient/"},
                    {"title": "Tibbiy yozuvlar (Tashxis)", "icon": "description", "link": "/admin/patients/medicalrecord/"},
                    {"title": "Allergiyalar", "icon": "vaccines", "link": "/admin/patients/patientallergy/"},
                    {"title": "Surunkali kasalliklar", "icon": "monitor_heart", "link": "/admin/patients/patientchronicdisease/"},
                ],
            },
            {
                "title": "Navbatlar (Appointments)",
                "separator": True,
                "collapsible": False,
                "items": [
                    {"title": "Uchrashuvlar", "icon": "calendar_month", "link": "/admin/appointments/appointment/"},
                    {"title": "Navbat holati", "icon": "confirmation_number", "link": "/admin/appointments/queue/"},
                    {"title": "Qabullar (Visit)", "icon": "assignment_turned_in", "link": "/admin/appointments/visit/"},
                ],
            },
        ],
    },
}   