/**
 * Cookie plugin
 *
 * Copyright (c) 2006 Klaus Hartl (stilbuero.de)
 * Dual licensed under the MIT and GPL licenses:
 * http://www.opensource.org/licenses/mit-license.php
 * http://www.gnu.org/licenses/gpl.html
 *
 */

/**
 * Create a cookie with the given name and value and other optional parameters.
 *
 * @example $.cookie('the_cookie', 'the_value');
 * @desc Set the value of a cookie.
 * @example $.cookie('the_cookie', 'the_value', { expires: 7, path: '/', domain: 'jquery.com', secure: true });
 * @desc Create a cookie with all available options.
 * @example $.cookie('the_cookie', 'the_value');
 * @desc Create a session cookie.
 * @example $.cookie('the_cookie', null);
 * @desc Delete a cookie by passing null as value. Keep in mind that you have to use the same path and domain
 *       used when the cookie was set.
 *
 * @param String name The name of the cookie.
 * @param String value The value of the cookie.
 * @param Object options An object literal containing key/value pairs to provide optional cookie attributes.
 * @option Number|Date expires Either an integer specifying the expiration date from now on in days or a Date object.
 *                             If a negative value is specified (e.g. a date in the past), the cookie will be deleted.
 *                             If set to null or omitted, the cookie will be a session cookie and will not be retained
 *                             when the the browser exits.
 * @option String path The value of the path atribute of the cookie (default: path of page that created the cookie).
 * @option String domain The value of the domain attribute of the cookie (default: domain of page that created the cookie).
 * @option Boolean secure If true, the secure attribute of the cookie will be set and the cookie transmission will
 *                        require a secure protocol (like HTTPS).
 * @type undefined
 *
 * @name $.cookie
 * @cat Plugins/Cookie
 * @author Klaus Hartl/klaus.hartl@stilbuero.de
 */

/**
 * Get the value of a cookie with the given name.
 *
 * @example $.cookie('the_cookie');
 * @desc Get the value of a cookie.
 *
 * @param String name The name of the cookie.
 * @return The value of the cookie.eee
 * @type String
 *
 * @name $.cookie
 * @cat Plugins/Cookie
 * @author Klaus Hartl/klaus.hartl@stilbuero.de
 */
