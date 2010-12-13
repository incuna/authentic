Simple data document generator containing a TOTP soft token
===========================================================

To use it from your python application just do:

  import totp_bookmarklet

  html_fragment = '<a href="%s">OTP Bookmarklet</a>' % totp_bookmarklet.otp_doc('my_secret')
