define( [
	"venv/static/js/jquery/src/css/var/cssExpand"
], function( cssExpand ) {
	"use strict";

	return new RegExp( cssExpand.join( "|" ), "i" );
} );
