# 🤖 Blueprint Generator Agent - הוראות שימוש

## מה זה?

זה פרומפט מוכן שאתה יכול להעתיק ל-**ChatGPT** או **Claude** והוא יייצר לך `blueprint.json` מוכן לייבוא ל-Make.com.

---

## 📋 איך משתמשים?

### שלב 1: העתק את הפרומפט
העתק את כל התוכן מהקובץ: `agent_prompts/blueprint_generator_agent.md`

### שלב 2: שלח ל-ChatGPT/Claude
1. פתח שיחה חדשה ב-ChatGPT (GPT-4) או Claude
2. הדבק את הפרומפט המלא
3. המתן לאישור מהסוכן

### שלב 3: בקש blueprint
כתוב מה אתה רוצה, למשל:
```
צור תרחיש שכאשר מגיע טופס חדש ב-Google Forms,
שולח מייל עם הפרטים דרך Gmail
```

### שלב 4: קבל JSON מוכן
הסוכן יחזיר לך:
```json
{
  "name": "...",
  "flow": [...],
  "metadata": {...}
}
```

### שלב 5: ייבא ל-Make.com
1. העתק את כל ה-JSON
2. ב-Make.com: Scenarios → Create → Import Blueprint
3. הדבק את ה-JSON
4. קשר חשבונות ידנית (Google Forms, Gmail)
5. Save & Run!

---

## ✅ מה הסוכן יודע לעשות?

- ✅ ליצור blueprints תקינים לפי Schema 2.1
- ✅ להשתמש במודולים נפוצים (Google Forms, Gmail, Sheets, Calendar, Slack, HTTP)
- ✅ ליצור ניתוב מותנה (Routers)
- ✅ להוסיף טיפול בשגיאות (Error handlers)
- ✅ לאמת את ה-JSON לפני החזרה
- ✅ להסביר מה הוא יצר

---

## 📚 דוגמאות לבקשות

### פשוט
```
שלח מייל כשמגיע טופס חדש
```

### בינוני
```
כשמתעדכן גיליון Google Sheets בעמודה "סטטוס" לערך "דחוף",
צור אירוע ב-Google Calendar ושלח הודעת Slack
```

### מתקדם
```
צור webhook שמקבל נתונים, בודק אם השדה "type" שווה ל-"order",
ואם כן שולח בקשת HTTP ל-API חיצוני עם retry של 3 פעמים,
ואז מעדכן את התוצאה בגיליון
```

---

## ⚠️ מגבלות

1. **הסוכן לא יכול לקשר חשבונות** - זה תמיד ידני ב-Make.com (תכונת אבטחה)
2. **צריך לדעת מה אתה רוצה** - ככל שהבקשה מפורטת יותר, התוצאה טובה יותר
3. **אימות ידני מומלץ** - תמיד כדאי לבדוק את ה-JSON לפני ייבוא

---

## 🔄 אם משהו לא עובד

אם קיבלת blueprint לא תקין:

### אפשרות 1: בקש תיקון
```
התרחיש לא עבר אימות ב-Make.com, אפשר לתקן?
השגיאה: [הדבק את הודעת השגיאה]
```

### אפשרות 2: בקש הסבר
```
תסביר לי מה כל module עושה בתרחיש
```

### אפשרות 3: התחל מחדש
```
בוא ננסה גישה פשוטה יותר - רק טופס ומייל
```

---

## 💡 טיפים לתוצאות טובות

1. **היה ספציפי**
   - ❌ "שלח מיילים"
   - ✅ "שלח מייל דרך Gmail לכתובת שהוזנה בטופס Google Forms"

2. **ציין את האפליקציות**
   - ❌ "עדכן גיליון"
   - ✅ "עדכן Google Sheets בעמודה A"

3. **תאר את הלוגיקה**
   - ❌ "עשה משהו אם צריך"
   - ✅ "אם השדה 'priority' שווה ל-'high', אז..."

4. **בקש הסברים**
   ```
   תסביר לי צעד-צעד מה התרחיש עושה
   ```

---

## 📖 מודולים נפוצים שהסוכן מכיר

| אפליקציה | טריגרים | פעולות |
|-----------|----------|---------|
| **Google Forms** | `watchResponses` | - |
| **Google Sheets** | `watchUpdatedCells` | `addRow`, `updateRow` |
| **Gmail** | `watchEmails` | `sendEmail` |
| **Google Calendar** | `watchEvents` | `createEvent` |
| **Slack** | `watchMessages` | `sendMessage` |
| **HTTP** | `webhookEvent` | `MakeARequest` |
| **Control Flow** | - | `BasicRouter`, `SetVariable` |

---

## 🎯 דוגמה מלאה

### הבקשה שלך:
```
צור תרחיש: כשמגיעה תגובה חדשה ב-Google Forms,
בדוק אם השדה "age" גדול מ-18.
אם כן - שלח מייל ל-manager@example.com
אם לא - שלח מייל ל-support@example.com
```

### התשובה שתקבל:
```json
{
  "name": "Form Response with Age Routing",
  "flow": [
    {
      "id": 1,
      "module": "google-forms:watchResponses",
      "version": 1,
      "parameters": {"__IMTCONN__": 123456},
      "mapper": {},
      "metadata": {"designer": {"x": 0, "y": 0}}
    },
    {
      "id": 2,
      "module": "builtin:BasicRouter",
      "version": 1,
      "routes": [
        {
          "flow": [
            {
              "id": 3,
              "module": "gmail:sendEmail",
              "version": 1,
              "parameters": {"__IMTCONN__": 234567},
              "mapper": {
                "to": "manager@example.com",
                "subject": "Adult Form Response",
                "text": "Received response from {{1.email}}"
              },
              "metadata": {"designer": {"x": 300, "y": -50}}
            }
          ],
          "filter": {
            "name": "Age >= 18",
            "conditions": [[
              {"a": "{{1.age}}", "b": "18", "o": "number:greaterOrEqual"}
            ]]
          }
        },
        {
          "flow": [
            {
              "id": 4,
              "module": "gmail:sendEmail",
              "version": 1,
              "parameters": {"__IMTCONN__": 234567},
              "mapper": {
                "to": "support@example.com",
                "subject": "Minor Form Response",
                "text": "Received response from {{1.email}}"
              },
              "metadata": {"designer": {"x": 300, "y": 50}}
            }
          ],
          "filter": {
            "name": "Age < 18",
            "conditions": [[
              {"a": "{{1.age}}", "b": "18", "o": "number:less"}
            ]]
          }
        }
      ],
      "metadata": {"designer": {"x": 150, "y": 0}}
    }
  ],
  "metadata": {
    "version": 1,
    "scenario": {
      "roundtrips": 1,
      "maxErrors": 3,
      "autoCommit": false,
      "sequential": false,
      "confidential": false,
      "dataloss": false,
      "dlq": false
    }
  }
}
```

---

## 🚀 מוכן להתחיל?

1. פתח את הקובץ: `agent_prompts/blueprint_generator_agent.md`
2. העתק הכל
3. הדבק ב-ChatGPT (GPT-4) או Claude
4. התחל לבקש blueprints!

---

**עצה אחרונה**: שמור את השיחה עם הסוכן - אפשר לבקש שינויים ושיפורים בתרחיש אותו הוא כבר יצר.
