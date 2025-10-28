# How to Get Facebook Cookies for Marketplace Scraper

This guide will help you export your Facebook cookies so the scraper can access Facebook Marketplace on your behalf.

---

## ⚠️ Important Notes

- **Your cookies = Your account**: Anyone with your cookies can access Facebook as you. Keep them secure!
- **Don't share cookies**: Never commit `fb_cookies.json` to git (it's already in `.gitignore`)
- **Cookies expire**: Facebook cookies typically last 30-60 days. Re-export if the scraper stops working
- **Use your own account**: Only use cookies from your personal Facebook account

---

## Method 1: Using "Cookie Editor" Extension (Recommended)

### Step 1: Install Cookie Editor

**Chrome / Edge:**
1. Go to: https://chrome.google.com/webstore/
2. Search for "Cookie Editor"
3. Install the extension (by cgagnier)

**Firefox:**
1. Go to: https://addons.mozilla.org/
2. Search for "Cookie Editor"
3. Install the add-on

### Step 2: Log into Facebook

1. Open your browser
2. Go to https://www.facebook.com
3. Log in with your credentials
4. Navigate to Facebook Marketplace: https://www.facebook.com/marketplace

### Step 3: Export Cookies

1. Click the "Cookie Editor" extension icon (usually in top-right corner)
2. You should see all Facebook cookies
3. Click "Export" button (usually looks like ⬇️ or has "Export" label)
4. Choose "JSON" format
5. Copy the exported cookies

### Step 4: Save Cookies

1. Open the file: `backend/fb_cookies.json.template`
2. Copy it and rename to: `backend/fb_cookies.json`
3. Paste your exported cookies into `fb_cookies.json`
4. Save the file

**Example format:**
```json
{
  "c_user": "1234567890",
  "xs": "12%3A0123456789abcdef...",
  "fr": "0abcdef123456789...",
  "datr": "ABCDEFG123456789...",
  "sb": "HIJKLMN987654321..."
}
```

---

## Method 2: Using Browser Developer Tools (Manual)

### For Chrome/Edge:

1. Log into Facebook and go to Marketplace
2. Press `F12` to open Developer Tools
3. Go to "Application" tab
4. In left sidebar: "Storage" → "Cookies" → "https://www.facebook.com"
5. Look for these important cookies:
   - `c_user` (your user ID)
   - `xs` (session token)
   - `fr` (identity verification)
   - `datr` (device token)
   - `sb` (session binding)
6. Copy Name and Value for each cookie
7. Create a JSON file with format shown above

### For Firefox:

1. Log into Facebook and go to Marketplace
2. Press `F12` to open Developer Tools
3. Go to "Storage" tab
4. In left sidebar: "Cookies" → "https://www.facebook.com"
5. Find and copy the same cookies as Chrome instructions
6. Create a JSON file with the values

---

## Testing Your Cookies

Once you've saved `fb_cookies.json`, test it:

```bash
cd backend
python scrapers/facebook_marketplace.py
```

**Expected output if cookies work:**
```
[INFO] Loaded 5 cookies
[INFO] Launching browser...
[SUCCESS] Authenticated successfully!
```

**Expected output if cookies don't work:**
```
[ERROR] Not logged in - cookies may be invalid or expired
```

If authentication fails:
1. Make sure you're logged into Facebook
2. Export fresh cookies
3. Check that `fb_cookies.json` has valid JSON format
4. Try again

---

## Troubleshooting

### "No Facebook cookies found"
- Make sure you saved the file as `fb_cookies.json` (not `.template`)
- Check the file is in `backend/` directory
- Verify the file contains actual cookies (not the template text)

### "Invalid JSON in fb_cookies.json"
- Cookies must be valid JSON format
- Use a JSON validator: https://jsonlint.com
- Make sure all strings are quoted
- No trailing commas

### "Not logged in - cookies may be invalid"
- Cookies have expired (export fresh ones)
- Facebook detected unusual activity (wait 24 hours, try again)
- Wrong cookies copied (re-export from Facebook, not another site)

### "Rate Limited"
- Facebook is limiting requests
- Wait 1-2 hours before trying again
- Reduce `max_results` parameter
- Use longer delays between scrapes

---

## Security Best Practices

1. ✅ **Keep cookies private**: Never share or upload them
2. ✅ **Use .gitignore**: Already configured to exclude `fb_cookies.json`
3. ✅ **Refresh regularly**: Export new cookies every month
4. ✅ **Monitor your account**: Check for unusual login activity
5. ✅ **Log out when done**: If you're concerned, log out of Facebook and cookies will be invalidated

---

## Cookie Expiration

Facebook cookies typically expire after:
- **30-60 days** of inactivity
- **Immediately** if you log out
- **Immediately** if you change your password
- **Variable** if Facebook detects suspicious activity

When cookies expire, simply export fresh ones and replace the file.

---

## Alternative: Manual Data Import (Future)

If Facebook's anti-scraping measures become too aggressive, we'll add a manual import feature where you can:
1. Download listing data directly from Facebook
2. Upload it to the app
3. Still get all the analytics and trends

This would be more reliable but require manual updates.

---

## Need Help?

If you're stuck:
1. Check `FB_MARKETPLACE_RESEARCH.md` for technical details
2. Review error messages carefully (they have hints!)
3. Ensure you're logged into Facebook before exporting
4. Try the Cookie Editor extension (easiest method)
5. Verify JSON format is correct

**Remember:** This scraper is a "best effort" tool. Facebook can change their structure anytime, making scraping difficult. The cookie-based approach is the most reliable method we have.

