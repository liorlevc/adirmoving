# אדיר שירותי הובלות ואחסנה

אתר סטטי. פרטי העסק (טלפון, וואטסאפ, שעות, אזורים) נערכים בבלוק `CONFIG` בתחתית `index.html`.

פריסה: Render Static Site, publish path `./`.

## עמודי SEO

כל תצוגה חשובה מקבלת גם כתובת אמיתית (למשל `/storage/`). אחרי כל שינוי ב-`index.html` מריצים `python3 build_pages.py`, שמייצר את העמודים ומעדכן את `sitemap.xml`.
