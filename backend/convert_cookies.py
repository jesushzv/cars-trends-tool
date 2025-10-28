"""
Quick script to convert Cookie Editor format to simple format
Run this once to convert your exported cookies
"""
import json

# Your exported cookies (paste them here)
cookie_array = [
  {
    "domain": ".facebook.com",
    "expirationDate": 1796009923.68555,
    "hostOnly": False,
    "httpOnly": True,
    "name": "datr",
    "path": "/",
    "sameSite": "no_restriction",
    "secure": True,
    "session": False,
    "storeId": "0",
    "value": "S5f9aOhVBs7BJpE0lYa5mfCf"
  },
  {
    "domain": ".facebook.com",
    "expirationDate": 1796009964.681622,
    "hostOnly": False,
    "httpOnly": True,
    "name": "sb",
    "path": "/",
    "sameSite": "no_restriction",
    "secure": True,
    "session": False,
    "storeId": "0",
    "value": "S5f9aL1Hf6dP1ccLgjAGNXE6"
  },
  {
    "domain": ".facebook.com",
    "expirationDate": 1796009829.978828,
    "hostOnly": False,
    "httpOnly": True,
    "name": "ps_l",
    "path": "/",
    "sameSite": "lax",
    "secure": True,
    "session": False,
    "storeId": "0",
    "value": "1"
  },
  {
    "domain": ".facebook.com",
    "expirationDate": 1796009829.978942,
    "hostOnly": False,
    "httpOnly": True,
    "name": "ps_n",
    "path": "/",
    "sameSite": "no_restriction",
    "secure": True,
    "session": False,
    "storeId": "0",
    "value": "1"
  },
  {
    "domain": ".facebook.com",
    "expirationDate": 1792985964.681345,
    "hostOnly": False,
    "httpOnly": False,
    "name": "c_user",
    "path": "/",
    "sameSite": "no_restriction",
    "secure": True,
    "session": False,
    "storeId": "0",
    "value": "100000801259693"
  },
  {
    "domain": ".facebook.com",
    "expirationDate": 1792985964.681847,
    "hostOnly": False,
    "httpOnly": True,
    "name": "xs",
    "path": "/",
    "sameSite": "no_restriction",
    "secure": True,
    "session": False,
    "storeId": "0",
    "value": "3%3AGA75YVNSzOUAug%3A2%3A1761449962%3A-1%3A-1"
  },
  {
    "domain": ".facebook.com",
    "expirationDate": 1769225964.992717,
    "hostOnly": False,
    "httpOnly": True,
    "name": "fr",
    "path": "/",
    "sameSite": "no_restriction",
    "secure": True,
    "session": False,
    "storeId": "0",
    "value": "0x7LXYq2NkOEUEAI1.AWc7YEcZ7PleIzvolahbqvpto9dlDtBYfZdj3gNiI1kvetyJ81o.Bo_ZdL..AAA.0.0.Bo_Zfs.AWcecInENexms_KHRrt56CcSrqs"
  },
  {
    "domain": ".facebook.com",
    "hostOnly": False,
    "httpOnly": False,
    "name": "presence",
    "path": "/",
    "sameSite": "unspecified",
    "secure": True,
    "session": True,
    "storeId": "0",
    "value": "C%7B%22t3%22%3A%5B%5D%2C%22utc3%22%3A1761449969100%2C%22v%22%3A1%7D"
  },
  {
    "domain": ".facebook.com",
    "expirationDate": 1762054856,
    "hostOnly": False,
    "httpOnly": False,
    "name": "wd",
    "path": "/",
    "sameSite": "lax",
    "secure": True,
    "session": False,
    "storeId": "0",
    "value": "901x711"
  }
]

# Convert to simple format
simple_cookies = {}
for cookie in cookie_array:
    simple_cookies[cookie['name']] = cookie['value']

# Save to fb_cookies.json
with open('fb_cookies.json', 'w') as f:
    json.dump(simple_cookies, f, indent=2)

print("✅ Cookies converted successfully!")
print(f"✅ Saved to fb_cookies.json")
print(f"✅ Found {len(simple_cookies)} cookies:")
for name in simple_cookies.keys():
    print(f"   - {name}")

print("\n🎉 Ready to test! Run: python scrapers/facebook_marketplace.py")

