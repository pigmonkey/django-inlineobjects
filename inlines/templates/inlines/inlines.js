{% load inlines_tags %}
<script type="text/javascript">
    function InlineInit() {
        var textarea = document.getElementById('id_{{ field }}');
        var target_div = textarea.parentNode;
        var content = ''
        content += '{% get_inline_types as inline_list %}'
        content += '<label>{{ field|capfirst }} inlines:</label>'

        content += '<strong>Inline type:</strong> '
        content += '<select id="id_inline_content_type" onchange="document.getElementById(\'lookup_id_inline\').href = \'../../../\'+this.value+\'/\';" style="margin-right:20px;">'
        content += '  <option>----------</option>'
        content += '  {% for inline in inline_list %}'
        content += '  <option value="{{ inline.content_type.app_label }}/{{ inline.content_type.model }}">{{ inline.content_type.app_label|capfirst }}: {{ inline.content_type.model|capfirst }}</option>'
        content += '  {% endfor %}'
        content += '</select> '

        content += '<strong>Object:</strong> '
        content += '<input type="text" class="vIntegerField" id="id_inline" size="10" /> '
        content += '<a id="lookup_id_inline" href="#" class="related-lookup" onclick="if(document.getElementById(\'id_inline_content_type\').value != \'----------\') { return showRelatedObjectLookupPopup(this); }" style="margin-right:20px;"><img src="{{ STATIC_URL }}admin/img/selector-search.gif" width="16" height="16" alt="Lookup" /></a> '

        content += '<strong>Size:</strong> '
        content += '<select id="id_inline_size" style="margin-right:20px;">'
        content += '  <option>----------</option>'
        content += '  <option value="thumbnail">Thumbnail</option>'
        content += '  <option value="small">Small</option>'
        content += '  <option value="medium">Medium</option>'
        content += '  <option value="large">Large</option>'
        content += '  <option value="original">Original</option>'
        content += '</select>'

        content += '<strong>Align:</strong> '
        content += '<select id="id_inline_align">'
        content += '  <option>----------</option>'
        content += '  <option value="left">Left</option>'
        content += '  <option value="right">Right</option>'
        content += '  <option value="center">Center</option>'
        content += '</select>'

        content += '<input type="button" value="Add" style="margin-left:20px;" onclick="return insertInline(document.getElementById(\'id_inline_content_type\').value, document.getElementById(\'id_inline\').value, document.getElementById(\'id_inline_size\').value, document.getElementById(\'id_inline_align\').value)" />'
        content += '<p class="help">Insert inlines into your {{ field }} by choosing an inline type, then an object, then a class.</p>'

        var div = document.createElement('div');
        div.setAttribute('style', 'margin-top:10px;');
        div.innerHTML = content;

        target_div.insertBefore(div, textarea.nextSibling);
    }

    function insertInline(type, id, size, align) {
        if (type != '----------' && id != '') {
            if (size != '----------' ) {
                var size_attribute = ' size="'+size+'"';
            } else {
                var size_attribute = '';
            }

            if (align != '----------' ) {
                var align_attribute = ' align="'+align+'"';
            } else {
                var align_attribute = '';
            }

            var inline = '<inline type="'+type.replace('/', '.')+'" id="'+id+'"'+size_attribute+''+align_attribute+'></inline>';
            var textarea = document.getElementById('id_{{ field }}');
            var scrollPos = textarea.scrollTop;
            var strPos = 0;
            var br = ((textarea.selectionStart || textarea.selectionStart == '0') ? 
                "ff" : (document.selection ? "ie" : false ) );
            if (br == "ie") { 
                textarea.focus();
                var range = document.selection.createRange();
                range.moveStart ('character', -textarea.value.length);
                strPos = range.text.length;
            }
            else if (br == "ff") strPos = textarea.selectionStart;

            var front = (textarea.value).substring(0,strPos);  
            var back = (textarea.value).substring(strPos,textarea.value.length); 
            textarea.value=front+inline+back;
            strPos = strPos + inline.length;
            if (br == "ie") { 
                textarea.focus();
                var range = document.selection.createRange();
                range.moveStart ('character', -textarea.value.length);
                range.moveStart ('character', strPos);
                range.moveEnd ('character', 0);
                range.select();
            }
            else if (br == "ff") {
                textarea.selectionStart = strPos;
                textarea.selectionEnd = strPos;
                textarea.focus();
            }
            textarea.scrollTop = scrollPos;
      }
    }

    addEvent(window, 'load', InlineInit);
</script>
