# Facebook Marketplace Research Notes

**Date**: October 25, 2025  
**Target**: Car listings in Tijuana, Mexico region  
**Status**: Initial Research

---

## URL Structure

### Main Search URL Pattern:
```
https://www.facebook.com/marketplace/tijuana/vehicles
https://www.facebook.com/marketplace/category/vehicles
```

### Listing URL Pattern:
```
https://www.facebook.com/marketplace/item/{ITEM_ID}
```

---

## Authentication Requirements

### Known Facts:
- Facebook Marketplace requires login to view full listing details
- Anonymous access is heavily restricted
- Engagement metrics (likes, saves) only visible when logged in
- Search results may be visible without auth, but details are not

### Authentication Approach:
**Decision**: Use cookie-based authentication
- User logs in manually to Facebook
- Exports cookies using browser extension
- We use cookies for authenticated requests
- More reliable than automated login (less likely to trigger security)

---

## Data Available

### On Search Results Page:
- Listing title
- Price
- Location
- Thumbnail image
- Basic preview text

### On Individual Listing Page (requires auth):
- Full description
- All images
- Seller information
- **Engagement metrics**: Likes, Saves, Messages
- Vehicle details (year, make, model, mileage)
- Listing creation date

---

## Engagement Metrics

### Available on FB Marketplace:
1. **Saves** (bookmark icon) - Number of people who saved the listing
2. **Likes/Reactions** - May not be visible for marketplace items
3. **Messages** - Not a public metric, but we could track "interested" count if visible

### What We'll Extract:
- `saves` - Most reliably available
- `views` - If available
- `comments` - If available (less common on marketplace)

---

## Anti-Bot Measures

### Known Protections:
1. **Rate Limiting** - Aggressive rate limits on requests
2. **CAPTCHA** - Triggered by suspicious behavior
3. **JavaScript Rendering** - Heavy client-side rendering
4. **Session Validation** - Checks for valid user sessions
5. **Device Fingerprinting** - Tracks browser signatures

### Mitigation Strategy:
- Use realistic delays (5-10 seconds between requests)
- Rotate user agents
- Use persistent cookies
- Limit scraping volume (max 10-20 listings per session)
- Headless browser with Playwright (renders JavaScript)

---

## Technical Requirements

### Tools Needed:
- ✅ Playwright (JavaScript rendering)
- ✅ Cookie management
- ✅ Request delays
- ✅ Error handling for rate limits

### Success Criteria:
- Can access authenticated pages with cookies
- Can extract at least 5 listings per run
- Engagement metrics captured
- Graceful handling of rate limits

---

## Risk Assessment

### High Risk:
- Account suspension if detected as bot
- IP blocking
- CAPTCHA challenges

### Mitigation:
- Use personal cookies (user owns the account)
- Low volume scraping only
- Long delays between requests
- Clear error messages if blocked
- **Fallback**: Manual data export feature

---

## Authentication Strategy Decision

### ✅ Chosen Approach: Cookie-Based Authentication

**Rationale:**
1. **Less Risk**: No automated login = lower chance of account suspension
2. **User Control**: User owns their account and cookies
3. **Simpler**: No complex automation of login forms
4. **Reliable**: Once cookies work, they're stable until expiration

### Implementation Plan:
1. User manually logs into Facebook in their browser
2. User exports cookies using browser extension (e.g., "Cookie Editor", "EditThisCookie")
3. User saves cookies to `backend/fb_cookies.json`
4. Scraper loads cookies and uses them for authenticated requests
5. Cookies expire → User re-exports (typically 30-60 days validity)

### Cookie Format:
```json
{
  "c_user": "123456789",
  "xs": "...",
  "fr": "...",
  ...
}
```

### Alternative: Manual Data Import (Fallback)
If Facebook blocks scraping too aggressively:
- Provide a manual import endpoint
- User downloads their marketplace data
- We import and process it
- Still capture engagement metrics

---

## Engagement Metrics Limitation (Verified 2025-10-26)

### Investigation Results

After thorough HTML analysis of authenticated Facebook Marketplace listing pages:

**❌ NOT Available Publicly:**
- Number of saves/likes ("X people saved this")
- View count ("X views")  
- Interested/message count ("X people messaged")

**Why?**
- Facebook Marketplace **does NOT publicly display** engagement metrics on listing pages
- Metrics are only visible to the seller in their dashboard
- **Intentional design** - prevents data from affecting buyer/seller negotiations

**Technical Confirmation:**
- Scraped authenticated listing page HTML (4.2MB) 
- Searched for all engagement patterns (saves, views, interested, messages)
- Found **NO public engagement data** in visible text, aria labels, or data attributes
- Conclusion: Data simply not present in public HTML

**Database Impact:**
- Engagement fields (views, likes, comments) remain in schema for other platforms
- Facebook listings will have `NULL` values (expected and documented behavior)

---

## Next Steps

1. ✅ Install Playwright
2. ✅ Create basic scraper structure  
3. ✅ Implement cookie loading
4. ✅ Test with real Facebook cookies
5. ✅ Extract basic listing data
6. ✅ Investigate engagement metrics (confirmed: NOT publicly available)

---

## Notes

- FB Marketplace structure changes frequently
- Selectors will need periodic updates
- Consider this a "best effort" scraper
- Manual import should be available as backup
- **User must provide their own cookies** - we won't automate login