jQuery.cookie = function(name, value, options) {
    if (typeof value != 'undefined') { // name and value given, set cookie
        options = options || {};
        if (value === null) {
            value = '';
            options.expires = -1;
        }
        var expires = '';
        if (options.expires && (typeof options.expires == 'number' || options.expires.toUTCString)) {
            var date;
            if (typeof options.expires == 'number') {
                date = new Date();
                date.setTime(date.getTime() + (options.expires * 24 * 60 * 60 * 1000));
            } else {
                date = options.expires;
            }
            expires = '; expires=' + date.toUTCString(); // use expires attribute, max-age is not supported by IE
        }
        // CAUTION: Needed to parenthesize options.path and options.domain
        // in the following expressions, otherwise they evaluate to undefined
        // in the packed version for some reason...
        var path = options.path ? '; path=' + (options.path) : '';
        var domain = options.domain ? '; domain=' + (options.domain) : '';
        var secure = options.secure ? '; secure' : '';
        document.cookie = [name, '=', encodeURIComponent(value), expires, path, domain, secure].join('');
    } else { // only name given, get cookie
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
};

var LoggedInWith = null;
var LoggedInWithURL = null;
var LoggedInWithTitle = null;

// popup function
(function($){
	$.fn.popupWindow = function(instanceSettings){

		return this.each(function(){

		$(this).click(function(){

		LoggedInWith = jQuery(this).attr('rel');
		LoggedInWithURL = jQuery(this).attr('href');
		LoggedInWithTitle = jQuery(this).attr('title');

		$.fn.popupWindow.defaultSettings = {
			centerBrowser:0, // center window over browser window? {1 (YES) or 0 (NO)}. overrides top and left
			centerScreen:0, // center window over entire screen? {1 (YES) or 0 (NO)}. overrides top and left
			height:500, // sets the height in pixels of the window.
			left:0, // left position when the window appears.
			location:1, // determines whether the address bar is displayed {1 (YES) or 0 (NO)}.
			menubar:1, // determines whether the menu bar is displayed {1 (YES) or 0 (NO)}.
			resizable:0, // whether the window can be resized {1 (YES) or 0 (NO)}. Can also be overloaded using resizable.
			scrollbars:0, // determines whether scrollbars appear on the window {1 (YES) or 0 (NO)}.
			status:0, // whether a status line appears at the bottom of the window {1 (YES) or 0 (NO)}.
			width:500, // sets the width in pixels of the window.
			windowName:null, // name of window set from the name attribute of the element that invokes the click
			windowURL:null, // url used for the popup
			top:0, // top position when the window appears.
			toolbar:1 // determines whether a toolbar (includes the forward and back buttons) is displayed {1 (YES) or 0 (NO)}.
		};

		settings = $.extend({}, $.fn.popupWindow.defaultSettings, instanceSettings || {});

		var windowFeatures =    'height=' + settings.height +
								',width=' + settings.width +
								',toolbar=' + settings.toolbar +
								',scrollbars=' + settings.scrollbars +
								',status=' + settings.status +
								',resizable=' + settings.resizable +
								',location=' + settings.location +
								',menuBar=' + settings.menubar;

				settings.windowName = this.name || settings.windowName;
				settings.windowURL = this.href || settings.windowURL;
				var centeredY,centeredX;

				if(settings.centerBrowser){

					if ($.browser.msie) {//hacked together for IE browsers
						centeredY = (window.screenTop - 120) + ((((document.documentElement.clientHeight + 120)/2) - (settings.height/2)));
						centeredX = window.screenLeft + ((((document.body.offsetWidth + 20)/2) - (settings.width/2)));
					}else{
						centeredY = window.screenY + (((window.outerHeight/2) - (settings.height/2)));
						centeredX = window.screenX + (((window.outerWidth/2) - (settings.width/2)));
					}
					window.open(settings.windowURL, settings.windowName, windowFeatures+',left=' + centeredX +',top=' + centeredY).focus();
				}else if(settings.centerScreen){
					centeredY = (screen.height - settings.height)/2;
					centeredX = (screen.width - settings.width)/2;
					window.open(settings.windowURL, settings.windowName, windowFeatures+',left=' + centeredX +',top=' + centeredY).focus();
				}else{
					window.open(settings.windowURL, settings.windowName, windowFeatures+',left=' + settings.left +',top=' + settings.top).focus();
				}
				return false;
			});

		});
	};
})(jQuery);

// default value function
(function($) {

	$.fn.defaultvalue = function() {

		// Scope
		var elements = this;
		var args = arguments;
		var c = 0;

		return(
			elements.each(function() {

				// Default values within scope
				var el = $(this);
				var def = args[c++];

				el.val(def).focus(function() {
					if(el.val() == def) {
						el.val("");
						jQuery(el).removeClass("empty");
						jQuery("div#scroller a").each(function() {
						if (jQuery(this).attr("title") != "") {
					      	if (jQuery("#loginsearch_flexselect_dropdown ul li:contains('" + jQuery(this).attr('title') + "')").length != 0) {
					      		jQuery(this).addClass("present");
					      		jQuery("#scroller").addClass("filtered");
					      	} else {
					      		jQuery(this).removeClass("present");
					      		jQuery("#scroller").addClass("filtered");
					      	}
					      	if (jQuery("#loginsearch_flexselect").val() == "")
						    {
						    	jQuery("#scroller").removeClass("filtered");
						    	jQuery(this).removeClass("present");
						    }
					    }

					      });

					}
					el.blur(function() {
						if(el.val() == "") {
							el.val(def);
							jQuery(el).addClass("empty");
						}
					});
				});

			})
		);
	}
})(jQuery)

var numOfAccounts = null;

function ulxClose() {
	$("#overlay").fadeOut("slow");
	$("#popup").fadeOut("fast");
	$("#scroller a").removeAttr("style");
}

function ulxControlClick() {
	if ($.cookie("ulx-status") == null) {
		$("#overlay").fadeIn("fast");
		$("#popup").fadeIn("slow");

		if ($.cookie("ulx-last") == null) {
			$("#maintitle").html("Sign in to <strong>Identity-hub</strong>");
			$("#subtitle").html("with 1 of the accounts below");
			$("#content2, #more, #moretext").hide();
			$("#search, #whatisthis").show();
		} else {
			$("#maintitle").html("Recently you signed in to <strong>Identity-hub</strong>");
			$("#subtitle").html("using this account...");
			$("#content2").show().html("<div id='scroller2' style='overflow: hidden; height: 50px;'><a href='login_" + $.cookie('ulx-last') + ".html' rel='" + $.cookie('ulx-last') + "' title='" + $.cookie('ulx-last-title') + "'><img src='./images/icon-" + $.cookie('ulx-last') + ".png' /></a></div>");
			initPopups();
			$("#more, #moretext").show();
			$("#moretext").html("...or sign in with 1 of the accounts below:");

			$("#search, #content, #whatisthis").hide();
		}


	} else {

		$.cookie("ulx-status", null);
		$("body").removeClass("loggedin").addClass("loggedout");

	}

	return false;
}

function LogIn() {
	$.cookie("ulx-status", LoggedInWith);
	$.cookie("ulx-last", LoggedInWith);
	$.cookie("ulx-last-title", LoggedInWithTitle);
	$("body").removeClass("loggedout").addClass("loggedin");
	ulxClose();
	$("#ulx-control").attr("class", $.cookie("ulx-last"));
	$("input#loginsearch_flexselect").val("").focus();
}

function initPopups() {
	jQuery("div#scroller a:not(.samewindow), div#scroller2 a:not(.samewindow)").popupWindow({
		windowName:'login',
		width: 479,
		height: 436,
		centerScreen:1
	});
}

function initSearchBox() {
	$("select#loginsearch").flexselect();
	$("input#loginsearch_flexselect").defaultvalue("or search accounts, i.e. Saint-Etienne University").addClass("empty");
}

function initSite() {
	numOfAccounts = $("select#loginsearch option").length;

	$("#ulx-control").attr("class", $.cookie("ulx-last"));

	$("#overlay, #popup, #content2, #more").hide();

	if ($.cookie("ulx-status") != null) {
		$("body").addClass("loggedin");
	} else {
		$("body").addClass("loggedout");
	}

	$("#ulx-control").click(function() {
		ulxControlClick();
	});

	$("#close, #overlay").click(function() {
		ulxClose();
	});

	$("#moreoptions").click(function() {
		$("#content, #search").show();
		$("#more").hide();
		$("#scroller a[rel='" + $.cookie("ulx-last") + "']").attr("style","display: none !important");
	});

	$("#what").click(function() {
		$("#whatisthis").toggleClass("show");
	});

	initSearchBox();
	initPopups();
}

$(document).ready(function() {
	initSite();
});
















