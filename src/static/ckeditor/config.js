/*
Copyright (c) 2003-2011, CKSource - Frederico Knabben. All rights reserved.
For licensing, see LICENSE.html or http://ckeditor.com/license
*/

CKEDITOR.editorConfig = function( config )
{
	// Define changes to default configuration here. For example:
	// config.language = 'fr';
	// config.uiColor = '#AADC6E';
	config.toolbar = [
	 	['Source','-','NewPage'],
	 	['Cut','Copy','Paste','PasteText','PasteFromWord','-','Print'],
	 	['Undo','Redo','-','Find','Replace','-','SelectAll','RemoveFormat'],
	 	'/',
	 	['Bold','Italic','Underline'],
	 	['NumberedList','BulletedList','-','Outdent','Indent','Blockquote'],
	 	['Link','Unlink','Anchor'],	['Image'],
	 	['Styles','Format']
 	 ];
	config.contentsCss = "/editor/default.css"
};
