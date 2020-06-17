define( [
	"venv/static/js/jquery/src/var/support"
], function( support ) {

"use strict";

support.focusin = "onfocusin" in window;

return support;

} );
